from datetime import datetime, timedelta
from app import db
from app.models import FogDevice

def check_device_status():
    """
    检查设备状态的定时任务
    如果设备在60秒内没有发送心跳包，则将其状态设置为离线
    """
    timeout = datetime.utcnow() - timedelta(seconds=60)
    offline_devices = FogDevice.query.filter(
        FogDevice.status == 'online',
        FogDevice.updated_at < timeout
    ).all()
    
    for device in offline_devices:
        device.status = 'offline'
    
    if offline_devices:
        db.session.commit()
        print(f"已将 {len(offline_devices)} 个设备标记为离线状态") 