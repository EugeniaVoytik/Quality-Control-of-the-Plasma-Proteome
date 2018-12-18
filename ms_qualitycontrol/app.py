import dash
from .view import apply_app_layout

app = dash.Dash('Quality marker project', csrf_protect=False)
apply_app_layout(app)