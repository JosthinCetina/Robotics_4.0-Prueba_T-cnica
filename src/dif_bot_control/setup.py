import os
from glob import glob
from setuptools import setup

package_name = 'dif_bot_control'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Robotics 4.0',
    maintainer_email='ceo@robotics40.com',
    description='Paquete de control de posición, teleoperación y validación TDD.',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'pose_controller = dif_bot_control.pose_controller:main',
            'teleop_keyboard = dif_bot_control.teleop_keyboard:main',
            'hardware_validation = dif_bot_control.hardware_validation:main',
        ],
    },
)
