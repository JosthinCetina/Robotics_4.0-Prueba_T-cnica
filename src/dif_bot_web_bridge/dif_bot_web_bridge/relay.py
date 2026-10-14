#!/usr/bin/env python3
import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import OccupancyGrid, Path
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy

class WebRelayNode(Node):
    def __init__(self):
        super().__init__('web_relay_node')

        # QoS Configs
        best_effort_qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)
        transient_qos = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL, reliability=ReliabilityPolicy.RELIABLE)

        # Suscriptores
        self.sub_scan = self.create_subscription(LaserScan, '/scan', self.scan_cb, best_effort_qos)
        self.sub_map = self.create_subscription(OccupancyGrid, '/map', self.map_cb, transient_qos)
        self.sub_plan = self.create_subscription(Path, '/plan', self.plan_cb, 10)

        # Publicadores Web
        self.pub_scan = self.create_publisher(LaserScan, '/dif_bot/web/scan', 10)
        self.pub_map = self.create_publisher(OccupancyGrid, '/dif_bot/web/map', transient_qos)
        self.pub_plan = self.create_publisher(Path, '/dif_bot/web/plan', 10)

    def scan_cb(self, msg):
        # Saneamiento de valores inf / nan para JSON de rosbridge
        sanitized_ranges = []
        for r in msg.ranges:
            if math.isnan(r) or math.isinf(r) or r > msg.range_max:
                sanitized_ranges.append(msg.range_max)
            elif r < msg.range_min:
                sanitized_ranges.append(msg.range_min)
            else:
                sanitized_ranges.append(float(r))
        
        msg.ranges = sanitized_ranges
        self.pub_scan.publish(msg)

    def map_cb(self, msg):
        self.pub_map.publish(msg)

    def plan_cb(self, msg):
        self.pub_plan.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = WebRelayNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
