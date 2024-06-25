from models import *
import pandas as pd
from google.cloud import bigquery as bq
# import bigquery_storage as bq_storage
import plotly.express as px
import plotly.graph_objects as go

# BigQuerry parameters
project_id = 'sublime-lyceum-426907-r9'
dataset_id = 'ama'

# # Plotly graph design
plot_bgcolor = 'white'
xy_font_family = "Roboto"
xy_font_color = "black"
xy_line_color = 'black'
tick_font_family = "monospace"
tick_font_size = 12
tick_font_color = 'black'
line1_color = 'royalblue'
line1_width = 3
line2_color = 'purple'
line2_width = line1_width
boundary_color = 'black'


def querry_bq(project, dataset, table):
    client = bq.Client()
    query = f"""
        SELECT * FROM `{project}.{dataset}.{table}`
        LIMIT 1200
        """
    df = client.query(query).to_dataframe()
    return df

DF_HISTORICAL = querry_bq(project_id, dataset_id, 'merged')
DF_PREDICTED = querry_bq(project_id, dataset_id, 'aggregated_data_with_necessity')

# Atendimentos Per Month
def df_atendimentos_per_month_historical(df_historical, location):
    df_historical['Type'] = 'Historical'
    df_historical['Data'] = pd.to_datetime(df_historical['Data'])
    df_historical = df_historical[df_historical['Designacao'] == location]
    df_historical['Meses'] = df_historical['Data'].dt.to_period('M')
    df_historical = df_historical.groupby('Meses').agg({'Atendimentos': 'sum'}).reset_index()
    # Convert Meses back to a datetime object for Plotly
    df_historical['Meses'] = df_historical['Meses'].dt.to_timestamp()
    return df_historical


def df_atendimentos_per_month_predicted(df_predicted, location):
    df_predicted['Type'] = 'Predicted'
    df_predicted['Meses'] = pd.to_datetime(df_predicted['Meses'])
    df_predicted = df_predicted[df_predicted['Designacao'] == location]
    df_predicted['Meses'] = df_predicted['Meses'].dt.to_period('M')
    df_predicted = df_predicted.groupby('Meses').agg({'Atendimentos': 'sum'}).reset_index()
    df_predicted['Meses'] = df_predicted['Meses'].dt.to_timestamp()
    return df_predicted


def plot_atendimentos_per_month(location, df_historical = None, df_predicted = None):
    fig = go.Figure()

    if df_historical is not None:
        df_historical = df_atendimentos_per_month_historical(df_historical, location)

        fig.add_trace(go.Scatter(
            x=df_historical['Meses'], 
            y=df_historical['Atendimentos'], 
            mode='lines', 
            name='Dados Históricos',
            line=dict(color=line1_color, width=line1_width)
        ))
    if df_predicted is not None:
        df_predicted = df_atendimentos_per_month_predicted(df_predicted, location)

        fig.add_trace(go.Scatter(
            x=df_predicted['Meses'], 
            y=df_predicted['Atendimentos'], 
            mode='lines', 
            name='Previsões',
            line=dict(color=line2_color, width=line2_width)
        ))
    if df_historical is not None and df_predicted is not None:
        boundary = df_predicted['Meses'].min()
        fig.update_traces(
            selector=dict(name='Previsões'),
            line=dict(dash='dot')
        )
        fig.add_vline(x=boundary, line_width=line1_width, line_dash="dash", line_color=boundary_color)

    # # Print BigQuery data on terminal
    # pd.set_option('display.max_rows', None)
    # pd.set_option('display.max_columns', None)
    # pd.set_option('display.width', 1000)
    # print(df_historical)
    # print(df_predicted)

    fig.update_layout(
        xaxis_title='Mês',
        yaxis_title='Atendimentos',
        font_family=xy_font_family,
        font_color=xy_font_color,
		plot_bgcolor=plot_bgcolor,
		xaxis=dict(
			showline=True,
			showgrid=True,
			showticklabels=True,
			linecolor=xy_line_color,
			linewidth=2,
			ticks='outside',
			tickfont=dict(family=tick_font_family, size=tick_font_size, color=tick_font_color)
		),
		yaxis=dict(
			showline=True,
			showgrid=True,
			showticklabels=True,
			linecolor=xy_line_color,
			linewidth=2,
			ticks='outside',
			tickfont=dict(family=tick_font_family, size=tick_font_size, color=tick_font_color)
		)
    )
    graph_html = fig.to_html(full_html=False)
    return graph_html

# Waiting Time Per Month
def df_waiting_time_per_month_historical(df_historical, location):
    df_historical['Type'] = 'Historical'
    df_historical['Data'] = pd.to_datetime(df_historical['Data'])
    df_historical = df_historical[df_historical['Designacao'] == location]
    df_historical['Meses'] = df_historical['Data'].dt.to_period('M')
    df_historical = df_historical.groupby('Meses').agg({'Tempo_medio_de_espera_diario': 'mean'}).reset_index()
    # Convert Meses back to a datetime object for Plotly
    df_historical['Meses'] = df_historical['Meses'].dt.to_timestamp()
    return df_historical


