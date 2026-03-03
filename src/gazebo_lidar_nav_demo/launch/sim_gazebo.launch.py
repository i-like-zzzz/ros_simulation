#!/usr/bin/python3
# -*- coding: utf-8 -*-

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import EnvironmentVariable, LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_dir = get_package_share_directory('gazebo_lidar_nav_demo')
    gazebo_ros_dir = get_package_share_directory('gazebo_ros')

    world = LaunchConfiguration('world')
    use_sim_time = LaunchConfiguration('use_sim_time')
    gazebo_gui = LaunchConfiguration('gazebo_gui')
    x_pose = LaunchConfiguration('x_pose')
    y_pose = LaunchConfiguration('y_pose')
    z_pose = LaunchConfiguration('z_pose')

    gazebo_model_path = SetEnvironmentVariable(
        name='GAZEBO_MODEL_PATH',
        value=[
            f'{pkg_dir}/models',
            ':',
            EnvironmentVariable('GAZEBO_MODEL_PATH', default_value='')
        ]
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(f'{gazebo_ros_dir}/launch/gazebo.launch.py'),
        launch_arguments={
            'world': world,
            'gui': gazebo_gui
        }.items()
    )

    robot_description_path = f'{pkg_dir}/urdf/dual_lidar_bot.urdf'

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[
            {'robot_description': open(robot_description_path, 'r', encoding='utf-8').read()},
            {'use_sim_time': use_sim_time}
        ]
    )

    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        output='screen',
        arguments=[
            '-entity', 'dual_lidar_bot',
            '-file', robot_description_path,
            '-x', x_pose,
            '-y', y_pose,
            '-z', z_pose
        ]
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
            default_value=f'{pkg_dir}/worlds/lidar_lab.world',
            description='Absolute path of Gazebo world file'),
        DeclareLaunchArgument('x_pose', default_value='0.0'),
        DeclareLaunchArgument('y_pose', default_value='0.0'),
        DeclareLaunchArgument('z_pose', default_value='0.15'),
        gazebo_model_path,
        gazebo,
        robot_state_publisher,
        spawn_entity,
    ])
