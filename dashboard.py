# Importations de bibliothèques
import streamlit as st
import requests
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from PIL import Image

# Définition de l'URL de l'API
url_api = 'http://127.0.0.1:5000'  # local API

# Fonction principale
def main():
    # Title and subtitle
    st.title("Prêt à dépenser")
    st.markdown("<i>Calculateur de risque de défaut </i>", unsafe_allow_html=True)
    st.markdown("Cette application web permet à l'utilisateur de savoir quelle est la probabilité qu'un demandeur de crédit donné entre en défaut de paiement, elle affiche certaines informations sur les clients et elle compare le demandeur à tous les autre.", unsafe_allow_html=True)
    
    # Logo
    logo = load_logo()
    st.sidebar.image(logo, width=300)
    
    # Sidebar
    st.sidebar.subheader("Informations générales")
    id_list = load_id_list()
    client_id = st.sidebar.selectbox("Sélectionner un client", id_list)
    
    if client_id != 'Client ID':
        client_info = load_client_info(client_id)
        load_data(client_info)

# Chargement du logo
@st.cache
def load_logo(folder='img', filename='logo', ext='png'):
    path = './' + folder + '/' + filename + '.' + ext
    logo = Image.open(path) 
    return logo

# Chargement des informations client
@st.cache
def load_client_info(client_id):
    response = requests.get(url_api + "/client?id=" + str(client_id))
    if response.status_code == 200:
        client_info = response.json()
        return client_info
    else:
        st.error(f"Erreur lors du chargement des informations client: {response.status_code}")
        return None

# Chargement des données
@st.cache(allow_output_mutation=True)
def load_data(client_info):
    if client_info is not None:
        response = requests.get(url_api + '/data')
        if response.status_code == 200:
            data_list = response.json()
            return data_list
        else:
            st.error(f"Erreur lors du chargement des données: {response.status_code}")
            return None

# Chargement de la liste des IDs des clients
@st.cache
def load_id_list():
    response = requests.get(url_api + "/client_list")
    if response.status_code == 200:
        id_list = response.json()
        id_list = ['Client ID'] + id_list
        return id_list
    else:
        st.error(f"Erreur lors du chargement de la liste des IDs des clients: {response.status_code}")
        return None

# Tracé de l'histogramme
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
    fig = plt.gcf()
    return fig

# Tracé du graphique de risque
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

if __name__ == "__main__":
    main()


    
