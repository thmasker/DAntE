import os, datetime

import pandas as pd

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import plotly.graph_objects as go

from flask import current_app
from flask_login import current_user

from app.plotlydash.uploads import uploads_layout, parse_contents
from app.plotlydash.raw_data import raw_content
from app.plotlydash.activity import activity_content
from app.plotlydash.prototypes import prototypes_content
from app.plotlydash.generator import generator_layout
from app.visualization import createFigureFromDataFrame, createFigureFromTypes, createFigureFromPrototypes, createResultGraph
from app.processing import get_consumer_types, cleanDataFrame, setConsumerType, getPrototypes, generateConsumptions, applySmooth
import app.models.dbbroker as DBBroker


ALLOWED_EXTENSIONS = {'csv'}
RAWDATA_DB = 'RawData'
MEANPROTOS_DB = 'MeanPrototypes'
STDPROTOS_DB = 'StdPrototypes'


data_layout = html.Div(
    id='data-container',
    children=[
        dbc.Row(
            children=[
                dbc.Col(
                    width=2,
                    children=[
                        dbc.Nav(
                            vertical=True,
                            pills=True,
                            children=[
                                dbc.NavItem(dbc.NavLink('Raw Data', id='raw-data-nav')),
                                dbc.NavItem(dbc.NavLink('Activity', id='activity-nav')),
                                dbc.NavItem(dbc.NavLink('Prototypes', id='prototypes-nav'))
                            ]
                        )
                    ]
                ),
                dbc.Col(id='show-panel', width=10)
            ]
        )
    ]
)


def create_dashboard(server):
    app = dash.Dash(
        __name__,
        server=server,
        routes_pathname_prefix='/dashboard/',
        external_stylesheets=[dbc.themes.SANDSTONE],
        external_scripts=[
            {
                'src': 'https://code.jquery.com/jquery-3.5.1.slim.min.js',
                'integrity': 'sha256-4+XzXVhsDmqanXGHaHvgh1gMQKX40OUvDEBTu8JcmNs=',
                'crossorigin': 'anonymus'
            }
        ]
    )

    app.config['suppress_callback_exceptions'] = True

    app.title = 'DAntE'

    app.layout = html.Div(
        id='big-app-container',
        children=[
            dbc.NavbarSimple(
                id='banner',
                className='banner',
                color='#ff9c1b',
                brand='DAntE',
                brand_href='/',
                brand_external_link=True,
                children=[
                    dbc.NavItem(html.Span(id='session-info')),
                    dbc.NavItem(dbc.NavLink(id='session-btn', external_link=True)),
                    dbc.NavItem(dbc.NavLink('Sign Up', id='signup-btn', href='/auth/signup', external_link=True))
                ]
            ),
            dbc.Card(
                children=[
                    dbc.CardHeader(
                        id='tabs-header',
                        children=[
                            dcc.Tabs(
                                id='tabs',
                                children=[
                                    dcc.Tab(
                                        id='uploads-tab',
                                        label='UPLOAD FILES',
                                        selected_style={'border-bottom': 'none', 'border-top': '2px solid #ff9c1b'},
                                        children=uploads_layout
                                    ),
                                    dcc.Tab(
                                        id='data-tab',
                                        label='DATA ANALYSIS',
                                        selected_style={'border-bottom': 'none', 'border-top': '2px solid #ff9c1b'},
                                        children=data_layout
                                    ),
                                    dcc.Tab(
                                        id='generator-tab',
                                        label='GENERATOR',
                                        selected_style={'border-bottom': 'none', 'border-top': '2px solid #ff9c1b'},
                                        children=generator_layout
                                    )
                                ]
                            )
                        ]
                    )
                ]
            ),
            html.Div(id='cleandf-value', style={'display': 'none'}),
            html.Div(id='types-value', style={'display': 'none'}),
            html.Div(id='df-value', style={'display': 'none'}),
            html.Div(id='protos-value', style={'display': 'none'})
        ]
    )

    init_callbacks(app)

    return app.server


### HELPER FUNCTIONS

def createProjectOptions():
    return [{'label': project, 'value': project} for project in DBBroker.distinct(RAWDATA_DB, 'project', {'owner_id': current_user.get_id()})]

def createBuildingsOptions(project):
    return [{'label': building_id, 'value': building_id} for building_id in DBBroker.distinct(RAWDATA_DB, 'building_id', {'project': project, 'owner_id': current_user.get_id()})]

def createConsumerTypeOptions():
    return [{'label': 'Low', 'value': 0}, {'label': 'Medium', 'value': 1}, {'label': 'High', 'value': 2}]

def getTriggeredID(context):
    return context.triggered[0]['prop_id'].split('.')[0]


