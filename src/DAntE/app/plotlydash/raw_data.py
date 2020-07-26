import dash_bootstrap_components as dbc
import dash_core_components as dcc


raw_content = [
    dcc.Interval(id='raw-interval', max_intervals=0, n_intervals=1),
    dbc.Row(
        id='raw-data-selectors',
        children=[
            dbc.Col(
                children=[
                    dcc.Dropdown(
                        id='project-dropdown',
                        placeholder='Select Project',
                        persistence=True,
                        persistence_type='memory'
                    )
                ]
            ),
            dbc.Col(
                children=[
                    dcc.Dropdown(
                        id='building-dropdown',
                        placeholder='Select building(s)',
                        persistence=True,
                        persistence_type='memory',
                        multi=True
                    )
                ]
            ),
            dbc.Col(
                children=[
                    dcc.DatePickerRange(
                        id='raw-datepicker',
                        clearable=True,
                        minimum_nights=0
                    )
                ]
            )
        ]
    ),
    dcc.Graph(id='raw-data-graph')
]