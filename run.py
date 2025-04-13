from app import app
from app.tasks import check_device_status, prediction_task
import threading
import time

def run_status_check():
    with app.app_context():
        while True:
            check_device_status()
            time.sleep(30)  # Check the equipment status every 30 seconds.

if __name__ == '__main__':
    # Start the device status checking thread (daemon thread)
    status_thread = threading.Thread(target=run_status_check, daemon=True)
    status_thread.start()
    prediction_task.start()
    
    # Start Flask application
    app.run(host='0.0.0.0', port=5001, debug=True)
