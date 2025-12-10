"""
PDMS奖励函数简化使用示例 - 使用MetricCacheBuilder
Simplified PDMS Usage Example - Using MetricCacheBuilder

此示例展示了如何使用MetricCacheBuilder简化PDMS评分的使用。
This example demonstrates how to use MetricCacheBuilder to simplify PDMS scoring.

这是最简单的使用方式！
This is the simplest way to use PDMS!
"""

import numpy as np

# 从pdms_reward模块导入必要的组件
# Import necessary components from pdms_reward module
from pdms_reward import (
    pdm_score,
    build_metric_cache_from_scenario,
    MetricCacheBuilder,
    PDMSimulator,
    PDMScorer,
    PDMScorerConfig,
    PDMResults,
    Trajectory,
    METRIC_CACHE_BUILDER_AVAILABLE,
)
from nuplan.planning.simulation.trajectory.trajectory_sampling import TrajectorySampling


def example_simple_usage():
    """
    最简单的使用示例 - 使用MetricCacheBuilder
    Simplest usage example - Using MetricCacheBuilder
    """
    print("=" * 70)
    print("PDMS简化使用示例 / PDMS Simplified Usage Example")
    print("=" * 70)
    
    if not METRIC_CACHE_BUILDER_AVAILABLE:
        print("\n❌ MetricCacheBuilder 不可用")
        print("   需要安装 navsim 包: pip install navsim")
        print("\n❌ MetricCacheBuilder not available")
        print("   Please install navsim: pip install navsim")
        return
    
    print("\n✅ MetricCacheBuilder 可用")
    print("✅ MetricCacheBuilder available")
    
    # 1. 设置采样参数 / Setup sampling parameters
    future_sampling = TrajectorySampling(time_horizon=4.0, interval_length=0.5)
    proposal_sampling = TrajectorySampling(time_horizon=8.0, interval_length=0.5)
    
    print(f"\n1. 采样参数 / Sampling Parameters:")
    print(f"   Future horizon: {future_sampling.time_horizon}s")
    print(f"   Interval: {future_sampling.interval_length}s")
    
    # 2. 初始化模拟器和评分器（只需一次）
    # Initialize simulator and scorer (only once)
    simulator = PDMSimulator(proposal_sampling)
    scorer = PDMScorer(proposal_sampling)
    
    print(f"\n2. 初始化完成 / Initialization Complete:")
    print(f"   ✓ PDMSimulator")
    print(f"   ✓ PDMScorer")
    
    # 3. 准备你的预测轨迹 / Prepare your predicted trajectory
    num_poses = future_sampling.num_poses
    predicted_poses = np.zeros((num_poses, 3), dtype=np.float32)
    
    # 生成一条简单的轨迹 / Generate a simple trajectory
    for i in range(num_poses):
        t = i * future_sampling.interval_length
        predicted_poses[i] = [
            2.0 * t,    # x: 2m/s forward
            0.1 * t,    # y: slight lateral movement
            0.02 * t    # heading: slight turn
        ]
    
    model_trajectory = Trajectory(
        poses=predicted_poses,
        trajectory_sampling=future_sampling
    )
    
    print(f"\n3. 轨迹准备完成 / Trajectory Prepared:")
    print(f"   Number of poses: {num_poses}")
    print(f"   Start: {predicted_poses[0]}")
    print(f"   End: {predicted_poses[-1]}")
    
    # 4. 从scenario构建MetricCache（最关键的步骤！）
    # Build MetricCache from scenario (The key step!)
    print(f"\n4. 构建MetricCache / Build MetricCache:")
    print(f"""
    这是最简单的方式！只需一行代码:
    This is the simplest way! Just one line:
    
    metric_cache = build_metric_cache_from_scenario(scenario)
    
    MetricCacheBuilder 会自动处理:
    MetricCacheBuilder automatically handles:
    - ✓ PDM-Closed规划器初始化 / PDM-Closed planner initialization
    - ✓ 参考轨迹生成 / Reference trajectory generation
    - ✓ 观察数据插值 / Observation data interpolation
    - ✓ 中心线提取 / Centerline extraction
    - ✓ 可行驶区域地图 / Drivable area map
    - ✓ 所有复杂的数据准备 / All complex data preparation
    
    在实际使用中:
    In actual usage:
    
    from nuplan.planning.scenario_builder import ... # load your scenario
    metric_cache = build_metric_cache_from_scenario(scenario)
    """)
    
    # 5. 计算PDMS评分 / Calculate PDMS score
    print(f"\n5. 计算评分 / Calculate Score:")
    print(f"""
    使用pdm_score函数:
    Using pdm_score function:
    
    results = pdm_score(
        metric_cache,         # 从scenario自动构建 / Auto-built from scenario
        model_trajectory,     # 你的预测轨迹 / Your predicted trajectory
        future_sampling,
        simulator,
        scorer
    )
    
    # 获取评分作为奖励 / Get score as reward
    reward = results.score
    print(f"Reward: {{reward:.4f}}")
    print(f"Safety: {{results.no_at_fault_collisions}}")
    print(f"Progress: {{results.ego_progress:.2f}}m")
    """)
    
    print("\n" + "=" * 70)
    print("示例说明完成 / Example Explanation Complete")
    print("=" * 70)


