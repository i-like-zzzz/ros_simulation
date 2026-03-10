# bring_up 中接入 simple_slam 的说明

这次接入尽量沿用了仓库现在的启动习惯，没有额外再造一套入口。

## 新增了什么

- `launch/slam_simple_slam.launch.py`
  单独负责拉起 `simple_slam`。
- `launch/main.launch.py`
  新增 `slam_system:=simple_slam` 分支。

## 现在怎么用

Stage 下直接起：

```bash
ros2 launch bringup main.launch.py slam_system:=simple_slam simulator:=stage start_rviz:=true
```

如果只想验证 `simple_slam` 本身：

```bash
ros2 launch bringup slam_simple_slam.launch.py
```

切定位模式接口：

```bash
ros2 launch bringup main.launch.py slam_system:=simple_slam simple_slam_mode:=localization
```

## 参数入口

`main.launch.py` 里新增了两个参数：

- `simple_slam_config_file`
- `simple_slam_mode`

这样做是为了让 `main.launch.py` 保持“统一入口”，但 `simple_slam` 自己的参数文件还继续放在自己的包里维护。

## 目前的边界

`simple_slam` 现在主要覆盖的是前端，不是完整后端 SLAM。也就是说：

- 可以看前端轨迹和关键帧
- 可以在 Stage/Gazebo 的统一入口里切出来跑
- 还没有做到 Cartographer 那种完整回环和全局优化

后面如果继续接后端，`bring_up` 这里原则上不需要大改，只需要沿着现在这条 launch 链往下挂参数和节点。
