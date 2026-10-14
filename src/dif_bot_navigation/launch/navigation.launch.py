import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, SetEnvironmentVariable
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    autostart = LaunchConfiguration('autostart', default='true')
    
    pkg_dir = get_package_share_directory('dif_bot_navigation')
    default_map_path = os.path.join(pkg_dir, 'maps', 'my_map.yaml')
    default_param_path = os.path.join(pkg_dir, 'config', 'nav2_params.yaml')

    map_yaml_file = LaunchConfiguration('map', default=default_map_path)
    params_file = LaunchConfiguration('params_file', default=default_param_path)

    lifecycle_nodes_localization = ['map_server', 'amcl']
    lifecycle_nodes_navigation = ['controller_server',
                                   'planner_server',
                                   'bt_navigator',
                                   'waypoint_follower']

    return LaunchDescription([
        SetEnvironmentVariable('RCUTILS_LOGGING_BUFFERED_STREAM', '1'),

        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('autostart', default_value='true'),
        DeclareLaunchArgument('params_file', default_value=default_param_path),
        DeclareLaunchArgument('map', default_value=default_map_path),

        # 1. LOCALIZACIÓN
        Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            output='screen',
            parameters=[default_param_path, {'yaml_filename': default_map_path}, {'use_sim_time': True}]),

        Node(
            package='nav2_amcl',
            executable='amcl',
            name='amcl',
            output='screen',
            parameters=[default_param_path, {'use_sim_time': True}]),

        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_localization',
            output='screen',
            parameters=[{'use_sim_time': True},
                        {'autostart': True},
                        {'node_names': lifecycle_nodes_localization}]),

        # 2. NAVEGACIÓN
        Node(
            package='nav2_controller',
            executable='controller_server',
            name='controller_server',
            output='screen',
            parameters=[default_param_path, {'use_sim_time': True}]),

        Node(
            package='nav2_planner',
            executable='planner_server',
            name='planner_server',
            output='screen',
            parameters=[default_param_path, {'use_sim_time': True}]),

        Node(
            package='nav2_bt_navigator',
            executable='bt_navigator',
            name='bt_navigator',
            output='screen',
            parameters=[default_param_path, {'use_sim_time': True}]),

        Node(
            package='nav2_waypoint_follower',
            executable='waypoint_follower',
            name='waypoint_follower',
            output='screen',
            parameters=[default_param_path, {'use_sim_time': True}]),

        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_navigation',
            output='screen',
            parameters=[{'use_sim_time': True},
                        {'autostart': True},
                        {'node_names': lifecycle_nodes_navigation}])
    ])
