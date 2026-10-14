import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    pkg_description = get_package_share_directory('dif_bot_description')
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    pkg_control = get_package_share_directory('dif_bot_control')

    world_file = os.path.join(get_package_share_directory('dif_bot_gazebo'), 'worlds', 'my_world.world')
    xacro_file = os.path.join(pkg_description, 'urdf', 'dif_bot_description.urdf.xacro')
    twist_mux_config = os.path.join(pkg_control, 'config', 'twist_mux.yaml')

    robot_description_content = ParameterValue(Command(['xacro ', xacro_file]), value_type=str)

    # CORRECCIÓN CRÍTICA: use_sim_time declarado estrictamente como booleano True
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'use_sim_time': True, 'robot_description': robot_description_content}]
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py')),
        launch_arguments={'world': world_file}.items()
    )

    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description', '-entity', 'dif_bot', '-z', '0.1'],
        output='screen'
    )

    node_twist_mux = Node(
        package='twist_mux',
        executable='twist_mux',
        output='screen',
        parameters=[twist_mux_config, {'use_sim_time': True}],
        remappings=[('cmd_vel_out', '/cmd_vel')]
    )

    return LaunchDescription([
        node_robot_state_publisher,
        gazebo,
        spawn_entity,
        node_twist_mux
    ])
