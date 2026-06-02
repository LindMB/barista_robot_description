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
    urdf_file = 'barista_robot_model.urdf'
    
    robot_desc_path = os.path.join(get_package_share_directory(package_description), "urdf", urdf_file)
    
    # Robot State Publisher
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher_node',
        emulate_tty=True,
        parameters=[{'use_sim_time': True, 
                     'robot_description': Command(['xacro ', robot_desc_path])}],
        output="screen"
    )

    # Joint State Publisher
    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    # RViz Configuration
    rviz_config_dir = os.path.join(get_package_share_directory(package_description), 'rviz', 'config.rviz')
    
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
    
    # Robot Position and orientation when spawned
    position = [0.0, 0.0, 0.0878] # [X, Y, Z]
    orientation = [0.0, 0.0, 0.0]  # [Roll, Pitch, Yaw]

    entity_name = "barista_robot"

    # Spawn robot Set Gazebo
    spawn_robot = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        name='spawn_entity',
        output='screen',
        arguments=[
            '-entity', entity_name,
            '-x', str(position[0]), '-y', str(position[1]),'-z', str(position[2]),
            '-R', str(orientation[0]), '-P', str(orientation[1]), '-Y', str(orientation[2]),
            '-topic', '/robot_description'
        ]
    )

    return LaunchDescription(
        [
            robot_state_publisher_node,
            joint_state_publisher_node,
            rviz_node,
            gazebo,
            TimerAction(
                period=3.0,
                actions=[spawn_robot]
            )
        ]
    )