from collections import deque
import threading
import dash
from dash import dcc, html, Output, Input, Patch
import plotly.graph_objects as go

class ContinuousDataBuffer:
    """Thread-safe sliding buffer for real-time sensor streams."""
    def __init__(self, maxlen=100):
        self.lock = threading.Lock()
        self.timestamps = deque(maxlen=maxlen)
        self.x = deque(maxlen=maxlen)
        self.y = deque(maxlen=maxlen)
        self.z = deque(maxlen=maxlen)

    def push(self, t, x, y, z):
        with self.lock:
            self.timestamps.append(t)
            self.x.append(x)
            self.y.append(y)
            self.z.append(z)

    def read(self):
        with self.lock:
            return list(self.timestamps), list(self.x), list(self.y), list(self.z)

def create_smooth_dash_app(buffer_instance, update_interval_ms=50):
    """Wrapper function to build and configure the smooth Dash app."""
    app = dash.Dash(__name__)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[], y=[], mode='lines', name='Accel X'))
    fig.add_trace(go.Scatter(x=[], y=[], mode='lines', name='Accel Y'))
    fig.add_trace(go.Scatter(x=[], y=[], mode='lines', name='Accel Z'))
    fig.update_layout(title="Continuous Accelerometer Monitoring", xaxis_title="Time", yaxis_title="m/s²")

    app.layout = html.Div([
        dcc.Graph(id='live-graph', figure=fig),
        dcc.Interval(id='graph-interval', interval=update_interval_ms, n_intervals=0)
    ])

    @app.callback(
        Output('live-graph', 'figure'),
        Input('graph-interval', 'n_intervals'),
        prevent_initial_call=True
    )
    def update_smooth_graph(n):
        t, x, y, z = buffer_instance.read()
        
        patched_fig = Patch()
        patched_fig["data"][0]["x"] = t
        patched_fig["data"][0]["y"] = x
        patched_fig["data"][1]["x"] = t
        patched_fig["data"][1]["y"] = y
        patched_fig["data"][2]["x"] = t
        patched_fig["data"][2]["y"] = z
        
        return patched_fig

    return app