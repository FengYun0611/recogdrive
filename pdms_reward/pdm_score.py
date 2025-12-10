import numpy as np
import numpy.typing as npt

from typing import List

from nuplan.common.actor_state.state_representation import StateSE2, TimePoint
from nuplan.common.actor_state.ego_state import EgoState
from nuplan.common.geometry.convert import relative_to_absolute_poses
from nuplan.planning.simulation.trajectory.trajectory_sampling import TrajectorySampling
from nuplan.planning.simulation.trajectory.interpolated_trajectory import InterpolatedTrajectory
from nuplan.planning.simulation.planner.ml_planner.transform_utils import (
    _get_fixed_timesteps,
    _se2_vel_acc_to_ego_state,
)

from pdms_reward.dataclasses import PDMResults, Trajectory
from pdms_reward.simulation.pdm_simulator import PDMSimulator
from pdms_reward.scoring.pdm_scorer import PDMScorer
from pdms_reward.observation.pdm_observation import PDMObservation
from pdms_reward.observation.pdm_occupancy_map import PDMDrivableMap
from pdms_reward.utils.pdm_path import PDMPath
from pdms_reward.utils.pdm_array_representation import ego_states_to_state_array
from pdms_reward.utils.pdm_enums import MultiMetricIndex, WeightedMetricIndex

try:
    from navsim.planning.metric_caching.metric_cache import MetricCache
    METRIC_CACHE_AVAILABLE = True
except ImportError:
    METRIC_CACHE_AVAILABLE = False
    MetricCache = None


def transform_trajectory(pred_trajectory: Trajectory, initial_ego_state: EgoState) -> InterpolatedTrajectory:
    """
    Transform trajectory in global frame and return as InterpolatedTrajectory
    :param pred_trajectory: trajectory dataclass in ego frame
    :param initial_ego_state: nuPlan's ego state object
    :return: nuPlan's InterpolatedTrajectory
    """

    future_sampling = pred_trajectory.trajectory_sampling
    timesteps = _get_fixed_timesteps(initial_ego_state, future_sampling.time_horizon, future_sampling.interval_length)

    relative_poses = np.array(pred_trajectory.poses, dtype=np.float64)
    relative_states = [StateSE2.deserialize(pose) for pose in relative_poses]
    absolute_states = relative_to_absolute_poses(initial_ego_state.rear_axle, relative_states)

    # NOTE: velocity and acceleration ignored by LQR + bicycle model
    agent_states = [
        _se2_vel_acc_to_ego_state(
            state,
            [0.0, 0.0],
            [0.0, 0.0],
            timestep,
            initial_ego_state.car_footprint.vehicle_parameters,
        )
        for state, timestep in zip(absolute_states, timesteps)
    ]

    # NOTE: maybe make addition of initial_ego_state optional
    return InterpolatedTrajectory([initial_ego_state] + agent_states)


def get_trajectory_as_array(
    trajectory: InterpolatedTrajectory,
    future_sampling: TrajectorySampling,
    start_time: TimePoint,
) -> npt.NDArray[np.float64]:
    """
    Interpolated trajectory and return as numpy array
    :param trajectory: nuPlan's InterpolatedTrajectory object
    :param future_sampling: Sampling parameters for interpolation
    :param start_time: TimePoint object of start
    :return: Array of interpolated trajectory states.
    """

    times_s = np.arange(
        0.0,
        future_sampling.time_horizon + future_sampling.interval_length,
        future_sampling.interval_length,
    )
    times_s += start_time.time_s
    times_us = [int(time_s * 1e6) for time_s in times_s]
    times_us = np.clip(times_us, trajectory.start_time.time_us, trajectory.end_time.time_us)
    time_points = [TimePoint(time_us) for time_us in times_us]

    trajectory_ego_states: List[EgoState] = trajectory.get_state_at_times(time_points)

    return ego_states_to_state_array(trajectory_ego_states)


