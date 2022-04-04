import itertools
import urllib

import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
from dash.dependencies import Input, Output, State

import ms_qualitycontrol.analysis.functions as fn
import ms_qualitycontrol.analysis.plotting_functions as plot
from run import dir_path, platelet_contamination_markers, \
    erythrocyte_contamination_markers, \
    coagulation_contamination_markers, example_file, warning_encoded
from .app import app


#############################################
# Interaction Between Components / Controller
#############################################

@app.callback(
    Output('only-graphs', 'style'),
    [Input('intermediate-value', 'children')])
def update_layout(jsonified_df):
    if jsonified_df is not None:
        return {
            'padding': '10px 10px 3050px 10px',
            'display': '',
            'marginLeft': 'auto',
            'marginRight': 'auto',
            'marginTop': '20px',
            "width": "1300px",
            'boxShadow': '0px 0px 5px 5px',
            'background-color': '#EFEFEF'
        }
    else:
        return None


@app.callback(
    Output('output', 'children'),
    [Input('upload-data', 'isCompleted'),
     Input('button-example', 'n_clicks')],
    [State('upload-data', 'fileNames'),
     State('upload-data', 'upload_id')]
)
def upload_files(is_completed, example, file_names, upload_id):
    if example is not None:
        df = fn.read_own_table(example_file)
        return df.to_json(date_format='iso', orient='split')
    elif is_completed:
        path = dir_path + f'/{upload_id}/'
        df = fn.read_own_table(path + file_names[0])
        fn.delete_uploaded_file(path, file_names[0])
        return df.to_json(date_format='iso', orient='split')


@app.callback(
    Output('output-control', 'children'),
    [Input('output', 'children'),
     Input('input-control', 'value'),
     Input('button-example', 'n_clicks'),
     Input('button', 'n_clicks')])
def check_input_control(
    jsonified_df,
    control_input,
    example,
    submit
):
    if all([jsonified_df, submit]) and example is None:
        df = pd.read_json(jsonified_df, orient='split')
        columns_control_group = fn.get_list_of_col(
            df,
            fn.lower_input(control_input)
        )
        if not control_input:
            return html.Div([
                html.Img(
                    src='data:image/png;base64,{}'.format(
                        warning_encoded.decode()
                    )
                ),
                html.H6(
                    'Please, enter any identifier for the control group.'
                )
            ], className='warning-control')
        elif not columns_control_group:
            return html.Div([
                html.Img(
                    src='data:image/png;base64,{}'.format(
                        warning_encoded.decode()
                    )
                ),
                html.H6(
                    f'The "{control_input}" identifier does not \
                    present in the column names.'
                )
            ], className='warning-control')


@app.callback(
    Output('output-samples', 'children'),
    [Input('output', 'children'),
     Input('input-samples', 'value'),
     Input('button-example', 'n_clicks'),
     Input('button', 'n_clicks')])
def check_input_control_columns(
    jsonified_df,
    sample_input,
    example,
    submit
):
    if all([jsonified_df, sample_input, submit]) and example is None:
        df = pd.read_json(jsonified_df, orient='split')
        columns_samples_group = fn.get_list_of_col(
            df,
            fn.lower_input(sample_input)
        )
        if not all([columns_samples_group, sample_input]):
            return html.Div([
                html.Img(
                    src='data:image/png;base64,{}'.format(
                        warning_encoded.decode()
                    )
                ),
                html.H6(
                    f'"{sample_input}" identifier does not \
                    present in the file columns.'
                )
            ], className='warning-samples')


# to store a created dataframe based on the uploaded .txt file
@app.callback(
    Output('intermediate-value', 'children'),
    [Input('output', 'children'),
     Input('input-control', 'value'),
     Input('input-samples', 'value'),
     Input('button', 'n_clicks'),
     Input('button-example', 'n_clicks'),
     Input('output-control', 'children'),
     Input('output-samples', 'children')])
