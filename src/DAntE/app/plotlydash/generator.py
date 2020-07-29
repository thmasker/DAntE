import datetime

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html


MIN, MAX = 1, 4
SMOOTH_MIN, SMOOTH_MAX = 0, 3


generator_layout = [
    dcc.Interval(id='generator-interval', max_intervals=0, n_intervals=1),
    dbc.Row(
        id='generator-selectors',
        children=[
            dbc.Col(
                children=[
                    dcc.Dropdown(
                        id='generator-type-dropdown',
                        placeholder='Select consumer type'
                    )
                ]
            ),
            dbc.Col(
                children=[
                    dcc.RadioItems(
                        id='generator-radio',
                        options=[
                            {'label': 'Active', 'value': True},
                            {'label': 'Inactive', 'value': False}
                        ],
                        value=True
                    )
                ]
            ),
            dbc.Col(
                children=[
                    html.Fieldset(
                        id='smoothness-fieldset',
                        children=[
                            html.Legend(children='Smoothness'),
                            dbc.Row(
                                children=[
                                    dbc.Col(
                                        width=3,
                                        children=dbc.Label('Size', html_for='smooth-slider')
                                    ),
                                    dbc.Col(
                                        children=[
                                            dcc.Slider(
                                                id='smooth-slider',
                                                min=MIN,
                                                max=MAX,
                                                step=1,
                                                value=3,
                                                marks=dict([(n, n) for n in range(MIN, MAX + 1)])
                                            )
                                        ]
                                    )
                                ]
                            ),
                            dbc.Row(
                                children=[
                                    dbc.Col(
                                        width=3,
                                        children=dbc.Label('Iterations', html_for='times-slider')
                                    ),
                                    dbc.Col(
                                        children=[
                                            dcc.Slider(
                                                id='times-slider',
                                                min=SMOOTH_MIN,
                                                max=SMOOTH_MAX,
                                                step=1,
                                                value=2,
                                                marks=dict([(n, n) for n in range(SMOOTH_MIN, SMOOTH_MAX + 1)])
                                            )
                                        ]
                                    )
                                ]
                            )
                        ]
                    )
                ]
            ),
            dbc.Col(
                children=[
                    dcc.DatePickerRange(
                        id='generator-datepicker',
                        clearable=True,
                        minimum_nights=0,
                        min_date_allowed=datetime.datetime.today()
                    )
                ]
            ),
            dbc.Col(
                children=[
                    dbc.Button('Generate consumptions', id='generator-btn', outline=True, color='primary')
                ]
            ),
            dbc.Col(
                children=[
                    html.A('Download', id='download-btn', hidden=True)
                ]
            )
        ]
    ),
    dcc.Graph(id='generator-graph')
]