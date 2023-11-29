from io import StringIO
from multiprocessing import Process, Manager
import dash
import pandas as pd
import math
from Anony.preserver import Preserver
from Measurement import Measurement
from dash import dcc,html,Dash,dash_table, callback
from dash.dependencies import Input,Output,State
import base64
import io
import plotly.express as px
import dash_mantine_components as dmc
import dash_daq as daq
from dash_iconify import DashIconify

app = Dash(__name__)
server = app.server

app.title='VisTool'

data_uploader_button = dmc.Button(
    "Upload your data file here( .csv)",
    leftIcon=DashIconify(icon='solar:upload-linear'),
)

data_uploader = dcc.Upload(
    children= data_uploader_button,
    multiple=False,  # 只允许上传一个文件
    accept='.csv' # 限制上传的文件类型为 .csv
)

notify_done = dmc.Notification(
        title="Done!",
        id="anony-done",
        action="hide",
        autoClose=False,
        color='orange',
        message="The anonymization process is done! Now you can check the solutions in the scatter plot.",
        icon=DashIconify(icon="ic:round-celebration"))

notify_run = dmc.Notification(
        title="In Processing...",
        id="anony-run",
        action="show",
        autoClose=False,
        color='green',
        loading=True,
        disallowClose=True,
        message="The anonymization may take some time, please be patient.")

run_button = dmc.Button("Run Anonymization",leftIcon=DashIconify(icon='icomoon-free:switch'))

data_store = dcc.Store(id='data_store', storage_type='memory')

confirm_modal = dmc.Modal(
    title='The Anonymized Data:',
    size="75%",
    zIndex=10000,
    children=[
        dmc.Stack(html.Div(id='anony_table'),align='center'),
        dmc.Text("Note that the column 'count' means the number of same records. It's not from the original data!", size="sm"),
        dmc.Space(h=20),
        dmc.Group(
            [
                dmc.Button('Download this Anonymized Data Set',id='modal_submit'),
                data_store,
                dcc.Download(id='download'),
                dmc.Button('let me think again',id='modal_close',color='red',variant='outline')
            ],
            position='right',
        )
    ],
)
SA_selector = dmc.Select(
    label='Sensitive Attribute',
    placeholder='Select one',
    id='SA_selector',
    searchable=True,
    clearable=True,
    nothingFound="No options found",
    icon=DashIconify(icon='bxs:lock'),
    style={"width": 200},
)

more_settings_button = dmc.Button("more settings",variant='subtle',leftIcon=DashIconify(icon="fluent:settings-32-regular"),)
more_settings = dmc.Drawer(
            children=[SA_selector],
            title="More Settings",
            id="more_settings",
            padding="md",
            size=450,
            zIndex=10000,
)

QIs_selector = dmc.MultiSelect(
    label='Select Attributes you want to publish',
    placeholder="Select all you like!",
    clearable=True,
    searchable=True,
    nothingFound="No options found",
    icon=DashIconify(icon='arcticons:efa-publish'),
    style={"width": 400},
)
footer= dmc.Footer(
    height=50,
    fixed=True,
    children=[dmc.Text("Master Project of Zheng Yao")],
    style={"backgroundColor": "#1688FF",'color':'white'},
)
app.layout = dmc.NotificationsProvider(dmc.Grid(children=[
    dmc.Col(dmc.Navbar(
        width={"base": 450},
        children=[
            dmc.Stack([
            dmc.Text("VisTool", color="blue",weight=700),
            dmc.Title("Welcome to the Data Anonymization Tool",order=1),
            dmc.Text("""
            Upload a data set which you want to anonymize. Select the atrributes you want to publish, then run the anonymization. 
            You will see different anonymization solutions in the scatter plot, each point of which is an solution. Click the point to check the 
            anonymized data!
            """,weight=200),
            data_uploader,
            QIs_selector,
            more_settings_button,
            more_settings,
            run_button,
            notify_run,
            notify_done,
            confirm_modal,
            html.Div(id='test',children=[])],
            align="flex-start",
            justify="flex-start",
            )
        ],
    ),
        span=4),
    dmc.Col(dmc.Stack([html.Div(id='table_title'),
                       html.Div(id='table'),
                       dmc.Group([dmc.Tooltip(children=[dcc.Graph(id='scatterplot')],
                                              multiline=True,
                                              width=420,
                                              withArrow=True,
                                              transition="pop-top-right",
                                              color='blue',
                                              position='top-start',
                                              offset=-90,
                                              transitionDuration=1000,
                                              label="""
                                              After anonymization, please click a point to see the anonymized data.
                                              Each point of the plot indicates an unique anonymization solution.
                                              You can also check the privacy and information loss of the selected point.
                                              """,
                                              ),
                                  dmc.Stack([daq.Gauge(id='Indicator_U',
                                                       color={"gradient":True,"ranges":{"green":[0,0.6],"yellow":[0.6,0.8],"red":[0.8,1]}},
                                                       size=140,
                                                       value=0,
                                                       max=1,
                                                       min=0,
                                                       label='Information Loss'),
                                             daq.Gauge(id='Indicator_P',
                                                       color={"gradient":True,"ranges":{"green":[0,0.6],"yellow":[0.6,0.8],"red":[0.8,1]}},
                                                       size=140,
                                                       value=0,
                                                       max=1,
                                                       min=0,
                                                       label='Privacy Loss')
                                             ]),
                                  ])
                       ]),
            span=8),

],
    justify="space-around",
    align="flex-start",
    gutter="xl",
    grow=True,
),
position='bottom-left',zIndex=10000,transitionDuration=500)

