import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html


MIN, MAX = 1, 5

activity_content = [
    dcc.Interval(id='activity-interval', max_intervals=0, n_intervals=1),
    dbc.Row(
        id='activity-creator',
        children=[
            dbc.Col(
                children=[
                    dcc.Dropdown(
                        id='activity-project-dropdown',
                        placeholder='Select Project',
                        persistence=True,
                        persistence_type='memory'
                    )
                ]
            ),
            dbc.Col(
                children=[
                    dbc.Label('Consumer types', html_for='n-consumers-slider'),
                    dcc.Slider(
                        id='n-consumers-slider',
                        min=MIN,
                        max=MAX,
                        step=1,
                        value=3,
                        marks=dict([(n, n) for n in range(MIN, MAX + 1)])
                    )
                ]
            ),
            dbc.Col(
                children=[
                    dbc.Button('Calculate activity', id='calc-activity-btn', outline=True, color='primary'),
                    dbc.Label(id='activity-info')
                ]
            )
        ]
    ),
    dcc.Graph(id='activity-graph')
]