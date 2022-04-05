import os
import base64
import dash_uploader as du
from ms_qualitycontrol import app
import pandas as pd


def clean_directory(file_path):
    for root, dirs, files in os.walk(file_path, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))


logo = 'Images/logo.png'
github_logo = 'Images/github.png'
marker = 'Images/figure-markers.png'
warning = 'Images/warning-icon.png'
logo_encoded = base64.b64encode(open(logo, 'rb').read())
github_encoded = base64.b64encode(open(github_logo, 'rb').read())
markers_encoded = base64.b64encode(open(marker, 'rb').read())
warning_encoded = base64.b64encode(open(warning, 'rb').read())

dir_path = "uploads"

example_file = 'data/proteinGroups_Weight_loss_study.txt'

platelet_contamination_markers = pd.read_excel(
    'data/Marker List.xlsx',
    sheet_name='Platelets'
)
erythrocyte_contamination_markers = pd.read_excel(
    'data/Marker List.xlsx',
    sheet_name='Erythrocytes'
)
coagulation_contamination_markers = pd.read_excel(
    'data/Marker List.xlsx',
    sheet_name='Coagulation'
)

# start Flask server
if __name__ == '__main__':

    clean_directory(dir_path)

    du.configure_upload(app, dir_path, use_upload_id=True)

    app.run_server(
        debug=True, use_reloader=True,  # comment for the server
        threaded=True,
        host="0.0.0.0", port="8050"
    )
