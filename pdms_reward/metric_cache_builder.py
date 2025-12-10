"""
MetricCache Builder Module

This module provides utilities to build MetricCache objects from scenario data,
making it easier to use PDMS scoring without manually constructing all components.

从场景数据构建MetricCache对象的工具模块，
简化PDMS评分的使用，无需手动构造所有组件。
"""

from typing import Dict, Any, List, Optional
from pathlib import Path

import numpy as np

from nuplan.common.actor_state.agent import Agent
from nuplan.common.actor_state.static_object import StaticObject
from nuplan.common.actor_state.tracked_objects_types import AGENT_TYPES
from nuplan.common.actor_state.tracked_objects import TrackedObjects
from nuplan.common.actor_state.oriented_box import OrientedBox
from nuplan.common.actor_state.state_representation import StateSE2, StateVector2D
from nuplan.planning.scenario_builder.abstract_scenario import AbstractScenario
from nuplan.planning.simulation.observation.observation_type import DetectionsTracks
from nuplan.planning.simulation.planner.abstract_planner import PlannerInitialization, PlannerInput
from nuplan.planning.simulation.trajectory.trajectory_sampling import TrajectorySampling
from nuplan.planning.simulation.simulation_time_controller.simulation_iteration import SimulationIteration
from nuplan.planning.simulation.history.simulation_history_buffer import SimulationHistoryBuffer

from pdms_reward.observation.pdm_observation import PDMObservation
from pdms_reward.proposal.batch_idm_policy import BatchIDMPolicy
from pdms_reward.pdm_closed_planner import PDMClosedPlanner

# Try to import MetricCache, if available
try:
    from navsim.planning.metric_caching.metric_cache import MetricCache
    from navsim.planning.metric_caching.metric_caching_utils import StateInterpolator
    METRIC_CACHE_AVAILABLE = True
except ImportError:
    METRIC_CACHE_AVAILABLE = False
    MetricCache = None
    StateInterpolator = None


