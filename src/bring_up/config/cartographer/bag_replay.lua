-- ============================================
-- Cartographer 配置文件 - 用于 ROS2 Bag 回放 SLAM
-- ============================================
include "map_builder.lua"
include "trajectory_builder.lua"

options = {
  map_builder = MAP_BUILDER,
  trajectory_builder = TRAJECTORY_BUILDER,

  -- ==================== 坐标系配置 ====================
  map_frame = "map",                    -- 地图坐标系（全局坐标系）
  tracking_frame = "lidar_top",         -- 所有传感器数据转换到这个坐标系下（通常是激光雷达坐标系）
  published_frame = "base_footprint",   -- 发布的机器人位姿坐标系（通常是机器人底座）
  odom_frame = "odom",                  -- 里程计坐标系
  provide_odom_frame = true,            -- 是否提供 odom 的 tf 变换
                                        -- true:  map -> odom -> base_footprint
                                        -- false: map -> base_footprint
  publish_frame_projected_to_2d = true, -- 是否将 3D 坐标系投影到 2D 平面

  -- ==================== 传感器配置 ====================
  use_odometry = false,                 -- 是否使用里程计数据（bag 回放时可根据实际情况选择）
  use_nav_sat = false,                  -- 是否使用 GPS 数据
  use_landmarks = false,                -- 是否使用地标数据
  num_laser_scans = 1,                  -- 使用单线激光雷达数量（1 表示使用 /scan 话题）
  num_multi_echo_laser_scans = 0,       -- 使用多回波激光雷达数量
  num_subdivisions_per_laser_scan = 1,  -- 每帧激光数据分成的处理次数（通常为 1）
  num_point_clouds = 0,                  -- 使用点云数量（0 表示不使用）

  -- ==================== 时间参数 ====================
  lookup_transform_timeout_sec = 0.2,   -- 查找 tf 变换的超时时间（秒）
  submap_publish_period_sec = 0.3,       -- 发布子地图的时间间隔（秒）
  pose_publish_period_sec = 5e-3,        -- 发布位姿的时间间隔（秒）
  trajectory_publish_period_sec = 30e-3, -- 发布轨迹的时间间隔（秒）

  -- ==================== 采样率配置 ====================
  rangefinder_sampling_ratio = 1.,       -- 激光数据采样率（1.0 表示使用全部数据）
  odometry_sampling_ratio = 1.,          -- 里程计数据采样率
  fixed_frame_pose_sampling_ratio = 1.,  -- 固定帧位姿采样率
  imu_sampling_ratio = 1.,               -- IMU 数据采样率
  landmarks_sampling_ratio = 1.,          -- 地标数据采样率
}

-- ==================== 2D SLAM 配置 ====================
MAP_BUILDER.use_trajectory_builder_2d = true  -- 启用 2D 轨迹构建器

-- ==================== 前端配置 ====================
TRAJECTORY_BUILDER_2D.use_imu_data = false      -- 是否使用 IMU 数据（如果有）
TRAJECTORY_BUILDER_2D.min_range = 0.3           -- 激光最小有效距离（米）
TRAJECTORY_BUILDER_2D.max_range = 30.          -- 激光最大有效距离（米）
TRAJECTORY_BUILDER_2D.min_z = 0.0            -- 激光点云最小高度（米）
-- TRAJECTORY_BUILDER_2D.max_z = 2.0              -- 激光点云最大高度（米）
TRAJECTORY_BUILDER_2D.missing_data_ray_length = 3.  -- 缺失数据的射线长度（米）

-- 扫描匹配配置
TRAJECTORY_BUILDER_2D.use_online_correlative_scan_matching = false  -- 是否使用在线相关性扫描匹配（暴力匹配）
TRAJECTORY_BUILDER_2D.ceres_scan_matcher.occupied_space_weight = 1.    -- 占用空间权重（点云优化残差权重）
TRAJECTORY_BUILDER_2D.ceres_scan_matcher.translation_weight = 1.       -- 平移权重（位姿推断残差权重）
TRAJECTORY_BUILDER_2D.ceres_scan_matcher.rotation_weight = 1.           -- 旋转权重（角度优化残差权重）

-- ==================== 子地图配置 ====================
TRAJECTORY_BUILDER_2D.submaps.num_range_data = 80.  -- 每个子地图包含的激光帧数
TRAJECTORY_BUILDER_2D.submaps.grid_options_2d.resolution = 0.05  -- 地图分辨率（米/像素）

-- ==================== 后端优化配置 ====================
POSE_GRAPH.optimize_every_n_nodes = 160.  -- 每插入 N 个节点进行一次全局优化
POSE_GRAPH.constraint_builder.sampling_ratio = 0.3  -- 约束构建的采样率
POSE_GRAPH.constraint_builder.max_constraint_distance = 15.  -- 约束的最大距离（米）
POSE_GRAPH.constraint_builder.min_score = 0.48  -- 约束匹配的最小分数阈值
POSE_GRAPH.constraint_builder.global_localization_min_score = 0.60  -- 全局定位的最小分数阈值

return options
