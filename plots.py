from models import *
import pandas as pd
from google.cloud import bigquery as bq
from google.oauth2 import service_account
import plotly.express as px
import plotly.graph_objects as go
from openai import OpenAI
from dotenv import load_dotenv
from config import creds_dict

# Load environment variables
load_dotenv()

# BigQuery parameters
project_id = 'sublime-lyceum-426907-r9'
dataset_id = 'ama'

# Plotly graph design
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


credentials = service_account.Credentials.from_service_account_info(creds_dict)

client = OpenAI()
def respond_gpt(df_historical, df_predicted) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um analista de dados experiente. Sua função é fornecer insights de dataframes de forma coesa e coerente. Responder em alguns breves 'pontos' destacando as tendências mais importantes e dando recomendações sobre a interpretação dos dados. Não diga coisas genéricas. Não utilize nomes de colunas de uma tabela de dados em inglês. Produza a resposta de uma forma que possa ser exibida na página html com um layout adequado usando <ul> e <li> ."
                },
                {
                    "role": "user",
                    "content": f"Aqui está um conjunto de dados projetados: {df_predicted}, {df_predicted}, incluindo a métrica de necessidade que derivámos para ajudar o utilizador a entender estes dados. Os dados estão relacionados com atendimentos e tempos de espera de vários escritórios de uma entidade governamental e as suas recomendações têm como objetivo ajudar a abrir mais pontos de contacto, se necessário. Forneça insights e recomendações com base nesses dados. A resposta deve ser específica e direta evite frases genéricas. Responda em português de Portugal"
                }
            ],
            max_tokens=600,
            temperature=0.4,
        )
        response = (response.choices[0].message.content)
        return response
    except Exception as e:
        return f"Error: {e}"


def querry_bq(project, dataset, table):
    client = bq.Client(credentials=credentials, project=project)
    query = f"""
        SELECT * FROM `{project}.{dataset}.{table}`
        LIMIT 1200
        """
    df = client.query(query).to_dataframe()
    return df

DF_HISTORICAL = querry_bq(project_id, dataset_id, 'merged')
DF_PREDICTED = querry_bq(project_id, dataset_id, 'aggregated_data_with_necessity')

