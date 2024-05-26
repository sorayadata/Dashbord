import streamlit as st
import numpy as np
import pandas as pd
import requests
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from PIL import Image

# Définition de l'URL de l'API
url_api = 'http://127.0.0.1:5000/'  # local API
#url_api = 'http://credit.consommationapp.com/'  # online API

st.set_option('deprecation.showPyplotGlobalUse', False)

def main():
    label_list = ['age', 'annuity amount', 'credit amount', 'income amount']
    
    # Title and subtitle
    st.title("Prêt à dépenser")
    st.markdown("<i>Calculateur de risque de défaut </i>", unsafe_allow_html=True)
    st.markdown("Cette application web permet à l'utilisateur de savoir quelle est la probabilité qu'un demandeur de crédit donné entre en défaut de paiement, elle affiche certaines informations sur les clients et elle compare le demandeur à tous les autre.", unsafe_allow_html=True)
    
    # Logo
    logo = load_logo()
    st.sidebar.image(logo, width=300)
    
    # Affichage d'informations dans la sidebar
    st.sidebar.subheader("Informations générales")
    
    # Selectbox (client)
    id_list = load_id_list()
    global client_id
    client_id = st.sidebar.selectbox("Sélectionner un client", id_list)
    
    # ID list loading
    if client_id != 'Client ID':
        client_info = load_client_info(client_id)
        
        # Default probability calculation
        if client_id != 'Client ID':
            url_api_client = url_api + '/predict_default?id_client=' + str(client_id)
            response = requests.get(url_api_client)
            status_code = response.status_code    
            
            # Client not found
            if status_code != 200:
                st.markdown(f":red[Client not found (*Error {status_code}*).]")
            else:
                # Risk chart
                client_data = response.json()
                proba = client_data['proba_1']
                proba = proba * 100
                plot_risk(proba, treshold=50)
                
                # Client compare chart (age, annuity amount, credit amount, total income amount)
                chart_option_dict = {'DAYS_BIRTH': 'age', 
                                     'AMT_ANNUITY': 'annuity amount', 
                                     'AMT_CREDIT': 'credit amount', 
                                     'AMT_INCOME_TOTAL': 'income amount'}
                
                variable_list = chart_option_dict.keys()
                
                label_list = ['age', 'annuity amount', 'credit amount', 'income amount']
                title_list = ['Clients age', 'Annuities amount', 'Credits amount', 'Total incomes']
                unit_list_side  = ["years", "$", "$", "$"]
                unit_list  = ["years", "$", "millions $", "millions $"]
                divide_by_list = [365, 1, 1, 1]

                var_key_list = ['label', 'title', 'unit_side', 'unit', 'divisor']
                var_value_list = [label_list, title_list, unit_list_side, unit_list, divide_by_list]
                
                show_client_info = st.sidebar.checkbox("Afficher les informations client")
                
                chart_dict = dict()
                
                for i, v in enumerate(variable_list):
                    var = v
                    var_dict = dict()
                    for j, k in enumerate(var_key_list):
                        var_dict[k] = var_value_list[j][i]
                    
                    chart_dict[var] = var_dict
                    
                    # Client info (age, annuity amount, credit amount, total income amount)
                    if show_client_info:
                        var_label = chart_dict[var]['label'].capitalize()
                        var_val = client_info[var]
                        if divide_by_list[i] != 1:
                            var_val = int(var_val / divide_by_list[i])
                        st.sidebar.markdown(f"<b>{var_label}</b>: {var_val} {chart_dict[var]['unit_side']}", unsafe_allow_html=True)
                
                st.sidebar.subheader("Compare client")
                
                chart_option_list = list(chart_option_dict.values())
                chart_option_list = ['Chart type'] + chart_option_list
                chart_option_value = st.sidebar.selectbox("Sélectionner un graphique", chart_option_list)
                
                if chart_option_value != 'Chart type':
                    for key, value in chart_option_dict.items():
                        if value == chart_option_value:
                            col = key
                            break
                    
                    label = chart_dict[col]['label']
                    title = chart_dict[col]['title']
                    unit = chart_dict[col]['unit']
                    xlabel = f"{label.capitalize()} ({unit})"
                    divisor = chart_dict[col]['divisor']
                    data = load_data(col)
                    plot_hist(data, client_info[col], title=title, xlabel=xlabel, divisor=divisor)


@st.cache_data()
def load_logo(folder='img', filename='logo', ext='png'):
    path = './' + folder + '/' + filename + '.' + ext
    logo = Image.open(path) 
    return logo


@st.cache_data()
def plot_hist(data, client_value, title, xlabel, ylabel='count', divisor=1):
    if divisor != 1:
        data = [d / divisor for d in data]
        client_value = int(client_value / divisor)
    plt.style.use('fivethirtyeight')
    plt.figure(figsize=(9, 6))
    plt.hist(data, edgecolor='k', bins=25)
    plt.axvline(client_value, color="red", linestyle=":")
    plt.title(title, fontsize=15)
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    st.pyplot()


@st.cache_data()
def plot_risk(proba, treshold=10, max_val=None):
    if max_val is None:
        max_val = treshold * 2
    
    if proba > max_val:
        max_val = proba
    
    fig = go.Figure(go.Indicator(mode="gauge+number+delta",
                                 value=proba,
                                 domain={'x': [0, 1], 'y': [0, 1]},
                                 title={'text': "Risque de défaut (%)", 'font': {'size': 24}},
                                 delta={'reference': treshold, 'increasing': {'color': "red"}, 'decreasing': {'color': "green"}},
                                 gauge={'axis': {'range': [None, max_val], 'tickwidth': 1, 'tickcolor': "darkblue"},
                                        'bar': {'color': "lavender"},
                                        'bgcolor': "white",
                                        'borderwidth': 2,
                                        'bordercolor': "gray",
                                        'steps': [{'range': [0, treshold], 'color': 'green'},
                                                  {'range': [treshold, max_val], 'color': 'red'}]}))

    fig.update_layout(paper_bgcolor="white", font={'color': "darkblue", 'family': "Arial"})

    st.plotly_chart(fig)


@st.cache_data()
def load_client_info(client_id):
    response = requests.get(url_api + "/client?id=" + str(client_id))
    client_info = response.json()
    return client_info


@st.cache_data()
def load_data(col):
    url = url_api + '/data?col=' + col
    response = requests.get(url)
    data_list = response.json()
    return data_list


@st.cache_data()
def load_id_list():
    response = requests.get(url_api + "/client_list")
    id_list = response.json()
    id_list = ['Client ID'] + id_list
    return id_list


def get_label_list_str(label_list, sep=', '):
    string = sep.join(label_list)
    return string


if __name__ == "__main__":
    main()

    
