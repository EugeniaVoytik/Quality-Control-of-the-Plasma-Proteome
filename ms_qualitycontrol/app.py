import dash
from .view import apply_app_layout

app = dash.Dash('Quality marker project')
apply_app_layout(app)