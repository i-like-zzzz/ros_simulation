#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription,  GroupAction
from launch.substitutions import LaunchConfiguration, TextSubstitution
from launch.actions import DeclareLaunchArgument, OpaqueFunction, SetLaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    # --------------------------
    # 1. 路径与参数配置
    # --------------------------
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    #find some paths
    this_directory = get_package_share_directory('stage_ros2')
    cartographer_dir = get_package_share_directory('cartographer_ros')
    nav2_dir = get_package_share_directory('nav2_bringup')


    # --------------------------
    # 2. 声明启动参数与配置动作（变量化）
    # --------------------------
    # 世界文件参数声明
    stage_world_arg = DeclareLaunchArgument(
        'world',
        default_value=TextSubstitution(text='my_house'),
        description='World file relative to the project world file, without .world'
    )

    # 世界文件路径配置动作
    def stage_world_configuration(context):
        file = os.path.join(
            this_directory,
            'world',
            context.launch_configurations['world'] + '.world'
        )
        return [SetLaunchConfiguration('world_file', file)]
    stage_world_configuration_arg = OpaqueFunction(function=stage_world_configuration)

    # Cartographer 配置路径
    cartographer_config_dir = os.path.join(this_directory, 'config', 'cartographer')
    configuration_basename = 'stage_2d.lua'

    # --------------------------
    # 3. 节点定义（变量化）
    # --------------------------
    # Stage 仿真节点
    stage_node = Node(
        package='stage_ros2',
        executable='stage_ros2',
        name='stage',
        parameters=[{
            "world_file": LaunchConfiguration('world_file'),
            'use_sim_time': use_sim_time
        }],
        remappings=[("/base_scan", "/scan")]
    )

    # Cartographer SLAM 节点
    cartographer_node = Node(
        package='cartographer_ros',
        executable='cartographer_node',
        name='cartographer_node',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
        arguments=[
            '-configuration_directory', cartographer_config_dir,
            '-configuration_basename', configuration_basename
        ]
    )

    # Cartographer 栅格地图发布节点
    cartographer_occupancy_node = Node(
        package='cartographer_ros',
        executable='cartographer_occupancy_grid_node',
        name='cartographer_occupancy_grid_node',
        output='screen',
        parameters=[
            {'use_sim_time': use_sim_time},
            {'resolution': 0.05}
        ]
    )

    # RViz2 节点
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=[
            '-d', os.path.join(cartographer_dir, 'configuration_files', 'demo_2d.rviz')
        ],
        parameters=[{'use_sim_time': use_sim_time}]
    )


    nav2_including_maps_sever_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(nav2_dir, "launch",'nav2_navigation_only.launch.py')),
        launch_arguments={
            'use_sim_time': use_sim_time,
            # 'map': map_path,
        }.items(),
    )
    nav2_navigation_only_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(nav2_dir, "launch",'nav2_navigation_only.launch.py')),
        launch_arguments={
            'use_sim_time': use_sim_time,
            # 'map': map_path,
        }.items(),
        # condition=condition_using_ngp_loc_amcl
        # condition=condition_using_controller_rpp
    )
    navigation_group = GroupAction(
        actions=[
            nav2_including_maps_sever_launch,
            nav2_navigation_only_launch
        ]
    )


    # --------------------------
    # 4. return 中引用变量（不堆砌细节）
    # --------------------------
    return LaunchDescription([
        # 参数声明与配置
        stage_world_arg,
        stage_world_configuration_arg,

        # 节点启动
        stage_node,
        cartographer_node,
        cartographer_occupancy_node,
        rviz_node,
        navigation_group
    ])