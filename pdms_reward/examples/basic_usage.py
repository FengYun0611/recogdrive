"""
PDMS奖励函数基础使用示例
Basic Usage Example for PDMS Reward Function

此示例展示了如何使用PDMS模块计算轨迹评分。
This example demonstrates how to use the PDMS module to compute trajectory scores.
"""

import numpy as np
from typing import Dict, Any

# 从pdms_reward模块导入必要的组件
# Import necessary components from pdms_reward module
from pdms_reward import (
    pdm_score,
    PDMSimulator,
    PDMScorer,
    PDMScorerConfig,
    PDMResults,
    Trajectory,
)
from nuplan.planning.simulation.trajectory.trajectory_sampling import TrajectorySampling


def example_basic_scoring():
    """
    基础评分示例
    Basic scoring example
    """
    print("=" * 60)
    print("基础PDMS评分示例 / Basic PDMS Scoring Example")
    print("=" * 60)
    
    # 1. 设置采样参数 / Setup sampling parameters
    future_sampling = TrajectorySampling(time_horizon=4.0, interval_length=0.5)
    proposal_sampling = TrajectorySampling(time_horizon=8.0, interval_length=0.5)
    
    print(f"\n采样参数 / Sampling Parameters:")
    print(f"  Future horizon: {future_sampling.time_horizon}s")
    print(f"  Proposal horizon: {proposal_sampling.time_horizon}s")
    print(f"  Interval: {future_sampling.interval_length}s")
    
    # 2. 初始化模拟器和评分器 / Initialize simulator and scorer
    simulator = PDMSimulator(proposal_sampling)
    
    scorer_config = PDMScorerConfig(
        progress_weight=5.0,
        ttc_weight=5.0,
        comfortable_weight=2.0,
        driving_direction_weight=0.0
    )
    scorer = PDMScorer(proposal_sampling, scorer_config)
    
    print(f"\n评分器配置 / Scorer Configuration:")
    print(f"  Progress weight: {scorer_config.progress_weight}")
    print(f"  TTC weight: {scorer_config.ttc_weight}")
    print(f"  Comfort weight: {scorer_config.comfortable_weight}")
    
    # 3. 创建示例轨迹 / Create example trajectory
    # 注意: 在实际使用中，这些数据应该来自你的规划器或数据集
    # Note: In practice, this data should come from your planner or dataset
    num_poses = future_sampling.num_poses
    predicted_poses = np.zeros((num_poses, 3), dtype=np.float32)
    
    # 生成一条简单的直线轨迹 / Generate a simple straight trajectory
    for i in range(num_poses):
        t = i * future_sampling.interval_length
        predicted_poses[i] = [
            2.0 * t,    # x: 2m/s 前进 / 2m/s forward
            0.1 * t,    # y: 轻微侧向偏移 / slight lateral offset
            0.02 * t    # heading: 轻微转向 / slight turn
        ]
    
    model_trajectory = Trajectory(
        poses=predicted_poses,
        trajectory_sampling=future_sampling
    )
    
    print(f"\n轨迹信息 / Trajectory Information:")
    print(f"  Number of poses: {num_poses}")
    print(f"  Start position: {predicted_poses[0]}")
    print(f"  End position: {predicted_poses[-1]}")
    
    # 4. 注意：实际使用时需要提供真实的metric_cache
    # Note: In actual use, you need to provide real metric_cache
    # results = pdm_score(
    #     metric_cache,      # 从数据集加载 / Load from dataset
    #     model_trajectory,
    #     future_sampling,
    #     simulator,
    #     scorer
    # )
    
    # 展示结果结构 / Show result structure
    print(f"\n评分结果结构 / Scoring Result Structure:")
    print("  - no_at_fault_collisions: [0.0-1.0]")
    print("  - drivable_area_compliance: [0.0-1.0]")
    print("  - ego_progress: [meters]")
    print("  - time_to_collision_within_bound: [0.0-1.0]")
    print("  - comfort: [0.0-1.0]")
    print("  - driving_direction_compliance: [0.0-1.0]")
    print("  - score: [overall score]")
    
    print("\n" + "=" * 60)


