import pandas as pd

from plotly.subplots import make_subplots
import plotly.graph_objects as go


TYPES = {0: 'Low', 1: 'Medium', 2: 'High'}


def createIndex(start, end):
    '''
    Creates a date range between start and end, both included

    args:
        start -> datetime
        end -> datetime
    
    returns pd.DateTimeIndex
    '''

    return pd.date_range(start=start, end=end, freq='1H')


def getConsumptionsPerHour(df, start, end):
    '''
    Creates an array with hourly consumptions from start to end

    args:
        df -> pd.DataFrame
        start -> datetime
        end -> datetime

    returns List[float]
    '''

    days = pd.date_range(start=start, end=end, freq='D')

    consumptions = []
    for day in days:
        if day in df.index:
            cons = df['consumptions'].loc[day]
        else:
            cons = [0 for _ in range(24)]

        for h in cons:
            consumptions.append(h)

    return consumptions


def createFigureFromDataFrame(df, start, end):
    '''
    Creates the Figure with consumptions corresponding to df between start and end dates

    args:
        df -> pd.DataFrame
        start -> datetime
        end -> datetime

    returns go.Figure
    '''
    x = createIndex(start, end)
    fig = go.Figure()

    for building in df['building_id'].unique():
        fig.add_trace(go.Scatter(x=x, y=getConsumptionsPerHour(df[df['building_id'] == building], start, end), name='Building ' + str(building)))

    fig.update_layout(
        xaxis_title='date',
        yaxis_title='consumtpion'
    )

    return fig


def createFigureFromTypes(df):
    '''
    Creates Figure for showing consumer types result

    args:
        df -> pd.DataFrame

    returns go.Figure
    '''

    fig = make_subplots(rows=1, cols=2, shared_yaxes=True)

    for a in df['active'].unique():
        df_selected = df[df['active'] == a]

        activity = 'Active' if a else 'Inactive'

        df_ordered = df_selected.sort_values(by=['mean_cons'], ignore_index=True)

        for t in df_ordered['type'].unique(): 
            x = df_ordered['building_id'][df_ordered['type'] == t].tolist()
            y = df_ordered['mean_cons'][df_ordered['type'] == t].tolist()

            fig.add_trace(
                go.Bar(x=x, y=y, text=y, textposition='outside', name=activity + ' ' + TYPES[t]),
                1, 1 if a else 2
            )

    fig.update_layout(
        xaxis_type='category',
        xaxis2_type='category',
        xaxis_title='buildings',
        yaxis_title='mean consumption',
        xaxis2_title='buildings',
        title={
            'text': 'consumer types',
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )

    return fig


def createFigureFromPrototypes(df):
    '''
    Creates the Figure for prototypes

    args:
        df -> pd.DataFrame

    returns go.Figure
    '''

    weekdays = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}

    x = pd.date_range(start='5:00', periods=24, freq='H').time
    fig = go.Figure()

    for i in df.index:
        current = df.loc[i]

        consumer_type = current['type']
        weekday = weekdays[current['weekday']]
        active = 'Active' if current['active'] else 'Inactive'
        
        fig.add_trace(go.Scatter(x=x, y=current['consumptions'], name=active + ' ' + weekday + '; consumer: ' + str(consumer_type)))

    fig.update_layout(
        xaxis_title='date',
        yaxis_title='consumtpion'
    )

    return fig


def createResultGraph(df, protos):
    '''
    Creates graph for the generated consumptions, comparing them with the prototype used to generate them

    args:
        df -> pd.DataFrame
        protos -> pd.DataFrame

    returns go.Figure()
    '''

    data = []
    d = 0
    x = df.index

    while d < df.shape[0]:
        consumptions = protos['consumptions'][protos['weekday'] == x[d].weekday()].tolist()

        for conss in consumptions:
            for c in conss:
                data.append(c)
        
        d += 24

    cons_proto = pd.Series(data, index=x)

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=x, y=cons_proto, name='Prototype'))
    fig.add_trace(go.Scatter(x=x, y=df, name='Result'))

    fig.update_layout(
        xaxis_title='date',
        yaxis_title='consumtpion'
    )

    return fig