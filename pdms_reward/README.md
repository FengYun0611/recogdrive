# PDMS奖励函数模块 / PDMS Reward Function Module

完整的PDMS（Planning Decision Making Scoring）计算方法提取，可作为独立的奖励函数在其他项目中使用。

Complete PDMS (Planning Decision Making Scoring) computation extraction that can be used as a standalone reward function in other projects.

## 📋 目录 / Table of Contents

- [概述 / Overview](#概述--overview)
- [模块结构 / Module Structure](#模块结构--module-structure)
- [核心组件 / Core Components](#核心组件--core-components)
- [安装 / Installation](#安装--installation)
- [使用示例 / Usage Examples](#使用示例--usage-examples)
- [依赖项 / Dependencies](#依赖项--dependencies)
- [API文档 / API Documentation](#api文档--api-documentation)

## 概述 / Overview

PDMS（Planning Decision Making Scoring）是一个用于评估自动驾驶规划轨迹质量的综合评分系统。此模块提供了完整的PDMS计算流程，包括：

PDMS (Planning Decision Making Scoring) is a comprehensive scoring system for evaluating the quality of autonomous driving planning trajectories. This module provides the complete PDMS computation pipeline, including:

- **碰撞检测** / **Collision Detection**: 检测与其他车辆和障碍物的碰撞 / Detects collisions with other vehicles and obstacles
- **可行驶区域合规性** / **Drivable Area Compliance**: 确保车辆保持在可行驶区域内 / Ensures vehicle stays within drivable areas
- **舒适度评估** / **Comfort Assessment**: 评估加速度、急转弯等舒适度指标 / Evaluates comfort metrics like acceleration and sharp turns
- **进度跟踪** / **Progress Tracking**: 沿着规划路径的进度测量 / Measures progress along planned route
- **碰撞时间（TTC）** / **Time-to-Collision (TTC)**: 预测潜在碰撞的时间 / Predicts time to potential collisions
- **行驶方向合规性** / **Driving Direction Compliance**: 确保正确的行驶方向 / Ensures correct driving direction

## 模块结构 / Module Structure

```
pdms_reward/
├── __init__.py                      # 主模块入口 / Main module entry
├── README.md                        # 本文档 / This documentation
├── dataclasses.py                   # 数据类定义 / Dataclass definitions
├── pdm_score.py                     # 主要评分函数 / Main scoring function
├── abstract_pdm_planner.py          # 抽象规划器基类 / Abstract planner base
├── abstract_pdm_closed_planner.py   # 闭环规划器基类 / Closed-loop planner base
├── pdm_closed_planner.py            # 闭环规划器实现 / Closed-loop planner impl
│
├── scoring/                         # 评分模块 / Scoring module
│   ├── __init__.py
│   ├── pdm_scorer.py               # 核心评分器 / Core scorer
│   ├── pdm_comfort_metrics.py      # 舒适度指标 / Comfort metrics
│   └── pdm_scorer_utils.py         # 评分工具函数 / Scoring utilities
│
├── simulation/                      # 模拟模块 / Simulation module
│   ├── __init__.py
│   ├── pdm_simulator.py            # 轨迹模拟器 / Trajectory simulator
│   ├── batch_kinematic_bicycle.py  # 运动学自行车模型 / Kinematic bicycle model
│   ├── batch_lqr.py                # LQR跟踪控制器 / LQR tracker controller
│   └── batch_lqr_utils.py          # LQR工具函数 / LQR utilities
│
├── observation/                     # 观察模块 / Observation module
│   ├── __init__.py
│   ├── pdm_observation.py          # 环境观察 / Environment observation
│   ├── pdm_occupancy_map.py        # 占用地图 / Occupancy map
│   └── pdm_object_manager.py       # 对象管理 / Object management
│
├── proposal/                        # 提案模块 / Proposal module
│   ├── __init__.py
│   ├── batch_idm_policy.py         # IDM策略 / IDM policy
│   ├── pdm_generator.py            # 轨迹生成器 / Trajectory generator
│   └── pdm_proposal.py             # 提案管理 / Proposal management
│
├── utils/                           # 工具模块 / Utilities module
│   ├── __init__.py
│   ├── pdm_array_representation.py # 数组表示转换 / Array representation
│   ├── pdm_enums.py                # 枚举定义 / Enum definitions
│   ├── pdm_geometry_utils.py       # 几何工具 / Geometry utilities
│   ├── pdm_path.py                 # 路径类 / Path class
│   ├── pdm_emergency_brake.py      # 紧急制动 / Emergency brake
│   ├── route_utils.py              # 路由工具 / Route utilities
│   └── graph_search/               # 图搜索算法 / Graph search algorithms
│       ├── __init__.py
│       ├── bfs_roadblock.py        # BFS搜索 / BFS search
│       └── dijkstra.py             # Dijkstra搜索 / Dijkstra search
│
└── examples/                        # 使用示例 / Usage examples
    └── basic_usage.py              # 基础使用示例 / Basic usage example
```

## 核心组件 / Core Components

### 1. PDMScorer（评分器）

核心评分组件，实现了多种评估指标：

The core scoring component that implements multiple evaluation metrics:

```python
from pdms_reward.scoring import PDMScorer, PDMScorerConfig

# 配置评分器 / Configure scorer
config = PDMScorerConfig(
    progress_weight=5.0,           # 进度权重 / Progress weight
    ttc_weight=5.0,                # TTC权重 / TTC weight
    comfortable_weight=2.0,        # 舒适度权重 / Comfort weight
    driving_direction_weight=0.0   # 方向权重 / Direction weight
)

scorer = PDMScorer(proposal_sampling, config)
```

### 2. PDMSimulator（模拟器）

模拟车辆动力学和轨迹执行：

Simulates vehicle dynamics and trajectory execution:

```python
from pdms_reward.simulation import PDMSimulator

simulator = PDMSimulator(proposal_sampling)
simulated_states = simulator.simulate_proposals(trajectory_states, initial_ego_state)
```

### 3. pdm_score（主函数）

主要的PDMS评分函数：

Main PDMS scoring function:

```python
from pdms_reward import pdm_score, PDMResults

results: PDMResults = pdm_score(
    metric_cache,
    model_trajectory,
    future_sampling,
    simulator,
    scorer
)
```

## 安装 / Installation

### 前置要求 / Prerequisites

- Python >= 3.8
- NumPy
- nuPlan devkit
- Shapely

### 安装步骤 / Installation Steps

1. 将`pdms_reward`目录复制到你的项目中：

   Copy the `pdms_reward` directory to your project:

```bash
cp -r pdms_reward /path/to/your/project/
```

2. 安装依赖项（如果还没有安装）：

   Install dependencies (if not already installed):

```bash
pip install numpy shapely nuplan-devkit
```

3. 在你的代码中导入：

   Import in your code:

```python
from pdms_reward import pdm_score, PDMResults
```

## 使用示例 / Usage Examples

### 基础使用 / Basic Usage

```python
import numpy as np
from pdms_reward import (
    pdm_score,
    PDMSimulator,
    PDMScorer,
    PDMScorerConfig,
    Trajectory,
)
from nuplan.planning.simulation.trajectory.trajectory_sampling import TrajectorySampling

# 1. 设置采样参数 / Setup sampling parameters
future_sampling = TrajectorySampling(time_horizon=4.0, interval_length=0.5)
proposal_sampling = TrajectorySampling(time_horizon=8.0, interval_length=0.5)

# 2. 初始化模拟器和评分器 / Initialize simulator and scorer
simulator = PDMSimulator(proposal_sampling)
scorer_config = PDMScorerConfig()
scorer = PDMScorer(proposal_sampling, scorer_config)

# 3. 准备轨迹数据 / Prepare trajectory data
# 假设你有一个预测轨迹 / Assume you have a predicted trajectory
predicted_poses = np.array([
    [0.0, 0.0, 0.0],      # [x, y, heading] 相对坐标 / relative coordinates
    [2.0, 0.1, 0.05],
    [4.0, 0.2, 0.08],
    # ... 更多姿态 / more poses
])

model_trajectory = Trajectory(
    poses=predicted_poses,
    trajectory_sampling=future_sampling
)

# 4. 计算PDMS评分 / Calculate PDMS score
results = pdm_score(
    metric_cache,           # 来自数据集 / from dataset
    model_trajectory,
    future_sampling,
    simulator,
    scorer
)

# 5. 使用评分结果 / Use scoring results
print(f"Overall Score: {results.score:.4f}")
print(f"No Collision: {results.no_at_fault_collisions}")
print(f"Drivable Area: {results.drivable_area_compliance}")
print(f"Progress: {results.ego_progress:.2f}m")
print(f"TTC: {results.time_to_collision_within_bound}")
print(f"Comfort: {results.comfort}")
print(f"Direction: {results.driving_direction_compliance}")
```

### 作为强化学习奖励函数 / As Reinforcement Learning Reward Function

```python
from pdms_reward import pdm_score, PDMResults

class PDMRewardFunction:
    """使用PDMS作为RL奖励函数 / Use PDMS as RL reward function"""
    
    def __init__(self, simulator, scorer):
        self.simulator = simulator
        self.scorer = scorer
        
    def compute_reward(self, trajectory, metric_cache, future_sampling):
        """
        计算给定轨迹的奖励
        Compute reward for given trajectory
        
        Returns:
            reward (float): 标准化的奖励值 / Normalized reward value
            info (dict): 详细的评分信息 / Detailed scoring information
        """
        results = pdm_score(
            metric_cache,
            trajectory,
            future_sampling,
            self.simulator,
            self.scorer
        )
        
        # 将PDMS分数转换为奖励 / Convert PDMS score to reward
        reward = results.score
        
        # 可以添加惩罚项 / Can add penalty terms
        if results.no_at_fault_collisions == 0.0:
            reward -= 10.0  # 碰撞惩罚 / Collision penalty
        
        if results.drivable_area_compliance == 0.0:
            reward -= 5.0   # 偏离道路惩罚 / Off-road penalty
        
        info = results.to_dict()
        return reward, info

# 使用示例 / Usage example
reward_fn = PDMRewardFunction(simulator, scorer)
reward, info = reward_fn.compute_reward(trajectory, metric_cache, future_sampling)
```

### 高级使用：自定义评分权重 / Advanced Usage: Custom Scoring Weights

```python
from pdms_reward.scoring import PDMScorerConfig

# 创建自定义配置 / Create custom configuration
custom_config = PDMScorerConfig(
    # 权重 / Weights
    progress_weight=10.0,          # 更高的进度权重 / Higher progress weight
    ttc_weight=8.0,                # 更高的安全权重 / Higher safety weight
    comfortable_weight=1.0,        # 较低的舒适度权重 / Lower comfort weight
    driving_direction_weight=2.0,  # 添加方向权重 / Add direction weight
    
    # 阈值 / Thresholds
    driving_direction_horizon=1.5,                   # 方向检查时间范围 / Direction check horizon
    driving_direction_compliance_threshold=1.5,       # 合规阈值 / Compliance threshold
    driving_direction_violation_threshold=5.0,        # 违规阈值 / Violation threshold
    stopped_speed_threshold=0.01,                     # 停止速度阈值 / Stopped speed threshold
    progress_distance_threshold=3.0,                  # 进度距离阈值 / Progress distance threshold
)

scorer = PDMScorer(proposal_sampling, custom_config)
```

## 依赖项 / Dependencies

### Python包 / Python Packages

```
numpy>=1.19.0
shapely>=1.8.0
nuplan-devkit>=1.0.0
```

### nuPlan组件 / nuPlan Components

此模块依赖nuPlan devkit的以下组件：

This module depends on the following nuPlan devkit components:

- `nuplan.common.actor_state`: 车辆状态表示 / Vehicle state representation
- `nuplan.common.maps`: 地图API / Map API
- `nuplan.planning.simulation`: 模拟工具 / Simulation utilities
- `nuplan.planning.metrics`: 评估指标 / Evaluation metrics

## API文档 / API Documentation

### PDMResults 数据类

评分结果的数据类：

Dataclass for scoring results:

```python
@dataclass
class PDMResults:
    no_at_fault_collisions: float          # 0.0-1.0, 1.0表示无碰撞 / 1.0 means no collision
    drivable_area_compliance: float        # 0.0-1.0, 1.0表示完全合规 / 1.0 means fully compliant
    ego_progress: float                    # 米 / meters
    time_to_collision_within_bound: float  # 0.0-1.0
    comfort: float                         # 0.0-1.0, 1.0表示舒适 / 1.0 means comfortable
    driving_direction_compliance: float    # 0.0-1.0, 1.0表示合规 / 1.0 means compliant
    score: float                           # 综合评分 / Overall score
```

### pdm_score 函数

```python
def pdm_score(
    metric_cache: MetricCache,
    model_trajectory: Trajectory,
    future_sampling: TrajectorySampling,
    simulator: PDMSimulator,
    scorer: PDMScorer,
) -> PDMResults:
    """
    运行PDM-Score并返回结果
    Run PDM-Score and return results
    
    Args:
        metric_cache: 包含场景信息的指标缓存 / Metric cache with scene info
        model_trajectory: 自车坐标系下的预测轨迹 / Predicted trajectory in ego frame
        future_sampling: 未来轨迹的采样参数 / Sampling params for future trajectory
        simulator: PDM模拟器实例 / PDM simulator instance
        scorer: PDM评分器实例 / PDM scorer instance
        
    Returns:
        PDMResults: PDMS子分数的数据类 / Dataclass of PDMS subscores
    """
```

### PDMScorer 类

```python
class PDMScorer:
    """评分提案的类，重新实现nuPlan的闭环指标"""
    
    def __init__(
        self,
        proposal_sampling: TrajectorySampling,
        config: PDMScorerConfig = PDMScorerConfig(),
        vehicle_parameters: VehicleParameters = get_pacifica_parameters(),
    ):
        """初始化PDMScorer"""
        
    def score_proposals(
        self,
        states: npt.NDArray[np.float64],
        observation: PDMObservation,
        centerline: PDMPath,
        route_lane_ids: List[str],
        drivable_area_map: PDMDrivableMap,
    ) -> npt.NDArray[np.float64]:
        """
        类似nuPlan闭环指标评分提案
        Score proposals similar to nuPlan's closed-loop metrics
        
        Returns:
            包含每个提案评分的数组 / Array containing score of each proposal
        """
```

### PDMSimulator 类

```python
class PDMSimulator:
    """nuPlan模拟管道的重新实现，支持批量模拟"""
    
    def __init__(self, proposal_sampling: TrajectorySampling):
        """初始化PDMSimulator"""
        
    def simulate_proposals(
        self,
        states: npt.NDArray[np.float64],
        initial_ego_state: EgoState
    ) -> npt.NDArray[np.float64]:
        """
        在批次维度上模拟所有提案
        Simulate all proposals over batch dimension
        
        Returns:
            模拟提案状态的数组 / Array of simulated proposal states
        """
```

## 评分指标详解 / Scoring Metrics Details

### 1. 无过失碰撞 (no_at_fault_collisions)

- **范围**: 0.0 - 1.0
- **1.0**: 无碰撞 / No collisions
- **0.5**: 与非代理对象碰撞 / Collision with non-agent
- **0.0**: 与代理车辆碰撞 / Collision with agent vehicle

### 2. 可行驶区域合规性 (drivable_area_compliance)

- **范围**: 0.0 - 1.0
- **1.0**: 始终在可行驶区域内 / Always in drivable area
- **0.0**: 至少一次偏离可行驶区域 / At least once off drivable area

### 3. 自车进度 (ego_progress)

- **单位**: 米 (meters)
- **含义**: 沿中心线的进度距离 / Progress distance along centerline

### 4. 碰撞时间限制内 (time_to_collision_within_bound)

- **范围**: 0.0 - 1.0
- **1.0**: TTC在安全范围内 / TTC within safe bounds
- **0.0**: TTC违规 / TTC violation

### 5. 舒适度 (comfort)

- **范围**: 0.0 - 1.0
- **评估**: 加速度、急转弯等 / Evaluates acceleration, sharp turns, etc.

### 6. 行驶方向合规性 (driving_direction_compliance)

- **范围**: 0.0 - 1.0
- **1.0**: 完全合规 / Fully compliant
- **0.5**: 轻微违规 / Minor violation
- **0.0**: 严重违规 / Major violation

## 性能优化建议 / Performance Optimization Tips

1. **批处理**: 尽可能批量处理多个轨迹以提高效率
   
   **Batch Processing**: Process multiple trajectories in batch when possible

2. **缓存**: 重用`PDMSimulator`和`PDMScorer`实例
   
   **Caching**: Reuse `PDMSimulator` and `PDMScorer` instances

3. **采样率**: 根据需要调整时间采样率
   
   **Sampling Rate**: Adjust time sampling rate as needed

## 常见问题 / FAQ

### Q: 如何调整评分权重？

**A**: 通过`PDMScorerConfig`类配置各项权重：

```python
config = PDMScorerConfig(
    progress_weight=5.0,
    ttc_weight=5.0,
    comfortable_weight=2.0,
    driving_direction_weight=0.0
)
```

### Q: 如何处理不同的车辆参数？

**A**: 在创建`PDMScorer`时传入自定义的`VehicleParameters`：

```python
from nuplan.common.actor_state.vehicle_parameters import VehicleParameters

custom_vehicle = VehicleParameters(
    width=2.0,
    length=5.0,
    # ... 其他参数
)
scorer = PDMScorer(proposal_sampling, config, custom_vehicle)
```

### Q: 此模块是否支持GPU加速？

**A**: 当前版本使用NumPy实现，主要在CPU上运行。如需GPU加速，可以考虑将关键计算部分转换为PyTorch或JAX实现。

### Q: How to adjust scoring weights?

**A**: Configure weights through the `PDMScorerConfig` class (see code above)

### Q: How to handle different vehicle parameters?

**A**: Pass custom `VehicleParameters` when creating `PDMScorer` (see code above)

### Q: Does this module support GPU acceleration?

**A**: Current version uses NumPy and runs primarily on CPU. For GPU acceleration, consider converting key computations to PyTorch or JAX.

## 贡献 / Contributing

欢迎提交问题和改进建议！

Welcome to submit issues and improvement suggestions!

## 许可证 / License

此模块提取自recogdrive项目，遵循相同的许可证。

This module is extracted from the recogdrive project and follows the same license.

## 致谢 / Acknowledgments

此模块基于nuPlan和NAVSIM框架开发。

This module is developed based on nuPlan and NAVSIM frameworks.

---

**版本 / Version**: 1.0.0

**最后更新 / Last Updated**: 2025-12-09
