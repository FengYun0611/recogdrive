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

    方式1: 使用MetricCacheBuilder (推荐，最简单)
    Method 1: Using MetricCacheBuilder (Recommended, Simplest)
    
    from pdms_reward import pdm_score, build_metric_cache_from_scenario
    from pdms_reward import PDMSimulator, PDMScorer
    
    # Initialize simulator and scorer (only once)
    simulator = PDMSimulator(proposal_sampling)
    scorer = PDMScorer(proposal_sampling)
    
    # Build MetricCache from scenario (handles all complexity)
    metric_cache = build_metric_cache_from_scenario(scenario)
    
    # Calculate PDMS score
    results = pdm_score(
        metric_cache,
        model_trajectory,
        future_sampling,
        simulator,
        scorer
    )
    
    print(f"PDMS Score: {results.score}")
    
    ---
    
    方式2: 直接使用各组件 (更灵活)
    Method 2: Using components directly (More flexible)
    
    from pdms_reward import pdm_score_direct
    
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
"""

from .pdm_score import pdm_score, pdm_score_direct, transform_trajectory, get_trajectory_as_array
from .dataclasses import PDMResults, Trajectory

# Import MetricCache builder (optional, requires navsim)
try:
    from .metric_cache_builder import MetricCacheBuilder, build_metric_cache_from_scenario
    METRIC_CACHE_BUILDER_AVAILABLE = True
except ImportError:
    METRIC_CACHE_BUILDER_AVAILABLE = False
    MetricCacheBuilder = None
    build_metric_cache_from_scenario = None

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
    
    # MetricCache builder (optional)
    'MetricCacheBuilder',
    'build_metric_cache_from_scenario',
    'METRIC_CACHE_BUILDER_AVAILABLE',
    
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