def init_callbacks(dash_app):

    ##########################
    # INFORMATION
    ##########################

    @dash_app.callback(
        [Output('session-btn', 'children'),
        Output('session-btn', 'href'),
        Output('session-info', 'children'),
        Output('signup-btn', 'hidden')],
        [Input('session-btn', 'id')]
    )
    def sessionButtonChange(id):
        if current_user.is_authenticated:
            return 'Logout', '/auth/logout', 'Logged in as ' + current_user.get_id(), True
        else:
            return 'Login', '/auth/login', None, False

    @dash_app.callback(
        Output('upload-info', 'children'),
        [Input('upload-data', 'contents')],
        [State('upload-data', 'filename')]
    )
    def upload(contents, filename):
        if contents is not None:
            return parse_contents(contents, filename, RAWDATA_DB, ALLOWED_EXTENSIONS)

    @dash_app.callback(
        Output('activity-info', 'children'),
        [Input('calc-activity-btn', 'n_clicks'), Input('protos-value', 'children')]
    )
    def activityInfo(n_clicks, children):
        ctx = dash.callback_context

        if ctx.triggered:
            btn_id = getTriggeredID(ctx)
        
            if btn_id == 'calc-activity-btn':
                return 'This may take some time...'

        return None

    
    #######################
    # DROPDOWNS
    #######################

    @dash_app.callback(Output('building-dropdown', 'options'), [Input('project-dropdown', 'value')])
    def getBuildingIDs(project):
        return createBuildingsOptions(project)

    @dash_app.callback(Output('project-dropdown', 'options'), [Input('raw-interval', 'n_intervals')])
    def getProjects(n_intervals):
        return createProjectOptions()

    @dash_app.callback(Output('activity-project-dropdown', 'options'), [Input('activity-interval', 'n_intervals')])
    def getProjects(n_intervals):
        return createProjectOptions()

    @dash_app.callback(
        Output('prototypes-types-dropdown', 'options'),
        [Input('protos-value', 'children'), Input('prototypes-weekday-dropdown', 'value')]
    )
    def getPrototypesTypesDropdown(json_mean, value):
        if json_mean:
            # mean_proto = DBBroker.findPrototypes(MEANPROTOS_DB, current_user.get_id())
            # return [{'label': t, 'value': t} for t in mean_proto['type'].unique()]
            return createConsumerTypeOptions()
        else:
            return None

    @dash_app.callback(Output('generator-type-dropdown', 'options'), [Input('generator-interval', 'n_intervals')])
    def consumerTypeGenerator(n_intervals):
        return createConsumerTypeOptions()


    #############################
    # GRAPHICS
    #############################

    @dash_app.callback(
        Output('raw-data-graph', 'figure'),
        [Input('raw-datepicker', 'start_date'),
        Input('raw-datepicker', 'end_date'),
        Input('project-dropdown', 'value'),
        Input('building-dropdown', 'value')]
    )
    def plotRawData(start, end, project, buildings):
        if start and end and project and buildings:
            df = DBBroker.findRawData(RAWDATA_DB, project, current_user.get_id())
            df = df[(df['building_id'].isin(buildings)) & (df.index >= start) & (df.index <= end)]

            return createFigureFromDataFrame(df, start, end)
        else:
            return go.Figure()

    @dash_app.callback(
        Output('activity-graph', 'figure'),
        [Input('types-value', 'children')]
    )
    def plotActivity(json_types):
        if json_types:
            types = pd.read_json(json_types, orient='split')
            return createFigureFromTypes(types)
        else:
            return go.Figure()

    @dash_app.callback(
        Output('prototypes-graph', 'figure'),
        [Input('prototypes-weekday-dropdown', 'value'),
        Input('prototypes-types-dropdown', 'value'),
        Input('prototypes-radio', 'value'),
        Input('protos-value', 'children')]
    )
    def plotPrototypes(weekdays, types, active, json_mean):
        if weekdays and types and json_mean:
            mean_protos = DBBroker.findPrototypes(MEANPROTOS_DB, current_user.get_id())

            protos = mean_protos[mean_protos['type'].isin(types) & mean_protos['weekday'].isin(weekdays)]
            if active == False:
                protos = protos[protos['active'] == False]
            elif active == True:
                protos = protos[protos['active']]

            return createFigureFromPrototypes(protos)
        else:
            return go.Figure()

    @dash_app.callback(
        [Output('generator-graph', 'figure'), Output('download-btn', 'hidden'), Output('download-btn', 'href')],
        [Input('generator-btn', 'n_clicks'),
        Input('generator-type-dropdown', 'value'),
        Input('generator-radio', 'value'),
        Input('generator-datepicker', 'start_date'),
        Input('generator-datepicker', 'end_date'),
        Input('smooth-slider', 'value'),
        Input('times-slider', 'value')]
    )
    def plotGenerator(n_clicks, consumer_type, active, start, end, window_size, times):
        if (consumer_type is not None) and start and end:
            ctx = dash.callback_context

            if ctx.triggered:
                btn_id = getTriggeredID(ctx)

            if btn_id == 'generator-btn':
                mean_protos = DBBroker.findPrototypes(MEANPROTOS_DB, current_user.get_id())
                std_protos = DBBroker.findPrototypes(STDPROTOS_DB, current_user.get_id())

                start = datetime.datetime.strptime(start, '%Y-%m-%d').replace(hour=5, minute=0)
                end = datetime.datetime.strptime(end, '%Y-%m-%d').replace(hour=4, minute=0)

                df = generateConsumptions(start, end, consumer_type, active, mean_protos, std_protos)
                df = applySmooth(df, window_size, times)

                df.to_csv(os.path.join(current_app.root_path, current_app.config['DATA_DIR'], current_user.get_id() + '-generated.csv'))

                protos = mean_protos[(mean_protos['active'] == active) & (mean_protos['type'] == consumer_type)]
                
                return createResultGraph(df, protos), False, '/download/' + current_user.get_id() + '-generated.csv'
        
        return go.Figure(), True, None

    
    #######################################
    #  SHARED DATA
    #######################################

    @dash_app.callback(
        [Output('cleandf-value', 'children'), Output('types-value', 'children')],
        [Input('n-consumers-slider', 'value'), Input('activity-project-dropdown', 'value'), Input('calc-activity-btn', 'n_clicks')]
    )
    def calculateActivity(n_consumers, project, activity_btn):
        n_consumers = 3 # Only for simulation

        ctx = dash.callback_context

        if ctx.triggered:
            btn_id = getTriggeredID(ctx)
        
        if n_consumers and project and btn_id == 'calc-activity-btn':
            df = DBBroker.findRawData(RAWDATA_DB, project, current_user.get_id())
            clean_df = cleanDataFrame(df)
            types = get_consumer_types(clean_df, n_consumers)

            return clean_df.to_json(date_format='iso', orient='split'), types.to_json(date_format='iso', orient='split')
        else:
            return None, None

    @dash_app.callback(
        Output('df-value', 'children'),
        [Input('cleandf-value', 'children'), Input('types-value', 'children')]
    )
    def obtainCleanDataFrame(json_clean_df, json_types):
        if json_clean_df and json_types:
            clean_df = pd.read_json(json_clean_df, orient='split')
            types = pd.read_json(json_types, orient='split')
            return setConsumerType(clean_df, types).to_json(date_format='iso', orient='split')
        else:
            return None

    @dash_app.callback(Output('protos-value', 'children'), [Input('df-value', 'children')])
    def obtainPrototypes(json_df):
        if json_df:
            df = pd.read_json(json_df, orient='split')
            mean_proto, std_proto = getPrototypes(df)

            DBBroker.replace(MEANPROTOS_DB, {'owner_id': current_user.get_id()}, {'owner_id': current_user.get_id(), 'data': mean_proto.to_dict('records')})
            DBBroker.replace(STDPROTOS_DB, {'owner_id': current_user.get_id()}, {'owner_id': current_user.get_id(), 'data': std_proto.to_dict('records')})

            return 'Ready'
        else:
            return None


    ###########################
    # NAVIGATION
    ###########################

    @dash_app.callback(
        [Output('raw-data-nav', 'active'), Output('activity-nav', 'active'), Output('prototypes-nav', 'active')],
        [Input('raw-data-nav', 'n_clicks'), Input('activity-nav', 'n_clicks'), Input('prototypes-nav', 'n_clicks')]
    )
    def changeActiveNav(raw, activity, prototypes):
        if raw or activity or prototypes:
            ctx = dash.callback_context
            
            if ctx.triggered:
                button_id = getTriggeredID(ctx)
            else:
                return True, False, False

            if button_id == 'activity-nav':
                return False, True, False
            elif button_id == 'prototypes-nav':
                return False, False, True
            else:
                return True, False, False
        else:
            return True, False, False

    @dash_app.callback(
        Output('show-panel', 'children'),
        [Input('raw-data-nav', 'active'), Input('activity-nav', 'active'), Input('prototypes-nav', 'active')]
    )
    def changeShowPanel(raw, activity, prototypes):
        if raw:
            return raw_content
        elif activity:
            return activity_content
        elif prototypes:
            return prototypes_content