def example_reward_function():
    """
    作为强化学习奖励函数的示例
    Example as reinforcement learning reward function
    """
    print("\n" + "=" * 60)
    print("RL奖励函数示例 / RL Reward Function Example")
    print("=" * 60)
    
    class PDMRewardFunction:
        """
        使用PDMS作为RL奖励函数
        Use PDMS as RL reward function
        """
        
        def __init__(self, simulator, scorer):
            self.simulator = simulator
            self.scorer = scorer
            
        def compute_reward(
            self,
            trajectory: Trajectory,
            metric_cache: Any,
            future_sampling: TrajectorySampling
        ) -> tuple[float, Dict[str, float]]:
            """
            计算给定轨迹的奖励
            Compute reward for given trajectory
            
            Args:
                trajectory: 预测轨迹 / Predicted trajectory
                metric_cache: 场景缓存 / Scene cache
                future_sampling: 采样参数 / Sampling parameters
                
            Returns:
                reward: 标准化的奖励值 / Normalized reward value
                info: 详细的评分信息 / Detailed scoring information
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
            
            # 添加惩罚项 / Add penalty terms
            if results.no_at_fault_collisions == 0.0:
                reward -= 10.0  # 碰撞惩罚 / Collision penalty
                
            if results.drivable_area_compliance == 0.0:
                reward -= 5.0   # 偏离道路惩罚 / Off-road penalty
            
            # 鼓励进度 / Encourage progress
            reward += results.ego_progress * 0.1
            
            info = results.to_dict()
            return reward, info
    
    # 初始化奖励函数 / Initialize reward function
    proposal_sampling = TrajectorySampling(time_horizon=8.0, interval_length=0.5)
    simulator = PDMSimulator(proposal_sampling)
    scorer = PDMScorer(proposal_sampling)
    
    reward_fn = PDMRewardFunction(simulator, scorer)
    
    print("\n奖励函数已初始化 / Reward function initialized")
    print("奖励计算组件 / Reward computation components:")
    print("  - 基础PDMS分数 / Base PDMS score")
    print("  - 碰撞惩罚: -10.0 / Collision penalty: -10.0")
    print("  - 偏离道路惩罚: -5.0 / Off-road penalty: -5.0")
    print("  - 进度奖励: +0.1 × progress / Progress reward: +0.1 × progress")
    
    print("\n使用示例 / Usage example:")
    print("  reward, info = reward_fn.compute_reward(trajectory, metric_cache, future_sampling)")
    print("  print(f'Reward: {reward:.2f}')")
    print("  print(f'Info: {info}')")
    
    print("=" * 60)


def example_custom_config():
    """
    自定义配置示例
    Custom configuration example
    """
    print("\n" + "=" * 60)
    print("自定义配置示例 / Custom Configuration Example")
    print("=" * 60)
    
    # 创建自定义配置 / Create custom configuration
    custom_config = PDMScorerConfig(
        # 调整权重以适应特定场景 / Adjust weights for specific scenarios
        progress_weight=10.0,          # 更重视进度 / Emphasize progress more
        ttc_weight=8.0,                # 高安全性要求 / High safety requirement
        comfortable_weight=1.0,        # 降低舒适度要求 / Lower comfort requirement
        driving_direction_weight=2.0,  # 添加方向合规性 / Add direction compliance
        
        # 调整阈值 / Adjust thresholds
        driving_direction_horizon=1.5,
        driving_direction_compliance_threshold=1.5,
        driving_direction_violation_threshold=5.0,
        stopped_speed_threshold=0.01,
        progress_distance_threshold=3.0,
    )
    
    print("\n自定义权重 / Custom Weights:")
    print(f"  Progress: {custom_config.progress_weight}")
    print(f"  TTC: {custom_config.ttc_weight}")
    print(f"  Comfort: {custom_config.comfortable_weight}")
    print(f"  Direction: {custom_config.driving_direction_weight}")
    
    print("\n自定义阈值 / Custom Thresholds:")
    print(f"  Direction horizon: {custom_config.driving_direction_horizon}s")
    print(f"  Compliance threshold: {custom_config.driving_direction_compliance_threshold}m")
    print(f"  Violation threshold: {custom_config.driving_direction_violation_threshold}m")
    print(f"  Stopped speed: {custom_config.stopped_speed_threshold}m/s")
    print(f"  Progress distance: {custom_config.progress_distance_threshold}m")
    
    # 使用自定义配置创建评分器 / Create scorer with custom config
    proposal_sampling = TrajectorySampling(time_horizon=8.0, interval_length=0.5)
    scorer = PDMScorer(proposal_sampling, custom_config)
    
    print("\n评分器已使用自定义配置创建 / Scorer created with custom configuration")
    print("=" * 60)


def main():
    """
    主函数 - 运行所有示例
    Main function - Run all examples
    """
    print("\n")
    print("*" * 60)
    print("*" + " " * 58 + "*")
    print("*" + "  PDMS奖励函数使用示例集".center(56) + "*")
    print("*" + "  PDMS Reward Function Usage Examples".center(56) + "*")
    print("*" + " " * 58 + "*")
    print("*" * 60)
    
    # 运行各个示例 / Run examples
    example_basic_scoring()
    example_reward_function()
    example_custom_config()
    
    print("\n")
    print("*" * 60)
    print("示例运行完成！/ Examples completed!")
    print("*" * 60)
    print("\n更多信息请参考 README.md / For more information, see README.md")
    print()


if __name__ == "__main__":
    main()
