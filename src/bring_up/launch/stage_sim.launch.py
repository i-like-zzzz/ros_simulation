#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction, SetLaunchConfiguration
from launch.substitutions import LaunchConfiguration, TextSubstitution
from launch_ros.actions import Node


def generate_launch_description():
    stage_pkg_dir = get_package_share_directory('stage_ros2')
    use_sim_time = LaunchConfiguration('use_sim_time')
    stage_enable_gui = LaunchConfiguration('stage_enable_gui')

    stage_world_arg = DeclareLaunchArgument(
        'world',
        default_value=TextSubstitution(text='my_house'),
        description='Stage world file name without .world'
    )

    def stage_world_configuration(context):
        world_file = os.path.join(
            stage_pkg_dir,
            'world',
            context.launch_configurations['world'] + '.world'
        )
        return [SetLaunchConfiguration('world_file', world_file)]

    stage_world_configuration_arg = OpaqueFunction(function=stage_world_configuration)

    stage_node = Node(
        package='stage_ros2',
        executable='stage_ros2',
        name='stage',
        parameters=[{
            'world_file': LaunchConfiguration('world_file'),
            'use_sim_time': use_sim_time,
            'enable_gui': stage_enable_gui
        }],
        remappings=[('/base_scan', '/scan')]
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation time'),
        DeclareLaunchArgument(
            'stage_enable_gui',
            default_value='true',
            description='Enable Stage GUI window'),
        stage_world_arg,
        stage_world_configuration_arg,
        stage_node,
    ])