def example_with_custom_config():
    """
    使用自定义配置的示例
    Example with custom configuration
    """
    print("\n" + "=" * 70)
    print("自定义配置示例 / Custom Configuration Example")
    print("=" * 70)
    
    if not METRIC_CACHE_BUILDER_AVAILABLE:
        print("\n需要 navsim 包 / Requires navsim package")
        return
    
    print("""
    你可以自定义MetricCacheBuilder的参数:
    You can customize MetricCacheBuilder parameters:
    
    from pdms_reward import MetricCacheBuilder
    from nuplan.planning.simulation.trajectory.trajectory_sampling import TrajectorySampling
    
    # 创建自定义builder / Create custom builder
    builder = MetricCacheBuilder(
        future_sampling=TrajectorySampling(time_horizon=5.0, interval_length=0.1),
        proposal_sampling=TrajectorySampling(time_horizon=6.0, interval_length=0.1),
        map_radius=150.0  # 扩大地图范围 / Larger map radius
    )
    
    # 构建MetricCache / Build MetricCache
    metric_cache = builder.build_from_scenario(scenario)
    
    # 使用 / Use
    results = pdm_score(metric_cache, model_trajectory, ...)
    """)
    
    print("=" * 70)


def example_complete_workflow():
    """
    完整工作流程示例
    Complete workflow example
    """
    print("\n" + "=" * 70)
    print("完整工作流程 / Complete Workflow")
    print("=" * 70)
    
    print("""
    完整的PDMS评分工作流程:
    Complete PDMS scoring workflow:
    
    1. 准备 / Preparation
    ─────────────────────────────────────────────────────────────
    from pdms_reward import (
        pdm_score,
        build_metric_cache_from_scenario,
        PDMSimulator,
        PDMScorer,
        Trajectory,
    )
    from nuplan.planning.simulation.trajectory.trajectory_sampling import TrajectorySampling
    import numpy as np
    
    
    2. 初始化（只需一次）/ Initialize (once)
    ─────────────────────────────────────────────────────────────
    # 设置采样参数
    future_sampling = TrajectorySampling(time_horizon=4.0, interval_length=0.5)
    proposal_sampling = TrajectorySampling(time_horizon=8.0, interval_length=0.5)
    
    # 初始化模拟器和评分器
    simulator = PDMSimulator(proposal_sampling)
    scorer = PDMScorer(proposal_sampling)
    
    
    3. 对每个场景 / For each scenario
    ─────────────────────────────────────────────────────────────
    # 从scenario构建MetricCache（自动处理所有复杂度）
    metric_cache = build_metric_cache_from_scenario(scenario)
    
    # 准备你的模型预测轨迹
    predicted_poses = np.array([...])  # 你的模型输出 / Your model output
    model_trajectory = Trajectory(poses=predicted_poses, trajectory_sampling=future_sampling)
    
    # 计算PDMS评分
    results = pdm_score(
        metric_cache,
        model_trajectory,
        future_sampling,
        simulator,
        scorer
    )
    
    # 使用评分作为奖励
    reward = results.score
    
    
    4. 详细信息 / Detailed Information
    ─────────────────────────────────────────────────────────────
    print(f"Overall Score: {results.score:.4f}")
    print(f"Collision Safety: {results.no_at_fault_collisions}")  # 0.0-1.0
    print(f"Drivable Area: {results.drivable_area_compliance}")   # 0.0-1.0
    print(f"Progress: {results.ego_progress:.2f}m")               # meters
    print(f"TTC: {results.time_to_collision_within_bound}")       # 0.0-1.0
    print(f"Comfort: {results.comfort}")                          # 0.0-1.0
    print(f"Direction: {results.driving_direction_compliance}")   # 0.0-1.0
    
    
    5. 在强化学习中使用 / Use in Reinforcement Learning
    ─────────────────────────────────────────────────────────────
    class RLRewardFunction:
        def __init__(self):
            self.simulator = PDMSimulator(proposal_sampling)
            self.scorer = PDMScorer(proposal_sampling)
        
        def compute_reward(self, scenario, model_trajectory):
            # 从scenario构建cache
            metric_cache = build_metric_cache_from_scenario(scenario)
            
            # 计算PDMS评分
            results = pdm_score(
                metric_cache,
                model_trajectory,
                future_sampling,
                self.simulator,
                self.scorer
            )
            
            # 自定义奖励逻辑
            reward = results.score
            
            if results.no_at_fault_collisions == 0.0:
                reward -= 100.0  # 碰撞惩罚
            
            reward += results.ego_progress * 0.5  # 鼓励进度
            
            return reward, results.to_dict()
    """)
    
    print("=" * 70)


def main():
    """
    主函数 - 运行所有示例
    Main function - Run all examples
    """
    print("\n")
    print("*" * 70)
    print("*" + " " * 68 + "*")
    print("*" + "  PDMS简化使用指南 - MetricCacheBuilder".center(66) + "*")
    print("*" + "  PDMS Simplified Guide - MetricCacheBuilder".center(66) + "*")
    print("*" + " " * 68 + "*")
    print("*" * 70)
    
    print("""
    ┌────────────────────────────────────────────────────────────────┐
    │                                                                │
    │  💡 关键要点 / Key Point:                                      │
    │                                                                │
    │  使用 MetricCacheBuilder，你只需要:                            │
    │  With MetricCacheBuilder, you only need:                       │
    │                                                                │
    │  1. scenario（来自nuPlan数据集）                               │
    │     scenario (from nuPlan dataset)                             │
    │                                                                │
    │  2. 你的模型预测轨迹                                           │
    │     Your model's predicted trajectory                          │
    │                                                                │
    │  其他所有复杂的数据准备都自动完成！                            │
    │  All other complex data preparation is done automatically!     │
    │                                                                │
    └────────────────────────────────────────────────────────────────┘
    """)
    
    # 运行示例 / Run examples
    example_simple_usage()
    example_with_custom_config()
    example_complete_workflow()
    
    print("\n")
    print("*" * 70)
    print("示例运行完成！/ Examples completed!")
    print("*" * 70)
    print("\n更多信息请参考 README_CN.md / For more information, see README_CN.md")
    print()


if __name__ == "__main__":
    main()
