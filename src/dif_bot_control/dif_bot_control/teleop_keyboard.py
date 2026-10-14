#!/usr/bin/env python3
import sys
import select
import tty
import termios
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

msg_info = """
-------------------------------------------------
Control de Teleoperación por Teclado - WASD
-------------------------------------------------
  w : Avanzar
  s : Retroceder
  a : Girar Izquierda
  d : Girar Derecha
  Space / k : Detener
-------------------------------------------------
CTRL+C para salir
"""

def get_key(settings):
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ''
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

def main(args=None):
    settings = termios.tcgetattr(sys.stdin)
    rclpy.init(args=args)
    node = Node('teleop_keyboard')
    pub = node.create_publisher(Twist, 'cmd_vel_teleop', 10)

    linear_speed = 0.3
    angular_speed = 0.8

    print(msg_info)
    try:
        while rclpy.ok():
            key = get_key(settings)
            twist = Twist()
            if key == 'w':
                twist.linear.x = linear_speed
            elif key == 's':
                twist.linear.x = -linear_speed
            elif key == 'a':
                twist.angular.z = angular_speed
            elif key == 'd':
                twist.angular.z = -angular_speed
            elif key == ' ' or key == 'k':
                twist.linear.x = 0.0
                twist.angular.z = 0.0
            elif key == '\x03': # CTRL+C
                break
            else:
                continue

            pub.publish(twist)
    except Exception as e:
        print(e)
    finally:
        twist = Twist()
        pub.publish(twist)
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
