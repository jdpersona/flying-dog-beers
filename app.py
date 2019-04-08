#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr  7 22:32:55 2019

@author: john.ekedum@ibm.com
"""
import dash
import io
import dash_auth
import dash_core_components as dcc
import dash_html_components as html
import plotly
from dash.dependencies import Input, Output, State
import pybase64
import pandas as pd
import knackpy
from knackpy import Knack




# Keep this out of source code repository - save in a file or a database
VALID_USERNAME_PASSWORD_PAIRS = [
    ['hello', 'world']
]


cols = {
 "First":"first",
"Last":"last",
"Company is sponsor user":"field_300",
"SU":"field_432",
"Company name":"field_326",
"Address":"street",
"Zip":"zip",
"City":"city",
"State":"state",
"Country":"country",
"Time zone":"field_640",
"Recruiting source":"field_605",
"Phone":"field_302",
"Email":"field_303",
"LinkedIn profile":"field_304",
"Total compensation this year":"field_325",
"Personas":"field_306",
"Date added":"field_594",
"Last updated":"field_595",
"Updated by":"field_804",
"Wants to participate in future activities?":"field_596",
"Age range":"field_597",
"Years in current role":"field_601",
"Years in current industry":"field_602",
"Job duties":"field_603",
"Time Zone Selector":"field_606",
"Tome Zone Hours":"field_607",
"Current Time Equation":"field_608",
"Business Model":"field_794",
"Company size":"field_795",
"Company Revenue":"field_796",
"Team size":"field_797",
"Industry":"field_800",
"Job title":"field_801",
"Role/Responsibilities":"field_802",
"WCE Products used":"field_803",
"UserTesting ID":"field_805",
"id":"id"
}



external_stylesheets =  ["https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css"]
#, external_stylesheets = external_stylesheets


app = dash.Dash(__name__,external_stylesheets = external_stylesheets)
server = app.server

auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)


#### main app
app.config.suppress_callback_exceptions = True

app.layout = html.Div([
    html.H3('Knack Data Migrate', style = {"font-family":"IBM Plex Serif","font-style":"italic"}),
    dcc.Location(id='url', refresh=False),

    html.Div(id='page-content'),
    #html.Img(src=app.get_asset_url('my-image.png'))
    # html.Img(src='/Users/john.ekedum@ibm.com/Documents/Dash_application/assets/my-image.png')

], style={'backgroundColor':'white'})



index_page = html.Div(style={'text-align':'center','margin-top':'50px',
    'opacity':'0.8',
    'backgroundColor':'#e3c9c9',
    'position':'fixed',
    'width':'100%',
    'height':'100%',
    'top':'0px',
    'left':'0px',
    'z-index':'1000'},children=[


html.Div( children=[

html.Div( children=[
   html.H1("Easily bulk upload your participant data into Knack database", style = { "color":"black",  "font-family":"IBM Plex Sans", "font-weight":"100", "margin-top":"350px", "text-align":"center", 'margin-left':'30px' }),
   dcc.Link(
       html.Button('Continue', id='button', style = {'margin-top':'40px','align':'left','margin-left':'30px',"font-family":"IBM Plex Sans"}, className = "btn btn-danger btn-lg"),\
    href='/upload-data')

], className="col"),



html.Div(children=[
html.Img(src=app.get_asset_url('device.png'), style = {'margin-right':'150px', 'margin-top':'200px'}),
],className="col")


],className="row")#end of row div


])#end of container




#id='waitfor'

page_1_layout = html.Div([

    html.Div([
    html.Div(),
    dcc.Upload(
        id='upload',

        children=html.Div([
            'Drag and Drop or ',
            html.A('Upload Participant File')
        ]),

        style={
            'width': '70%',
            'height': '100px',
            'lineHeight': '100px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'textAlign': 'center',
            'margin': '200px',
            "font-family":"IBM Plex Sans",
            'backgroundColor':'#e3c9c9',
            "color":"purple"

        }
    ),
    html.Div(id='output'),
    #html.Div(dt.DataTable(rows=[{}]), style={'display': 'none'})
])

])

pre_style = {
    'whiteSpace': 'pre-wrap',
    'wordBreak': 'break-all',
    'whiteSpace': 'normal'
}


# Update the index
@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/upload-data':
        return page_1_layout
    else:
        return index_page



@app.callback(Output('output', 'children'),
              [Input('upload', 'contents')])
def update_output(contents):
    kn = Knack(
          obj='object_17',
          app_id='59ca76c0e4c83424df3eee62',
          api_key='a0998110-a889-11e7-9b23-7d5afe966012 '
        )# added
    if contents is not None:
        content_type, content_string = contents.split(',')
        if 'csv' in content_type:
            knack_csv = pd.read_csv(io.StringIO(pybase64.b64decode(content_string).decode('utf-8')))
            knack_db = pd.DataFrame(kn.data)
            knack_db.drop('Email',  axis=1, inplace=True)
            knack_db['LinkedIn profile'] = knack_db['LinkedIn profile_url']
            #rename knack data to fit the new data
            knack_db.rename(columns={'Participant Name_first': 'First','Participant Name_last':'Last' ,
                 'Address_city':'City', 'Email_email':'Email', 'Address_street':'street', 'Address_country':'Country', 'Address_state':'State','Address_zip' : 'Zip'}, inplace=True)
            knack_db.id=''
            knack_db.drop(
              ['Address_latitude','Address_longitude', 'Address',
                     'Participant Name_middle','Participant Name_title',], axis=1, inplace=True)

            knack_db = knack_db[knack_csv.columns.tolist()]
            knack_db['Current Time Equation'] = ''
            knack_db['Date added']= ''
            knack_db['Last updated'] = ''
            knack_db.Phone  = knack_db.Phone.apply(pd.Series).iloc[::,3:4]

            for col in knack_csv.columns.tolist():
                knack_csv[col]= knack_csv[col].astype('object')
            list_of_columns = ['First', 'Last', 'Company is sponsor user', 'SU', 'Company name', 'street','Zip','City', 'State', 'Country',
                          'Time zone',
                         'Recruiting source', 'Phone', 'Email', 'LinkedIn profile',
                           'Total compensation this year', 'Personas', 'Date added',
                           'Last updated', 'Updated by','Wants to participate in future activities?', 'Age range',
                           'Years in current role', 'Years in current industry', 'Job duties',
                           'Time Zone Selector', 'Tome Zone Hours', 'Current Time Equation','Business Model', 'Company size', 'Company Revenue', 'Team size',
                           'Industry', 'Job title', 'Role/Responsibilities', 'WCE Products used',
                           'UserTesting ID', 'id']
            knack_csv = knack_csv[list_of_columns]
            knack_csv = knack_csv.apply(lambda x: x.astype('str'))
            knack_csv = knack_csv.replace('nan','', regex=True)
            knack_csv['Company size'] = knack_csv['Company size'].str.split('.', expand=True)[0]

            knack_db = knack_db[list_of_columns]
            knack_db = knack_db.apply(lambda x: x.astype('str'))
            knack_db = knack_db.replace('nan','', regex=True)

            knack_csv = knack_csv.apply(lambda x: x.str.title())
            knack_db = knack_db.apply(lambda x: x.str.title())

            knack_csv = knack_csv.astype(knack_db.dtypes.to_dict())
            df_knack = knack_csv.merge(knack_db, how='left', indicator=True)
            received = df_knack.shape[0]
            df_knack = df_knack[df_knack['_merge']=='left_only']
            df_knack.drop('_merge', axis=1, inplace=True)


            df_knack.columns = cols.values()
            # Ectract other non objects values in their dataframe
            df_knack_sub1 = df_knack.iloc[::, 2:5]
            df_knack_sub2 = df_knack.iloc[::, 10:38]
            df_knack_sub = pd.concat([df_knack_sub1,df_knack_sub2], axis=1)

            # convert data into dict
            df_knack_sub_dict = df_knack_sub.to_dict(orient='records')

            dict_with_values = []
            for dict_data in df_knack_sub_dict :
                dic = {i:j for i,j in dict_data.items() if j != 'N/A'}
                dict_with_values.append(dic)

            # lets get the name objects
            bio_object = df_knack.iloc[::,0:2]
            bio_object_dict = bio_object.to_dict(orient='records')

            #lets get address objects
            address_object = df_knack.iloc[::,5:10]
            address_object.columns = address_object.columns.str.lower()
            address_object_dict = address_object.to_dict(orient='records')

            bio_val = []
            for i, dicti in enumerate(dict_with_values):
                dicti['field_298']= bio_object_dict[i]
                bio_val.append(dicti)

            bio_val_addr = []
            for i, dicti in enumerate(bio_val ):
                dicti["field_301"]= address_object_dict[i]
                bio_val_addr.append(dicti)

            all_data = []
            for record in bio_val_addr:
                response = knackpy.record(
                        record,
                        obj_key='object_17',
                        app_id='59ca76c0e4c83424df3eee62',
                        api_key = 'a0998110-a889-11e7-9b23-7d5afe966012',
                        method='create')
                all_data.append(record)
            return html.Div(children=[
                    '{} records received, {} unique record succesfully loaded into Knack'.format(received, len(all_data))
            ],style = {'text-align':'center','width':'600px', 'margin-left':'520px', 'margin-bottom':'300px','backgroundColor':'#e3c9c9'}, className = "alert alert-success alert-dismissible fade show")

        elif 'xlsx' in content_type:

            return html.Div([
                html.h5("Knack migrate does not allow excel files files, save your file as csv")
            ])
        else:
            return html.Div([
                html.h5(html.P("Wrong file upload"))
            ])

app.scripts.config.serve_locally = True


if __name__ == '__main__':
    app.run_server()
