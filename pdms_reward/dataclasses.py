"""
Dataclasses for PDMS Reward Function

This module contains the essential dataclasses used in PDMS computation.
Extracted from navsim.common.dataclasses for standalone usage.
"""

from dataclasses import dataclass
import numpy as np
import numpy.typing as npt
from nuplan.planning.simulation.trajectory.trajectory_sampling import TrajectorySampling


@dataclass
class Trajectory:
    """Trajectory dataclass in NAVSIM."""

    poses: npt.NDArray[np.float32]  # local coordinates
    trajectory_sampling: TrajectorySampling = TrajectorySampling(time_horizon=4, interval_length=0.5)

    def __post_init__(self):
        assert self.poses.ndim == 2, "Trajectory poses should have two dimensions for samples and poses."
        assert (
            self.poses.shape[0] == self.trajectory_sampling.num_poses
        ), "Trajectory poses and sampling have unequal number of poses."
        assert self.poses.shape[1] == 3, "Trajectory requires (x, y, heading) at last dim."


@dataclass
class PDMResults:
    """Helper dataclass to record PDM results."""

    no_at_fault_collisions: float
    drivable_area_compliance: float

    ego_progress: float
    time_to_collision_within_bound: float
    comfort: float
    driving_direction_compliance: float

    score: float

    def to_dict(self):
        """Convert to dictionary for easy serialization."""
        return {
            'no_at_fault_collisions': self.no_at_fault_collisions,
            'drivable_area_compliance': self.drivable_area_compliance,
            'ego_progress': self.ego_progress,
            'time_to_collision_within_bound': self.time_to_collision_within_bound,
            'comfort': self.comfort,
            'driving_direction_compliance': self.driving_direction_compliance,
            'score': self.score,
        }
