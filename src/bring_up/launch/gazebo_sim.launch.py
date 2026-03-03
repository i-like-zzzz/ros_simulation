#!/usr/bin/python3
# -*- coding: utf-8 -*-

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')
    world = LaunchConfiguration('world')
    gazebo_gui = LaunchConfiguration('gazebo_gui')

    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare('gazebo_lidar_nav_demo'),
                'launch',
                'sim_gazebo.launch.py'
            ])
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'world': world,
            'gazebo_gui': gazebo_gui
        }.items()
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation time'),
        DeclareLaunchArgument(
            'gazebo_gui',
            default_value='true',
            description='Enable Gazebo GUI'),
        DeclareLaunchArgument(
            'world',
            default_value=PathJoinSubstitution([
                FindPackageShare('gazebo_lidar_nav_demo'),
                'worlds',
                'lidar_lab.world'
            ]),
            description='Gazebo world absolute path'),
        gazebo_launch,
    ])
