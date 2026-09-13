import time
import threading
from arduino_iot_cloud import ArduinoCloudClient
from smooth_dash import ContinuousDataBuffer, create_smooth_dash_app

# 1. Initialize buffer
data_buffer = ContinuousDataBuffer(maxlen=100)

# 2. Enter your real Arduino IoT Cloud credentials here
DEVICE_ID = "961dab04-1693-414c-bf0a-2f31c0efd3f0"
SECRET_KEY = "kOSv0w92fKBSCQw1MIGvBTtSC"

# Track baseline time and latest values
start_time = time.time()
latest_vals = {"x": 0.0, "y": 0.0, "z": 0.0}

# 3. Callback functions when IoT variables update
def on_x_changed(client, value):
    latest_vals["x"] = float(value)
    data_buffer.push(
        round(time.time() - start_time, 2),
        latest_vals["x"],
        latest_vals["y"],
        latest_vals["z"]
    )

def on_y_changed(client, value):
    latest_vals["y"] = float(value)

def on_z_changed(client, value):
    latest_vals["z"] = float(value)

# 4. Initialize client in synchronous mode for safe background polling
client = ArduinoCloudClient(
    device_id=DEVICE_ID,
    username=DEVICE_ID,
    password=SECRET_KEY,
    sync_mode=True
)

client.register("accel_x", value=None, on_write=on_x_changed)
client.register("accel_y", value=None, on_write=on_y_changed)
client.register("accel_z", value=None, on_write=on_z_changed)

def run_arduino_cloud():
    client.start()
    while True:
        client.update()
        time.sleep(0.1)

# Start Arduino cloud loop in a separate daemon thread
cloud_thread = threading.Thread(target=run_arduino_cloud, daemon=True)
cloud_thread.start()

# 5. Build and run Dash app
app = create_smooth_dash_app(data_buffer, update_interval_ms=50)

if __name__ == '__main__':
    app.run(debug=True)