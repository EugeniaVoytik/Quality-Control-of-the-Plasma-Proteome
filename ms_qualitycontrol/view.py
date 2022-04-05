import os
import dash_core_components as dcc
import dash_html_components as html
import dash_uploader as du
from run import logo_encoded, markers_encoded, github_encoded

#########################
# Dashboard Layout / View
#########################


def apply_app_layout(app):
    app.layout = html.Div([
        html.Div(children=[
            # Banner display
            html.Div([
                html.A([
                    html.Img(
                        src=f'data:image/png;base64,{github_encoded.decode()}',
                        style={
                            'float': 'left',
                            'position': 'relative',
                            'padding-top': 0,
                            'padding-right': 0,
                            'padding-left': 20,
                        }
                    )
                ], href='https://github.com/MannLabs/Quality-Control-of-the-Plasma-Proteome', target="_blank"),
                html.H1("Quality Control of the Plasma Proteome"),
                html.Img(
                    src='data:image/png;base64,{}'.format(
                        logo_encoded.decode()
                    ),
                )
            ], className='banner'),
            dcc.Markdown(
                '''
                #### A Question of Quality
                High quality clinical samples are the foundation of high \
                quality results and vice versa samples of poor quality \
                might eliminate the probability to find biologically and \
                medically interesting proteins in your sample.

                Recently, we identfied **erythrocyte lysis**, **platelet \
                contamination** and **coagulation events** as the most \
                pressuring problems for sample quality.

                Here, we supply an automated analysis of your proteomics \
                data to
                - Detect samples of poor quality;
                - Identify systematic bias in your study;
                - Check your candidates for a connection to the quality \
                marker panels.
                '''.replace('  ', ''),
                className='four columns intro'
            ),
            html.Div([
                html.Div([
                    du.Upload(
                        id='upload-data',
                        max_files=1,
                        max_file_size=1800,  # 1800 MB
                        cancel_button=True,
                        # upload_id='data',
                        pause_button=True,
                        filetypes=['txt'],
                        default_style={
                            'background-color': '#A9A9A9',
                            'font-size': '1.2vw',
                            'font-family': 'Arial',
                            'white-space': 'nowrap',
                            'padding': '45px',
                            'color': 'white',
                            'display': 'fixed',
                            'justify-content': 'center',
                            'margin': '65px auto 10px auto',
                            'width': '65%',
                            'border-radius': '20px'
                        }
                    ),
                    html.Div(
                        id='output', style={'display': 'none'}
                    )
                ]),
                html.Div([
                    dcc.Input(
                        id='input-control',
                        placeholder="Enter an identifier for control group:",
                        multiple=True,
                        type='text',
                        value='',
                        debounce=True
                    ),
                    html.Div(id='output-control', style={'height': '20px'})
                ], className='input_control',
                ),
                html.Div([
                    dcc.Input(
                        id='input-samples',
                        placeholder='Enter an identifier for sample group:',
                        multiple=True,
                        type='text',
                        value='',
                        debounce=True
                    ),
                    html.Div(id='output-samples', style={'height': '20px'})
                ], className='input_samples',
                ),
                html.Div([
                    html.Button(
                        'Submit',
                        id='button',
                        n_clicks=0,
                    ),
                    html.Div(id='intermediate-value', style={'display': 'none'}
                             ),
                    html.Div(
                        id='intermediate-value-heatmap',
                        style={'display': 'none'}
                    )
                ],
                    className='submit_button'),
            ], className='six columns all_buttons'),
            html.Div([
                html.Img(
                    src=f'data:image/png;base64,{markers_encoded.decode()}',
                ),
                dcc.Markdown(
                    '''
                    According to a literature search, including more \
                    than 200 publications in plasma proteomics. Around \
                    40% of all studies reported proteins that were \
                    associated with quality issues as biomarker \
                    candidates.
                    '''.replace('  ', ''),
                ),
                html.Button(
                    'Example',
                    id='button-example',
                    n_clicks=0,
                ),
            ], className='four columns markers')
        ], className='row',
            style={
                'padding': '0px 10px 20px 10px',
                'marginLeft': 'auto', 'marginRight': 'auto',
                "width": "1300px",
                'boxShadow': '0px 0px 5px 5px',
                'background-color': '#EFEFEF'
            }
        ),

        html.Div(id='only-graphs', children=[
            html.Div(id='before-graphs'),
            # first row - platelets
            html.Div(id='barchart-platelets-common', children=[
                dcc.RadioItems(
                    id='radio-button-platelets',
                ),
                dcc.Slider(
                    id='slider-platelets',
                ),
                dcc.Graph(
                    id='barchart-platelets',
                ),
            ], className='twelve columns barchart-platelets'),
            # second row - erythrocytes
            html.Div(id='barchart-erythro-common', children=[
                dcc.RadioItems(
                    id='radio-button-erythrocytes',
                ),
                dcc.Slider(
                    id='slider-erythro',
                ),
                dcc.Graph(
                    id='barchart-erythrocytes',
                ),
            ], className='twelve columns barchart-platelets'),
            # third row - coagulation
            html.Div(id='barchart-coag-common', children=[
                dcc.RadioItems(
                    id='radio-button-coagulation',
                ),
                dcc.Slider(
                    id='slider-coag',
                ),
                dcc.Graph(
                    id='barchart-coagulation',
                ),
                html.Button(id='button-report'),
                html.A(
                    'Download Data',
                    id='download-link',
                    download="rawdata.csv",
                    target="_blank"
                ),
                html.Hr(),
            ], className='twelve columns barchart-platelets'),

            html.Div(id='common-volcano', children=[
                dcc.Graph(
                    id='plot-volcano',
                ),
            ], className='five columns volcano-plot'),

            html.Pre(
                id='update-on-click-data',
                style={
                    'display': 'none'
                }
            ),

            html.Div(id='common-heatmap', children=[
                dcc.Graph(
                    id='plot-heatmap',
                ),
            ], className='eight columns heatmap-plot'),

        ], style={'display': 'none'}
                 ),

        html.Div([
            html.H5("Designed using"),
            html.Img(
                src="https://s3-us-west-1.amazonaws.com/plotly-tutorials/logo/new-branding/dash-logo-by-plotly-stripe-inverted.png"),
        ], className='banner-low',
            style={
                'padding': '0px 10px 10px 10px',
                'marginLeft': 'auto',
                'marginRight': 'auto',
                "width": "1300px",
            }
        ),
    ]
    )

    if 'DYNO' in os.environ:
        app.scripts.append_script({
            'external_url': 'https://cdn.rawgit.com/chriddyp/ca0d8f02a1659981a0ea7f013a378bbd/raw/'
            'e79f3f789517deec58f41251f7dbb6bee72c44ab/plotly_ga.js'
        })
