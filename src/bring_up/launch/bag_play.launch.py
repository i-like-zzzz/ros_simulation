#!/usr/bin/python3
# -*- coding: utf-8 -*-
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    bag_file = LaunchConfiguration('bag_file')
    bag_rate = LaunchConfiguration('bag_rate')
    bag_loop = LaunchConfiguration('bag_loop')

    bag_play_once = ExecuteProcess(
        cmd=[
            'ros2', 'bag', 'play',
            bag_file,
            '--rate', bag_rate
        ],
        output='screen',
        condition=UnlessCondition(bag_loop)
    )

    bag_play_loop = ExecuteProcess(
        cmd=[
            'ros2', 'bag', 'play',
            bag_file,
            '--rate', bag_rate,
            '--loop'
        ],
        output='screen',
        condition=IfCondition(bag_loop)
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'bag_file',
            default_value='/home/zwc/ros_simulation/1111',
            description='Path to rosbag directory or db3 file'),
        DeclareLaunchArgument(
            'bag_rate',
            default_value='1.0',
            description='Playback rate for rosbag'),
        DeclareLaunchArgument(
            'bag_loop',
            default_value='false',
            description='Whether to loop rosbag playback'),
        bag_play_once,
        bag_play_loop,
    ])
