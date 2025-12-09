# PDMS奖励函数模块 - 文件清单
# PDMS Reward Function Module - File Manifest

本文档列出了pdms_reward模块中的所有文件及其用途。

This document lists all files in the pdms_reward module and their purposes.

## 📄 核心文件 / Core Files

| 文件 | 用途 | 依赖关系 |
|-----|------|---------|
| `__init__.py` | 模块主入口，导出所有公共API | 所有子模块 |
| `pdm_score.py` | 主评分函数，整合所有评分流程 | scoring, simulation, utils, dataclasses |
| `dataclasses.py` | 数据类定义（PDMResults, Trajectory） | nuPlan基础库 |
| `abstract_pdm_planner.py` | 抽象规划器基类 | nuPlan, utils |
| `abstract_pdm_closed_planner.py` | 闭环规划器基类 | abstract_pdm_planner, proposal, scoring, simulation |
| `pdm_closed_planner.py` | 闭环规划器实现 | abstract_pdm_closed_planner |

## 📊 评分模块 / Scoring Module (`scoring/`)

| 文件 | 功能 | 主要类/函数 |
|-----|------|------------|
| `__init__.py` | 评分模块入口 | - |
| `pdm_scorer.py` | 核心评分器实现 | `PDMScorer`, `PDMScorerConfig` |
| `pdm_comfort_metrics.py` | 舒适度指标计算 | `ego_is_comfortable()` |
| `pdm_scorer_utils.py` | 评分辅助函数 | `get_collision_type()` |

**评分器功能清单：**
- ✅ 碰撞检测与分类
- ✅ 可行驶区域合规检查
- ✅ 行驶方向合规检查
- ✅ 进度计算
- ✅ TTC（碰撞时间）计算
- ✅ 舒适度评估

## 🚗 模拟模块 / Simulation Module (`simulation/`)

| 文件 | 功能 | 主要类/函数 |
|-----|------|------------|
| `__init__.py` | 模拟模块入口 | - |
| `pdm_simulator.py` | 轨迹模拟器 | `PDMSimulator` |
| `batch_kinematic_bicycle.py` | 运动学自行车模型 | `BatchKinematicBicycleModel` |
| `batch_lqr.py` | LQR跟踪控制器 | `BatchLQRTracker` |
| `batch_lqr_utils.py` | LQR辅助函数 | LQR计算函数 |

**模拟器功能清单：**
- ✅ 批量轨迹模拟
- ✅ 运动学模型
- ✅ LQR轨迹跟踪
- ✅ 车辆动力学

## 👁️ 观察模块 / Observation Module (`observation/`)

| 文件 | 功能 | 主要类/函数 |
|-----|------|------------|
| `__init__.py` | 观察模块入口 | - |
| `pdm_observation.py` | 环境观察管理 | `PDMObservation` |
| `pdm_occupancy_map.py` | 占用地图构建 | `PDMOccupancyMap`, `PDMDrivableMap` |
| `pdm_object_manager.py` | 对象跟踪管理 | `PDMObjectManager` |

**观察器功能清单：**
- ✅ 其他车辆跟踪
- ✅ 障碍物检测
- ✅ 交通灯状态
- ✅ 占用地图构建
- ✅ 可行驶区域识别

## 📝 提案模块 / Proposal Module (`proposal/`)

| 文件 | 功能 | 主要类/函数 |
|-----|------|------------|
| `__init__.py` | 提案模块入口 | - |
| `batch_idm_policy.py` | IDM跟车策略 | `BatchIDMPolicy` |
| `pdm_generator.py` | 轨迹生成器 | `PDMGenerator` |
| `pdm_proposal.py` | 提案管理 | `PDMProposalManager` |

**提案生成功能清单：**
- ✅ IDM纵向控制
- ✅ 多轨迹生成
- ✅ 提案管理

## 🛠️ 工具模块 / Utils Module (`utils/`)

| 文件 | 功能 | 主要类/函数 |
|-----|------|------------|
| `__init__.py` | 工具模块入口 | - |
| `pdm_array_representation.py` | 数组表示转换 | `ego_state_to_state_array()`, `state_array_to_coords_array()` |
| `pdm_enums.py` | 枚举定义 | `StateIndex`, `BBCoordsIndex`, `MultiMetricIndex` 等 |
| `pdm_geometry_utils.py` | 几何工具函数 | `convert_absolute_to_relative_se2_array()`, `parallel_discrete_path()` |
| `pdm_path.py` | 路径类 | `PDMPath` |
| `pdm_emergency_brake.py` | 紧急制动 | `PDMEmergencyBrake` |
| `route_utils.py` | 路由工具 | 路由规划函数 |

### 图搜索子模块 / Graph Search Submodule (`utils/graph_search/`)

| 文件 | 功能 |
|-----|------|
| `__init__.py` | 图搜索模块入口 |
| `bfs_roadblock.py` | BFS搜索算法 |
| `dijkstra.py` | Dijkstra最短路径算法 |

## 📚 文档 / Documentation

