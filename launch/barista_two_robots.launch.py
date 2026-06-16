import os

from ament_index_python.packages import get_package_share_directory
from ament_index_python.packages import get_package_prefix

from launch import LaunchDescription
from launch.substitutions import Command
from launch_ros.actions import Node

from launch.actions import IncludeLaunchDescription
from launch.actions import TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():

    package_description = "barista_robot_description"
    urdf_file = 'barista_robot_model.urdf.xacro'
    
    robot_desc_path = os.path.join(get_package_share_directory(package_description), "xacro", urdf_file)

    # RViz Configuration
    rviz_config_dir = os.path.join(get_package_share_directory(package_description), 'rviz', 'config_two_robots.rviz')
    
    # RViz 
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz_node',
        parameters=[{'use_sim_time': True}],
        arguments=['-d', rviz_config_dir],
        output='screen'
    )

    install_dir = get_package_prefix(package_description)
    pkg_share = get_package_share_directory(package_description)

    # Path to /meshes (/meshes folder in /share folder of the barista_robot_description package)
    gazebo_models_path = os.path.join(pkg_share, 'meshes')
    
    if 'GAZEBO_MODEL_PATH' in os.environ:
        os.environ['GAZEBO_MODEL_PATH'] = os.environ['GAZEBO_MODEL_PATH'] + ':' + install_dir + '/share' + ':' + gazebo_models_path
    else:
        os.environ['GAZEBO_MODEL_PATH'] = install_dir + "/share" + ':' + gazebo_models_path

    print("GAZEBO MODELS PATH=="+str(os.environ["GAZEBO_MODEL_PATH"]))
    print("GAZEBO PLUGINS PATH=="+str(os.environ["GAZEBO_PLUGIN_PATH"]))

    # Start Gazebo
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py')
        )
    )
    
    robot_name_1 = "rick"
    robot_name_2 = "morty"

    # Robot State Publisher for robot 1
    rsp_robot_1 = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher_node',
        namespace=robot_name_1,
        parameters=[{'frame_prefix': robot_name_1 +'/',
                    'use_sim_time': True, 
                     'robot_description': Command(['xacro ', robot_desc_path, 
                                                   ' robot_name:=', robot_name_1])}],
        emulate_tty=True,
        output="screen"
    )

    # Robot State Publisher for robot 2
    rsp_robot_2 = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher_node',
        namespace=robot_name_2,
        parameters=[{'frame_prefix': robot_name_2 +'/',
                    'use_sim_time': True, 
                     'robot_description': Command(['xacro ', robot_desc_path, 
                                                   ' robot_name:=', robot_name_2])}],
        emulate_tty=True,
        output="screen"
    )
    
    # Robot Position and orientation when spawned
    robot_1_position = [0.0, 0.0, 0.0] # [X, Y, Z]
    robot_1_orientation = [0.0, 0.0, 0.0]  # [Roll, Pitch, Yaw]

    # Spawn robot 1 Set Gazebo
    spawn_robot_1 = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        name='spawn_entity',
        output='screen',
        arguments=[
            '-entity', robot_name_1,
            '-x', str(robot_1_position[0]), '-y', str(robot_1_position[1]),'-z', str(robot_1_position[2]),
            '-R', str(robot_1_orientation[0]), '-P', str(robot_1_orientation[1]), '-Y', str(robot_1_orientation[2]),
            '-topic', robot_name_1 + '/robot_description'
        ]
    )

    # Robot Position and orientation when spawned
    robot_2_position = [0.0, 1.0, 0.0] # [X, Y, Z]
    robot_2_orientation = [0.0, 0.0, 0.0]  # [Roll, Pitch, Yaw]

    # Spawn robot 2 Set Gazebo
    spawn_robot_2 = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        name='spawn_entity',
        output='screen',
        arguments=[
            '-entity', robot_name_2,
            '-x', str(robot_2_position[0]), '-y', str(robot_2_position[1]),'-z', str(robot_2_position[2]),
            '-R', str(robot_2_orientation[0]), '-P', str(robot_2_orientation[1]), '-Y', str(robot_2_orientation[2]),
            '-topic', robot_name_2 + '/robot_description'
        ]
    )

    # Static Transform Publisher - TF between /world and /rick/odom
    static_tf_pub_to_rick_odom = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_tf_pub_world_to_' + robot_name_1 +'_odom', 
        emulate_tty=True,
        output='screen',
        parameters=[{'use_sim_time':True}],
        arguments=[str(robot_1_position[0]), str(robot_1_position[1]), str(robot_1_position[2]),
                   str(robot_1_orientation[0]), str(robot_1_orientation[1]), str(robot_1_orientation[2]),
                   'world', robot_name_1 + '/odom']
    )

    # Static Transform Publisher - TF between /world and /morty/odom
    static_tf_pub_to_morty_odom = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_tf_pub_world_to_' + robot_name_2 +'_odom', 
        emulate_tty=True,
        output='screen',
        parameters=[{'use_sim_time':True}],
        arguments=[str(robot_2_position[0]), str(robot_2_position[1]), str(robot_2_position[2]),
                   str(robot_2_orientation[0]), str(robot_2_orientation[1]), str(robot_2_orientation[2]),
                   'world', robot_name_2 + '/odom']
    )

    return LaunchDescription(
        [
            gazebo,
            rsp_robot_1,
            rsp_robot_2,
            rviz_node,
            static_tf_pub_to_rick_odom,
            static_tf_pub_to_morty_odom,
            TimerAction(
                period=3.0,
                actions=[spawn_robot_1, 
                         spawn_robot_2]
            )
        ]
    )