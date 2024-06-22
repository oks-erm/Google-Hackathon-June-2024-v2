from models import *
import pandas as pd
from google.cloud import bigquery as bq
# import bigquery_storage as bq_storage
import plotly.express as px

def querry_bq():
    client = bq.Client()
    query = """
        SELECT * FROM `sublime-lyceum-426907-r9.ama.merged`
        LIMIT 1200
    """
    df = client.query(query).to_dataframe()
    return df

def plot_atendimentos_per_month(df):
    ## Historical atendimentos per month line graph ## 
    # Make sure 'Data_e...' field is in datetime format
    df['Data'] = pd.to_datetime(df['Data'])
    # Location provided by the model
    location = 'Loja de Cidadão Laranjeiras'
    df_filtered = df[df['Designacao'] == location]
    df_filtered['Meses'] = df_filtered['Data'].dt.to_period('M')
    df_grouped = df_filtered.groupby('Meses').agg({'Atendimentos': 'sum'}).reset_index()
    # Convert Meses back to a datetime object for Plotly
    df_grouped['Meses'] = df_grouped['Meses'].dt.to_timestamp()

    # Print BigQuery data on terminal
    # pd.set_option('display.max_rows', None)
    # pd.set_option('display.max_columns', None)
    # pd.set_option('display.width', 1000)
    # print(df_grouped)

    # Create Plotly Graph
    fig = px.line(df_grouped, x='Meses', y='Atendimentos', title=f'Atendimentos Over Time for {location}')
    fig.update_layout(
        title=f'Atendimentos ao longo dos meses em {location}',
        xaxis_title='Mês',
        yaxis_title='Atendimentos'
    )
    fig.update_traces(
        line=dict(color='royalblue', width=4, dash='dash')
    )
    graph_html = fig.to_html(full_html=False)
    return graph_html
    

def make_plots():
    df = querry_bq()
    plot_list = [
        plot_atendimentos_per_month(df),
        
	]
    return plot_list
    
    
    