class MetricCacheBuilder:
    """
    Builder class to construct MetricCache from scenario data.
    
    构建器类，从场景数据构建MetricCache。
    
    This class simplifies the process of creating a MetricCache by handling:
    - PDM-Closed planner initialization and trajectory generation
    - Observation interpolation to higher temporal resolution
    - Extraction of centerline and drivable area map
    
    此类简化了创建MetricCache的过程，处理：
    - PDM-Closed规划器初始化和轨迹生成
    - 观察数据插值到更高时间分辨率
    - 提取中心线和可行驶区域地图
    
    Example:
        >>> from pdms_reward.metric_cache_builder import MetricCacheBuilder
        >>> 
        >>> # Create builder
        >>> builder = MetricCacheBuilder()
        >>> 
        >>> # Build MetricCache from scenario
        >>> metric_cache = builder.build_from_scenario(scenario)
        >>> 
        >>> # Use with pdm_score
        >>> results = pdm_score(
        >>>     metric_cache,
        >>>     model_trajectory,
        >>>     future_sampling,
        >>>     simulator,
        >>>     scorer
        >>> )
    """
    
    def __init__(
        self,
        future_sampling: Optional[TrajectorySampling] = None,
        proposal_sampling: Optional[TrajectorySampling] = None,
        map_radius: float = 100.0,
    ):
        """
        Initialize MetricCacheBuilder.
        
        初始化MetricCacheBuilder。
        
        :param future_sampling: Sampling parameters for future trajectory (default: 5s @ 0.1s)
        :param proposal_sampling: Sampling parameters for proposals (default: 4s @ 0.1s)
        :param map_radius: Radius for map queries in meters (default: 100m)
        """
        if not METRIC_CACHE_AVAILABLE:
            raise ImportError(
                "MetricCache requires navsim package. "
                "Install with: pip install navsim"
            )
        
        # Default sampling parameters
        self._future_sampling = future_sampling or TrajectorySampling(num_poses=50, interval_length=0.1)
        self._proposal_sampling = proposal_sampling or TrajectorySampling(num_poses=40, interval_length=0.1)
        self._map_radius = map_radius
        
        # Initialize PDM-Closed planner
        self._pdm_closed = PDMClosedPlanner(
            trajectory_sampling=self._future_sampling,
            proposal_sampling=self._proposal_sampling,
            idm_policies=BatchIDMPolicy(
                speed_limit_fraction=[0.2, 0.4, 0.6, 0.8, 1.0],
                fallback_target_velocity=15.0,
                min_gap_to_lead_agent=1.0,
                headway_time=1.5,
                accel_max=1.5,
                decel_max=3.0,
            ),
            lateral_offsets=[-1.0, 1.0],
            map_radius=self._map_radius,
        )
    
    def _get_planner_inputs(self, scenario: AbstractScenario) -> tuple:
        """
        Creates planner input arguments from scenario object.
        
        从场景对象创建规划器输入参数。
        
        :param scenario: scenario object of nuPlan
        :return: tuple of planner input and initialization objects
        """
        # Initialize Planner
        planner_initialization = PlannerInitialization(
            route_roadblock_ids=scenario.get_route_roadblock_ids(),
            mission_goal=scenario.get_mission_goal(),
            map_api=scenario.map_api,
        )
        
        history = SimulationHistoryBuffer.initialize_from_list(
            buffer_size=1,
            ego_states=[scenario.initial_ego_state],
            observations=[scenario.initial_tracked_objects],
        )
        
        planner_input = PlannerInput(
            iteration=SimulationIteration(index=0, time_point=scenario.start_time),
            history=history,
            traffic_light_data=list(scenario.get_traffic_light_status_at_iteration(0)),
        )
        
        return planner_input, planner_initialization
    
    def _interpolate_gt_observation(self, scenario: AbstractScenario) -> PDMObservation:
        """
        Helper function to interpolate detections tracks to higher temporal resolution.
        
        将检测轨迹插值到更高时间分辨率的辅助函数。
        
        :param scenario: scenario interface of nuPlan framework
        :return: observation object of PDM-Closed
        """
        # State size: (time, x, y, heading, velo_x, velo_y)
        state_size = 6
        
        time_horizon = 5.0  # [s]
        resolution_step = 0.5  # [s]
        interpolate_step = 0.1  # [s]
        
        scenario_step = scenario.database_interval  # [s]
        
        # Sample detection tracks at 2Hz
        relative_time_s = np.arange(0, (time_horizon * 1 / resolution_step) + 1, 1, dtype=float) * resolution_step
        
        gt_indices = np.arange(0, int(time_horizon / scenario_step) + 1, int(resolution_step / scenario_step))
        gt_detection_tracks = [
            scenario.get_tracked_objects_at_iteration(iteration=iteration) for iteration in gt_indices
        ]
        
        detection_tracks_states: Dict[str, Any] = {}
        unique_detection_tracks: Dict[str, Any] = {}
        
        for time_s, detection_track in zip(relative_time_s, gt_detection_tracks):
            for tracked_object in detection_track.tracked_objects:
                token = tracked_object.track_token
                
                # Extract states for dynamic and static objects
                tracked_state = np.zeros(state_size, dtype=np.float64)
                tracked_state[:4] = (
                    time_s,
                    tracked_object.center.x,
                    tracked_object.center.y,
                    tracked_object.center.heading,
                )
                
                if tracked_object.tracked_object_type in AGENT_TYPES:
                    # Extract additional states for dynamic objects
                    tracked_state[4:] = (
                        tracked_object.velocity.x,
                        tracked_object.velocity.y,
                    )
                
                # Found new object
                if token not in detection_tracks_states.keys():
                    detection_tracks_states[token] = [tracked_state]
                    unique_detection_tracks[token] = tracked_object
                else:
                    # Object already existed
                    detection_tracks_states[token].append(tracked_state)
        
        # Create time interpolators
        detection_interpolators: Dict[str, StateInterpolator] = {}
        for token, states_list in detection_tracks_states.items():
            states = np.array(states_list, dtype=np.float64)
            detection_interpolators[token] = StateInterpolator(states)
        
        # Interpolate at 10Hz
        interpolated_time_s = np.arange(0, int(time_horizon / interpolate_step) + 1, 1, dtype=float) * interpolate_step
        
        interpolated_detection_tracks = []
        for time_s in interpolated_time_s:
            interpolated_tracks = []
            for token, interpolator in detection_interpolators.items():
                initial_detection_track = unique_detection_tracks[token]
                interpolated_state = interpolator.interpolate(time_s)
                
                if interpolator.start_time == interpolator.end_time:
                    interpolated_tracks.append(initial_detection_track)
                elif interpolated_state is not None:
                    tracked_type = initial_detection_track.tracked_object_type
                    metadata = initial_detection_track.metadata
                    
                    oriented_box = OrientedBox(
                        StateSE2(*interpolated_state[:3]),
                        initial_detection_track.box.length,
                        initial_detection_track.box.width,
                        initial_detection_track.box.height,
                    )
                    
                    if tracked_type in AGENT_TYPES:
                        velocity = StateVector2D(*interpolated_state[3:])
                        detection_track = Agent(
                            tracked_object_type=tracked_type,
                            oriented_box=oriented_box,
                            velocity=velocity,
                            metadata=initial_detection_track.metadata,
                        )
                    else:
                        detection_track = StaticObject(
                            tracked_object_type=tracked_type,
                            oriented_box=oriented_box,
                            metadata=metadata,
                        )
                    
                    interpolated_tracks.append(detection_track)
            interpolated_detection_tracks.append(DetectionsTracks(TrackedObjects(interpolated_tracks)))
        
        # Convert to PDM observation
        pdm_observation = PDMObservation(
            self._future_sampling,
            self._proposal_sampling,
            self._map_radius,
            observation_sample_res=1,
        )
        pdm_observation.update_detections_tracks(interpolated_detection_tracks)
        return pdm_observation
    
    def build_from_scenario(
        self,
        scenario: AbstractScenario,
        file_path: Optional[Path] = None,
    ) -> 'MetricCache':
        """
        Build MetricCache from a nuPlan scenario.
        
        从nuPlan场景构建MetricCache。
        
        This method handles all the complex steps of creating a MetricCache:
        1. Initialize PDM-Closed planner with scenario
        2. Generate reference trajectory using PDM-Closed
        3. Interpolate observation data to higher resolution
        4. Extract centerline and drivable area map
        5. Assemble all components into MetricCache
        
        此方法处理创建MetricCache的所有复杂步骤：
        1. 使用场景初始化PDM-Closed规划器
        2. 使用PDM-Closed生成参考轨迹
        3. 将观察数据插值到更高分辨率
        4. 提取中心线和可行驶区域地图
        5. 将所有组件组装成MetricCache
        
        :param scenario: nuPlan scenario object
        :param file_path: Optional path for caching (not used for computation)
        :return: MetricCache object ready for use with pdm_score
        
        Example:
            >>> from nuplan.planning.scenario_builder import ... # load scenario
            >>> builder = MetricCacheBuilder()
            >>> metric_cache = builder.build_from_scenario(scenario)
            >>> 
            >>> # Now use with pdm_score
            >>> results = pdm_score(metric_cache, trajectory, ...)
        """
        if not METRIC_CACHE_AVAILABLE:
            raise ImportError("MetricCache requires navsim package")
        
        # Get planner inputs and initialize
        planner_input, planner_initialization = self._get_planner_inputs(scenario)
        self._pdm_closed.initialize(planner_initialization)
        
        # Generate reference trajectory using PDM-Closed
        pdm_closed_trajectory = self._pdm_closed.compute_planner_trajectory(planner_input)
        
        # Interpolate observations
        observation = self._interpolate_gt_observation(scenario)
        
        # Create file path if not provided
        if file_path is None:
            file_path = Path(f"/tmp/metric_cache_{scenario.token}.pkl")
        
        # Create and return MetricCache
        return MetricCache(
            file_path=file_path,
            trajectory=pdm_closed_trajectory,
            ego_state=scenario.initial_ego_state,
            observation=observation,
            centerline=self._pdm_closed._centerline,
            route_lane_ids=list(self._pdm_closed._route_lane_dict.keys()),
            drivable_area_map=self._pdm_closed._drivable_area_map,
        )


def build_metric_cache_from_scenario(
    scenario: AbstractScenario,
    future_sampling: Optional[TrajectorySampling] = None,
    proposal_sampling: Optional[TrajectorySampling] = None,
    map_radius: float = 100.0,
) -> 'MetricCache':
    """
    Convenience function to build MetricCache from scenario.
    
    从场景构建MetricCache的便捷函数。
    
    :param scenario: nuPlan scenario object
    :param future_sampling: Optional sampling parameters for future trajectory
    :param proposal_sampling: Optional sampling parameters for proposals
    :param map_radius: Radius for map queries in meters
    :return: MetricCache object
    
    Example:
        >>> from pdms_reward.metric_cache_builder import build_metric_cache_from_scenario
        >>> 
        >>> # Simple one-line creation
        >>> metric_cache = build_metric_cache_from_scenario(scenario)
        >>> 
        >>> # Use with pdm_score
        >>> results = pdm_score(metric_cache, model_trajectory, ...)
    """
    builder = MetricCacheBuilder(future_sampling, proposal_sampling, map_radius)
    return builder.build_from_scenario(scenario)
