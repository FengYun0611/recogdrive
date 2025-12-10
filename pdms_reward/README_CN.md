# PDMS奖励函数模块

完整的PDMS（Planning Decision Making Scoring）计算方法提取，可作为独立的奖励函数在其他项目中使用。

## 📋 目录

- [概述](#概述)
- [模块结构](#模块结构)
- [核心组件](#核心组件)
- [安装](#安装)
- [快速开始](#快速开始)
- [详细使用说明](#详细使用说明)
- [API参考](#api参考)
- [常见问题](#常见问题)

## 概述

PDMS（Planning Decision Making Scoring）是一个用于评估自动驾驶规划轨迹质量的综合评分系统。此模块从RecogDrive项目中提取，提供了完整、独立的PDMS计算流程。

### 主要特性

- ✅ **完整的PDMS计算** - 包含所有评分组件，无需任何简化
- ✅ **模块化设计** - 清晰的模块结构，易于理解和使用
- ✅ **独立运行** - 可作为独立模块在其他项目中使用
- ✅ **丰富的文档** - 中英文双语文档，详细的使用示例
- ✅ **灵活配置** - 支持自定义评分权重和阈值

### 评估维度

1. **碰撞安全性** - 检测并评估与其他车辆和障碍物的碰撞风险
2. **道路合规性** - 确保车辆保持在可行驶区域内
3. **行驶舒适度** - 评估加速度、急转弯等舒适度指标
4. **任务进度** - 测量沿规划路径的完成进度
5. **碰撞时间** - 预测潜在碰撞的时间窗口
6. **方向合规性** - 确保正确的行驶方向

## 模块结构

```
pdms_reward/
├── __init__.py                      # 主模块入口
├── README.md                        # 英文文档
├── README_CN.md                     # 中文文档（本文件）
├── requirements.txt                 # 依赖列表
├── setup.py                         # 安装脚本
├── dataclasses.py                   # 数据类定义
├── pdm_score.py                     # 主要评分函数
│
├── scoring/                         # 评分模块
│   ├── pdm_scorer.py               # 核心评分器实现
│   ├── pdm_comfort_metrics.py      # 舒适度评估
│   └── pdm_scorer_utils.py         # 评分辅助函数
│
├── simulation/                      # 模拟模块
│   ├── pdm_simulator.py            # 轨迹模拟器
│   ├── batch_kinematic_bicycle.py  # 运动学自行车模型
│   ├── batch_lqr.py                # LQR跟踪控制器
│   └── batch_lqr_utils.py          # LQR工具函数
│
├── observation/                     # 观察模块
│   ├── pdm_observation.py          # 环境观察
│   ├── pdm_occupancy_map.py        # 占用地图
│   └── pdm_object_manager.py       # 对象管理
│
├── proposal/                        # 提案生成模块
│   ├── batch_idm_policy.py         # IDM跟车策略
│   ├── pdm_generator.py            # 轨迹生成器
│   └── pdm_proposal.py             # 提案管理
│
├── utils/                           # 工具模块
│   ├── pdm_array_representation.py # 数组表示转换
│   ├── pdm_enums.py                # 枚举定义
│   ├── pdm_geometry_utils.py       # 几何工具
│   ├── pdm_path.py                 # 路径类
│   ├── pdm_emergency_brake.py      # 紧急制动
│   └── graph_search/               # 图搜索算法
│
└── examples/                        # 使用示例
    └── basic_usage.py              # 基础使用示例
```

## 核心组件

### 1. PDMScorer - 评分器

核心评分组件，负责计算所有评估指标。

**主要功能：**
- 碰撞检测与分类
- 可行驶区域合规性检查
- 舒适度评估
- 进度计算
- TTC（碰撞时间）计算
- 行驶方向检查

**配置参数：**
```python
from pdms_reward.scoring import PDMScorerConfig

config = PDMScorerConfig(
    progress_weight=5.0,           # 进度权重
    ttc_weight=5.0,                # 安全性权重
    comfortable_weight=2.0,        # 舒适度权重
    driving_direction_weight=0.0   # 方向权重
)
```

### 2. PDMSimulator - 模拟器

模拟车辆动力学和轨迹执行。

**主要功能：**
- 批量轨迹模拟
- 运动学自行车模型
- LQR轨迹跟踪控制

### 3. PDMObservation - 环境观察

处理环境感知信息。

**主要功能：**
- 其他车辆跟踪
- 障碍物检测
- 交通灯状态
- 占用地图构建

### 4. pdm_score - 主函数

整合所有组件的主评分函数。

## 安装

### 方法1: 直接复制

```bash
# 复制整个pdms_reward目录到你的项目
cp -r pdms_reward /path/to/your/project/

# 安装依赖
cd /path/to/your/project/pdms_reward
pip install -r requirements.txt
```

### 方法2: 使用setup.py安装

```bash
# 进入pdms_reward目录
cd pdms_reward

# 开发模式安装（推荐）
pip install -e .

# 或者正式安装
pip install .
```

### 依赖项

必需：
- Python >= 3.8
- NumPy >= 1.19.0
- Shapely >= 1.8.0
- nuPlan devkit

可选：
- Matplotlib >= 3.3.0 (用于可视化)

## 快速开始

### ⭐ 推荐方式：使用MetricCacheBuilder（最简单！）

**适用场景**：你有nuPlan的scenario数据，想要最简单的使用方式

这是**最简单**的方式！MetricCacheBuilder会自动处理所有复杂的数据准备工作。

```python
from pdms_reward import (
    pdm_score,
    build_metric_cache_from_scenario,  # 一行代码构建MetricCache
    PDMSimulator,
    PDMScorer,
    Trajectory,
)
from nuplan.planning.simulation.trajectory.trajectory_sampling import TrajectorySampling
import numpy as np

# 1. 初始化（只需一次）
future_sampling = TrajectorySampling(time_horizon=4.0, interval_length=0.5)
proposal_sampling = TrajectorySampling(time_horizon=8.0, interval_length=0.5)

simulator = PDMSimulator(proposal_sampling)
scorer = PDMScorer(proposal_sampling)

# 2. 准备你的预测轨迹
predicted_poses = np.array([
    [0.0, 0.0, 0.0],    # [x, y, heading]
    [2.0, 0.0, 0.0],
    [4.0, 0.0, 0.0],
    # ... 更多点
])

trajectory = Trajectory(
    poses=predicted_poses,
    trajectory_sampling=future_sampling
)

# 3. 从scenario自动构建MetricCache（关键步骤！）
# 这一步会自动处理所有复杂的数据准备：
# - PDM-Closed规划器初始化
# - 参考轨迹生成
# - 观察数据插值
# - 中心线提取
# - 可行驶区域地图构建
metric_cache = build_metric_cache_from_scenario(scenario)

# 4. 计算评分（简单！）
results = pdm_score(
    metric_cache,
    trajectory,
    future_sampling,
    simulator,
    scorer
)

# 5. 使用结果
print(f"总分: {results.score:.4f}")
reward = results.score  # 作为奖励函数使用
```

**优势**：
- ✅ 只需要scenario和你的预测轨迹
- ✅ 自动处理所有复杂的数据准备
- ✅ 一行代码构建MetricCache
- ✅ 无需手动创建observation、centerline等

---

### 方式2：使用直接API（高级用户）

**适用场景**：你已经有准备好的各个组件，想要更灵活的控制

```python
from pdms_reward import (
    pdm_score_direct,  # 使用直接API
    PDMSimulator,
    PDMScorer,
    Trajectory,
)
from nuplan.planning.simulation.trajectory.trajectory_sampling import TrajectorySampling
import numpy as np

# 1. 初始化
future_sampling = TrajectorySampling(time_horizon=4.0, interval_length=0.5)
proposal_sampling = TrajectorySampling(time_horizon=8.0, interval_length=0.5)

simulator = PDMSimulator(proposal_sampling)
scorer = PDMScorer(proposal_sampling)

# 2. 准备轨迹数据（相对坐标）
predicted_poses = np.array([
    [0.0, 0.0, 0.0],    # [x, y, heading]
    [2.0, 0.0, 0.0],
    [4.0, 0.0, 0.0],
    # ... 更多点
])

trajectory = Trajectory(
    poses=predicted_poses,
    trajectory_sampling=future_sampling
)

# 3. 准备场景数据（从你的数据源获取）
# - initial_ego_state: 当前自车状态
# - observation: 其他车辆和障碍物
# - centerline: 规划路径中心线
# - route_lane_ids: 路线车道ID列表
# - drivable_area_map: 可行驶区域地图

# 4. 计算评分 - 直接传入各个组件
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

# 5. 查看结果
print(f"总分: {results.score:.4f}")
print(f"无碰撞: {results.no_at_fault_collisions}")
print(f"道路合规: {results.drivable_area_compliance}")
print(f"进度: {results.ego_progress:.2f}米")
```

### 方式3：已有MetricCache对象

**适用场景**：你已经有现成的MetricCache对象（从缓存文件加载等）

```python
from pdms_reward import pdm_score

# 直接使用已有的MetricCache
results = pdm_score(
    metric_cache,      # 已有的MetricCache对象
    trajectory,
    future_sampling,
    simulator,
    scorer
)
```

## 输入数据准备指南

使用`pdm_score_direct()`时，你需要准备以下输入数据：

### 1. model_trajectory (Trajectory)
你的模型预测的轨迹，相对坐标系（ego frame）

```python
import numpy as np
from pdms_reward import Trajectory
from nuplan.planning.simulation.trajectory.trajectory_sampling import TrajectorySampling

# 创建轨迹poses: [[x, y, heading], ...]
poses = np.array([
    [0.0, 0.0, 0.0],      # 起点
    [2.0, 0.1, 0.05],     # 0.5秒后
    [4.0, 0.2, 0.08],     # 1.0秒后
    # ... 更多点
], dtype=np.float32)

trajectory = Trajectory(
    poses=poses,
    trajectory_sampling=TrajectorySampling(time_horizon=4.0, interval_length=0.5)
)
```

### 2. initial_ego_state (EgoState)
当前时刻的自车状态

```python
from nuplan.common.actor_state.ego_state import EgoState
from nuplan.common.actor_state.state_representation import StateSE2, StateVector2D, TimePoint
from nuplan.common.actor_state.vehicle_parameters import get_pacifica_parameters

# 从你的数据创建
ego_state = EgoState.build_from_rear_axle(
    rear_axle_pose=StateSE2(x, y, heading),
    rear_axle_velocity_2d=StateVector2D(vx, vy),
    rear_axle_acceleration_2d=StateVector2D(ax, ay),
    tire_steering_angle=steering_angle,
    time_point=TimePoint(timestamp_microseconds),
    vehicle_parameters=get_pacifica_parameters()
)
```

### 3. observation (PDMObservation)
环境观察数据（其他车辆、障碍物等）

```python
from pdms_reward.observation import PDMObservation

# 创建观察对象
observation = PDMObservation(
    trajectory_sampling=trajectory_sampling,
    proposal_sampling=proposal_sampling,
    map_radius=150.0  # 考虑150米范围内的物体
)

# 更新观察数据（从你的场景数据）
observation.update(
    ego_state,
    detected_objects,     # 从传感器或数据集获取
    traffic_light_data,   # 交通灯状态
    route_lane_dict       # 路由信息
)
```

### 4. centerline (PDMPath)
规划路径的中心线，用于计算进度

```python
from pdms_reward.utils import PDMPath

# 从路由规划获取中心线点
centerline_points = [...]  # List[StateSE2]
centerline = PDMPath(centerline_points)
```

### 5. route_lane_ids (List[str])
规划路线上的车道ID列表

```python
# 从路由规划获取
route_lane_ids = ['lane_connector_123', 'lane_456', ...]
```

### 6. drivable_area_map (PDMDrivableMap)
可行驶区域地图

```python
from pdms_reward.observation import PDMDrivableMap

# 从地图API创建
drivable_map = PDMDrivableMap(
    map_api,      # nuPlan的地图API
    ego_state,    # 当前自车状态
    map_radius=150.0  # 地图范围
)
```

### 完整示例

```python
from pdms_reward import pdm_score_direct, PDMSimulator, PDMScorer

# 初始化（只需一次）
simulator = PDMSimulator(proposal_sampling)
scorer = PDMScorer(proposal_sampling)

# 计算评分
results = pdm_score_direct(
    model_trajectory=trajectory,
    initial_ego_state=ego_state,
    observation=observation,
    centerline=centerline,
    route_lane_ids=route_lane_ids,
    drivable_area_map=drivable_area_map,
    future_sampling=future_sampling,
    simulator=simulator,
    scorer=scorer
)

# 使用结果作为奖励
reward = results.score
```

更多详细示例请参考：`examples/direct_api_usage.py`

## 详细使用说明

### 场景1: 作为强化学习的奖励函数

```python
class RLRewardFunction:
    """强化学习奖励函数"""
    
    def __init__(self):
        # 初始化PDMS组件
        self.proposal_sampling = TrajectorySampling(
            time_horizon=8.0, 
            interval_length=0.5
        )
        self.simulator = PDMSimulator(self.proposal_sampling)
        self.scorer = PDMScorer(self.proposal_sampling)
        
    def compute_reward(self, trajectory, metric_cache, future_sampling):
        """计算奖励值"""
        # 获取PDMS评分
        results = pdm_score(
            metric_cache,
            trajectory,
            future_sampling,
            self.simulator,
            self.scorer
        )
        
        # 基础奖励
        reward = results.score
        
        # 添加额外的奖励/惩罚
        if results.no_at_fault_collisions == 0.0:
            reward -= 100.0  # 严重碰撞惩罚
        
        if results.drivable_area_compliance == 0.0:
            reward -= 50.0   # 驶出道路惩罚
        
        # 鼓励进度
        reward += results.ego_progress * 0.5
        
        # 鼓励舒适驾驶
        if results.comfort > 0.9:
            reward += 10.0
        
        return reward, results.to_dict()

# 使用示例
reward_fn = RLRewardFunction()
reward, info = reward_fn.compute_reward(trajectory, cache, sampling)
```

### 场景2: 轨迹评估和比较

```python
def compare_trajectories(trajectories, metric_cache, future_sampling):
    """比较多条轨迹的质量"""
    
    # 初始化评分组件
    proposal_sampling = TrajectorySampling(time_horizon=8.0, interval_length=0.5)
    simulator = PDMSimulator(proposal_sampling)
    scorer = PDMScorer(proposal_sampling)
    
    results_list = []
    for i, traj in enumerate(trajectories):
        results = pdm_score(
            metric_cache,
            traj,
            future_sampling,
            simulator,
            scorer
        )
        results_list.append(results)
        
        print(f"\n轨迹 {i+1}:")
        print(f"  总分: {results.score:.4f}")
        print(f"  安全性: {results.no_at_fault_collisions:.2f}")
        print(f"  进度: {results.ego_progress:.2f}米")
        print(f"  舒适度: {results.comfort:.2f}")
    
    # 找出最佳轨迹
    best_idx = max(range(len(results_list)), 
                   key=lambda i: results_list[i].score)
    print(f"\n最佳轨迹: #{best_idx+1}")
    
    return results_list, best_idx
```

### 场景3: 自定义评分标准

```python
from pdms_reward.scoring import PDMScorerConfig

# 场景A: 高速公路 - 重视效率和舒适度
highway_config = PDMScorerConfig(
    progress_weight=8.0,          # 高进度权重
    ttc_weight=4.0,               # 中等安全权重
    comfortable_weight=5.0,       # 高舒适度权重
    driving_direction_weight=0.0  # 方向不重要
)

# 场景B: 城市交叉口 - 重视安全性
intersection_config = PDMScorerConfig(
    progress_weight=2.0,          # 低进度权重
    ttc_weight=10.0,              # 极高安全权重
    comfortable_weight=1.0,       # 低舒适度权重
    driving_direction_weight=3.0  # 重视方向合规
)

# 场景C: 停车场 - 重视精确性
parking_config = PDMScorerConfig(
    progress_weight=1.0,
    ttc_weight=8.0,
    comfortable_weight=6.0,       # 非常平滑的动作
    driving_direction_weight=2.0
)

# 根据场景选择配置
def get_scorer_for_scenario(scenario_type, proposal_sampling):
    if scenario_type == "highway":
        config = highway_config
    elif scenario_type == "intersection":
        config = intersection_config
    elif scenario_type == "parking":
        config = parking_config
    else:
        config = PDMScorerConfig()  # 默认配置
    
    return PDMScorer(proposal_sampling, config)
```

### 场景4: 批量评估

```python
def batch_evaluate(trajectories, metric_caches, future_sampling):
    """批量评估多个场景的轨迹"""
    
    proposal_sampling = TrajectorySampling(time_horizon=8.0, interval_length=0.5)
    simulator = PDMSimulator(proposal_sampling)
    scorer = PDMScorer(proposal_sampling)
    
    all_results = []
    for traj, cache in zip(trajectories, metric_caches):
        results = pdm_score(cache, traj, future_sampling, simulator, scorer)
        all_results.append(results)
    
    # 统计分析
    scores = [r.score for r in all_results]
    collisions = [r.no_at_fault_collisions for r in all_results]
    
    print(f"平均分数: {np.mean(scores):.4f} ± {np.std(scores):.4f}")
    print(f"无碰撞率: {np.mean(collisions):.2%}")
    
    return all_results
```

## API参考

### PDMResults 类

评分结果数据类：

```python
@dataclass
class PDMResults:
    no_at_fault_collisions: float          # 范围 [0.0-1.0]
    drivable_area_compliance: float        # 范围 [0.0-1.0]
    ego_progress: float                    # 单位：米
    time_to_collision_within_bound: float  # 范围 [0.0-1.0]
    comfort: float                         # 范围 [0.0-1.0]
    driving_direction_compliance: float    # 范围 [0.0-1.0]
    score: float                           # 综合评分
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
```

**字段说明：**

| 字段 | 含义 | 数值范围 | 说明 |
|-----|------|---------|------|
| no_at_fault_collisions | 无过失碰撞 | 0.0-1.0 | 1.0表示无碰撞，0.0表示碰撞 |
| drivable_area_compliance | 道路合规性 | 0.0-1.0 | 1.0表示始终在道路上 |
| ego_progress | 行驶进度 | ≥0.0 | 沿中心线的行驶距离（米） |
| time_to_collision_within_bound | TTC合规 | 0.0-1.0 | 1.0表示安全，0.0表示危险 |
| comfort | 舒适度 | 0.0-1.0 | 1.0表示非常舒适 |
| driving_direction_compliance | 方向合规 | 0.0-1.0 | 1.0表示完全合规 |
| score | 综合得分 | 取决于配置 | 所有指标的加权综合 |

### pdm_score 函数

主评分函数：

```python
def pdm_score(
    metric_cache: MetricCache,
    model_trajectory: Trajectory,
    future_sampling: TrajectorySampling,
    simulator: PDMSimulator,
    scorer: PDMScorer,
) -> PDMResults:
    """
    计算PDMS评分
    
    参数:
        metric_cache: 场景指标缓存
        model_trajectory: 预测轨迹（相对坐标）
        future_sampling: 采样参数
        simulator: PDM模拟器实例
        scorer: PDM评分器实例
    
    返回:
        PDMResults: 评分结果
    """
```

### PDMScorer 类

评分器类：

```python
class PDMScorer:
    def __init__(
        self,
        proposal_sampling: TrajectorySampling,
        config: PDMScorerConfig = PDMScorerConfig(),
        vehicle_parameters: VehicleParameters = get_pacifica_parameters(),
    ):
        """初始化评分器"""
    
    def score_proposals(
        self,
        states: npt.NDArray[np.float64],
        observation: PDMObservation,
        centerline: PDMPath,
        route_lane_ids: List[str],
        drivable_area_map: PDMDrivableMap,
    ) -> npt.NDArray[np.float64]:
        """评分多个轨迹提案"""
```

### PDMScorerConfig 类

评分器配置：

```python
@dataclass
class PDMScorerConfig:
    # 权重
    progress_weight: float = 5.0
    ttc_weight: float = 5.0
    comfortable_weight: float = 2.0
    driving_direction_weight: float = 0.0
    
    # 阈值
    driving_direction_horizon: float = 1.0
    driving_direction_compliance_threshold: float = 2.0
    driving_direction_violation_threshold: float = 6.0
    stopped_speed_threshold: float = 5e-03
    progress_distance_threshold: float = 5.0
```

**参数说明：**

- **progress_weight**: 进度指标的权重，越大越重视完成任务
- **ttc_weight**: 安全性（TTC）的权重，越大越保守
- **comfortable_weight**: 舒适度的权重，影响加速度和转向平滑度
- **driving_direction_weight**: 方向合规的权重

### PDMSimulator 类

模拟器类：

```python
class PDMSimulator:
    def __init__(self, proposal_sampling: TrajectorySampling):
        """初始化模拟器"""
    
    def simulate_proposals(
        self,
        states: npt.NDArray[np.float64],
        initial_ego_state: EgoState
    ) -> npt.NDArray[np.float64]:
        """模拟轨迹执行"""
```

## 常见问题

### Q1: 如何调整评分对不同指标的重视程度？

**A:** 通过`PDMScorerConfig`调整各项权重：

```python
# 更重视安全性
safe_config = PDMScorerConfig(
    progress_weight=3.0,
    ttc_weight=10.0,      # 提高安全权重
    comfortable_weight=2.0,
)

# 更重视效率
efficient_config = PDMScorerConfig(
    progress_weight=10.0,  # 提高进度权重
    ttc_weight=4.0,
    comfortable_weight=1.0,
)
```

### Q2: 评分结果的数值范围是多少？

**A:** 
- 大多数子指标在 [0.0, 1.0] 范围内
- `ego_progress` 是实际距离（米），可以是任意非负值
- `score` 是加权综合，其范围取决于权重配置，通常在 [0.0, 10.0] 左右

### Q3: 如何处理不同的车辆参数？

**A:** 创建自定义的`VehicleParameters`：

```python
from nuplan.common.actor_state.vehicle_parameters import VehicleParameters

custom_vehicle = VehicleParameters(
    width=2.0,          # 车宽（米）
    length=5.0,         # 车长（米）
    # ... 其他参数
)

scorer = PDMScorer(proposal_sampling, config, custom_vehicle)
```

### Q4: 模块是否支持GPU加速？

**A:** 当前版本主要使用NumPy，在CPU上运行。如果需要GPU加速：
1. 可以考虑将关键计算转换为PyTorch
2. 使用CuPy替代NumPy
3. 批量处理多个轨迹以提高效率

### Q5: 如何理解碰撞评分的0.5值？

**A:** 
- 1.0: 完全无碰撞
- 0.5: 与非车辆代理（如静态物体）的轻微碰撞
- 0.0: 与其他车辆的严重碰撞

### Q6: 如何集成到现有的训练流程？

**A:** 基本步骤：

```python
# 1. 在训练开始时初始化PDMS组件（只需一次）
from pdms_reward import PDMSimulator, PDMScorer

simulator = PDMSimulator(proposal_sampling)
scorer = PDMScorer(proposal_sampling)

# 2. 在训练循环中
for episode in episodes:
    # ... 你的规划器生成轨迹
    trajectory = your_planner.plan()
    
    # 计算PDMS评分作为奖励
    from pdms_reward import pdm_score
    results = pdm_score(
        metric_cache, trajectory, 
        future_sampling, simulator, scorer
    )
    
    # 使用评分
    reward = results.score
    # 或者自定义奖励
    reward = custom_reward_function(results)
    
    # ... 继续训练
```

### Q7: 轨迹坐标系是什么？

**A:** 
- 输入轨迹应该在**车辆坐标系**（ego frame）下
- 格式: `[x, y, heading]`
- x: 前后方向（前为正）
- y: 左右方向（左为正）
- heading: 朝向角（弧度）

### Q8: 如何处理不同的时间采样率？

**A:** 通过`TrajectorySampling`指定：

```python
# 更高频率采样（0.2秒间隔）
high_freq = TrajectorySampling(time_horizon=4.0, interval_length=0.2)

# 更低频率采样（1.0秒间隔）
low_freq = TrajectorySampling(time_horizon=8.0, interval_length=1.0)
```

建议：
- 规划轨迹：0.5s间隔
- 评估时域：4-8秒

### Q9: 性能优化建议？

**A:**
1. **重用对象**: 不要每次都创建新的`simulator`和`scorer`
2. **批处理**: 一次评估多条轨迹
3. **合理采样**: 不要使用过高的采样频率
4. **缓存地图**: 地图数据可以缓存重用

```python
# 好的做法
simulator = PDMSimulator(sampling)  # 创建一次
scorer = PDMScorer(sampling)        # 创建一次

for trajectory in trajectories:
    results = pdm_score(cache, trajectory, sampling, 
                       simulator, scorer)  # 重用
```

### Q10: 如何调试评分异常？

**A:** 检查以下内容：

```python
results = pdm_score(...)

# 检查各个子指标
if results.score < 0.1:
    print("低分原因排查:")
    print(f"碰撞: {results.no_at_fault_collisions}")
    print(f"道路: {results.drivable_area_compliance}")
    print(f"进度: {results.ego_progress}")
    print(f"TTC: {results.time_to_collision_within_bound}")
    print(f"舒适: {results.comfort}")
    print(f"方向: {results.driving_direction_compliance}")
```

## 更新日志

### v1.0.0 (2025-12-09)
- 🎉 首次发布
- ✅ 完整提取PDMS计算方法
- ✅ 支持独立使用
- ✅ 完善的中英文文档
- ✅ 使用示例

## 致谢

此模块从RecogDrive项目中提取，基于nuPlan和NAVSIM框架开发。

## 许可证

遵循RecogDrive项目的许可证。

---

**如有问题或建议，欢迎提交Issue！**
