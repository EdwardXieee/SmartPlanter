from app import app
from app.tasks import check_device_status
import threading
import time

def run_status_check():
    with app.app_context():
        while True:
            check_device_status()
            time.sleep(30)  # 每30秒检查一次设备状态

if __name__ == '__main__':
    # 启动设备状态检查线程（守护线程）
    status_thread = threading.Thread(target=run_status_check, daemon=True)
    status_thread.start()
    
    # 启动Flask应用
    app.run(host='0.0.0.0', port=5001, debug=True)
