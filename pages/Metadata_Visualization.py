import os
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from datetime import timedelta
######################## ################################################################################################################################################################################

st.set_page_config(layout="wide")

hide_st_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """
st.markdown("""
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css">
    """, unsafe_allow_html=True)



st.markdown(
    """
    <style>
    
    body {
        background-color: #ffffff; /* Couleur de fond par défaut */
        color: #000000; /* Couleur de texte par défaut */
        font-family: Arial, sans-serif;
        padding: 1rem;
    }
    .video-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 500px; /* Ajustez la hauteur de la vidéo selon vos besoins */
    }
    
    
   .stApp {
        /* Utilisez l'URL de votre image comme valeur de background-image */
      
        background-image: url('https://cdn.pixabay.com/photo/2020/06/01/06/11/magnifier-5245329_640.jpg');
        background-size: contain; /* Ajuste la taille de l'image pour couvrir tout l'arrière-plan */
        background-repeat: no-repeat; /* Empêche la répétition de l'image */
        background-position: center center; /* Centre l'image horizontalement et verticalement */
        color: #ffffff;
        font-family: Arial, sans-serif;
        padding: 1rem;
        
        background-attachment: scroll; # doesn't work;
        
    }
    .stButton button {
        background-color:#866ef0;
        color:white;
        padding: 0.5rem 1rem;
        border: none;
        border-radius: 0.25rem;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }

    .stButton button:hover {
        background-color:#D3F7F4;
    }

    .stHeader {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }

    
    </style>
    """,
    unsafe_allow_html=True
)

######################## ################################################################################################################################################################################

# Fonction pour lister tous les fichiers .xlsx dans le dossier actuel

def list_excel_files():
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'Scrapping_Channel_Informations')
    return [f for f in os.listdir(data_dir) if f.endswith('.xlsx')]



######################## ################################################################################################################################################################################

def load_data(file_name):
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'Scrapping_Channel_Informations')
    file_path = os.path.join(data_dir, file_name)
    # Charger les données à partir du fichier Excel
    df = pd.read_excel(file_path)
    return df

######################## ################################################################################################################################################################################




# Fonction pour convertir les dates et filtrer par plage de dates
def filter_data_by_date(df, date_col, start_date, end_date):
    # Convertir la colonne PublishedDate en datetime
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce', format='%Y-%m-%dT%H:%M:%S.%fZ')
    
    # Convertir start_date et end_date en datetime
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    
    # Filtrer les données par plage de dates
    df_filtered = df[(df[date_col] >= start_date) & (df[date_col] <= end_date)]
    
    return df_filtered


######################## ################################################################################################################################################################################


def create_candlestick_chart(df, date_col, value_col, title):
    # Trier les données par date
    df = df.sort_values(by=date_col)

    # Créer un graphique en chandelier japonais avec des points de données
    fig = go.Figure(data=[go.Scatter(x=df[date_col], 
                                    y=df[value_col], 
                                    mode='lines+markers', 
                                    name=value_col)])

    # Ajouter des titres et des labels
    fig.update_layout(title=title,
                      xaxis_title='Date',
                      yaxis_title=value_col)

    # Afficher le graphique dans Streamlit
    st.plotly_chart(fig)



######################## ################################################################################################################################################################################



def get_top_videos(df_filtered, column, n=10):
    return df_filtered.nlargest(n, column)


######################## ################################################################################################################################################################################


def calculate_average(df_filtered, columns):
    return df_filtered[columns].mean()


######################## ################################################################################################################################################################################


def calculate_correlations(df_filtered, columns):
    return df_filtered[columns].corr()

######################## ################################################################################################################################################################################

def main():
    html_titre = """ 
        <div style="padding: 13px; background-color: #866ef0; border: 5px solid #0d0c0c; border-radius: 10px;">
        <h1 style="color:#0d0c0c; text-align: center; background: linear-gradient(to right, rgba(255, 255, 255, 0), rgba(255, 255, 255, 1));">🤖 ANALYSEUR DE SENTIMENT ET PREDICATEUR DE SUJETS🤖<small><br> Powered by An\'s Learning </h3></h1></h1>
        </div> 
        </div> 
        """
    
    st.markdown(html_titre, unsafe_allow_html = True)

    st.markdown('<p style="text-align: center;font-size:15px;" > <bold><center><h1 style="color:#D3F7F4"> <bold>Analyse des données avec diagramme en chandelier japonais<h1></bold><p>', unsafe_allow_html=True)
    

    # Télécharger un fichier Excel
    uploaded_file = st.file_uploader("Téléchargez un fichier Excel", type=["xlsx", "xls"])

    if uploaded_file:
        # Charger les données
        df = pd.read_excel(uploaded_file)

        # Fixer la colonne de date à "PublishedDate"
        date_column = "PublishedDate"

        # Convertir les dates en datetime pour les widgets de sélection de date
        df[date_column] = pd.to_datetime(df[date_column], errors='coerce', format='%Y-%m-%dT%H:%M:%S.%fZ')

        # Demander à l'utilisateur de choisir une date de début et de fin
        min_date = df[date_column].min()
        max_date = df[date_column].max()

        start_date = st.date_input("Choisissez la date de début", min_date.date())
        end_date = st.date_input("Choisissez la date de fin", max_date.date())

        # Bouton pour créer et afficher les graphiques
        if st.button("Afficher les graphiques"):
            df_filtered = filter_data_by_date(df, date_column, start_date, end_date)

            # Créer et afficher les graphiques pour chaque colonne
            for column in ["Likes", "Views", "Comments", "Categorie", "Periodicite"]:
                create_candlestick_chart(df_filtered, date_column, column, f'Graphique de {column}')

            # Calculer la liste des 10 vidéos avec le plus de commentaires, likes, views sur 6 mois et 3 mois
            six_months_ago = pd.to_datetime(end_date) - timedelta(days=6*30)
            three_months_ago = pd.to_datetime(end_date) - timedelta(days=3*30)

            df_last_6_months = filter_data_by_date(df_filtered, date_column, six_months_ago, end_date)
            df_last_3_months = filter_data_by_date(df_filtered, date_column, three_months_ago, end_date)

            st.write("Top 10 vidéos des 6 derniers mois")
            for column in ["Comments", "Likes", "Views"]:
                st.write(f'Top 10 vidéos par {column}')
                st.write(get_top_videos(df_last_6_months, column))

            st.write("Top 10 vidéos des 3 derniers mois")
            for column in ["Comments", "Likes", "Views"]:
                st.write(f'Top 10 vidéos par {column}')
                st.write(get_top_videos(df_last_3_months, column))

            # Calculer la moyenne des colonnes Likes, Comment, Views, Periodicite sur 6 mois et 3 mois
            avg_6_months = calculate_average(df_last_6_months, ["Likes", "Comments", "Views", "Periodicite"])
            avg_3_months = calculate_average(df_last_3_months, ["Likes", "Comments", "Views", "Periodicite"])

            st.write("Moyenne des 6 derniers mois")
            st.write(avg_6_months)

            st.write("Moyenne des 3 derniers mois")
            st.write(avg_3_months)

            # Calculer et afficher les valeurs de corrélation sur 6 mois et 3 mois
            st.write("Valeurs de corrélation des 6 derniers mois")
            st.write(calculate_correlations(df_last_6_months, ["Likes", "Comments", "Views", "Periodicite"]))

            st.write("Valeurs de corrélation des 3 derniers mois")
            st.write(calculate_correlations(df_last_3_months, ["Likes", "Comments", "Views", "Periodicite"]))

# Exécuter la fonction principale
if __name__ == "__main__":
    main()
