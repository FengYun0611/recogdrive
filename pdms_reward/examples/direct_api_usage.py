"""
PDMS奖励函数直接API使用示例
Direct API Usage Example for PDMS Reward Function

此示例展示了如何使用pdm_score_direct()函数，无需MetricCache即可计算PDMS评分。
This example demonstrates how to use pdm_score_direct() to compute PDMS scores 
without requiring MetricCache.
"""

import numpy as np
from typing import List

# 从pdms_reward模块导入必要的组件
# Import necessary components from pdms_reward module
from pdms_reward import (
    pdm_score_direct,
    PDMSimulator,
    PDMScorer,
    PDMScorerConfig,
    PDMResults,
    Trajectory,
)
from pdms_reward.observation import PDMObservation, PDMDrivableMap
from pdms_reward.utils import PDMPath

from nuplan.planning.simulation.trajectory.trajectory_sampling import TrajectorySampling
from nuplan.common.actor_state.ego_state import EgoState


def example_direct_api():
    """
    使用直接API的示例 - 无需MetricCache
    Example using direct API - no MetricCache needed
    """
    print("=" * 70)
    print("PDMS直接API使用示例 / PDMS Direct API Usage Example")
    print("=" * 70)
    
    # 1. 设置采样参数 / Setup sampling parameters
    future_sampling = TrajectorySampling(time_horizon=4.0, interval_length=0.5)
    proposal_sampling = TrajectorySampling(time_horizon=8.0, interval_length=0.5)
    
    print(f"\n1. 采样参数 / Sampling Parameters:")
    print(f"   Future horizon: {future_sampling.time_horizon}s")
    print(f"   Proposal horizon: {proposal_sampling.time_horizon}s")
    print(f"   Interval: {future_sampling.interval_length}s")
    
    # 2. 初始化模拟器和评分器 / Initialize simulator and scorer
    simulator = PDMSimulator(proposal_sampling)
    
    scorer_config = PDMScorerConfig(
        progress_weight=5.0,
        ttc_weight=5.0,
        comfortable_weight=2.0,
        driving_direction_weight=0.0
    )
    scorer = PDMScorer(proposal_sampling, scorer_config)
    
    print(f"\n2. 初始化完成 / Initialization Complete:")
    print(f"   Simulator: PDMSimulator")
    print(f"   Scorer: PDMScorer with custom config")
    
    # 3. 准备输入数据 / Prepare input data
    print(f"\n3. 准备输入数据 / Prepare Input Data:")
    
    # 3a. 创建轨迹 / Create trajectory
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
    print(f"   ✓ Trajectory created: {num_poses} poses")
    
    # 3b. 初始自车状态 / Initial ego state
    # 注意: 在实际使用中，这应该来自你的数据
    # Note: In practice, this should come from your data
    print(f"   ✓ Initial ego state: (需要从数据中获取 / from your data)")
    
    # 3c. 观察数据 / Observation data
    # 包含其他车辆、障碍物等信息
    # Contains other vehicles, obstacles, etc.
    print(f"   ✓ Observation: (需要从场景数据创建 / create from scene data)")
    
    # 3d. 中心线路径 / Centerline path
    # 用于计算进度指标
    # Used for progress calculation
    print(f"   ✓ Centerline: (需要从地图数据创建 / create from map data)")
    
    # 3e. 路线车道ID / Route lane IDs
    # 规划路线上的车道ID列表
    # List of lane IDs on planned route
    print(f"   ✓ Route lane IDs: (需要从路由规划获取 / from route planning)")
    
    # 3f. 可行驶区域地图 / Drivable area map
    # 地图的可行驶区域
    # Drivable areas of the map
    print(f"   ✓ Drivable area map: (需要从地图数据创建 / create from map data)")
    
    print(f"\n4. 使用方法说明 / Usage Instructions:")
    print(f"""
    在实际使用中，你需要准备以下输入:
    In practice, you need to prepare the following inputs:
    
    a) model_trajectory: Trajectory
       - 你的模型预测的轨迹（相对坐标系）
       - Your model's predicted trajectory (in ego frame)
       - 格式: np.array([[x, y, heading], ...])
    
    b) initial_ego_state: EgoState
       - 当前时刻的自车状态
       - Current ego vehicle state
       - 包含: 位置、速度、加速度、车辆参数等
       - Contains: position, velocity, acceleration, vehicle params, etc.
    
    c) observation: PDMObservation
       - 环境观察数据（其他车辆、障碍物）
       - Environment observation (other vehicles, obstacles)
       - 从传感器数据或场景数据创建
       - Created from sensor data or scene data
    
    d) centerline: PDMPath
       - 规划路径的中心线
       - Centerline of planned route
       - 用于计算沿路径的进度
       - Used to calculate progress along route
    
    e) route_lane_ids: List[str]
       - 规划路线上的车道ID列表
       - List of lane IDs on planned route
       - 用于判断是否在正确车道
       - Used to check if on correct lanes
    
    f) drivable_area_map: PDMDrivableMap
       - 可行驶区域地图
       - Drivable area map
       - 用于检查是否偏离道路
       - Used to check off-road violations
    """)
    
    print(f"\n5. 调用示例 / Example Call:")
    print("""
    # 当你准备好所有输入后 / When you have all inputs ready:
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
    
    # 使用结果 / Use results:
    print(f"Overall Score: {results.score:.4f}")
    print(f"Collision Safety: {results.no_at_fault_collisions}")
    print(f"Drivable Area: {results.drivable_area_compliance}")
    print(f"Progress: {results.ego_progress:.2f}m")
    print(f"TTC: {results.time_to_collision_within_bound}")
    print(f"Comfort: {results.comfort}")
    print(f"Direction: {results.driving_direction_compliance}")
    """)
    
    print(f"\n" + "=" * 70)
    print("示例完成 / Example Complete")
    print("=" * 70)


