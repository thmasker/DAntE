import base64
import io

import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html

from flask_login import current_user

from app.processing import read_data, dropNan, add_weekday
import app.models.dbbroker as DBBroker


uploads_layout = html.Div(
    id='uploads-layout',
    children=[
        dbc.Jumbotron(
            children=[
                html.P(
                    className='lead',
                    children=[
                        'File\'s content must include: ',
                        html.Code(
                            className='text-primary',
                            children='day'
                        ),
                        ', ',
                        html.Code(
                            className='text-primary',
                            children='building_id'
                        ),
                        ' and ',
                        html.Code(
                            className='text-primary',
                            children='consumptions'
                        )
                    ]
                ),
                dcc.Upload(
                    id='upload-data',
                    max_size=100 * 1024 * 1024,
                    children=[html.Div(children=['Drag and Drop or ', html.A('Select CSV')])]
                ),
                html.Div(id='output-data-upload', children=html.H5(id='upload-info'))
            ]
        )
    ]
)

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def parse_contents(contents, filename, db, allowed_extensions):
    project = filename.rsplit('.', 1)[0]

    if not current_user.is_authenticated:
        return 'You must be logged in to upload files'
    elif list(DBBroker.find(db, {'project': project})):
        return 'Project with name ' + project + ' already exists'
    elif allowed_file(filename, allowed_extensions):
        try:
            _, content_string = contents.split(',')
        except ValueError:
            return 'File does not contain valid information'

        decoded = base64.b64decode(content_string)
        try:
            df = read_data(io.StringIO(decoded.decode('utf-8')))
            df = add_weekday(df)
            df = dropNan(df)
        except (KeyError, ValueError):
            return 'File does not contain valid information'

        DBBroker.insertRawData(db, current_user.get_id(), project, df)
        return 'File successfully uploaded'
    else:
        return 'Only CSV files are allowed'