def table(df,id='spreadsheet'):
    return dash_table.DataTable(
        id=id,
        columns=[{'name': col, 'id': col} for col in df.columns],
        data=df.to_dict('records'),
        page_size=20,
        fixed_rows={'headers': True},
        style_table={'height': '300px', 'overflowY': 'auto', 'width': '900px', 'overflowX': 'auto'},
        style_cell={
            'height': 'auto',
            # all three widths are needed
            'minWidth': '80px', 'width': '100px', 'maxWidth': '100px',
            'whiteSpace': 'normal'
        },
        style_header={
            'backgroundColor': 'rgb(22, 136, 255)',
            'color': 'white',
            'fontWeight': 'bold'
        }
    )

@app.callback(
    Output("more_settings", "opened"),
    Input(more_settings_button, "n_clicks"),
    prevent_initial_call=True,
)
def drawer(n_clicks):
    return True

@app.callback(
    Output('anony_table','children'),
    Output('data_store','data'),
    Input('scatterplot','clickData'),
    State('SA_selector','value'),
    State(QIs_selector,'value'),
    State(data_uploader,'contents'),
    prevent_initial_call = True
)
def update_anony_sheet(click_data,SA,QIs,contents):
    if click_data is not None:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        df = df.drop(df.columns[0], axis=1)
        QIs.remove(SA)
        parameters = click_data['points'][0]['customdata'][:3]
        method = click_data['points'][0]['customdata'][3]
        anony_data = anonymization(data=df,QIs=QIs,SA=SA,method=method,parameters=parameters)
        json_data = anony_data.to_json(orient='split', date_format='iso')
        return table(anony_data),json_data
    else:
        return dash.no_update

@app.callback(Output('table', 'children'),
              Output('table_title','children'),
              Input(data_uploader, 'contents'),
              prevent_initial_call=True,
              )
def update_spreadsheet(contents):
    if contents is not None:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        # 检查上传的文件类型
        try:
            # 解析 .csv 文件
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            df = df.drop(df.columns[0], axis=1)
            return  table(df),dmc.Title('Uploaded Data',order=4)
        except Exception as e:
            return dmc.Alert(e, title="Error!", color="red"),dmc.Title('Uploaded Data',order=4)

def anonymization(data,QIs,SA,method,parameters):
    def check_dtype(df):
        for col in df.columns:
            if df[col].dtype.name == 'object':
                df[col] = df[col].astype('category')
    check_dtype(data)
    anony = Preserver(data,QIs,SA)
    if method=="k-anonymity":
        return pd.DataFrame(anony.k_anonymity(parameters[0]))
    elif method=="l-diversity":
        return pd.DataFrame(anony.l_diversity(k=parameters[0],l=parameters[1]))
    elif method=="t-closeness":
        return pd.DataFrame(anony.t_closeness(k=parameters[0],t=parameters[2]))

def PCC(p,num_sa,k_max=10):
    l_max = num_sa
    t_min = 1/l_max

    k = max(1,math.ceil(p*k_max))
    l = max(1,math.ceil(math.log2(k)))
    t = max(t_min,(l_max*t_min)/(1+l*p))

    return [k,l,t,p]

def Auto_PCC(data,QIs,SA,loop_num=11,k_max=10):
    num_SA = data[SA].nunique()
    parameters = []
    p = []
    P_loss = []
    U_loss = []
    method = []
    k = []
    l = []
    t = []

    for i in range(loop_num):
        p_value = i / (loop_num-1)
        parameters.append(PCC(p_value,num_SA,k_max))

    for i in range(loop_num):
        df_k = anonymization(data, QIs, SA, method='k-anonymity', parameters=parameters[i])
        df_l = anonymization(data, QIs, SA, method='l-diversity', parameters=parameters[i])
        df_t = anonymization(data, QIs, SA, method='t-closeness', parameters=parameters[i])

        measure_k = Measurement(data, df_k, QIs, SA)
        measure_l = Measurement(data, df_l, QIs, SA)
        measure_t = Measurement(data, df_t, QIs, SA)

        P_loss.append(max(measure_k.privacy_loss()))
        P_loss.append(max(measure_l.privacy_loss()))
        P_loss.append(max(measure_t.privacy_loss()))

        U_loss.append(measure_k.utility_loss())
        U_loss.append(measure_l.utility_loss())
        U_loss.append(measure_t.utility_loss())

        method.extend(['k-anonymity', 'l-diversity', 't-closeness'])
        k.extend([parameters[i][0], parameters[i][0], parameters[i][0]])
        l.extend([' ', parameters[i][1], ' '])
        t.extend(['', '', parameters[i][2]])
        p.extend([parameters[i][3], parameters[i][3], parameters[i][3]])

    info = pd.DataFrame(
        {
            'p': p,
            "P_loss": P_loss,
            "U_loss": U_loss,
            "method": method,
            'k': k,
            'l': l,
            't': t
        }
    )
    return info