def clean_data(
    jsonified_df,
    control_input,
    sample_input,
    submit,
    example,
    warning_control,
    warning_samples
):
    control = samples = df = pd.DataFrame()
    if example:
        df = pd.read_json(jsonified_df, orient='split')
        columns_control_group = fn.get_list_of_col(df, fn.lower_input('TP1'))
        control = df[columns_control_group].apply(pd.to_numeric)
        columns_samples_group = fn.get_list_of_col(df, fn.lower_input('TP4'))
        samples = df[columns_samples_group].apply(pd.to_numeric)
    elif all([jsonified_df, control_input, submit]) \
            and not all([warning_control, warning_samples]):
        df = pd.read_json(jsonified_df, orient='split')
        columns_control_group = fn.get_list_of_col(
            df,
            fn.lower_input(control_input)
        )
        control = df[columns_control_group].apply(pd.to_numeric)
        if not sample_input:
            columns_control_group.extend(
                ['Gene names', 'Protein IDs', 'Protein names']
            )
            samples = df.drop(columns=columns_control_group)
        else:
            columns_samples_group = fn.get_list_of_col(
                df,
                fn.lower_input(sample_input)
            )
            samples = df[columns_samples_group].apply(pd.to_numeric)
    if not control.empty and not samples.empty and not df.empty:
        # statistical analysis
        df = fn.two_sample_t_test(control, samples, df)
        df = fn.calculate_mean(control, samples, df)
        df = fn.calculate_LFC(df)
        df = df.dropna(subset=['Gene names'])
        df_filtered = fn.filter_valid_values(
            df,
            index=fn.get_reversed_list_of_col(
                df,
                fn.lower_input('LFQ')
            ),
            numeric_columns=fn.get_list_of_col(
                df,
                fn.lower_input('LFQ')
            ),
            percent=0.5,
            ax=0
        )
        return df_filtered.to_json(date_format='iso', orient='split')


@app.callback(
    Output('intermediate-value-heatmap', 'children'),
    [Input('intermediate-value', 'children')])
def prepare_data_heatmap(jsonified_df):
    if jsonified_df is not None:
        df = pd.read_json(jsonified_df, orient='split')
        data_filt = df.set_index('Gene names')[fn.get_list_of_col(
            df,
            fn.lower_input('LFQ')
        )]
        data_filt_log = np.log10(data_filt)
        data = data_filt_log.T.corr(method='pearson')
        return data.to_json(date_format='iso', orient='split')


@app.callback(
    Output('before-graphs', 'children'),
    [Input('intermediate-value', 'children')])
def plot_all_graphs(jsonified_df):
    if jsonified_df is not None:
        return html.Div([
            html.H2("Individual sample quality"),
            dcc.Markdown(
                '''
                You can use *the contamination ratio* to check \
                the quality of each individual sample.
                '''.replace('  ', ''),
                className='sample-quality-explan'
            )
        ], className='Title'),


@app.callback(
    Output('barchart-platelets-common', 'children'),
    [Input('intermediate-value', 'children')])
def plot_barchart_plat(jsonified_df):
    if jsonified_df is not None:
        return html.Div([
            html.H3("Platelets"),
            dcc.Markdown(
                '''
                Thrombocytes are a very common contamination of plasma \
                and serum samples. Due to their small size, it is more \
                difficult to separate them from plasma than other cell \
                types. Differences in the blood taking equipment, \
                centrifugation speed and how much of the plasma is \
                collected after centrifugation has an effect on the \
                degree of platelet contamination.
                '''.replace('  ', ''),
            ),
            dcc.RadioItems(
                id='radio-button-platelets',
                options=[
                    {'label': 'Contamination Ratio', 'value': 'rat'},
                ],
                value='rat',
            ),
            dcc.Slider(
                id='slider-platelets',
                min=1,
                max=4,
                marks={i: 'SD {}'.format(i) for i in range(1, 5)},
                value=3,
            ),
            dcc.Graph(
                id='barchart-platelets',
            ),
        ])


@app.callback(
    Output('barchart-platelets', 'figure'),
    [Input('intermediate-value', 'children'),
     Input('radio-button-platelets', 'value'),
     Input('slider-platelets', 'value')])
