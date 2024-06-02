import streamlit as st
import numpy as np
import pandas as pd
import requests
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from PIL import Image

# url_api = 'http://localhost:5000'  # local API
url_api = "http://13.38.29.238:5000" # online API

st.set_option('deprecation.showPyplotGlobalUse', False)

def main():
    label_list = ['age', 'annuity amount', 'credit amount', 'income amount']
    
    # Title and subtitle
    st.title("Prêt à dépenser")
    st.markdown("Calculateur de risque de défaut", unsafe_allow_html=True)
    st.markdown(
        "Cette application web permet à l'utilisateur de savoir quelle est la probabilité qu'un demandeur de crédit entre en situation de non-paiement des prêts, "
        "elle affiche certaines informations sur les clients et compare le demandeur à tous les demandeurs sur certains critères.",
        unsafe_allow_html=True
    )
    
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
        url_api_client = f"{url_api}/predict_default?id_client={client_id}"
        try:
            response = requests.get(url_api_client, timeout=10)
            response.raise_for_status()
            client_data = response.json()
            proba = client_data['proba_1'] * 100
            plot_risk(proba, treshold=50)
        except requests.exceptions.RequestException as e:
            st.error(f"Erreur lors de la récupération des données du client : {e}")
            return
        
        # Client compare chart (age, annuity amount, credit amount, total income amount)
        chart_option_dict = {
            'DAYS_BIRTH': 'age', 
            'AMT_ANNUITY': 'annuity amount', 
            'AMT_CREDIT': 'credit amount', 
            'AMT_INCOME_TOTAL': 'income amount'
        }
        
        variable_list = chart_option_dict.keys()
        title_list = ['Clients age', 'Annuities amount', 'Credits amount', 'Total incomes']
        unit_list_side  = ["years", "$", "$", "$"]
        unit_list  = ["years", "$", "millions $", "millions $"]
        divide_by_list = [1, 1, 1, 1]

        var_key_list = ['label', 'title', 'unit_side', 'unit', 'divisor']
        var_value_list = [label_list, title_list, unit_list_side, unit_list, divide_by_list]
        
        show_client_info = st.sidebar.checkbox("Show client info")
        
        chart_dict = {}
        
        for i, v in enumerate(variable_list):
            var_dict = {k: var_value_list[j][i] for j, k in enumerate(var_key_list)}
            chart_dict[v] = var_dict
            
            # Client info (age, annuity amount, credit amount, total income amount)
            if show_client_info:
                var_label = chart_dict[v]['label'].capitalize()
                var_val = client_info[v]
                if divide_by_list[i] != 1:
                    var_val = int(var_val / divide_by_list[i])
                st.sidebar.markdown(f"<b>{var_label}</b>: {var_val} {chart_dict[v]['unit_side']}", unsafe_allow_html=True)
        
        st.sidebar.subheader("Comparer les clients")
        
        chart_option_list = ['Chart type'] + list(chart_option_dict.values())
        chart_option_value = st.sidebar.selectbox("Sélectionner un graphique", chart_option_list)
        
        if chart_option_value != 'Chart type':
            col = next(key for key, value in chart_option_dict.items() if value == chart_option_value)
            
            label = chart_dict[col]['label']
            title = chart_dict[col]['title']
            unit = chart_dict[col]['unit']
            xlabel = f"{label.capitalize()} ({unit})"
            divisor = chart_dict[col]['divisor']
            data = load_data(col)
            plot_hist(data, client_info[col], title=title, xlabel=xlabel, divisor=divisor)

@st.cache_data()
def load_logo(folder='img', filename='logo', ext='png'):
    path = f'./{folder}/{filename}.{ext}'
    logo = Image.open(path) 
    return logo

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

def plot_risk(proba, treshold=10, max_val=None):
    if max_val is None:
        max_val = treshold * 2
        
    if proba > max_val:
        max_val = proba
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=proba,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Default risk (%)", 'font': {'size': 24}},
        delta={'reference': treshold, 'increasing': {'color': "red"}, 'decreasing': {'color': "green"}},
        gauge={
            'axis': {'range': [None, max_val], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "lavender"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, treshold], 'color': 'green'},
                {'range': [treshold, max_val], 'color': 'red'}
            ]
        }
    ))

    fig.update_layout(paper_bgcolor="white", font={'color': "darkblue", 'family': "Arial"})
    st.plotly_chart(fig)

@st.cache_data()
def load_client_info(client_id):
    try:
        response = requests.get(f"{url_api}/client?id={client_id}", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Erreur lors de la récupération des informations du client : {e}")
        return {}

@st.cache_data()
def load_data(col):
    try:
        response = requests.get(f"{url_api}/data?col={col}", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Erreur lors de la récupération des données : {e}")
        return []

@st.cache_data()
def load_id_list():
    try:
        response = requests.get(f"{url_api}/client_list", timeout=10)
        response.raise_for_status()
        id_list = response.json()
        return ['Client ID'] + id_list
    except requests.exceptions.RequestException as e:
        st.error(f"Erreur lors de la récupération de la liste des clients : {e}")
        return ['Client ID']

if __name__ == "__main__":
    main()
