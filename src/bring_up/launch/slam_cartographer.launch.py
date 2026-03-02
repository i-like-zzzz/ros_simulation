#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    bringup_dir = get_package_share_directory('bringup')

    default_config_dir = os.path.join(bringup_dir, 'config', 'cartographer')
    default_config_basename = 'stage_2d.lua'

    use_sim_time = LaunchConfiguration('use_sim_time')
    config_dir = LaunchConfiguration('cartographer_config_dir')
    config_basename = LaunchConfiguration('cartographer_config_basename')

    cartographer_node = Node(
        package='cartographer_ros',
        executable='cartographer_node',
        name='cartographer_node',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
        arguments=[
            '-configuration_directory', config_dir,
            '-configuration_basename', config_basename
        ]
    )

    occupancy_node = Node(
        package='cartographer_ros',
        executable='cartographer_occupancy_grid_node',
        name='cartographer_occupancy_grid_node',
        output='screen',
        parameters=[
            {'use_sim_time': use_sim_time},
            {'resolution': 0.05}
        ]
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation time'),
        DeclareLaunchArgument(
            'cartographer_config_dir',
            default_value=default_config_dir,
            description='Cartographer config directory'),
        DeclareLaunchArgument(
            'cartographer_config_basename',
            default_value=default_config_basename,
            description='Cartographer config basename'),
        cartographer_node,
        occupancy_node,
    ])
