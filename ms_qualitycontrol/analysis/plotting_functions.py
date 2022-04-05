import numpy as np
import plotly.figure_factory as FF
import plotly.graph_objs as go
from scipy.cluster.hierarchy import linkage


def get_heatmap(data, annotation):
    # Initialize figure by creating upper dendrogram
    figure = FF.create_dendrogram(
        data.values,
        orientation='bottom',
        labels=data.columns,
        linkagefun=lambda x: linkage(data, 'ward', metric='euclidean'),
        colorscale=list(['dimgray', 'dimgray', 'dimgray',
                        'dimgray', 'dimgray', 'dimgray', 'dimgray'])
    )
    for i in range(len(figure['data'])):
        figure['data'][i]['yaxis'] = 'y2'

    # Create Side Dendrogram
    dendro_side = FF.create_dendrogram(
        data.values,
        orientation='right',
        linkagefun=lambda x: linkage(data, 'ward', metric='euclidean'),
        colorscale=list(['dimgray', 'dimgray', 'dimgray', 'dimgray',
                        'dimgray', 'dimgray', 'dimgray'])
    )

    for i in range(len(dendro_side['data'])):
        dendro_side['data'][i]['xaxis'] = 'x2'

    for dendro_side_data in dendro_side['data']:
        figure.add_trace(dendro_side_data)

    dendro_leaves = dendro_side['layout']['yaxis']['ticktext']
    dendro_leaves = list(map(int, dendro_leaves))
    heat_data = data.values
    heat_data = heat_data[dendro_leaves, :]
    heat_data = heat_data[:, dendro_leaves]

    # Create Heatmap
    heatmap = [
        go.Heatmap(
            x=dendro_leaves,
            y=dendro_leaves,
            z=heat_data,
            zmin=-1,
            zmax=1,
            colorscale=[[0.0, 'dodgerblue'], [0.5, 'white'], [1.0, '#FF3B3F']],
            colorbar=dict(
                x=1.0,
                y=0.405,
                tickmode='array',
                tickvals=[-1, -0.5, 0, 0.5, 1],
                ticks='outside',
                len=0.83),
            name='',
            hoverlabel={'bgcolor': 'dimgray', 'font': {
                'family': 'Arial', 'size': 13, 'color': 'white'}}
        )
    ]

    heatmap[0]['x'] = figure['layout']['xaxis']['tickvals']
    heatmap[0]['y'] = dendro_side['layout']['yaxis']['tickvals']

    # # Add Heatmap Data to Figure
    for heatmap_data in heatmap:
        figure.add_trace(heatmap_data)

    # Edit Layout
    figure['layout'].update({
        'width': 710, 'height': 710, 'margin': {
            'l': 20, 'b': 50, 't': 20, 'r': 0},
        'showlegend': False, 'hovermode': 'closest',
        'paper_bgcolor': '#EFEFEF',
        'plot_bgcolor': '#EFEFEF', 'annotations': annotation
    })
    # Edit xaxis
    figure['layout']['xaxis'].update({'domain': [.15, 1],
                                      'mirror': False,
                                      'showgrid': False,
                                      'showline': False,
                                      'zeroline': False,
                                      'showticklabels': False,
                                      'ticks': ""})
    # Edit xaxis2
    figure['layout'].update({'xaxis2': {'domain': [0, .15],
                                        'mirror': False,
                                        'showgrid': False,
                                        'showline': False,
                                        'zeroline': False,
                                        'showticklabels': False,
                                        'ticks': ""}})

    # Edit yaxis
    figure['layout']['yaxis'].update({'domain': [0, .85],
                                      'mirror': False,
                                      'showgrid': False,
                                      'showline': False,
                                      'zeroline': False,
                                      'showticklabels': False,
                                      'ticks': ""})

    figure['layout']['yaxis']['ticktext'] = \
        figure['layout']['xaxis']['ticktext']
    figure['layout']['yaxis']['tickvals'] = \
        figure['layout']['xaxis']['tickvals']

    # Edit yaxis2
    figure['layout'].update({'yaxis2': {'domain': [.8, 1],
                                        'mirror': False,
                                        'showgrid': False,
                                        'showline': False,
                                        'zeroline': False,
                                        'showticklabels': False,
                                        'ticks': ""}})
    markers = dict(zip(
        figure['layout']['xaxis']['ticktext'],
        figure['layout']['xaxis']['tickvals'])
    )
    return figure, markers


def get_volcano_figure(
    data,
    color,
    marker_size=8,
    name=None,
    opacity=1,
    marker_symbol='circle'
):
    return go.Scatter(
        x=data['L10FC'],
        y=data['(-)log10_p_val'],
        name=name,
        mode='markers',
        text=data['Gene names'],
        marker=dict(
            size=marker_size,
            symbol=marker_symbol,
            color=color,
            opacity=opacity,
            line=dict(
                width=1,
                color='dimgray'),
            showscale=False),
        hoverinfo='x+y+text')


