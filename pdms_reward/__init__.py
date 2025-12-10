"""
PDMS Reward Function Module

完整的PDMS（Planning Decision Making Scoring）计算方法提取
Complete PDMS (Planning Decision Making Scoring) computation extraction

此模块包含了完整的PDMS计算流程，可以作为独立的奖励函数在其他项目中使用。
This module contains the complete PDMS computation pipeline and can be used 
as a standalone reward function in other projects.

主要组件 / Main Components:
- pdm_score: 主要的PDMS评分函数 / Main PDMS scoring function
- scoring: 评分相关模块 / Scoring related modules
- simulation: 模拟器模块 / Simulator modules
- observation: 观察模块 / Observation modules
- utils: 工具函数和类 / Utility functions and classes
- proposal: 提案生成模块 / Proposal generation modules
- dataclasses: 数据类定义 / Dataclass definitions

使用示例 / Usage Example:
    from pdms_reward import pdm_score_direct, PDMResults
    from pdms_reward.simulation import PDMSimulator
    from pdms_reward.scoring import PDMScorer
    
    # Initialize simulator and scorer
    simulator = PDMSimulator(proposal_sampling)
    scorer = PDMScorer(proposal_sampling)
    
    # Calculate PDMS score directly with trajectory and map data
    results = pdm_score_direct(
        model_trajectory=trajectory,
        initial_ego_state=ego_state,
        observation=observation,
        centerline=centerline,
        route_lane_ids=lane_ids,
        drivable_area_map=drivable_map,
        future_sampling=future_sampling,
        simulator=simulator,
        scorer=scorer
    )
    
    print(f"PDMS Score: {results.score}")
    print(f"Collision Safety: {results.no_at_fault_collisions}")
"""

from .pdm_score import pdm_score, pdm_score_direct, transform_trajectory, get_trajectory_as_array
from .dataclasses import PDMResults, Trajectory

# Import scoring components
from .scoring import PDMScorer, PDMScorerConfig, ego_is_comfortable, get_collision_type

# Import simulation components
from .simulation import PDMSimulator, BatchKinematicBicycleModel, BatchLQRTracker

# Import observation components
from .observation import PDMObservation, PDMDrivableMap, PDMOccupancyMap, PDMObjectManager

# Import utility components
from .utils import (
    ego_state_to_state_array,
    ego_states_to_state_array,
    state_array_to_coords_array,
    coords_array_to_polygon_array,
    BBCoordsIndex,
    EgoAreaIndex,
    MultiMetricIndex,
    StateIndex,
    WeightedMetricIndex,
    convert_absolute_to_relative_se2_array,
    parallel_discrete_path,
    PDMPath,
    PDMEmergencyBrake,
)

# Import proposal components
from .proposal import BatchIDMPolicy, PDMGenerator, PDMProposalManager

# Import planner components (if needed for complete functionality)
from .abstract_pdm_planner import AbstractPDMPlanner
from .abstract_pdm_closed_planner import AbstractPDMClosedPlanner
from .pdm_closed_planner import PDMClosedPlanner

__version__ = "1.0.0"

__all__ = [
    # Main scoring functions
    'pdm_score',
    'pdm_score_direct',
    'transform_trajectory',
    'get_trajectory_as_array',
    
    # Dataclasses
    'PDMResults',
    'Trajectory',
    
    # Scoring
    'PDMScorer',
    'PDMScorerConfig',
    'ego_is_comfortable',
    'get_collision_type',
    
    # Simulation
    'PDMSimulator',
    'BatchKinematicBicycleModel',
    'BatchLQRTracker',
    
    # Observation
    'PDMObservation',
    'PDMDrivableMap',
    'PDMOccupancyMap',
    'PDMObjectManager',
    
    # Utils
    'ego_state_to_state_array',
    'ego_states_to_state_array',
    'state_array_to_coords_array',
    'coords_array_to_polygon_array',
    'BBCoordsIndex',
    'EgoAreaIndex',
    'MultiMetricIndex',
    'StateIndex',
    'WeightedMetricIndex',
    'convert_absolute_to_relative_se2_array',
    'parallel_discrete_path',
    'PDMPath',
    'PDMEmergencyBrake',
    
    # Proposal
    'BatchIDMPolicy',
    'PDMGenerator',
    'PDMProposalManager',
    
    # Planners
    'AbstractPDMPlanner',
    'AbstractPDMClosedPlanner',
    'PDMClosedPlanner',
]
