# ros_simulation

`ros_simulation` 是一个 ROS 2 仿真与建图工作区，目标是把不同仿真后端和 SLAM 流程统一到一套启动入口中，方便在同一工程里进行联调、验证和回放测试。

## 仓库定位

这个仓库主要解决三类问题：

1. 统一仿真入口  
   同时支持 `Stage` 和 `Gazebo`，减少多套 launch 文件切换成本。
2. 统一建图入口  
   在相同启动框架下切换 `Cartographer` 或 `slam_toolbox`。
3. 统一数据回放入口  
   直接用 `main.launch.py` 进行 bag 回放与建图复现。

## 核心入口

- 主启动文件：`src/bring_up/launch/main.launch.py`

通过参数控制运行模式：

- 仿真后端：`stage` / `gazebo` / `none`
- SLAM 后端：`cartographer` / `slam_toolbox` / `none`
- 是否回放 bag：`play_bag=true|false`

## 模块说明

- `src/bring_up`  
  顶层编排模块。包含统一 launch、Cartographer 配置、RViz 配置和导航联动开关。

- `src/gazebo_lidar_nav_demo`  
  Gazebo 资产模块。包含 world、URDF 以及 Gazebo 侧启动文件。

- `src/stage_ros2`  
  Stage 仿真模块，提供场景地图、机器人模型和 Stage 节点。

- `src/cartographer`  
  Cartographer 相关源码（以子模块方式维护）。

- `bag/`  
  本地回放数据目录。当前默认回放路径指向 `bag/1111`。

## 当前工程特性

- 支持仿真启动与 bag 回放两条链路
- 支持在同一入口下切换 SLAM 系统
- 支持 RViz 联动显示和后续导航扩展
- 对缺失可选依赖（如 `slam_toolbox`、`nav2_bringup`）有显式跳过提示

## 依赖与版本

- ROS 2 Humble
- `colcon` 构建工作区
- Gazebo Classic（Gazebo 模式）
- Stage（Stage 模式）

## 相关文档

- 启动参数与命令示例：`docs/main_launch_usage.md`
