import json
import pandas as pd
import numpy as np

def build_table_for_cards(df_historic_data):
    
    #### Historic data #####

    # filter the dataframe
    filtered_df_2024 = df_historic_data[df_historic_data['Year'] == 2024]
    columns_to_drop = ["Latitude", "Longitude", "Year", "Month", "Day", "Localidade_Postal",
                       "Freguesia", "Codigo_do_Ponto_de_Atendimento", "Population_Density", "Codigo_Freguesia", "Data"]
    filtered_df_2024 = filtered_df_2024.drop(columns=columns_to_drop)
   
    # group the rows by designacao, averaging the other elements
    df_grouped = filtered_df_2024.groupby('Designacao').agg({"Procuras": 'mean',
                                                             "Atendimentos": 'mean',
                                                             "Desistencias": 'mean',
                                                             "Tempo_medio_de_espera_diario": 'mean',
                                                             "Population": 'mean',
                                                             }).reset_index()

    # Calculate the stress values
    stress_value = [int((a['Procuras'] * a['Desistencias'] * a['Tempo_medio_de_espera_diario'])
                        / (a['Atendimentos'] * a['Population']))
                    for a in json.loads(df_grouped.to_json(orient='records'))]

    # Dispose of unecessary data
    columns_to_drop = ["Procuras", "Atendimentos", "Desistencias",
                       "Tempo_medio_de_espera_diario", "Population"]
    df_grouped = df_grouped.drop(columns=columns_to_drop)
    df_grouped['stress_value'] = stress_value

    #### Predicted data #####

    original_df = pd.read_csv('./static/assets/model_frame.csv')
    original_df = original_df[original_df['Year'] == original_df['Year'].max()]
    columns_to_drop = ["Year", "Procuras",
                       "Tempo_medio_de_espera_diario", "Atendimentos", "Desistencias"]
    original_df = original_df.drop(
        columns=columns_to_drop)
    original_df.reset_index(drop=True, inplace=True)

    #### Merge data from both tables #####
    
    df_grouped = df_grouped.sort_values(by='Designacao')
    original_df = original_df.sort_values(by='Location')
    cards_table = []
    js = json.loads(df_grouped.to_json())
    js2 = json.loads(original_df.to_json())
    # print(js)
    for index in js['Designacao'].keys():
        cards_table.append({
            'Designacao': js['Designacao'][index],
            'stress_value': js['stress_value'][index],
            'necessity_metric': js2['necessity_metric'][index]
        })
    return cards_table