import dash_bootstrap_components as dbc
import dash_core_components as dcc


prototypes_content = [
    dbc.Row(
        id='prototypes-selectors',
        children=[
            dbc.Col(
                children=[
                    dcc.Dropdown(
                        id='prototypes-weekday-dropdown',
                        placeholder='Select weekday(s)',
                        multi=True,
                        options=[
                            {'label': 'Monday', 'value': 0},
                            {'label': 'Tuesday', 'value': 1},
                            {'label': 'Wednesday', 'value': 2},
                            {'label': 'Thursday', 'value': 3},
                            {'label': 'Friday', 'value': 4},
                            {'label': 'Saturday', 'value': 5},
                            {'label': 'Sunday', 'value': 6}
                        ]
                    )
                ]
            ),
            dbc.Col(
                children=[
                    dcc.Dropdown(
                        id='prototypes-types-dropdown',
                        placeholder='Select consumer type(s)',
                        multi=True
                    )
                ]
            ),
            dbc.Col(
                children=[
                    dcc.RadioItems(
                        id='prototypes-radio',
                        options=[
                            {'label': 'Active', 'value': True},
                            {'label': 'Inactive', 'value': False},
                            {'label': 'Both', 'value': 'both'}
                        ],
                        value='both'
                    )
                ]
            )
        ]
    ),
    dcc.Graph(id='prototypes-graph')
]