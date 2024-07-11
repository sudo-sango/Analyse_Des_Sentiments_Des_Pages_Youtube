import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import tensorflow as tf
import sentencepiece
import time
import io
import h5py as h5
from transformers import AutoTokenizer, TFCamembertForSequenceClassification, TFCamembertModel


######################## ################################################################################################################################################################################
os.system("lfs install")

os.system("lfs pull")
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
      
        background-image: url('https://cdn.pixabay.com/photo/2021/11/04/06/27/artificial-intelligence-6767502_640.jpg');
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

# Définition des classes
classes = {0: 'négatif', 1: 'neutre', 2: 'positif'}


def load_model_filee():
    model_path = 'a.h5'
    if os.path.exists(model_path):
        try:
            model = load_model(model_path)
            st.success("Modèle trouvé et chargé avec succès.")
            return model
        except Exception as e:
            st.error(f"Erreur lors du chargement du modèle : {e}")
            return None
    else:
        st.error("Le modèle n'a pas été trouvé dans le dossier spécifié.")
        return None
# Fonction pour charger le modèle
#@st.cache_resource



def load_model_fileee():
    chemin = os.path.dirname(os.path.abspath(__file__))
    filenames = os.listdir(chemin)
    filenames = [f for f in filenames if f.endswith('.h5')]
    
    if len(filenames) == 0:
        st.error("Aucun fichier de modèle trouvé dans le répertoire.")
        return None
    
    selected_filename = st.selectbox('Choisissez votre modèle ', filenames, key='model_select')
    model_path = os.path.join(chemin, selected_filename)
    
    # Affichage de la barre de progression
    progress_text = "Chargement du modèle en cours. Veuillez patienter..."
    my_bar = st.progress(0, text=progress_text)
    
    try:
        # Chargement du modèle
        model = tf.keras.models.load_model(model_path, custom_objects={'TFCamembertModel': TFCamembertModel}, compile=False)
        
        # Mise à jour de la barre de progression
        for percent_complete in range(100):
            time.sleep(0.1)
            my_bar.progress(percent_complete + 1, text=progress_text)
        
        # Succès du chargement
        st.success("Modèle chargé avec succès !")
        return model
    
    except Exception as e:
        st.error(f"Erreur lors du chargement du modèle : {str(e)}")
        return None

######################## ################################################################################################################################################################################

# Fonction pour prédire le sentiment d'un Commentaire# Fonction pour prédire le sentiment d'un Commentaire
def predict_sentiment(Comment, model, tokenizer):
    # Encodage du Commentaire avec le tokenizer
    inputs = tokenizer.encode_plus(Comment, add_special_tokens=True, return_tensors='tf', max_length=256, padding='max_length', truncation=True)
    # Prédiction du sentiment avec le modèle
    prediction = model.predict([inputs['input_ids'], inputs['attention_mask']])[0]
    # Récupération de l'indice de la classe prédite
    predicted_class_idx = np.argmax(prediction)
    # Récupération du label de la classe prédite
    predicted_class = classes[predicted_class_idx]
    
    return predicted_class


######################## ################################################################################################################################################################################

# Fonction pour afficher le diagramme
def plot_sentimentss(df):
    sentiment_counts = df['sentiment'].value_counts()
    fig, ax = plt.subplots()
    ax.bar(sentiment_counts.index, sentiment_counts.values, color=['green', 'gray', 'red'])
    ax.set_title('Répartition des sentiments')
    ax.set_xlabel('Sentiments')
    ax.set_ylabel('Nombre de Commentaires')
    # Ajout de la légende avec des valeurs numériques
    for i, v in enumerate(sentiment_counts.values):
        ax.text(i, v+1, str(v), ha='center', fontweight='bold')
    st.pyplot(fig)


def plot_sentiments(df):
    sentiment_counts = df['sentiment'].value_counts()
    fig, ax = plt.subplots(figsize=(6, 2))  # Spécification de la taille de la figure
    ax.bar(sentiment_counts.index, sentiment_counts.values, color=['#6f00ff', '#009dff', '#0a0a0a'])  # Couleurs hexadécimales
    ax.set_title('Répartition des sentiments', fontsize=12, fontweight='bold')
    ax.set_xlabel('Sentiments', fontsize=8)
    ax.set_ylabel('Nombre de Commentaires', fontsize=8)
    
    # Ajout de la légende avec des valeurs numériques
    #for i, v in enumerate(sentiment_counts.values):
    #    ax.text(i, v + 1, str(v), ha='center', fontweight='bold', fontsize=6)
    
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    
    st.pyplot(fig)