def update_barchart_plat(
    jsonified_df,
    radio_button_value,
    slider_plat
):
    if jsonified_df is not None:
        df = pd.read_json(jsonified_df, orient='split')
        df_platelet = fn.get_list_of_indices(
            df,
            'Gene names',
            fn.extract_val_from_col(
                platelet_contamination_markers,
                'Gene names',
                ';'
            ),
            ';'
        )
        platelet_calc = df_platelet[fn.get_list_of_col(
            df,
            fn.lower_input('LFQ')
        )]
        columns_names = [name.replace('LFQ', '').replace(
            ' intensity', '') for name in platelet_calc.columns]
        if radio_button_value == 'rat':
            platelet_calc_ratio, threshold_pl_std = fn.normal_ratio(
                df[fn.get_list_of_col(
                    df,
                    fn.lower_input('LFQ')
                )],
                platelet_calc,
                slider_plat
            )
            annotat = fn.create_annotations(
                platelet_calc_ratio,
                threshold_pl_std,
                columns_names
            )
            return {
                'data': plot.get_barchart_figure(
                    x=columns_names,
                    y=platelet_calc_ratio,
                    color='rgb(66, 196, 247)'
                ),
                'layout': plot.get_barchart_layout(
                    threshold=threshold_pl_std,
                    yaxis_title='Contamination Ratio<br>[Platelets : Plasma]',
                    annotations=annotat,
                )
            }


@app.callback(
    Output('barchart-erythro-common', 'children'),
    [Input('intermediate-value', 'children')])
def plot_barchart_erythro(jsonified_df):
    if jsonified_df is not None:
        return html.Div([
            html.H3("Erythrocytes"),
            dcc.Markdown(
                '''
                By contributing more than 40% of the total blood volume, \
                erythrocytes or red blood cells are a major component of \
                blood. Especially, recontamination or lysis of \
                erythrocytes are main sources for contamination.
                '''.replace('  ', ''),
            ),
            dcc.RadioItems(
                id='radio-button-erythrocytes',
                options=[
                    {'label': 'Contamination Ratio', 'value': 'rat'},
                ],
                value='rat',
            ),
            dcc.Slider(
                id='slider-erythro',
                min=1,
                max=4,
                marks={i: 'SD {}'.format(i) for i in range(1, 5)},
                value=3,
            ),
            dcc.Graph(
                id='barchart-erythrocytes',
            ),
        ])


@app.callback(
    Output('barchart-erythrocytes', 'figure'),
    [Input('intermediate-value', 'children'),
     Input('radio-button-erythrocytes', 'value'),
     Input('slider-erythro', 'value')])
def update_barchart_erythro(jsonified_df, radio_button_value, slider_erythro):
    if jsonified_df is not None:
        df = pd.read_json(jsonified_df, orient='split')
        df_erythrocyte = fn.get_list_of_indices(
            df,
            'Gene names',
            fn.extract_val_from_col(
                erythrocyte_contamination_markers,
                'Gene names',
                ';'
            ),
            ';'
        )
        erythrocyte_calc = df_erythrocyte[fn.get_list_of_col(
            df,
            fn.lower_input('LFQ')
        )]
        columns_names = [name.replace('LFQ', '').replace(
                ' intensity', '') for name in erythrocyte_calc.columns]
        if radio_button_value == 'rat':
            erythrocyte_calc_ratio, threshold_er_std = fn.normal_ratio(
                df[fn.get_list_of_col(
                    df,
                    fn.lower_input('LFQ')
                )],
                erythrocyte_calc,
                slider_erythro
            )
            annotat = fn.create_annotations(
                erythrocyte_calc_ratio,
                threshold_er_std,
                columns_names
            )
            return {
                'data': plot.get_barchart_figure(
                    x=columns_names,
                    y=erythrocyte_calc_ratio,
                    color='rgb(66, 196, 247)',
                ),
                'layout': plot.get_barchart_layout(
                    threshold=threshold_er_std,
                    yaxis_title='Contamination Ratio <br> [Erythrocytes : Plasma]',
                    annotations=annotat,
                )
            }


