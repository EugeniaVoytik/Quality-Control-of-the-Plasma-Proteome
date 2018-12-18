import os
import base64
from dash_resumable_upload import decorate_server
from ms_qualitycontrol import app
import pandas as pd

def clean_directory(file_path):
    for root, dirs, files in os.walk(file_path, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))

logo = 'logo.png'
marker = 'figure-markers.png'
warning = 'warning-icon.png'
logo_encoded = base64.b64encode(open(logo, 'rb').read())
markers_encoded = base64.b64encode(open(marker, 'rb').read())
warning_encoded = base64.b64encode(open(warning, 'rb').read())

dir_path = "uploads"

example_file = 'data/example_Weight_loss_study.txt'

platelet_contamination_markers = pd.read_excel('data/Marker List.xlsx', sheet_name='Platelets')
erythrocyte_contamination_markers = pd.read_excel('data/Marker List.xlsx', sheet_name='Erythrocytes')
coagulation_contamination_markers = pd.read_excel('data/Marker List.xlsx', sheet_name='Coagulation')

# start Flask server
if __name__ == '__main__':

    clean_directory(dir_path)

    decorate_server(app.server, dir_path)
    app.scripts.config.serve_locally = True  # Uploaded to npm, this can work online now too.

    app.run_server(debug=True, use_reloader=False, threaded=True)