def df_waiting_time_per_month_predicted(df_predicted, location):
    df_predicted['Type'] = 'Predicted'
    df_predicted['Meses'] = pd.to_datetime(df_predicted['Meses'])
    df_predicted = df_predicted[df_predicted['Designacao'] == location]
    df_predicted['Meses'] = df_predicted['Meses'].dt.to_period('M')
    df_predicted = df_predicted.groupby('Meses').agg({'Tempo_medio_de_espera_diario': 'mean'}).reset_index()
    df_predicted['Meses'] = df_predicted['Meses'].dt.to_timestamp()
    return df_predicted


def plot_waiting_time_per_month(location, df_historical = None, df_predicted = None):

    fig = go.Figure()

    if df_historical is not None:
        df_historical = df_waiting_time_per_month_historical(df_historical, location)

        fig.add_trace(go.Scatter(
            x=df_historical['Meses'], 
            y=df_historical['Tempo_medio_de_espera_diario'], 
            mode='lines', 
            name='Dados Históricos',
            line=dict(color=line1_color, width=line1_width)
        ))
    if df_predicted is not None:
        df_predicted = df_waiting_time_per_month_predicted(df_predicted, location)

        fig.add_trace(go.Scatter(
            x=df_predicted['Meses'], 
            y=df_predicted['Tempo_medio_de_espera_diario'], 
            mode='lines', 
            name='Previsões',
            line=dict(color=line2_color, width=line2_width)
        ))
    if df_historical is not None and df_predicted is not None:
        boundary = df_predicted['Meses'].min()
        fig.update_traces(
            selector=dict(name='Previsões'),
            line=dict(dash='dot')
        )
        fig.add_vline(x=boundary, line_width=line1_width, line_dash="dash", line_color=boundary_color)

    # # Print BigQuery data on terminal
    # pd.set_option('display.max_rows', None)
    # pd.set_option('display.max_columns', None)
    # pd.set_option('display.width', 1000)
    # print(df_historical)
    # print(df_predicted)

    fig.update_layout(
        xaxis_title='Mês',
        yaxis_title='Tempo médio de espera',
        font_family=xy_font_family,
        font_color=xy_font_color,
		plot_bgcolor=plot_bgcolor,
		xaxis=dict(
			showline=True,
			showgrid=True,
			showticklabels=True,
			linecolor=xy_line_color,
			linewidth=2,
			ticks='outside',
			tickfont=dict(family=tick_font_family, size=tick_font_size, color=tick_font_color)
		),
		yaxis=dict(
			showline=True,
			showgrid=True,
			showticklabels=True,
			linecolor=xy_line_color,
			linewidth=2,
			ticks='outside',
			tickfont=dict(family=tick_font_family, size=tick_font_size, color=tick_font_color)
		)
    )
    graph_html = fig.to_html(full_html=False)
    return graph_html

# Procuras Per Month
def df_procuras_per_month_historical(df_historical, location):
    df_historical['Type'] = 'Historical'
    df_historical['Data'] = pd.to_datetime(df_historical['Data'])
    df_historical = df_historical[df_historical['Designacao'] == location]
    df_historical['Meses'] = df_historical['Data'].dt.to_period('M')
    df_historical = df_historical.groupby('Meses').agg({'Procuras': 'sum'}).reset_index()
    # Convert Meses back to a datetime object for Plotly
    df_historical['Meses'] = df_historical['Meses'].dt.to_timestamp()
    return df_historical


def df_procuras_per_month_predicted(df_predicted, location):
    df_predicted['Type'] = 'Predicted'
    df_predicted['Meses'] = pd.to_datetime(df_predicted['Meses'])
    df_predicted = df_predicted[df_predicted['Designacao'] == location]
    df_predicted['Meses'] = df_predicted['Meses'].dt.to_period('M')
    df_predicted = df_predicted.groupby('Meses').agg({'Procuras': 'sum'}).reset_index()
    df_predicted['Meses'] = df_predicted['Meses'].dt.to_timestamp()
    return df_predicted