@app.callback(
    Output('barchart-coag-common', 'children'),
    [Input('intermediate-value', 'children'),
     Input('button', 'n_clicks'),
     Input('upload-data', 'fileNames'),
     Input('button-example', 'n_clicks')])
def plot_barchart_coag(
    jsonified_df,
    submit,
    file_name,
    example
):
    if example:
        return html.Div([
            html.H3("Coagulation"),
            dcc.Markdown(
                '''
                Plasma is obtained by mixing the blood sample with an \
                anticoagulant. Inappropriate sample handling might \
                result in unwanted coagulation. During the coagulation \
                process, several proteins will be decreased like \
                fibrinogen due to the blood clogging or will be elevated \
                like platelet factor 4, which is released from \
                thrombocytes.
                '''.replace('  ', ''),
            ),
            dcc.RadioItems(
                id='radio-button-coagulation',
                options=[
                    {'label': 'Contamination Ratio', 'value': 'rat'},
                ],
                value='rat',
            ),
            dcc.Slider(
                id='slider-coag',
                min=1,
                max=4,
                marks={i: 'SD {}'.format(i) for i in range(1, 5)},
                value=3,
            ),
            dcc.Graph(
                id='barchart-coagulation',
            ),
            html.Hr(),
        ])
    elif all([jsonified_df, submit]):
        return html.Div([
            html.H3("Coagulation"),
            dcc.Markdown(
                '''
                Plasma is obtained by mixing the blood sample with an \
                anticoagulant. Inappropriate sample handling might \
                result in unwanted coagulation. During the coagulation \
                process, several proteins will be decreased like \
                fibrinogen due to the blood clogging or will be elevated \
                like platelet factor 4, which is released from \
                thrombocytes.
                '''.replace('  ', ''),
            ),
            dcc.RadioItems(
                id='radio-button-coagulation',
                options=[
                    {'label': 'Contamination Ratio', 'value': 'rat'},
                ],
                value='rat',
            ),
            dcc.Slider(
                id='slider-coag',
                min=1,
                max=4,
                marks={i: 'SD {}'.format(i) for i in range(1, 5)},
                value=3,
            ),
            dcc.Graph(
                id='barchart-coagulation',
            ),
            html.A(
                'Download Calculated Data',
                id='download-link',
                download='%s_changed.csv' % file_name[0].split('.')[0],
                target="_blank",
                className='download-button'
            ),
            html.Hr(),
        ])


@app.callback(
    Output('barchart-coagulation', 'figure'),
    [Input('intermediate-value', 'children'),
     Input('radio-button-coagulation', 'value'),
     Input('slider-coag', 'value')])
def update_barchart_coag(
    jsonified_df,
    radio_button_value,
    slider_coag
):
    if jsonified_df is not None:
        df = pd.read_json(jsonified_df, orient='split')
        df_coagulation = fn.get_list_of_indices(
            df,
            'Gene names',
            [x for x in coagulation_contamination_markers['Gene names']
                if x in ['FGG', 'FGB', 'FGA']],
            ';'
        )
        coagulation_calc = df_coagulation[fn.get_list_of_col(
            df,
            fn.lower_input('LFQ')
        )]
        columns_names = [name.replace('LFQ', '').replace(
            ' intensity', '') for name in coagulation_calc.columns]
        if radio_button_value == 'rat':
            coagulation_calc_ratio, threshold_coag_std = fn.normal_ratio(
                df[fn.get_list_of_col(
                    df,
                    fn.lower_input('LFQ')
                )],
                coagulation_calc,
                slider_coag,
                reverse=True
            )
            annotat = fn.create_annotations(
                coagulation_calc_ratio,
                threshold_coag_std,
                columns_names
            )
            return {
                'data': plot.get_barchart_figure(
                    x=columns_names,
                    y=coagulation_calc_ratio,
                    color='rgb(66, 196, 247)'
                ),
                'layout': plot.get_barchart_layout(
                    threshold=threshold_coag_std,
                    yaxis_title='Contamination Ratio <br> [Plasma : Coagulation]',
                    annotations=annotat
                )
            }


@app.callback(
    Output('common-volcano', 'children'),
    [Input('intermediate-value', 'children')])
