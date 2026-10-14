#!/usr/bin/env python3
import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from tf2_ros import Buffer, TransformListener, TransformException

class RobotPosePublisher(Node):
    def __init__(self):
        super().__init__('robot_pose_publisher')
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        self.pose_pub = self.create_publisher(PoseStamped, '/dif_bot/web/robot_pose', 10)
        self.timer = self.create_timer(0.1, self.publish_pose) # 10 Hz

    def publish_pose(self):
        try:
            # Buscar transformacion desde map o odom hacia base_footprint
            target_frame = 'map'
            if not self.tf_buffer.can_transform('map', 'base_footprint', rclpy.time.Time()):
                target_frame = 'odom'

            t = self.tf_buffer.lookup_transform(target_frame, 'base_footprint', rclpy.time.Time())

            pose_msg = PoseStamped()
            pose_msg.header.stamp = self.get_clock().now().to_msg()
            pose_msg.header.frame_id = target_frame
            pose_msg.pose.position.x = t.transform.translation.x
            pose_msg.pose.position.y = t.transform.translation.y
            pose_msg.pose.position.z = t.transform.translation.z
            pose_msg.pose.orientation = t.transform.rotation

            self.pose_pub.publish(pose_msg)
        except TransformException:
            pass

def main(args=None):
    rclpy.init(args=args)
    node = RobotPosePublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
