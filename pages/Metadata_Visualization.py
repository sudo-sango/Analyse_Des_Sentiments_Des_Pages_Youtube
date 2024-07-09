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
def traitement(df_file):
    # Convertir les colonnes en entier
    df_file['Likes'] = pd.to_numeric(df_file['Likes'], errors='coerce')
    df_file['Comments'] = pd.to_numeric(df_file['Comments'], errors='coerce')
    df_file['Views'] = pd.to_numeric(df_file['Views'], errors='coerce')

    df_file['Likes'] = df_file['Likes'].fillna(0).astype(int)
    df_file['Comments'] = df_file['Comments'].fillna(0).astype(int)
    df_file['Views'] = df_file['Views'].fillna(0).astype(int)
  
        
    # Convertir la colonne PublishedDate en format datetime
    df_file["PublishedDate"] = pd.to_datetime(df_file["PublishedDate"])

    # Supprimer les informations de fuseau horaire des objets datetime
    df_file["PublishedDate"] = df_file["PublishedDate"].dt.tz_localize(None)


    # Filtrer les lignes avec des dates invalides (NaT)
    #df_file = df_file.dropna(subset=["PublishedDate"])
    
    return df_file

######################## ################################################################################################################################################################################
def main():
    # Télécharger un fichier Excel
    uploaded_file = st.file_uploader("Téléchargez un fichier Excel", type=["xlsx", "xls"])

    if uploaded_file:
        # Charger les données
        df_file = pd.read_excel(uploaded_file)

        # Traiter les données
        df = traitement(df_file)

        # Fixer la colonne de date à "PublishedDate"
        date_column = "PublishedDate"

        # Demander à l'utilisateur de choisir une date de début et de fin
        min_date = df[date_column].min()
        max_date = df[date_column].max()

        start_date = st.date_input("Choisissez la date de début", min_date.date())
        end_date = st.date_input("Choisissez la date de fin", max_date.date())

        # Bouton pour créer et afficher les graphiques
        if st.button("Afficher les graphiques"):
            df_filtered = filter_data_by_date(df, date_column, start_date, end_date)

            # Liste des colonnes à utiliser pour les opérations
            columns_to_use = ["Likes", "Views", "Comments", "Categorie", "Periodicite"]

            # Créer et afficher les graphiques pour chaque colonne disponible
            for column in columns_to_use:
                if column in df_filtered.columns:
                    create_candlestick_chart(df_filtered, date_column, column, f'Graphique de {column}')
                else:
                    st.success(f"Aucune donnée disponible pour '{column}' dans le dataset actuel.")

            # Calculer et afficher les top 10 vidéos par Likes, Comments, Views
            for period_label, period_df in [("6 derniers mois", df_filtered), ("3 derniers mois", df_filtered)]:
                if "Comments" in period_df.columns:
                    st.write(f"Top 10 vidéos des {period_label}")
                    st.write(f'Top 10 vidéos par Comments')
                    st.write(get_top_videos(period_df, "Comments"))
                else:
                    st.success(f"Aucune donnée disponible pour 'Comments' dans les {period_label}.")

                if "Likes" in period_df.columns:
                    st.write(f"Top 10 vidéos des {period_label}")
                    st.write(f'Top 10 vidéos par Likes')
                    st.write(get_top_videos(period_df, "Likes"))
                else:
                    st.success(f"Aucune donnée disponible pour 'Likes' dans les {period_label}.")

                if "Views" in period_df.columns:
                    st.write(f"Top 10 vidéos des {period_label}")
                    st.write(f'Top 10 vidéos par Views')
                    st.write(get_top_videos(period_df, "Views"))
                else:
                    st.success(f"Aucune donnée disponible pour 'Views' dans les {period_label}.")

            # Calculer et afficher les moyennes sur 6 mois et 3 mois
            for period_label, period_df in [("6 derniers mois", df_filtered), ("3 derniers mois", df_filtered)]:
                columns_to_average = ["Likes", "Comments", "Views", "Periodicite"]
                for column in columns_to_average:
                    if column in period_df.columns:
                        avg_data = calculate_average(period_df, [column])
                        st.write(f"Moyenne des {period_label} par {column}")
                        st.write(avg_data)
                    else:
                        st.success(f"Aucune donnée disponible pour '{column}' dans les {period_label}.")

            # Calculer et afficher les corrélations sur 6 mois et 3 mois
            for period_label, period_df in [("6 derniers mois", df_filtered), ("3 derniers mois", df_filtered)]:
                columns_to_correlate = ["Likes", "Comments", "Views", "Periodicite"]
                if all(column in period_df.columns for column in columns_to_correlate):
                    st.write(f"Valeurs de corrélation des {period_label}")
                    st.write(calculate_correlations(period_df, columns_to_correlate))
                else:
                    #st.write(f"Les colonnes nécessaires pour calculer la corrélation ne sont pas toutes présentes dans les {period_label}.")
                    st.success(f"Les colonnes nécessaires pour calculer la corrélation ne sont pas toutes présentes dans les {period_label}.")

# Exécuter la fonction principale
if __name__ == "__main__":
    main()