#optimise moi cette fonction pour qu'elle soit plus belle, mets les mesures de la figure et que les courleurs mise soit hexadecimal'




######################## ################################################################################################################################################################################


REPO_URL = "https://github.com/sudo-sango/Analyse_Des_Sentiments_Des_Pages_Youtube.git"
REPO_DIR = "Analyse_Des_Sentiments_Des_Pages_Youtube"

def clone_and_pull_lfs(repo_url, repo_dir):
    if not os.path.exists(repo_dir):
        os.system("git lfs install")
        git.Repo.clone_from(repo_url, repo_dir)
        os.chdir(repo_dir)
        os.system("git lfs pull")
    else:
        os.chdir(repo_dir)
        os.system("git lfs pull")



def load_model_file(repo_dir):
    model_dir = os.path.join(repo_dir, "pages")
    filenames = [f for f in os.listdir(model_dir) if f.endswith('.h5')]
    
    if len(filenames) == 0:
        st.error("Aucun fichier de modèle trouvé dans le répertoire.")
        return None
    
    selected_filename = st.selectbox('Choisissez votre modèle ', filenames, key='model_select')
    model_path = os.path.join(model_dir, selected_filename)
    
    progress_text = "Chargement du modèle en cours. Veuillez patienter..."
    my_bar = st.progress(0, text=progress_text)
    
    try:
        model = tf.keras.models.load_model(model_path, custom_objects={'TFCamembertModel': TFCamembertModel}, compile=False)
        
        for percent_complete in range(100):
            time.sleep(0.1)
            my_bar.progress(percent_complete + 1, text=progress_text)
        
        st.success("Modèle chargé avec succès !")
        return model
    
    except Exception as e:
        st.error(f"Erreur lors du chargement du modèle : {str(e)}")
        return None




def main():

    html_titre = """ 
        <div style="padding: 13px; background-color: #866ef0; border: 5px solid #0d0c0c; border-radius: 10px;">
        <h1 style="color:#0d0c0c; text-align: center; background: linear-gradient(to right, rgba(255, 255, 255, 0), rgba(255, 255, 255, 1));">🤖 ANALYSEUR DE SENTIMENT ET PREDICATEUR DE SUJETS🤖<small><br> Powered by An\'s Learning </h3></h1></h1>
        </div> 
        </div> 
        """
    
    st.markdown(html_titre, unsafe_allow_html = True)

    st.markdown('<p style="text-align: center;font-size:15px;" > <bold><center><h1 style="color:#D3F7F4"> <bold>UPLOADER LE FICHIER DONT VOUS VOULEZ AVOIR LA PREDICTION DE SUJET DE VIDEO YOUTUBE<h1></bold><p>', unsafe_allow_html=True)
    

    uploaded_file = st.file_uploader("Choisissez un fichier CSV ou Excel", type=["csv", "xlsx"])

    if st.button("Lancer la prédiction"):
        if uploaded_file is not None:
            file_name = uploaded_file.name
            try:
                df = pd.read_excel(uploaded_file) if file_name.endswith('.xlsx') else pd.read_csv(uploaded_file, encoding='utf-8', errors='ignore')
            except UnicodeDecodeError:
                st.error("Erreur de décodage du fichier. Veuillez vérifier l'encodage.")
                return
            
            st.write(df)
            clone_and_pull_lfs(REPO_URL, REPO_DIR)
            
            with st.spinner('Chargement du modèle...'):
                model = load_model_file(REPO_DIR)
                if model is None:
                    return
                tokenizer = AutoTokenizer.from_pretrained("camembert/camembert-base-ccnet")
            
            with st.spinner('Prédiction des sentiments des Commentaires...'):
                df['sentiment'] = df['Comment'].apply(lambda x: predict_sentiment(x, model, tokenizer))
                plot_sentiments(df)
                
                base_name, ext = os.path.splitext(file_name)
                output_file_name = f"analysis_sentiment_of_videos_{base_name}{ext}"
                output_file_path = os.path.join("Analysis_Sentiment_Of_Videos", output_file_name)
                
                os.makedirs("Analysis_Sentiment_Of_Videos", exist_ok=True)
                df.to_csv(output_file_path, index=False, encoding='utf-8', errors='ignore')
                
                with open(output_file_path, "r", encoding='utf-8', errors='ignore') as f:
                    st.download_button(label="Télécharger les résultats", data=f.read(), file_name=output_file_name, mime='text/csv')

                if st.button("Réinitialiser"):
                    uploaded_file = None

if __name__ == "__main__":
    main()



######################## ################################################################################################################################################################################