def plot_procuras_per_month(location, df_historical = None, df_predicted = None):

    fig = go.Figure()

    if df_historical is not None:
        df_historical = df_procuras_per_month_historical(df_historical, location)

        fig.add_trace(go.Scatter(
            x=df_historical['Meses'], 
            y=df_historical['Procuras'], 
            mode='lines', 
            name='Dados Históricos',
            line=dict(color=line1_color, width=line1_width)
        ))
    if df_predicted is not None:
        df_predicted = df_procuras_per_month_predicted(df_predicted, location)

        fig.add_trace(go.Scatter(
            x=df_predicted['Meses'], 
            y=df_predicted['Procuras'], 
            mode='lines', 
            name='Previsões',
            line=dict(color=line2_color, width=line2_width)
        ))
    if df_historical is not None and df_predicted is not None:
        boundary = df_predicted['Meses'].min()
        fig.update_traces(
            selector=dict(name='Previsões'),
            line=dict(dash='dot')
        )
        fig.add_vline(x=boundary, line_width=line1_width, line_dash="dash", line_color=boundary_color)

    fig.update_layout(
        xaxis_title='Mês',
        yaxis_title='Procuras',
        font_family=xy_font_family,
        font_color=xy_font_color,
		plot_bgcolor=plot_bgcolor,
		xaxis=dict(
			showline=True,
			showgrid=True,
			showticklabels=True,
			linecolor=xy_line_color,
			linewidth=2,
			ticks='outside',
			tickfont=dict(family=tick_font_family, size=tick_font_size, color=tick_font_color)
		),
		yaxis=dict(
			showline=True,
			showgrid=True,
			showticklabels=True,
			linecolor=xy_line_color,
			linewidth=2,
			ticks='outside',
			tickfont=dict(family=tick_font_family, size=tick_font_size, color=tick_font_color)
		)
    )
    graph_html = fig.to_html(full_html=False)
    return graph_html

# Desistencias Per Month
def df_desistencias_per_month_historical(df_historical, location):
    df_historical['Type'] = 'Historical'
    df_historical['Data'] = pd.to_datetime(df_historical['Data'])
    df_historical = df_historical[df_historical['Designacao'] == location]
    df_historical['Meses'] = df_historical['Data'].dt.to_period('M')
    df_historical = df_historical.groupby('Meses').agg({'Desistencias': 'sum'}).reset_index()
    # Convert Meses back to a datetime object for Plotly
    df_historical['Meses'] = df_historical['Meses'].dt.to_timestamp()
    return df_historical


def df_desistencias_per_month_predicted(df_predicted, location):
    df_predicted['Type'] = 'Predicted'
    df_predicted['Meses'] = pd.to_datetime(df_predicted['Meses'])
    df_predicted = df_predicted[df_predicted['Designacao'] == location]
    df_predicted['Meses'] = df_predicted['Meses'].dt.to_period('M')
    df_predicted = df_predicted.groupby('Meses').agg({'Desistencias': 'sum'}).reset_index()
    df_predicted['Meses'] = df_predicted['Meses'].dt.to_timestamp()
    return df_predicted


def plot_desistencias_per_month(location, df_historical = None, df_predicted = None):

    fig = go.Figure()

    if df_historical is not None:
        df_historical = df_desistencias_per_month_historical(df_historical, location)

        fig.add_trace(go.Scatter(
            x=df_historical['Meses'], 
            y=df_historical['Desistencias'], 
            mode='lines', 
            name='Dados Históricos',
            line=dict(color=line1_color, width=line1_width)
        ))
    if df_predicted is not None:
        df_predicted = df_desistencias_per_month_predicted(df_predicted, location)

        fig.add_trace(go.Scatter(
            x=df_predicted['Meses'], 
            y=df_predicted['Desistencias'], 
            mode='lines', 
            name='Previsões',
            line=dict(color=line2_color, width=line2_width)
        ))
    if df_historical is not None and df_predicted is not None:
        boundary = df_predicted['Meses'].min()
        fig.update_traces(
            selector=dict(name='Previsões'),
            line=dict(dash='dot')
        )
        fig.add_vline(x=boundary, line_width=line1_width, line_dash="dash", line_color=boundary_color)

    fig.update_layout(
        xaxis_title='Mês',
        yaxis_title='Desistencias',
        font_family=xy_font_family,
        font_color=xy_font_color,
		plot_bgcolor=plot_bgcolor,
		xaxis=dict(
			showline=True,
			showgrid=True,
			showticklabels=True,
			linecolor=xy_line_color,
			linewidth=2,
			ticks='outside',
			tickfont=dict(family=tick_font_family, size=tick_font_size, color=tick_font_color)
		),
		yaxis=dict(
			showline=True,
			showgrid=True,
			showticklabels=True,
			linecolor=xy_line_color,
			linewidth=2,
			ticks='outside',
			tickfont=dict(family=tick_font_family, size=tick_font_size, color=tick_font_color)
		)
    )
    graph_html = fig.to_html(full_html=False)
    return graph_html


# Plots to implement

# def plot_necessity_metric(df):
# def plot_waiting_time_per_month(df):
# def plot_desistencias_per_month(df):
# def plot_(df):

def make_plots(location):
    df_historical = DF_HISTORICAL
    df_predicted = DF_PREDICTED
    plot_list = [
        plot_atendimentos_per_month(location, df_historical=df_historical, df_predicted=df_predicted),
        plot_waiting_time_per_month(location, df_historical=df_historical, df_predicted=df_predicted),
        plot_procuras_per_month(location, df_historical=df_historical, df_predicted=df_predicted),
        plot_desistencias_per_month(location, df_historical=df_historical, df_predicted=df_predicted)
	]
    return plot_list
