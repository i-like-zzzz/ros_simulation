#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, OpaqueFunction, GroupAction, SetLaunchConfiguration
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
import yaml


def generate_launch_description():
    # ========================
    # 1. 参数声明
    # ========================
    bag_file_arg = DeclareLaunchArgument(
        'bag_file',
        default_value='/home/zwc/ros_simulation/1111',
        description='Path to the rosbag file to replay'
    )

    bag_rate_arg = DeclareLaunchArgument(
        'bag_rate',
        default_value='1.0',
        description='Playback rate for the rosbag'
    )

    bag_loop_arg = DeclareLaunchArgument(
        'bag_loop',
        default_value='false',
        description='Whether to loop the rosbag playback'
    )

    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation time'
    )

    # ========================
    # 2. 获取路径
    # ========================
    this_package = get_package_share_directory('bringup')
    cartographer_dir = get_package_share_directory('cartographer_ros')

    # Cartographer 配置路径
    cartographer_config_dir = os.path.join(this_package, 'config', 'cartographer')
    configuration_basename = 'bag_replay.lua'

    # 加载参数文件
    params_file = os.path.join(this_package, 'config', 'bag_replay_params.yaml')
    with open(params_file, 'r') as f:
        params = yaml.safe_load(f)

    # ========================
    # 3. Bag 回放节点
    # ========================
    def bag_replay_configuration(context):
        """Get the bag file path."""
        bag_path = context.launch_configurations.get('bag_file', '/home/wenchen/workspace/1111/1111.zip')
        # 检查文件是否存在
        if not os.path.exists(bag_path):
            # 如果是 zip 文件，尝试找到解压后的 db3 文件
            bag_dir = os.path.dirname(bag_path)
            bag_name = os.path.splitext(os.path.basename(bag_path))[0]
            db3_path = os.path.join(bag_dir, bag_name + '.db3')
            if os.path.exists(db3_path):
                bag_path = db3_path

        # 如果是 .zip 文件，需要先解压
        if bag_path.endswith('.zip'):
            import zipfile
            extract_dir = os.path.dirname(bag_path)
            # 检查是否已解压
            db3_path = os.path.join(extract_dir, os.path.splitext(os.path.basename(bag_path))[0] + '.db3')
            if not os.path.exists(db3_path):
                # 解压 zip 文件
                with zipfile.ZipFile(bag_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                bag_path = db3_path

        return [SetLaunchConfiguration('bag_path', bag_path)]

    bag_replay_configuration_arg = OpaqueFunction(function=bag_replay_configuration)

    # Bag 回放节点
    bag_replay_node = ExecuteProcess(
        cmd=[
            'ros2', 'bag', 'play',
            LaunchConfiguration('bag_path'),
            '--rate', LaunchConfiguration('bag_rate'),
            '--loop'
        ],
        output='screen',
        condition=None  # 使用 LaunchCondition 控制是否循环播放
    )

    # 如果不需要循环播放，取消下面这行的注释
    bag_replay_node_no_loop = ExecuteProcess(
        cmd=[
            'ros2', 'bag', 'play',
            LaunchConfiguration('bag_path'),
            '--rate', LaunchConfiguration('bag_rate')
        ],
        output='screen'
    )

    # ========================
    # 4. Cartographer 节点
    # ========================
    cartographer_node = Node(
        package='cartographer_ros',
        executable='cartographer_node',
        name='cartographer_node',
        output='screen',
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
        arguments=[
            '-configuration_directory', cartographer_config_dir,
            '-configuration_basename', configuration_basename
        ]
    )

    # Cartographer 占用栅格地图发布节点
    cartographer_occupancy_node = Node(
        package='cartographer_ros',
        executable='cartographer_occupancy_grid_node',
        name='cartographer_occupancy_grid_node',
        output='screen',
        parameters=[
            {'use_sim_time': LaunchConfiguration('use_sim_time')},
            {'resolution': 0.05}
        ]
    )

    # ========================
    # 5. RViz2 可视化节点
    # ========================
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=[
            '-d', os.path.join(cartographer_dir, 'configuration_files', 'demo_2d.rviz')
        ],
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
        # condition=None  # 取消注释以启用 RViz
    )

    # ========================
    # 6. 返回 LaunchDescription
    # ========================
    return LaunchDescription([
        # 参数声明
        bag_file_arg,
        bag_rate_arg,
        bag_loop_arg,
        use_sim_time_arg,
        bag_replay_configuration_arg,

        # 节点（根据需要选择是否循环播放）
        bag_replay_node_no_loop,  # 不循环播放
        # bag_replay_node,  # 循环播放
        cartographer_node,
        cartographer_occupancy_node,
        # rviz_node,  # 取消注释以启动 RViz
    ])
