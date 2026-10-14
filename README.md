# RB_dif_RB4: Sistema de Navegacion Autonoma y Teleoperacion Web

Este repositorio contiene el codigo fuente del proyecto RB_dif_RB4, un sistema integral para el control, simulacion y navegacion autonoma de un robot diferencial. 

## 1. Explicacion breve de la arquitectura de software utilizada

La arquitectura de software se divide en tres capas principales interconectadas a traves de ROS 2 y WebSockets:

1. Capa de Simulacion y Control (Backend): Utiliza Gazebo para la simulacion fisica del robot diferencial (dif_bot_description).
2. Capa de Navegacion (Core): Implementa Nav2 y AMCL (dif_bot_navigation) para el trazado de rutas, planificacion global (NavfnPlanner) y local (DWB Local Planner) con evasion activa de obstaculos.
3. Capa de Interfaz de Usuario (Frontend): Una aplicacion web desarrollada en React (web) que se comunica con el entorno ROS 2 mediante rosbridge_suite (WebSocket en el puerto 9090) para el envio de objetivos (waypoints), teleoperacion manual y visualizacion del sensor LiDAR 2D en tiempo real.

Estructura de directorios del codigo fuente:
.
├── dif_bot_description/    # Paquete ROS 2: URDF, modelos y plugins de Gazebo
├── dif_bot_navigation/     # Paquete ROS 2: Configuracion de Nav2, AMCL, mapas y arbol de comportamiento
├── web/                    # Aplicacion Frontend: React, Vite y roslibjs
├── start_system.sh         # Script principal de orquestacion
└── README.md               # Documentacion del proyecto

## 2. Dependencias necesarias y comandos de instalacion

Para ejecutar este proyecto, el entorno debe contar con las siguientes dependencias de sistema y software.

### Requisitos del Sistema
* Sistema Operativo: Ubuntu 20.04 LTS (ROS 2 Foxy) o Ubuntu 24.04 LTS (ROS 2 Jazzy).
* Entorno de ejecucion: Node.js (v18 o superior) y npm.

### Dependencias de ROS 2
Se requiere la instalacion de los modulos de navegacion, simulacion y comunicacion web. Ejecute el siguiente comando para instalarlas:

sudo apt update && sudo apt install -y \
  ros-$ROS_DISTRO-navigation2 \
  ros-$ROS_DISTRO-nav2-bringup \
  ros-$ROS_DISTRO-gazebo-ros-pkgs \
  ros-$ROS_DISTRO-rosbridge-suite \
  ros-$ROS_DISTRO-twist-mux \
  ros-$ROS_DISTRO-tf2-tools \
  python3-colcon-common-extensions

### Dependencias de la Aplicacion Web
El cliente de interfaz de usuario requiere paquetes especificos de Node.js. Para instalarlos, dirijase a la carpeta web y ejecute el instalador:

cd web/
npm install

## 3. Instrucciones claras de ejecucion

Antes de ejecutar cualquier comando, asegurese de compilar los paquetes de ROS 2 en la raiz de su espacio de trabajo y de proveer el entorno:

cd /ruta/a/su/espacio_de_trabajo
colcon build --packages-select dif_bot_description dif_bot_navigation
source install/setup.bash

### Metodo de ejecucion modular (Comandos ros2 launch)
Para inicializar el sistema de forma segmentada, abra cuatro terminales distintas, provea el entorno (source install/setup.bash) en cada una y ejecute los comandos en el siguiente orden estricto:

1. Iniciar el simulador Gazebo y la descripcion del robot:
ros2 launch dif_bot_description gazebo.launch.py

2. Iniciar el sistema de navegacion autonoma (Nav2 + AMCL):
ros2 launch dif_bot_navigation navigation.launch.py

3. Iniciar el servidor de comunicacion WebSocket (ROSBridge):
ros2 launch rosbridge_server rosbridge_websocket_launch.xml

4. Iniciar la interfaz web de usuario:
cd web/
npm run dev

### Metodo de ejecucion orquestada (Script automatizado)
Puede inicializar todos los modulos simultaneamente mediante el script bash proporcionado:

./start_system.sh

Una vez iniciados los servicios, la interfaz grafica estara disponible en su navegador web a traves de la direccion: http://localhost:3000

## Aviso Importante
Asegurese de no incluir archivos compilados ni carpetas build/, install/ o log/ en el repositorio. Envie unicamente el codigo fuente. El archivo .gitignore incluido en este proyecto esta configurado para descartar automaticamente dichos directorios, asi como los modulos de Node.js (node_modules/) y los empaquetados estaticos de la web (dist/).
