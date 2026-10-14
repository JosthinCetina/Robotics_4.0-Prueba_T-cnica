import os
from glob import glob
from setuptools import setup

package_name = 'dif_bot_web_bridge'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Robotics 4.0',
    maintainer_email='ceo@robotics40.com',
    description='Módulo puente entre ROS 2 y la interfaz Web.',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'robot_pose = dif_bot_web_bridge.robot_pose:main',
            'relay = dif_bot_web_bridge.relay:main',
            'goal_bridge = dif_bot_web_bridge.goal_bridge:main',
        ],
    },
)