def pdm_score_direct(
    model_trajectory: Trajectory,
    initial_ego_state: EgoState,
    observation: PDMObservation,
    centerline: PDMPath,
    route_lane_ids: List[str],
    drivable_area_map: PDMDrivableMap,
    future_sampling: TrajectorySampling,
    simulator: PDMSimulator,
    scorer: PDMScorer,
    reference_trajectory: InterpolatedTrajectory = None,
) -> PDMResults:
    """
    Runs PDM-Score with direct inputs without requiring MetricCache.
    
    This is the recommended function for standalone usage where you have
    trajectory and map information directly.
    
    :param model_trajectory: Predicted trajectory in ego frame
    :param initial_ego_state: Initial ego vehicle state
    :param observation: PDM observation with detected objects
    :param centerline: Centerline path for progress calculation
    :param route_lane_ids: List of lane IDs on the planned route
    :param drivable_area_map: Map of drivable areas
    :param future_sampling: Sampling parameters for future trajectory
    :param simulator: PDM simulator instance
    :param scorer: PDM scorer instance
    :param reference_trajectory: Optional reference trajectory (if None, uses predicted trajectory)
    :return: Dataclass of PDM-Subscores
    
    Example:
        >>> from pdms_reward import pdm_score_direct, PDMSimulator, PDMScorer
        >>> from pdms_reward.observation import PDMObservation, PDMDrivableMap
        >>> from pdms_reward.utils import PDMPath
        >>> 
        >>> # Initialize simulator and scorer
        >>> simulator = PDMSimulator(proposal_sampling)
        >>> scorer = PDMScorer(proposal_sampling)
        >>> 
        >>> # Prepare inputs
        >>> # ... create observation, centerline, drivable_area_map, etc.
        >>> 
        >>> # Compute score
        >>> results = pdm_score_direct(
        >>>     model_trajectory=trajectory,
        >>>     initial_ego_state=ego_state,
        >>>     observation=observation,
        >>>     centerline=centerline,
        >>>     route_lane_ids=lane_ids,
        >>>     drivable_area_map=drivable_map,
        >>>     future_sampling=future_sampling,
        >>>     simulator=simulator,
        >>>     scorer=scorer
        >>> )
        >>> print(f"Score: {results.score}")
    """
    
    # Transform predicted trajectory to absolute frame
    pred_trajectory = transform_trajectory(model_trajectory, initial_ego_state)
    
    # Use reference trajectory if provided, otherwise use predicted trajectory as reference
    if reference_trajectory is None:
        reference_trajectory = pred_trajectory
    
    # Convert trajectories to array format
    pdm_states = get_trajectory_as_array(reference_trajectory, future_sampling, initial_ego_state.time_point)
    pred_states = get_trajectory_as_array(pred_trajectory, future_sampling, initial_ego_state.time_point)
    
    # Concatenate for batch processing
    trajectory_states = np.concatenate([pdm_states[None, ...], pred_states[None, ...]], axis=0)
    
    # Simulate trajectory execution
    simulated_states = simulator.simulate_proposals(trajectory_states, initial_ego_state)
    
    # Score the simulated trajectories
    scores = scorer.score_proposals(
        simulated_states,
        observation,
        centerline,
        route_lane_ids,
        drivable_area_map,
    )
    
    # Extract scores for predicted trajectory (index 1)
    pred_idx = 1
    
    no_at_fault_collisions = scorer._multi_metrics[MultiMetricIndex.NO_COLLISION, pred_idx]
    drivable_area_compliance = scorer._multi_metrics[MultiMetricIndex.DRIVABLE_AREA, pred_idx]
    
    ego_progress = scorer._weighted_metrics[WeightedMetricIndex.PROGRESS, pred_idx]
    time_to_collision_within_bound = scorer._weighted_metrics[WeightedMetricIndex.TTC, pred_idx]
    comfort = scorer._weighted_metrics[WeightedMetricIndex.COMFORTABLE, pred_idx]
    driving_direction_compliance = scorer._weighted_metrics[WeightedMetricIndex.DRIVING_DIRECTION, pred_idx]
    
    score = scores[pred_idx]
    
    return PDMResults(
        no_at_fault_collisions,
        drivable_area_compliance,
        ego_progress,
        time_to_collision_within_bound,
        comfort,
        driving_direction_compliance,
        score,
    )


def pdm_score(
    metric_cache: MetricCache,
    model_trajectory: Trajectory,
    future_sampling: TrajectorySampling,
    simulator: PDMSimulator,
    scorer: PDMScorer,
) -> PDMResults:
    """
    Runs PDM-Score with MetricCache (legacy interface).
    
    Note: This function requires the navsim package. For standalone usage
    without navsim, use pdm_score_direct() instead.
    
    :param metric_cache: Metric cache dataclass from navsim
    :param model_trajectory: Predicted trajectory in ego frame
    :param future_sampling: Sampling parameters for future trajectory
    :param simulator: PDM simulator instance
    :param scorer: PDM scorer instance
    :return: Dataclass of PDM-Subscores
    """
    if not METRIC_CACHE_AVAILABLE:
        raise ImportError(
            "MetricCache requires navsim package. For standalone usage, "
            "use pdm_score_direct() instead which takes individual components."
        )
    
    return pdm_score_direct(
        model_trajectory=model_trajectory,
        initial_ego_state=metric_cache.ego_state,
        observation=metric_cache.observation,
        centerline=metric_cache.centerline,
        route_lane_ids=metric_cache.route_lane_ids,
        drivable_area_map=metric_cache.drivable_area_map,
        future_sampling=future_sampling,
        simulator=simulator,
        scorer=scorer,
        reference_trajectory=metric_cache.trajectory,
    )
