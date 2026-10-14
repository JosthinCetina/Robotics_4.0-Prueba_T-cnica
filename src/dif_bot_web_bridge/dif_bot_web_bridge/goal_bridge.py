#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import String
from nav2_msgs.action import NavigateToPose
from action_msgs.msg import GoalStatus
from rclpy.time import Time

class GoalBridgeNode(Node):
    def __init__(self):
        super().__init__('goal_bridge_node')
        self.nav_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        self.sub_goal = self.create_subscription(PoseStamped, '/dif_bot/web/goal_pose', self.goal_cb, 10)
        self.pub_status = self.create_publisher(String, '/dif_bot/web/nav_status', 10)

    def goal_cb(self, msg):
        if not self.nav_client.wait_for_server(timeout_sec=2.0):
            self.publish_status("ERROR: Servidor Nav2 inactivo")
            return

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = msg

        # 1. Asignar frame id 'map' y tiempo cero para forzar a TF2 a usar la transformada más reciente
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = Time().to_msg()

        # 2. SANITIZACIÓN MATEMÁTICA DEL CUATERNIÓN:
        # Si la web envía una orientación nula (norma ~ 0), forzamos un cuaternión identitario válido (w = 1.0)
        # Esto previene divisiones por cero y NaNs en C++ (tf2/planner_server).
        q = goal_msg.pose.pose.orientation
        norm_sq = q.x * q.x + q.y * q.y + q.z * q.z + q.w * q.w
        if norm_sq < 1e-4:
            goal_msg.pose.pose.orientation.x = 0.0
            goal_msg.pose.pose.orientation.y = 0.0
            goal_msg.pose.pose.orientation.z = 0.0
            goal_msg.pose.pose.orientation.w = 1.0

        self.publish_status(f"PROCESANDO: Evaluando ruta hacia X={msg.pose.position.x:.2f}, Y={msg.pose.position.y:.2f}...")

        send_goal_future = self.nav_client.send_goal_async(goal_msg, feedback_callback=self.feedback_cb)
        send_goal_future.add_done_callback(self.goal_response_cb)

    def goal_response_cb(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.publish_status("RECHAZADO: Meta inaccesible (Obstáculo o Fuera del Mapa)")
            return

        self.publish_status("EN_RUTA: Ejecutando comandos de velocidad...")
        res_future = goal_handle.get_result_async()
        res_future.add_done_callback(self.result_cb)

    def feedback_cb(self, feedback_msg):
        dist = feedback_msg.feedback.distance_remaining
        self.publish_status(f"EN_RUTA: Distancia restante {dist:.2f} m")

    def result_cb(self, future):
        status = future.result().status
        if status == GoalStatus.STATUS_SUCCEEDED:
            self.publish_status("EXITO: Meta alcanzada con precision")
        elif status == GoalStatus.STATUS_ABORTED:
            self.publish_status("ABORTADO: Nav2 fallo la ruta (Atasco o Error de Planificación)")
        elif status == GoalStatus.STATUS_CANCELED:
            self.publish_status("CANCELADO: Navegacion interrumpida")
        else:
            self.publish_status(f"FINALIZADO: Código de estado anormal ({status})")

    def publish_status(self, text):
        msg = String()
        msg.data = text
        self.pub_status.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = GoalBridgeNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
