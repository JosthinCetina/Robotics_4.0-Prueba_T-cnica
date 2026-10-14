#!/usr/bin/env python3
import math
import time
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
from tf2_ros import Buffer, TransformListener

def math_isnan_all(ranges):
    return all(math.isnan(r) or math.isinf(r) for r in ranges)

class HardwareValidation(Node):
    def __init__(self):
        super().__init__('hardware_validation')

        self.scan_count = 0
        self.odom_count = 0
        self.valid_scan_data = False

        self.sub_scan = self.create_subscription(LaserScan, 'scan', self.scan_cb, 10)
        self.sub_odom = self.create_subscription(Odometry, 'odom', self.odom_cb, 10)

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        self.timer = self.create_timer(3.0, self.run_diagnostics)
        self.get_logger().info('Iniciando batería de pruebas TDD de Hardware...')

    def scan_cb(self, msg):
        self.scan_count += 1
        if len(msg.ranges) > 0 and not math_isnan_all(msg.ranges):
            self.valid_scan_data = True

    def odom_cb(self, msg):
        self.odom_count += 1

    def run_diagnostics(self):
        print("\n==================================================")
        print("        REPORTE DE VALIDACIÓN TDD DE HARDWARE      ")
        print("==================================================")

        # 1. Prueba LiDAR
        scan_status = "PASS" if (self.scan_count > 5 and self.valid_scan_data) else "FAIL"
        print(f"[*] Sensor LiDAR (/scan)        : {scan_status} (Muestras: {self.scan_count})")

        # 2. Prueba Odometría
        odom_status = "PASS" if self.odom_count > 5 else "FAIL"
        print(f"[*] Odometría (/odom)            : {odom_status} (Muestras: {self.odom_count})")

        # 3. Prueba Cadena TF
        tf_status = "FAIL"
        try:
            if self.tf_buffer.can_transform('base_footprint', 'base_link', rclpy.time.Time()):
                tf_status = "PASS"
        except Exception:
            pass
        print(f"[*] Cadena TF (base_footprint->base_link) : {tf_status}")

        print("==================================================\n")
        self.timer.cancel()
        rclpy.shutdown()

def main(args=None):
    rclpy.init(args=args)
    node = HardwareValidation()
    try:
        rclpy.spin(node)
    except SystemExit:
        pass

if __name__ == '__main__':
    main()
