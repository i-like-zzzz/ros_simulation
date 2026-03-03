#!/usr/bin/python3
# -*- coding: utf-8 -*-
from ament_index_python.packages import PackageNotFoundError, get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, LogInfo, TimerAction
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
    simulator = LaunchConfiguration('simulator')
    start_navigation = LaunchConfiguration('start_navigation')
    start_rviz = LaunchConfiguration('start_rviz')
    start_stage = LaunchConfiguration('start_stage')
    stage_enable_gui = LaunchConfiguration('stage_enable_gui')
    stage_world = LaunchConfiguration('stage_world')
    gazebo_world = LaunchConfiguration('gazebo_world')
    gazebo_gui = LaunchConfiguration('gazebo_gui')
    slam_system = LaunchConfiguration('slam_system')
    cartographer_config_dir = LaunchConfiguration('cartographer_config_dir')
    nav2_autostart = LaunchConfiguration('nav2_autostart')

    bringup_launch_dir = PathJoinSubstitution([FindPackageShare('bringup'), 'launch'])

    slam_toolbox_available = True
    nav2_bringup_available = True
    gazebo_ros_available = True
    gazebo_demo_available = True

    try:
        get_package_share_directory('slam_toolbox')
    except PackageNotFoundError:
        slam_toolbox_available = False

    try:
        get_package_share_directory('nav2_bringup')
    except PackageNotFoundError:
        nav2_bringup_available = False

    try:
        get_package_share_directory('gazebo_ros')
    except PackageNotFoundError:
        gazebo_ros_available = False

    try:
        get_package_share_directory('gazebo_lidar_nav_demo')
    except PackageNotFoundError:
        gazebo_demo_available = False

    stage_include = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([bringup_launch_dir, 'stage_sim.launch.py'])
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'world': stage_world,
            'stage_enable_gui': stage_enable_gui
        }.items(),
        condition=IfCondition(
            PythonExpression([
                "'", simulator, "' == 'stage' and '", start_stage, "' == 'true' and '", play_bag, "' != 'true'"
            ])
        )
    )

    if gazebo_ros_available and gazebo_demo_available:
        gazebo_include = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution([bringup_launch_dir, 'gazebo_sim.launch.py'])
            ),
            launch_arguments={
                'use_sim_time': use_sim_time,
                'world': gazebo_world,
                'gazebo_gui': gazebo_gui
            }.items(),
            condition=IfCondition(
                PythonExpression([
                    "'", simulator, "' == 'gazebo' and '", play_bag, "' != 'true'"
                ])
            )
        )
    else:
        gazebo_include = LogInfo(
            msg='[main.launch] gazebo_ros or gazebo_lidar_nav_demo not installed, skip Gazebo launch.',
            condition=LaunchConfigurationEquals('simulator', 'gazebo')
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
                "'", slam_system,
                "' == 'cartographer' and '", play_bag,
                "' != 'true' and '", simulator,
                "' == 'stage'"
            ])
        )
    )

    cartographer_gazebo_include = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([bringup_launch_dir, 'slam_cartographer.launch.py'])
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'cartographer_config_dir': cartographer_config_dir,
            'cartographer_config_basename': 'gazebo_2d3d.lua'
        }.items(),
        condition=IfCondition(
            PythonExpression([
                "'", slam_system,
                "' == 'cartographer' and '", play_bag,
                "' != 'true' and '", simulator,
                "' == 'gazebo'"
            ])
        )
    )

    # In Gazebo mode, give gzserver/factory enough time to expose /spawn_entity first.
    cartographer_gazebo_delayed_include = TimerAction(
        period=15.0,
        actions=[cartographer_gazebo_include]
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
            default_value='/home/zwc/ros_simulation/bag/1111/zwc_0.db3',
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
            'simulator',
            default_value='stage',
            description='Simulator backend: stage | gazebo | none'),
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
            description='Legacy switch for stage. Keep true in stage mode.'),
        DeclareLaunchArgument(
            'stage_enable_gui',
            default_value='true',
            description='Enable Stage GUI window'),
        DeclareLaunchArgument(
            'stage_world',
            default_value='my_house',
            description='Stage world file name without .world'),
        DeclareLaunchArgument(
            'gazebo_gui',
            default_value='true',
            description='Enable Gazebo GUI window'),
        DeclareLaunchArgument(
            'gazebo_world',
            default_value=PathJoinSubstitution([
                FindPackageShare('gazebo_lidar_nav_demo'),
                'worlds',
                'lidar_lab.world'
            ]),
            description='Gazebo world absolute path'),
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
        LogInfo(msg=['[main.launch] simulator = ', simulator, ', slam_system = ', slam_system]),
        LogInfo(msg=['[main.launch] play_bag = ', play_bag, ', start_navigation = ', start_navigation]),
        LogInfo(msg=['[main.launch] start_rviz = ', start_rviz]),
        stage_include,
        gazebo_include,
        bag_include,
        cartographer_stage_include,
        cartographer_gazebo_delayed_include,
        cartographer_bag_include,
        slam_toolbox_include,
        navigation_include,
        rviz_include,
    ])