@app.callback(
              Output(QIs_selector,'data'),
              Output(QIs_selector,'value'),
              Input(data_uploader,'contents'))
def update_QIs_selector(contents):
    if contents is not None:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        df = df.drop(df.columns[0], axis=1)
        return df.columns,df.columns
    return [],[]

@app.callback(
    Output('SA_selector','data'),
    Output('SA_selector','value'),
    Input(QIs_selector,'value'),
    prevent_initial_call=True,
)
def update_SA_selector(QIs):
    if QIs:
        return QIs,QIs[-1]
    else:
        return dash.no_update,dash.no_update


@app.callback(
    Output('scatterplot','figure'),
    Output(run_button,'loading'),
    Output(notify_done,'action'),
    Output(notify_run,'action'),
    Output(QIs_selector, 'disabled'),
    Output(more_settings_button, 'disabled'),
    Output(data_uploader, 'disabled'),
    Input(run_button,'n_clicks'),
    State('SA_selector','value'),
    State(QIs_selector,'value'),
    State(data_uploader,'contents'),
    prevent_initial_call=True,
)
def run_anonymization(n_clicks,SA,QIs,contents):
    if  contents is not None:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        df = df.drop(df.columns[0], axis=1)
        QIs.remove(SA)
        info = Auto_PCC(df,QIs,SA)
        fig = px.scatter(info, x="P_loss", y="U_loss",hover_data=['k','l','t','method','P_loss','U_loss'],range_x=[0,1],range_y=[0,1])
        fig.update_layout(
            title_text='Scatter Plot of different anonymization solutions',
            title_font=dict(size=18, family='Arial', color='black'),
            xaxis_title='Privacy Loss',
            yaxis_title='Information Loss',
            clickmode='event+select',
        )
        fig.update_traces(
            hovertemplate='This solution may cause:<br>Privacy Loss: %{x}<br>Information Loss: %{y}',
            marker=dict(color='rgb(22, 136, 255)')
        )
        return fig,False,'show','hide',False,False,False
    else:
        return { 'data': [], 'layout': {}, 'frames': [],},False,dash.no_update,dash.no_update,dash.no_update,dash.no_update,dash.no_update

@app.callback(
    Output('Indicator_U','value'),
    Output('Indicator_P','value'),
    Input('scatterplot','hoverData'),
    prevent_initial_call = True
)
def update_indicator(data):
    if data and 'points' in data:
        first_point = data['points'][0]
        x = first_point['x']
        y= first_point['y']
        return float(y),float(x)
    return dash.no_update,dash.no_update

@app.callback(
    Output(run_button,'disabled'),
    Input('SA_selector','value'),
    Input(QIs_selector,'value'),
    Input(data_uploader,'contents'),
)
def disable_run_btn(sa,QIs,contents):
    if sa is None or QIs is None or contents is None:
        return True
    else:
        return False

@app.callback(
    Output(run_button,'loading',allow_duplicate=True),
    Output(notify_run,'action',allow_duplicate=True),
    Output(notify_done,'action',allow_duplicate=True),
    Output(QIs_selector,'disabled',allow_duplicate=True),
    Output(more_settings_button,'disabled',allow_duplicate=True),
    Output(data_uploader,'disabled',allow_duplicate=True),
    Input(run_button,'n_clicks'),
    prevent_initial_call=True,
)
def loading_run_btn(n_clicks):

    if n_clicks is not None:
        return True,'show','hide',True,True,True

@app.callback(
    Output(confirm_modal,'opened'),
    Input('scatterplot','clickData'),
    Input('modal_close','n_clicks'),
    State(confirm_modal,'opened'),
    prevent_initial_call = True
)
def modal(click,close,opened):
    return not opened

@app.callback(
    Output('download','data'),
    Input('modal_submit','n_clicks'),
    State('data_store','data'),
    prevent_initial_call = True
)
def download(n_clicks,data):
    df_from_json = pd.read_json(StringIO(data), orient='split')
    return dcc.send_data_frame(df_from_json.to_csv, "anony_data.csv")

if __name__ == '__main__':
    app.run(debug=True)