# Atendimentos Per Month
def plot_atendimentos_per_month(location, df_historical = None, df_predicted = None):
    fig = go.Figure()

    if df_historical is not None:
        fig.add_trace(go.Scatter(
            x=df_historical['Meses'], 
            y=df_historical['Atendimentos'], 
            mode='lines', 
            name='Dados Históricos',
            line=dict(color=line1_color, width=line1_width)
        ))
    if df_predicted is not None:
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

    fig.update_layout(
        xaxis_title='Mês',
        yaxis_title='Atendimentos',
        font_family=xy_font_family,
        font_color=xy_font_color,
        plot_bgcolor=plot_bgcolor,
        xaxis_autorange=True,
        yaxis_autorange=True,
        autosize=True,
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
def plot_waiting_time_per_month(location, df_historical = None, df_predicted = None):

    fig = go.Figure()

    if df_historical is not None:
        fig.add_trace(go.Scatter(
            x=df_historical['Meses'], 
            y=df_historical['Tempo_medio_de_espera_diario'], 
            mode='lines', 
            name='Dados Históricos',
            line=dict(color=line1_color, width=line1_width)
        ))
    if df_predicted is not None:
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

    fig.update_layout(
        xaxis_title='Mês',
        yaxis_title='Tempo médio de espera',
        font_family=xy_font_family,
        font_color=xy_font_color,
        plot_bgcolor=plot_bgcolor,
        xaxis_autorange=True,
        yaxis_autorange=True,
        autosize=True,
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
def plot_procuras_per_month(location, df_historical = None, df_predicted = None):

    fig = go.Figure()

    if df_historical is not None:

        fig.add_trace(go.Scatter(
            x=df_historical['Meses'], 
            y=df_historical['Procuras'], 
            mode='lines', 
            name='Dados Históricos',
            line=dict(color=line1_color, width=line1_width)
        ))
    if df_predicted is not None:

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
        xaxis_autorange=True,
        yaxis_autorange=True,
        autosize=True,
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
def plot_desistencias_per_month(location, df_historical = None, df_predicted = None):

    fig = go.Figure()

    if df_historical is not None:
        fig.add_trace(go.Scatter(
            x=df_historical['Meses'], 
            y=df_historical['Desistencias'], 
            mode='lines', 
            name='Dados Históricos',
            line=dict(color=line1_color, width=line1_width)
        ))
    if df_predicted is not None:
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
        xaxis_autorange=True,
        yaxis_autorange=True,
        autosize=True,
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


def filter_historical_data(df_historical, location):
    df_historical['Type'] = 'Historical'
    df_historical['Data'] = pd.to_datetime(df_historical['Data'])
    df_historical = df_historical[df_historical['Designacao'] == location]
    df_historical['Meses'] = df_historical['Data'].dt.to_period('M')
    df_historical = df_historical.groupby('Meses').agg({'Procuras': 'sum',
        'Atendimentos': 'sum',
        'Desistencias': 'sum',
        'Tempo_medio_de_espera_diario': 'mean'}).reset_index()
    df_historical['Meses'] = df_historical['Meses'].dt.to_timestamp()
    return df_historical


def filter_predicted_data(df_predicted, location):
    df_predicted['Type'] = 'Predicted'
    df_predicted['Meses'] = pd.to_datetime(df_predicted['Meses'])
    df_predicted = df_predicted[df_predicted['Designacao'] == location]
    df_predicted['Meses'] = df_predicted['Meses'].dt.to_period('M')
    df_predicted = df_predicted.groupby('Meses').agg({'Procuras': 'sum',
        'Atendimentos': 'sum',
        'Desistencias': 'sum',
        'Tempo_medio_de_espera_diario': 'mean',
        'Necessity_Metric': 'mean'}).reset_index()
    df_predicted['Meses'] = df_predicted['Meses'].dt.to_timestamp()
    return df_predicted

def get_data_per_year(df):
    df['Ano'] = df['Meses'].dt.to_period('Y')
    df = df.groupby('Ano').agg({'Procuras': 'sum',
        'Atendimentos': 'sum',
        'Desistencias': 'sum',
        'Tempo_medio_de_espera_diario': 'mean',
        'Necessity_Metric': 'max'}).reset_index()
    df['Procuras'] = df['Procuras'].astype(int)
    df['Atendimentos'] = df['Atendimentos'].astype(int)
    df['Desistencias'] = df['Desistencias'].astype(int)
    df['Atendimentos'] = df['Atendimentos'].astype(int)
    df['Tempo_medio_de_espera_diario'] = df['Tempo_medio_de_espera_diario'].astype(int)
    df['Necessity_Metric'] = df['Necessity_Metric'].round(2)
    df['Index'] = df.index

    return df.to_dict(orient='list')

def make_plots(location):
    df_historical = DF_HISTORICAL
    df_predicted = DF_PREDICTED

    df_historical = filter_historical_data(df_historical, location)
    df_predicted = filter_predicted_data(df_predicted, location)
    plot_merged_list = [
        plot_atendimentos_per_month(location, df_historical=df_historical, df_predicted=df_predicted),
        plot_waiting_time_per_month(location, df_historical=df_historical, df_predicted=df_predicted),
        plot_procuras_per_month(location, df_historical=df_historical, df_predicted=df_predicted),
        plot_desistencias_per_month(location, df_historical=df_historical, df_predicted=df_predicted),
	]
    plot_historical_list = [
        plot_atendimentos_per_month(location, df_historical=df_historical),
        plot_waiting_time_per_month(location, df_historical=df_historical),
        plot_procuras_per_month(location, df_historical=df_historical),
        plot_desistencias_per_month(location, df_historical=df_historical),
    ]
    ai_insights = respond_gpt(df_historical.to_string(), df_predicted.to_string())
    
    # Dictionary containing columns and data, grouped by year
    data_by_year = get_data_per_year(df_predicted)

    return plot_merged_list, plot_historical_list, data_by_year, ai_insights
