#!/usr/bin/python3
# -*- coding: utf-8 -*-
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')
    system_mode = LaunchConfiguration('system_mode')
    config_file = LaunchConfiguration('simple_slam_config_file')

    default_config = get_package_share_directory('simple_slam') + '/config/simple_slam_2d.yaml'

    simple_slam_node = Node(
        package='simple_slam',
        executable='simple_slam_node',
        name='simple_slam_node',
        output='screen',
        parameters=[
            config_file,
            {
                'use_sim_time': use_sim_time,
                'system_mode': system_mode
            }
        ]
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation time'),
        DeclareLaunchArgument(
            'system_mode',
            default_value='mapping',
            description='simple_slam mode: mapping | localization'),
        DeclareLaunchArgument(
            'simple_slam_config_file',
            default_value=default_config,
            description='simple_slam parameter file'),
        simple_slam_node,
    ])
