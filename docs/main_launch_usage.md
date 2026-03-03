# main.launch.py 使用文档（Gazebo/Stage + 可选 SLAM）

## 修复结果
- 已修复 Gazebo 启动不稳定问题：
  - `spawn_entity` 改为 `-file` 方式加载 URDF，避免 topic 模式阻塞。
  - Gazebo 默认世界改为 `lidar_lab.world`，启动后可直接看到场景障碍物，不再是只有小车。
- 已完成仓库精简：`src` 中不再依赖额外的 `turtlebot3*` 仓库目录，当前启动仅依赖本仓库内 `gazebo_lidar_nav_demo` 提供的 world/model/urdf 资产。
- 已验证：Gazebo 世界显示、URDF 成功生成、RViz2 启动、SLAM 可选。

## 关键参数
- `simulator:=gazebo|stage|none`
- `slam_system:=cartographer|slam_toolbox|none`
- `start_rviz:=true|false`
- `start_navigation:=true|false`
- `gazebo_world:=<absolute_world_path>`

## 一键启动命令（可直接复制）

### 1) Gazebo + Cartographer + RViz（推荐）
```bash
cd /home/zwc/ros_simulation && source /opt/ros/humble/setup.bash && source install/setup.bash && ros2 launch bringup main.launch.py simulator:=gazebo gazebo_gui:=true gazebo_world:=/home/zwc/ros_simulation/install/gazebo_lidar_nav_demo/share/gazebo_lidar_nav_demo/worlds/lidar_lab.world slam_system:=cartographer start_navigation:=false start_rviz:=true
```

### 2) Gazebo + SLAM Toolbox + RViz
```bash
cd /home/zwc/ros_simulation && source /opt/ros/humble/setup.bash && source install/setup.bash && ros2 launch bringup main.launch.py simulator:=gazebo gazebo_gui:=true gazebo_world:=/home/zwc/ros_simulation/install/gazebo_lidar_nav_demo/share/gazebo_lidar_nav_demo/worlds/lidar_lab.world slam_system:=slam_toolbox start_navigation:=false start_rviz:=true
```
说明：需要系统已安装 `slam_toolbox`。若未安装，启动会打印 `slam_toolbox is not installed, skip slam_toolbox launch.`。

### 3) Gazebo + 无SLAM（仅看世界和机器人）
```bash
cd /home/zwc/ros_simulation && source /opt/ros/humble/setup.bash && source install/setup.bash && ros2 launch bringup main.launch.py simulator:=gazebo gazebo_gui:=true gazebo_world:=/home/zwc/ros_simulation/install/gazebo_lidar_nav_demo/share/gazebo_lidar_nav_demo/worlds/lidar_lab.world slam_system:=none start_navigation:=false start_rviz:=true
```

## 可选世界
- 推荐：`/home/zwc/ros_simulation/install/gazebo_lidar_nav_demo/share/gazebo_lidar_nav_demo/worlds/lidar_lab.world`
- 兼容：`/home/zwc/ros_simulation/install/gazebo_lidar_nav_demo/share/gazebo_lidar_nav_demo/worlds/turtlebot3_empty.world`
- 可选：`/home/zwc/ros_simulation/install/gazebo_lidar_nav_demo/share/gazebo_lidar_nav_demo/worlds/turtlebot3_house.world`
  - 注：house 场景依赖更多外部模型，部分环境下可能加载较慢或不稳定。

## 本次实际测试（本地已执行）
- 构建：`colcon build --packages-select bringup gazebo_lidar_nav_demo` 通过。
- 启动验证（Gazebo + lidar_lab + cartographer + rviz）通过：
  - Gazebo 节点存在：`/gazebo`
  - 机器人成功生成：`Successfully spawned entity [dual_lidar_bot]`
  - 传感器发布：
    - `/scan` publisher = 1
    - `/points2` publisher = 1
  - 建图输出：`/map` publisher = 1
  - RViz2 节点存在：`/rviz2`
- 启动验证（Gazebo + lidar_lab + slam_system:=none）通过：
  - 机器人成功生成，`/scan` 与 `/points2` 均有 publisher。
- 启动验证（Gazebo + lidar_lab + slam_system:=slam_toolbox）通过启动链路：
  - 当前环境未安装 `slam_toolbox`，日志已正确提示并跳过该模块，其余 Gazebo/URDF 正常运行。