def example_with_data_preparation():
    """
    数据准备的详细说明
    Detailed explanation of data preparation
    """
    print("\n" + "=" * 70)
    print("数据准备详细说明 / Data Preparation Details")
    print("=" * 70)
    
    print("""
    1. 准备轨迹 (Trajectory)
    ─────────────────────────────────────────────────────────
    import numpy as np
    from pdms_reward import Trajectory
    from nuplan.planning.simulation.trajectory.trajectory_sampling import TrajectorySampling
    
    # 创建轨迹数据（相对坐标系）
    # Create trajectory data (in ego frame)
    poses = np.array([
        [0.0, 0.0, 0.0],      # [x, y, heading] at t=0
        [2.0, 0.1, 0.05],     # at t=0.5s
        [4.0, 0.2, 0.08],     # at t=1.0s
        # ... more poses
    ], dtype=np.float32)
    
    trajectory = Trajectory(
        poses=poses,
        trajectory_sampling=TrajectorySampling(
            time_horizon=4.0, 
            interval_length=0.5
        )
    )
    
    
    2. 准备自车状态 (EgoState)
    ─────────────────────────────────────────────────────────
    from nuplan.common.actor_state.ego_state import EgoState
    from nuplan.common.actor_state.state_representation import StateSE2, StateVector2D
    from nuplan.common.actor_state.vehicle_parameters import get_pacifica_parameters
    
    # 从你的数据创建EgoState
    # Create EgoState from your data
    ego_state = EgoState.build_from_rear_axle(
        rear_axle_pose=StateSE2(x, y, heading),
        rear_axle_velocity_2d=StateVector2D(vx, vy),
        rear_axle_acceleration_2d=StateVector2D(ax, ay),
        tire_steering_angle=steering_angle,
        time_point=TimePoint(timestamp_us),
        vehicle_parameters=get_pacifica_parameters()
    )
    
    
    3. 准备观察数据 (PDMObservation)
    ─────────────────────────────────────────────────────────
    from pdms_reward.observation import PDMObservation
    
    # 从场景数据创建观察
    # Create observation from scene data
    observation = PDMObservation(
        trajectory_sampling=trajectory_sampling,
        proposal_sampling=proposal_sampling,
        map_radius=map_radius
    )
    
    # 更新观察数据
    # Update with current observation data
    observation.update(
        ego_state,
        detected_objects,  # 从传感器或场景获取
        traffic_light_data,
        route_lane_dict
    )
    
    
    4. 准备中心线 (PDMPath)
    ─────────────────────────────────────────────────────────
    from pdms_reward.utils import PDMPath
    
    # 从路由规划获取中心线点
    # Get centerline points from route planning
    centerline_points = [...]  # List of StateSE2
    centerline = PDMPath(centerline_points)
    
    
    5. 准备可行驶区域地图 (PDMDrivableMap)
    ─────────────────────────────────────────────────────────
    from pdms_reward.observation import PDMDrivableMap
    
    # 从地图数据创建可行驶区域地图
    # Create drivable area map from map data
    drivable_map = PDMDrivableMap(map_api, ego_state, map_radius)
    
    
    6. 完整调用示例
    ─────────────────────────────────────────────────────────
    from pdms_reward import pdm_score_direct
    
    results = pdm_score_direct(
        model_trajectory=trajectory,
        initial_ego_state=ego_state,
        observation=observation,
        centerline=centerline,
        route_lane_ids=['lane_1', 'lane_2', ...],
        drivable_area_map=drivable_map,
        future_sampling=future_sampling,
        simulator=simulator,
        scorer=scorer
    )
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
    print("*" + "  PDMS直接API使用指南".center(66) + "*")
    print("*" + "  PDMS Direct API Usage Guide".center(66) + "*")
    print("*" + " " * 68 + "*")
    print("*" * 70)
    
    # 运行示例 / Run examples
    example_direct_api()
    example_with_data_preparation()
    
    print("\n")
    print("*" * 70)
    print("示例运行完成！/ Examples completed!")
    print("*" * 70)
    print("\n更多信息请参考 README.md / For more information, see README.md")
    print()


if __name__ == "__main__":
    main()
