#!/usr/bin/env python3
import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, PoseStamped
from nav_msgs.msg import Odometry

class PoseController(Node):
    def __init__(self):
        super().__init__('pose_controller')

        # Parámetros mecánicos del robot (métricas en metros)
        self.r = 0.05  # Radio de la rueda (m)
        self.L = 0.30  # Distancia entre ruedas (m)

        # Ganancias de control proporcional
        self.Kp_lin = 0.8
        self.Kp_ang = 2.0

        # Límites de saturación
        self.max_v = 0.4   # m/s
        self.max_w = 1.2   # rad/s
        self.tol_pos = 0.05 # 5 cm de tolerancia

        # Estado actual y meta
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_theta = 0.0

        self.goal_x = None
        self.goal_y = None
        self.goal_active = False

        # Suscriptores y Publicadores
        self.sub_odom = self.create_subscription(Odometry, 'odom', self.odom_callback, 10)
        self.sub_goal = self.create_subscription(PoseStamped, 'goal_pose', self.goal_callback, 10)
        self.pub_cmd = self.create_publisher(Twist, 'cmd_vel_pose', 10)

        # Bucle de control a 20 Hz
        self.timer = self.create_timer(0.05, self.control_loop)
        self.get_logger().info('Nodo PoseController iniciado y esperando metas en /goal_pose...')

    def odom_callback(self, msg):
        self.current_x = msg.pose.pose.position.x
        self.current_y = msg.pose.pose.position.y

        # Extracción de Yaw desde Quaternion
        q = msg.pose.pose.orientation
        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        self.current_theta = math.atan2(siny_cosp, cosy_cosp)

    def goal_callback(self, msg):
        self.goal_x = msg.pose.position.x
        self.goal_y = msg.pose.position.y
        self.goal_active = True
        self.get_logger().info(f'Nueva meta recibida: X={self.goal_x:.2f}, Y={self.goal_y:.2f}')

    def control_loop(self):
        if not self.goal_active or self.goal_x is None:
            return

        dx = self.goal_x - self.current_x
        dy = self.goal_y - self.current_y
        error_pos = math.hypot(dx, dy)

        cmd = Twist()

        if error_pos < self.tol_pos:
            self.get_logger().info('¡Meta alcanzada con éxito!')
            self.goal_active = False
            self.pub_cmd.publish(cmd)
            return

        target_theta = math.atan2(dy, dx)
        error_theta = math.atan2(math.sin(target_theta - self.current_theta), math.cos(target_theta - self.current_theta))

        # Alineación previa si la orientación difiere más de 45 grados
        if abs(error_theta) > math.radians(45):
            v = 0.0
            w = self.Kp_ang * error_theta
        else:
            v = self.Kp_lin * error_pos
            w = self.Kp_ang * error_theta

        # Saturaciones
        v = max(min(v, self.max_v), -self.max_v)
        w = max(min(w, self.max_w), -self.max_w)

        # Cinemática Inversa hacia las ruedas
        w_R = (2.0 * v + w * self.L) / (2.0 * self.r)
        w_L = (2.0 * v - w * self.L) / (2.0 * self.r)

        cmd.linear.x = float(v)
        cmd.angular.z = float(w)
        self.pub_cmd.publish(cmd)

def main(args=None):
    rclpy.init(args=args)
    node = PoseController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