def plot_volcano(
    jsonified_df
):
    if jsonified_df is not None:
        df = pd.read_json(jsonified_df, orient='split').round(4)
        df_platelet = fn.get_list_of_indices(
            df,
            'Gene names',
            fn.extract_val_from_col(
                platelet_contamination_markers,
                'Gene names',
                ';'
            ),
            ';'
        )
        df_erythrocyte = fn.get_list_of_indices(
            df,
            'Gene names',
            fn.extract_val_from_col(
                erythrocyte_contamination_markers,
                'Gene names',
                ';'
            ),
            ';'
        )
        df_coagulation = fn.get_list_of_indices(
            df,
            'Gene names',
            fn.extract_val_from_col(
                coagulation_contamination_markers,
                'Gene names',
                ';'
            ),
            ';'
        )

        trace_vol_pl = plot.get_volcano_figure(
            df_platelet,
            '#990000',
            name='Platelets'
        )
        trace_vol_er = plot.get_volcano_figure(
            df_erythrocyte,
            '#006699',
            name='Erythrocytes'
        )
        trace_vol_coag = plot.get_volcano_figure(
            df_coagulation,
            '#66CCCC',
            name='Coagulation'
        )

        all_markers = []
        all_markers.extend(
            [
                df_platelet['Gene names'],
                df_erythrocyte['Gene names'],
                df_coagulation['Gene names']
            ]
        )
        all_markers_list = list(itertools.chain.from_iterable(all_markers))
        trace_vol_other = plot.get_volcano_figure(
            df.drop(
                index=[idx for idx in df.index if df.loc[
                    idx, 'Gene names'
                ] in all_markers_list
                ]
            ),
            'gray',
            opacity=0.4,
            name='Other proteins'
        )
        data_vol = [trace_vol_pl, trace_vol_er,
                    trace_vol_coag, trace_vol_other]

        figure = dict(
            data=data_vol,
            layout=plot.get_volcano_layout()
        )

        return html.Div([
            html.H2("Systemic bias"),
            dcc.Markdown(
                '''
                The volcano plot illustrates the significance and the \
                fold change of a comparison of two groups for the \
                proteins in a study. Proteins above the red dashed line \
                are considered as significantly different between both \
                groups. Proteins of each of the three quality marker \
                panels can be highlighted by clicking in the legend.
                '''.replace('  ', ''),
            ),
            dcc.Graph(
                id='plot-volcano',
                figure=figure
            )
        ])


@app.callback(
    Output('common-heatmap', 'children'),
    [Input('intermediate-value-heatmap', 'children'),
     Input('update-on-click-data', 'children')
     ])
def plot_heatmap(
    jsonified_data,
    gene
):
    if jsonified_data is not None:
        df = pd.read_json(jsonified_data, orient='split')
        annotation = []
        figure, markers = plot.get_heatmap(df, annotation)
        top3_proteins = {'erythrocytes': ['HBA1', 'HBB', 'CA1'],
                         'platelets': ['FLNA', 'TLN1', 'MYH9'],
                         'coagulation': ['FGB', 'FGG', 'FGA']}
        for each in top3_proteins['platelets']:
            stable_coordinate_platelets = [
                val for key, val in markers.items() if each in key
            ][0]
            annotation.append(
                plot.add_heatmap_annot(
                    stable_coordinate_platelets,
                    each,
                    '#990000',
                    -50,
                    label=False
                )
            )
        for each in top3_proteins['erythrocytes']:
            stable_coordinate_erythrocytes = [
                val for key, val in markers.items() if each in key
            ][0]
            annotation.append(
                plot.add_heatmap_annot(
                    stable_coordinate_erythrocytes,
                    each,
                    '#006699',
                    -50,
                    label=False
                )
            )
        for each in top3_proteins['coagulation']:
            stable_coordinate_coagulation = [
                val for key, val in markers.items() if each in key
            ][0]
            annotation.append(
                plot.add_heatmap_annot(
                    stable_coordinate_coagulation,
                    each,
                    '#66CCCC',
                    -50,
                    label=False
                )
            )
        if gene:
            colors = {
                0: '#990000', 1: '#006699', 2: '#66CCCC', 3: 'gray'
            }
            coordinate = [
                val for key, val in markers.items() if gene['text'] in key
            ][0]
            annotation.append(
                plot.add_heatmap_annot(
                    coordinate,
                    gene['text'],
                    colors[gene['curveNumber']],
                    50
                )
            )
        figure, markers = plot.get_heatmap(df, annotation)
        return html.Div([
            html.H2("Evaluation of potential markers"),
            dcc.Markdown(
                '''
                Global correlation analysis to follow up interesting \
                proteins. Pair-waise correlation of all proteins with at \
                least 50% valid values and a hierarchical clustering \
                analysis results in a global correlation map, where \
                proteins of the same origin or with the same regulation \
                mechanism will cluster together. You can select a \
                protein in the volcano plot to check if the proteins \
                falls into a cluster of erythrocyte or \
                thrombocyte-specific proteins.
                '''.replace('  ', ''),
            ),
            dcc.Graph(
                id='plot-heatmap',
                figure=figure
            ),
        ])