def get_volcano_layout():
    return go.Layout(
        height=680, width=500,
        margin={'l': 40, 'b': 40, 't': 40, 'r': 20},
        paper_bgcolor='#EFEFEF',
        plot_bgcolor='#EFEFEF',
        titlefont=dict(size=20, color='black', family='Arial, sans-serif'),
        hovermode='closest',
        xaxis=dict(
            range=[-1.0, 1.0],
            title='Fold-change[Log10]',
            titlefont=dict(size=14, color='black', family='Arial, sans-serif'),
            zeroline=True,
            zerolinecolor='black',
            zerolinewidth=1,
            gridwidth=1,
            autorange=False,
            showgrid=True,
            showline=True,
            # autotick=True,
            ticks='',
            showticklabels=True),
        yaxis=dict(
            title='p-value[Log10]',
            titlefont=dict(size=14, color='black', family='Arial, sans-serif'),
            range=[0, 8],
            zeroline=False,
            zerolinecolor='black',
            zerolinewidth=1,
            gridwidth=1,
            autorange=False,
            showgrid=True,
            showline=False,
            # autotick=True,
            ticks='',
            showticklabels=True
        ),
        showlegend=True,
        shapes=[{
            'type': 'line', 'xref': 'paper', 'opacity': 1.0,
            'x0': 0, 'y0': -np.log10(0.05), 'x1': 1, 'y1': -np.log10(0.05),
            'line': {'color': '#FF3B3F', 'width': 2, 'dash': 'dash'}, }, ],
        legend=dict(x=0.82, y=1.0, traceorder='grouped', orientation="v",
                    font=dict(family='sans-serif', size=12, color='black'),
                    bordercolor='black', borderwidth=2),
    )


def get_barchart_figure(x, y, color):
    return [go.Bar(
        x=x,
        y=y,
        marker=dict(
            color=color,
        )
    )]


def get_barchart_layout(
    threshold,
    yaxis_title,
    annotations
):
    return go.Layout(
        margin={'l': 70, 'b': 100, 't': 70, 'r': 70},
        paper_bgcolor='#EFEFEF',
        plot_bgcolor='#EFEFEF',
        xaxis=dict(
            title='Sample name',
            showticklabels=True,
            tickangle=70,
            autorange=True,
            showgrid=True,
            showline=True,
            titlefont={
                'family': 'Arial, sans-serif',
                'size': 16,
                'color': 'black'
            },
            zeroline=True,
            tickfont={'size': 10, 'color': 'dimgray'},
            ticks='', ),
        yaxis=dict(
            title=yaxis_title,
            titlefont=dict(
                family='Arial, sans-serif',
                size=16,
                color='black'
            ),
            autorange=True,
            showgrid=True,
            zeroline=False,
            showline=False,
            ticks='',
            showticklabels=True,
            tickfont={'size': 10, 'color': 'dimgray'}
          ),
        shapes=[{
            'type': 'line', 'xref': 'paper', 'opacity': 0.8, 'x0': 0,
            'y0': threshold, 'x1': 1, 'y1': threshold,
            'line': {'color': 'red', 'width': 2, 'dash': 'dash'}
        }],
        annotations=annotations,
        hoverlabel=dict(
            bgcolor='#F19F4D',
            bordercolor='#A9A9A9',
            font=dict(
                family='Arial',
                size=12,
                color='white'
            ),
        ),
        autosize=True
    )


def get_barchart_layout_coag(
    threshold,
    yaxis_title,
    annotations
):
    return go.Layout(
        margin={'l': 70, 'b': 100, 't': 70, 'r': 70},
        paper_bgcolor='#EFEFEF',
        plot_bgcolor='#EFEFEF',
        xaxis=dict(
            title='Sample name',
            showticklabels=True,
            tickangle=70,
            autorange=True,
            showgrid=True,
            showline=True,
            titlefont={
                'family': 'Arial, sans-serif',
                'size': 16,
                'color': 'black'
            },
            zeroline=True,
            tickfont={'size': 10, 'color': 'dimgray'},
            ticks='',
        ),
        yaxis=dict(
            title=yaxis_title,
            titlefont=dict(
                family='Arial, sans-serif',
                size=16,
                color='black'
            ),
            autorange=True,
            showgrid=True,
            zeroline=False,
            showline=False,
            ticks='',
            showticklabels=True,
            tickfont={'size': 10, 'color': 'dimgray'}
        ),
        shapes=[{
            'type': 'line',
            'xref': 'paper',
            'opacity': 0.8,
            'x0': 0, 'y0': threshold,
            'x1': 1,
            'y1': threshold,
            'line': {'color': 'red', 'width': 2, 'dash': 'dash'}
        }],
        annotations=annotations,
        hoverlabel=dict(
            bgcolor='#F19F4D',
            bordercolor='#A9A9A9',
            font=dict(
                family='Arial',
                size=12,
                color='white'
            )
        ),
        autosize=True
    )


def add_heatmap_annot(
    coordinate,
    gene_name,
    arrow_color,
    ay,
    label=True
):
    if label is True:
        return dict(
            x=coordinate,
            y=coordinate,
            xref='x',
            yref='y',
            text='<b>{}</b>'.format(gene_name),
            showarrow=True,
            arrowcolor=arrow_color,
            arrowsize=1,
            arrowwidth=2,
            arrowhead=5,
            ax=0,
            ay=ay,
            font=dict(
                color=arrow_color,
                size=15,
                family='Arial'
            )
        )
    else:
        return dict(
            x=coordinate,
            y=coordinate,
            xref='x',
            yref='y',
            showarrow=True,
            arrowcolor=arrow_color,
            arrowsize=1,
            arrowwidth=2,
            arrowhead=5,
            ax=0,
            ay=ay,
            font=dict(
                color=arrow_color,
                size=15,
                family='Arial'
            )
        )
