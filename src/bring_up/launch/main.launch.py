#!/usr/bin/python3
# -*- coding: utf-8 -*-
from ament_index_python.packages import PackageNotFoundError, get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, LogInfo
from launch.conditions import IfCondition, LaunchConfigurationEquals
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, PythonExpression
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')
    play_bag = LaunchConfiguration('play_bag')
    bag_file = LaunchConfiguration('bag_file')
    bag_rate = LaunchConfiguration('bag_rate')
    bag_loop = LaunchConfiguration('bag_loop')
    start_navigation = LaunchConfiguration('start_navigation')
    start_rviz = LaunchConfiguration('start_rviz')
    start_stage = LaunchConfiguration('start_stage')
    stage_enable_gui = LaunchConfiguration('stage_enable_gui')
    world = LaunchConfiguration('world')
    slam_system = LaunchConfiguration('slam_system')
    cartographer_config_dir = LaunchConfiguration('cartographer_config_dir')
    nav2_autostart = LaunchConfiguration('nav2_autostart')

    bringup_launch_dir = PathJoinSubstitution([FindPackageShare('bringup'), 'launch'])
    slam_toolbox_available = True
    nav2_bringup_available = True
    try:
        get_package_share_directory('slam_toolbox')
    except PackageNotFoundError:
        slam_toolbox_available = False
    try:
        get_package_share_directory('nav2_bringup')
    except PackageNotFoundError:
        nav2_bringup_available = False

    stage_include = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([bringup_launch_dir, 'stage_sim.launch.py'])
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'world': world,
            'stage_enable_gui': stage_enable_gui
        }.items(),
        condition=IfCondition(
            PythonExpression([
                "'", start_stage, "' == 'true' and '", play_bag, "' != 'true'"
            ])
        )
    )

    bag_include = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([bringup_launch_dir, 'bag_play.launch.py'])
        ),
        launch_arguments={
            'bag_file': bag_file,
            'bag_rate': bag_rate,
            'bag_loop': bag_loop
        }.items(),
        condition=IfCondition(play_bag)
    )

    cartographer_stage_include = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([bringup_launch_dir, 'slam_cartographer.launch.py'])
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'cartographer_config_dir': cartographer_config_dir,
            'cartographer_config_basename': 'stage_scan_2d.lua'
        }.items(),
        condition=IfCondition(
            PythonExpression([
                "'", slam_system, "' == 'cartographer' and '", play_bag, "' != 'true'"
            ])
        )
    )

    cartographer_bag_include = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([bringup_launch_dir, 'slam_cartographer.launch.py'])
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'cartographer_config_dir': cartographer_config_dir,
            'cartographer_config_basename': 'bag_replay.lua'
        }.items(),
        condition=IfCondition(
            PythonExpression([
                "'", slam_system, "' == 'cartographer' and '", play_bag, "' == 'true'"
            ])
        )
    )

    if slam_toolbox_available:
        slam_toolbox_include = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution([bringup_launch_dir, 'slam_toolbox.launch.py'])
            ),
            launch_arguments={
                'use_sim_time': use_sim_time
            }.items(),
            condition=LaunchConfigurationEquals('slam_system', 'slam_toolbox')
        )
    else:
        slam_toolbox_include = LogInfo(
            msg='[main.launch] slam_toolbox is not installed, skip slam_toolbox launch.',
            condition=LaunchConfigurationEquals('slam_system', 'slam_toolbox')
        )

    if nav2_bringup_available:
        navigation_include = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution([bringup_launch_dir, 'navigation.launch.py'])
            ),
            launch_arguments={
                'use_sim_time': use_sim_time,
                'autostart': nav2_autostart
            }.items(),
            condition=IfCondition(start_navigation)
        )
    else:
        navigation_include = LogInfo(
            msg='[main.launch] nav2_bringup is not installed, skip navigation launch.',
            condition=IfCondition(start_navigation)
        )

    rviz_include = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([bringup_launch_dir, 'rviz.launch.py'])
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'rviz_config': LaunchConfiguration('rviz_config')
        }.items(),
        condition=IfCondition(start_rviz)
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation time'),
        DeclareLaunchArgument(
            'play_bag',
            default_value='false',
            description='Start rosbag playback'),
        DeclareLaunchArgument(
            'bag_file',
            default_value='/home/zwc/ros_simulation/1111',
            description='Path to rosbag directory or db3 file'),
        DeclareLaunchArgument(
            'bag_rate',
            default_value='1.0',
            description='Rosbag playback rate'),
        DeclareLaunchArgument(
            'bag_loop',
            default_value='false',
            description='Whether rosbag loops playback'),
        DeclareLaunchArgument(
            'slam_system',
            default_value='none',
            description='SLAM system: cartographer | slam_toolbox | none'),
        DeclareLaunchArgument(
            'start_navigation',
            default_value='false',
            description='Start Nav2 navigation stack'),
        DeclareLaunchArgument(
            'start_rviz',
            default_value='false',
            description='Start RViz2'),
        DeclareLaunchArgument(
            'start_stage',
            default_value='true',
            description='Start stage simulator (disabled automatically when play_bag=true)'),
        DeclareLaunchArgument(
            'stage_enable_gui',
            default_value='true',
            description='Enable Stage GUI window'),
        DeclareLaunchArgument(
            'world',
            default_value='my_house',
            description='Stage world name without .world'),
        DeclareLaunchArgument(
            'cartographer_config_dir',
            default_value=PathJoinSubstitution([
                FindPackageShare('bringup'),
                'config',
                'cartographer'
            ]),
            description='Cartographer config directory'),
        DeclareLaunchArgument(
            'nav2_autostart',
            default_value='true',
            description='Autostart Nav2 lifecycle nodes'),
        DeclareLaunchArgument(
            'rviz_config',
            default_value=PathJoinSubstitution([
                FindPackageShare('bringup'),
                'rviz',
                'common.rviz'
            ]),
            description='RViz config file path'),
        LogInfo(msg=['[main.launch] slam_system = ', slam_system]),
        LogInfo(msg=['[main.launch] play_bag = ', play_bag, ', start_navigation = ', start_navigation]),
        LogInfo(msg=['[main.launch] start_rviz = ', start_rviz]),
        stage_include,
        bag_include,
        cartographer_stage_include,
        cartographer_bag_include,
        slam_toolbox_include,
        navigation_include,
        rviz_include,
    ])
