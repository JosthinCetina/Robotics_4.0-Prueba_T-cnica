#!/bin/bash
export ROS_DOMAIN_ID=42
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export ROS_LOCALHOST_ONLY=0
export LIBGL_ALWAYS_SOFTWARE=1
source /opt/ros/foxy/setup.bash
source /ros2_ws/install/setup.bash

echo "=== RESTAURANDO RESTABLECIMIENTO FIJO SAVEPOINT #1 ==="

# 1. Purga limpia preventiva
pkill -9 -f gazebo 2>/dev/null
pkill -9 -f gzserver 2>/dev/null
pkill -9 -f gzclient 2>/dev/null
pkill -9 -f nav2 2>/dev/null
pkill -9 -f rosbridge 2>/dev/null
pkill -9 -f twist_mux 2>/dev/null
pkill -9 -f node 2>/dev/null
fuser -k 9090/tcp 3000/tcp 5173/tcp 2>/dev/null
rm -rf /dev/shm/fastrtps_* /dev/shm/sem.fastrtps_* 2>/dev/null

sleep 2

# 2. Lanzar Gazebo 3D + Robot Bringup
ros2 launch dif_bot_bringup main.launch.py &
PID_GAZEBO=$!
echo "Esperando 25s a que Gazebo cargue el mundo 3D y haga el spawn de dif_bot..."
sleep 25

# 3. Servidor Web Frontend
cd /ros2_ws/web
npm run dev &
PID_WEB=$!
echo "Esperando 5s a que el frontend conecte..."
sleep 5

# 4. Lanzar Navegación Autónoma Nav2
ros2 launch dif_bot_navigation navigation.launch.py map:=/ros2_ws/src/dif_bot_navigation/maps/my_map.yaml autostart:=true &
PID_NAV2=$!
echo "Esperando 12s a que Nav2 configure los nodos lifecycle..."
sleep 12

echo "=== SAVEPOINT #1 RESTAURADO Y OPERATIVO ==="

trap "kill -9 $PID_GAZEBO $PID_NAV2 $PID_WEB 2>/dev/null; pkill -9 -f gzserver; pkill -9 -f gzclient; fuser -k 3000/tcp 5173/tcp 9090/tcp 2>/dev/null" EXIT

wait
