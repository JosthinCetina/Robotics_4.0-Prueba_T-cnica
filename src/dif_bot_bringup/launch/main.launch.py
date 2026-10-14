import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    pkg_gazebo = get_package_share_directory('dif_bot_gazebo')
    pkg_control = get_package_share_directory('dif_bot_control')
    pkg_web_bridge = get_package_share_directory('dif_bot_web_bridge')

    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    # 1. Simulación Gazebo (Inicia Gazebo, robot_state_publisher y spawn_entity)
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={'use_sim_time': use_sim_time}.items()
    )

    # 2. Multiplexor de Velocidad Twist Mux
    twist_mux_params = os.path.join(pkg_control, 'config', 'twist_mux.yaml')
    twist_mux_node = Node(
        package='twist_mux',
        executable='twist_mux',
        name='twist_mux',
        parameters=[twist_mux_params, {'use_sim_time': True}],
        remappings=[('/cmd_vel_out', '/cmd_vel')],
        output='screen'
    )

    # 3. Servidor WebSocket Rosbridge
    rosbridge_node = Node(
        package='rosbridge_server',
        executable='rosbridge_websocket',
        name='rosbridge_websocket',
        parameters=[{'port': 9090, 'use_sim_time': True}],
        output='screen'
    )

    # 4. Nodos Puente para la Interfaz Web
    relay_node = Node(
        package='dif_bot_web_bridge',
        executable='relay',
        name='web_relay_node',
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    robot_pose_node = Node(
        package='dif_bot_web_bridge',
        executable='robot_pose',
        name='robot_pose_node',
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    goal_bridge_node = Node(
        package='dif_bot_web_bridge',
        executable='goal_bridge',
        name='goal_bridge_node',
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        gazebo_launch,
        twist_mux_node,
        rosbridge_node,
        relay_node,
        robot_pose_node,
        goal_bridge_node
    ])