| 文件 | 语言 | 内容 |
|-----|------|------|
| `README.md` | 英文 | 完整使用文档 |
| `README_CN.md` | 中文 | 完整使用文档（中文版） |
| `MANIFEST.md` | 双语 | 本文件，文件清单 |

## 🔧 配置文件 / Configuration Files

| 文件 | 用途 |
|-----|------|
| `requirements.txt` | Python依赖列表 |
| `setup.py` | 安装配置脚本 |

## 📖 示例 / Examples (`examples/`)

| 文件 | 内容 |
|-----|------|
| `__init__.py` | 示例模块入口 |
| `basic_usage.py` | 基础使用示例，包含3个场景 |

**示例内容：**
1. 基础评分示例
2. 作为RL奖励函数
3. 自定义配置示例

## 🔗 依赖关系图 / Dependency Graph

```
pdms_reward/
│
├── __init__.py ─────────────┐
│                            │
├── pdm_score.py ────────────┼────► dataclasses.py
│   │                        │
│   ├──► scoring/            │
│   ├──► simulation/         │
│   └──► utils/              │
│                            │
├── scoring/                 │
│   ├── pdm_scorer.py ───────┼────► observation/
│   ├── pdm_comfort_metrics  │      utils/
│   └── pdm_scorer_utils     │
│                            │
├── simulation/              │
│   ├── pdm_simulator.py ────┼────► utils/
│   ├── batch_kinematic_bicycle
│   ├── batch_lqr ───────────┼────► batch_lqr_utils
│   └── batch_lqr_utils      │
│                            │
├── observation/             │
│   ├── pdm_observation.py ──┼────► pdm_occupancy_map
│   ├── pdm_occupancy_map    │      pdm_object_manager
│   └── pdm_object_manager   │      utils/
│                            │
├── proposal/                │
│   ├── batch_idm_policy     │
│   ├── pdm_generator ───────┼────► utils/
│   └── pdm_proposal         │      observation/
│                            │
└── utils/ ──────────────────┘
    ├── pdm_array_representation
    ├── pdm_enums
    ├── pdm_geometry_utils
    ├── pdm_path
    ├── pdm_emergency_brake
    └── graph_search/
```

## 📦 模块大小统计 / Module Size Statistics

| 模块 | 文件数 | 总行数（估计） |
|-----|-------|--------------|
| 核心文件 | 6 | ~1,500 |
| scoring/ | 4 | ~650 |
| simulation/ | 5 | ~600 |
| observation/ | 4 | ~800 |
| proposal/ | 4 | ~700 |
| utils/ | 9 | ~1,200 |
| examples/ | 2 | ~300 |
| 文档 | 3 | - |
| **总计** | **37** | **~5,750** |

## ✅ 完整性检查清单 / Completeness Checklist

### 核心功能 / Core Functions
- [x] PDM评分主函数
- [x] 轨迹转换函数
- [x] 数据类定义

### 评分组件 / Scoring Components
- [x] 碰撞检测
- [x] 可行驶区域检查
- [x] 舒适度评估
- [x] 进度计算
- [x] TTC计算
- [x] 方向合规检查

### 模拟组件 / Simulation Components
- [x] 轨迹模拟器
- [x] 运动学模型
- [x] LQR控制器

### 观察组件 / Observation Components
- [x] 环境观察
- [x] 占用地图
- [x] 对象管理

### 工具函数 / Utilities
- [x] 数组转换
- [x] 几何计算
- [x] 枚举定义
- [x] 路径类
- [x] 图搜索算法

### 文档 / Documentation
- [x] 英文README
- [x] 中文README
- [x] 使用示例
- [x] API文档
- [x] 文件清单

### 配置 / Configuration
- [x] requirements.txt
- [x] setup.py
- [x] __init__.py (所有模块)

## 🎯 使用建议 / Usage Recommendations

### 必须使用的文件 / Must-Use Files
```python
from pdms_reward import pdm_score, PDMSimulator, PDMScorer
```
这三个是最核心的组件。

### 可选使用的文件 / Optional Files
- `abstract_pdm_planner.py` - 如果需要完整规划器
- `proposal/` - 如果需要轨迹生成
- `examples/` - 学习如何使用

### 通常不需要直接使用 / Usually Not Directly Used
- `utils/` 内部函数（通过主API间接调用）
- `observation/` 内部类（由scorer自动使用）

## 📞 技术支持 / Technical Support

如遇到问题，请检查：

1. **导入错误**：确保所有依赖已安装
2. **评分异常**：查看README中的常见问题
3. **性能问题**：参考性能优化建议

## 🔄 版本信息 / Version Info

- **当前版本 / Current Version**: 1.0.0
- **发布日期 / Release Date**: 2025-12-09
- **Python要求 / Python Requirement**: >= 3.8
- **状态 / Status**: 稳定版 / Stable

---

**注意 / Note**: 此模块是完整提取，未做任何简化或删减。所有PDMS计算功能都已包含。

**Note**: This module is a complete extraction without any simplification or reduction. All PDMS computation functions are included.