@app.callback(
    Output('update-on-click-data', 'children'),
    [Input('plot-volcano', 'clickData')]
)
def update_volcano_clicked_gene(
    volcano_click
):
    if volcano_click:
        return volcano_click['points'][0]


@app.callback(
    Output('download-link', 'href'),
    [Input('intermediate-value', 'children'),
     Input('barchart-platelets', 'figure'),
     Input('barchart-erythrocytes', 'figure'),
     Input('barchart-coagulation', 'figure'),
     Input('radio-button-platelets', 'value'),
     Input('slider-platelets', 'value'),
     Input('radio-button-erythrocytes', 'value'),
     Input('slider-erythro', 'value'),
     Input('radio-button-coagulation', 'value'),
     Input('slider-coag', 'value')])
def create_report(
    jsonified_df,
    barchart_plat,
    barchart_eryth,
    barchart_coag,
    radio_plat,
    slider_plat,
    radio_erythro,
    slider_erythro,
    radio_coag,
    slider_coag
):
    df = pd.read_json(jsonified_df, orient='split')
    if not df.empty:
        eigth_col = df.columns[8]
        if radio_plat == 'rat':
            plat_row_name = 'plat_contamination_ratio_SD' + str(slider_plat) \
                + '=' + str(barchart_plat['layout']['shapes'][0]['y1'])
        df.loc[plat_row_name, eigth_col:] = barchart_plat['data'][0]['y']
        df.loc[plat_row_name + '_high', eigth_col:] = [
            'no' if x < barchart_plat['layout']['shapes'][0]['y1']
            else 'yes' for x in df.loc[plat_row_name, eigth_col:]
        ]
        if radio_erythro == 'rat':
            erythro_row_name = 'erythro_contamination_ratio_SD' + \
                str(slider_erythro) + '=' + \
                str(barchart_eryth['layout']['shapes'][0]['y1'])
        df.loc[erythro_row_name, eigth_col:] = barchart_eryth['data'][0]['y']
        df.loc[erythro_row_name + '_high', eigth_col:] = [
            'no' if x < barchart_eryth['layout']['shapes'][0]['y1']
            else 'yes' for x in df.loc[erythro_row_name, eigth_col:]
        ]
        if radio_coag == 'rat':
            coag_row_name = 'coag_contamination_ratio_SD' + str(slider_coag) \
                + '=' + str(barchart_coag['layout']['shapes'][0]['y1'])
        df.loc[coag_row_name, eigth_col:] = barchart_coag['data'][0]['y']
        df.loc[coag_row_name + '_high', eigth_col:] = [
            'no' if x < barchart_coag['layout']['shapes'][0]['y1']
            else 'yes' for x in df.loc[coag_row_name, eigth_col:]
        ]
        csv_string = df.iloc[-6:, 8:].to_csv(index=True, encoding='utf-8')
        csv_string = "data:text/csv;charset=utf-8,%EF%BB%BF" + \
            urllib.parse.quote(csv_string)
        return csv_string
