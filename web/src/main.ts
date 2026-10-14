import ROSLIB from 'roslib';

const ros = new ROSLIB.Ros({ url: `ws://${window.location.hostname}:9090` });
const statusBadge = document.getElementById('ws-status')!;

ros.on('connection', () => { statusBadge.textContent = 'Conectado (WS: 9090)'; statusBadge.classList.add('connected'); });
ros.on('error', () => { statusBadge.textContent = 'Error WS'; statusBadge.classList.remove('connected'); });
ros.on('close', () => { statusBadge.textContent = 'Desconectado'; statusBadge.classList.remove('connected'); });

// Teleoperación Web redirigida a /cmd_vel
const cmdVelPub = new ROSLIB.Topic({ ros: ros, name: '/cmd_vel_teleop', messageType: 'geometry_msgs/Twist' });
const sendCmd = (lin: number, ang: number) => {
  const twist = new ROSLIB.Message({ linear: {x: lin, y: 0, z: 0}, angular: {x: 0, y: 0, z: ang} });
  cmdVelPub.publish(twist);
};

document.getElementById('btn-up')?.addEventListener('click', () => sendCmd(0.3, 0));
document.getElementById('btn-down')?.addEventListener('click', () => sendCmd(-0.3, 0));
document.getElementById('btn-left')?.addEventListener('click', () => sendCmd(0, 0.8));
document.getElementById('btn-right')?.addEventListener('click', () => sendCmd(0, -0.8));
document.getElementById('btn-stop')?.addEventListener('click', () => sendCmd(0, 0));

window.addEventListener('keydown', (e) => {
  if (['input'].includes((e.target as HTMLElement).tagName.toLowerCase())) return;
  switch(e.key.toLowerCase()) {
    case 'w': case 'i': sendCmd(0.3, 0); break;
    case 's': case 'm': sendCmd(-0.3, 0); break;
    case 'a': case 'j': sendCmd(0, 0.8); break;
    case 'd': case 'l': sendCmd(0, -0.8); break;
    case 'k': case ' ': sendCmd(0, 0); break;
  }
});

// Telemetría
new ROSLIB.Topic({ ros: ros, name: '/dif_bot/web/robot_pose', messageType: 'geometry_msgs/msg/PoseStamped' })
  .subscribe((msg: any) => {
    document.getElementById('pose-frame')!.textContent = msg.header.frame_id;
    document.getElementById('pose-x')!.textContent = msg.pose.position.x.toFixed(2);
    document.getElementById('pose-y')!.textContent = msg.pose.position.y.toFixed(2);
  });

new ROSLIB.Topic({ ros: ros, name: '/dif_bot/web/nav_status', messageType: 'std_msgs/msg/String' })
  .subscribe((msg: any) => { document.getElementById('nav-status-text')!.textContent = msg.data; });

// Metas Nav2 con Saneamiento de Comas a Puntos
const goalPub = new ROSLIB.Topic({ ros: ros, name: '/dif_bot/web/goal_pose', messageType: 'geometry_msgs/msg/PoseStamped' });
document.getElementById('goal-form')?.addEventListener('submit', (e) => {
  e.preventDefault();

  const rawX = (document.getElementById('goal-x') as HTMLInputElement).value.replace(',', '.');
  const rawY = (document.getElementById('goal-y') as HTMLInputElement).value.replace(',', '.');

  const x = parseFloat(rawX);
  const y = parseFloat(rawY);

  if (isNaN(x) || isNaN(y)) return;

  goalPub.publish(new ROSLIB.Message({
    header: { frame_id: 'map' },
    pose: {
      position: { x: x, y: y, z: 0.0 },
      orientation: { x: 0.0, y: 0.0, z: 0.0, w: 1.0 }
    }
  }));
});

// Canvas LiDAR
const canvas = document.getElementById('lidar-canvas') as HTMLCanvasElement;
const ctx = canvas.getContext('2d')!;
new ROSLIB.Topic({ ros: ros, name: '/dif_bot/web/scan', messageType: 'sensor_msgs/msg/LaserScan' })
  .subscribe((msg: any) => {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const cX = canvas.width/2, cY = canvas.height/2, scale = 35;
    ctx.fillStyle = '#38bdf8'; ctx.beginPath(); ctx.arc(cX, cY, 6, 0, 2*Math.PI); ctx.fill();
    ctx.fillStyle = '#ef4444';
    let angle = msg.angle_min;
    for(let i=0; i<msg.ranges.length; i++) {
      const r = msg.ranges[i];
      if(r >= msg.range_min && r <= msg.range_max) ctx.fillRect(cX + r*Math.cos(angle)*scale, cY - r*Math.sin(angle)*scale, 2, 2);
      angle += msg.angle_increment;
    }
  });
