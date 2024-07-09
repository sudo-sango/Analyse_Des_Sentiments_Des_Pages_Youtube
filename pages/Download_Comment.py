import streamlit as st 
import pandas as pd 
import base64
import io
from googleapiclient.discovery import build 
import streamlit.components.v1 as components
import os
import time


######################## ################################################################################################################################################################################

st.set_page_config(layout="wide")

hide_st_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """

######################## ################################################################################################################################################################################

st.markdown("""
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css">
    """, unsafe_allow_html=True)



######################## ################################################################################################################################################################################

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
      
        background-image: url('https://cdn.pixabay.com/photo/2016/03/26/13/09/laptop-1280536_640.jpg');
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

# Fonction pour télécharger les commentaires 
def download_comments(video_id, api_key):     
    youtube = build('youtube', 'v3', developerKey=api_key)      
    box = [['Name', 'Comment', 'Time', 'Likes', 'Reply Count']]     
    data = youtube.commentThreads().list(part='snippet', videoId=video_id, maxResults='100', textFormat="plainText").execute()     
    for i in data["items"]:         
        name = i["snippet"]['topLevelComment']["snippet"]["authorDisplayName"]         
        comment = i["snippet"]['topLevelComment']["snippet"]["textDisplay"]         
        published_at = i["snippet"]['topLevelComment']["snippet"]['publishedAt']         
        likes = i["snippet"]['topLevelComment']["snippet"]['likeCount']         
        replies = i["snippet"]['totalReplyCount']         
        box.append([name, comment, published_at, likes, replies])         
        totalReplyCount = i["snippet"]['totalReplyCount']         
        if totalReplyCount > 0:             
            parent = i["snippet"]['topLevelComment']["id"]             
            data2 = youtube.comments().list(part='snippet', maxResults='100', parentId=parent, textFormat="plainText").execute()             
            for i in data2["items"]:                 
                name = i["snippet"]["authorDisplayName"]                 
                comment = i["snippet"]["textDisplay"]                 
                published_at = i["snippet"]['publishedAt']                 
                likes = i["snippet"]['likeCount']                 
                replies = ""                 
                box.append([name, comment, published_at, likes, replies])     
    while ("nextPageToken" in data):         
        data = youtube.commentThreads().list(part='snippet', videoId=video_id, pageToken=data["nextPageToken"], maxResults='100', textFormat="plainText").execute()         
        for i in data["items"]:             
            name = i["snippet"]['topLevelComment']["snippet"]["authorDisplayName"]             
            comment = i["snippet"]['topLevelComment']["snippet"]["textDisplay"]             
            published_at = i["snippet"]['topLevelComment']["snippet"]['publishedAt']             
            likes = i["snippet"]['topLevelComment']["snippet"]['likeCount']             
            replies = i["snippet"]['totalReplyCount']             
            box.append([name, comment, published_at, likes, replies])             
            totalReplyCount = i["snippet"]['totalReplyCount']             
            if totalReplyCount > 0:                 
                parent = i["snippet"]['topLevelComment']["id"]                 
                data2 = youtube.comments().list(part='snippet', maxResults='100', parentId=parent, textFormat="plainText").execute()                 
                for i in data2["items"]:                     
                    name = i["snippet"]["authorDisplayName"]                     
                    comment = i["snippet"]["textDisplay"]                     
                    published_at = i["snippet"]['publishedAt']                     
                    likes = i["snippet"]['likeCount']                     
                    replies = ''                     
                    box.append([name, comment, published_at, likes, replies])     
    df_comments = pd.DataFrame({'Name': [i[0] for i in box], 'Comment': [i[1] for i in box], 'Time': [i[2] for i in box], 'Likes': [i[3] for i in box], 'Reply Count': [i[4] for i in box]})  
    
    return df_comments 

######################## ################################################################################################################################################################################


# Fonction pour afficher les informations de la vidéo 
def display_video_info(video_id, api_key):     
    youtube = build('youtube', 'v3', developerKey=api_key)     
    video = youtube.videos().list(part="snippet,statistics", id=video_id).execute()      
    if not video['items']:         
        st.error('Cette vidéo n\'existe pas.')     
    else:         
        video_title = video['items'][0]['snippet']['title']         
        video_views = video['items'][0]['statistics']['viewCount']         
        video_likes = video['items'][0]['statistics']['likeCount']         
        video_comments = video['items'][0]['statistics']['commentCount']          
        st.write(f"Titre de la vidéo : {video_title}")         
        st.write(f"Nombre de vues : {video_views}")         
        st.write(f"Nombre de likes : {video_likes}")         
        st.write(f"Nombre de commentaires : {video_comments}") 
    return video_title


######################## ################################################################################################################################################################################

# Fonction pour filtrer les commentaires
def predictionS(df_comments):
    df_comments['Likes'] = pd.to_numeric(df_comments['Likes'], errors='coerce')
    df_comments['Reply Count'] = pd.to_numeric(df_comments['Reply Count'], errors='coerce')
    df_comments['Likes'] = df_comments['Likes'].fillna(0).astype(int)
    df_comments['Reply Count'] = df_comments['Reply Count'].fillna(0).astype(int)
  
    df_filtered = df_comments[(df_comments['Likes'] > 5) & (df_comments['Reply Count'] > 5)]
    return df_filtered



def predictionaa(df_comments):
    try:
        df_comments['Likes'] = df_comments['Likes'].fillna(0)
        df_comments['Reply Count'] = df_comments['Reply Count'].fillna(0)
        
        df_comments['Likes'] = pd.to_numeric(df_comments['Likes'], errors='coerce').astype(int)
        df_comments['Reply Count'] = pd.to_numeric(df_comments['Reply Count'], errors='coerce').astype(int)
    except Exception as e:
        st.error(f"Erreur lors du remplissage des valeurs NaN et de la conversion en entier : {e}")
        return pd.DataFrame()  # Retourne un DataFrame vide en cas d'erreur

    try:
        df_filtered = df_comments[(df_comments['Likes'] > 5) & (df_comments['Reply Count'] > 5)]
    except Exception as e:
        st.error(f"Erreur lors du filtrage du DataFrame : {e}")
        return pd.DataFrame()  # Retourne un DataFrame vide en cas d'erreur

    return df_filtered
    #le script renvois cette erreur corrige <Erreur lors du remplissage des valeurs NaN et de la conversion en entier : Cannot convert non-finite values (NA or inf) to integer>


def prediction(df_comments):
    # Suppression de la première ligne
    

    try:
        df_comments = df_comments.iloc[1:]
        df_comments['Likes'] = pd.to_numeric(df_comments['Likes'], errors='coerce').fillna(0).astype(int)
        df_comments['Reply Count'] = pd.to_numeric(df_comments['Reply Count'], errors='coerce').fillna(0).astype(int)
    except Exception as e:
        st.error(f"Erreur lors du remplissage des valeurs NaN et de la conversion en entier : {e}")
        return pd.DataFrame()  # Retourne un DataFrame vide en cas d'erreur

    try:
        df_filtered = df_comments[(df_comments['Likes'] > 5) & (df_comments['Reply Count'] > 5)]
    except Exception as e:
        st.error(f"Erreur lors du filtrage du DataFrame : {e}")
        return pd.DataFrame()  # Retourne un DataFrame vide en cas d'erreur

    return df_filtered

#ooptimise moi cette fonction car la premiere chose qu'elle doit faire c'est de supprimer la premiere ligne de df qui est une ligne qui contient [Name,Likes etcc]


def predictionaaaaa(df_comments):
    try:
        df_comments['Likes'] = pd.to_numeric(df_comments['Likes'], errors='coerce')
        
        df_comments['Reply Count'] = pd.to_numeric(df_comments['Reply Count'], errors='coerce')
    except Exception as e:
        st.error(f"Erreur lors de la conversion de 'Likes' en numérique : {e}")
        return pd.DataFrame()  # Retourne un DataFrame vide en cas d'erreur

    #try:
    #    df_comments['Reply Count'] = pd.to_numeric(df_comments['Reply Count'], errors='coerce')
    #except Exception as e:
    #    st.error(f"Erreur lors de la conversion de 'Reply Count' en numérique : {e}")
    #    return pd.DataFrame()  # Retourne un DataFrame vide en cas d'erreur

    try:
        df_comments['Likes'] = df_comments['Likes'].fillna(0).astype(int)
        df_comments['Reply Count'] = df_comments['Reply Count'].fillna(0).astype(int)
    except Exception as e:
        st.error(f"Erreur lors du remplissage des valeurs NaN et de la conversion en entier : {e}")
        return pd.DataFrame()  # Retourne un DataFrame vide en cas d'erreur

    try:
        df_filtered = df_comments[(df_comments['Likes'] > 5) & (df_comments['Reply Count'] > 5)]
    except Exception as e:
        st.error(f"Erreur lors du filtrage du DataFrame : {e}")
        return pd.DataFrame()  # Retourne un DataFrame vide en cas d'erreur

    return df_filtered

######################## ################################################################################################################################################################################

def extract_video_id(link):
  
    start_index = link.rfind("=") + 1
    video_id = link[start_index:]
    return video_id
######################## ################################################################################################################################################################################


#def create_folder(folder_name):
 #   if not os.path.exists(folder_name):
 #       os.makedirs(folder_name)
######################## ################################################################################################################################################################################


def main():

    html_titre = """ 
        <div style="padding: 13px; background-color: #866ef0; border: 5px solid #0d0c0c; border-radius: 10px;">
        <h1 style="color:#0d0c0c; text-align: center; background: linear-gradient(to right, rgba(255, 255, 255, 0), rgba(255, 255, 255, 1));">🤖 ANALYSEUR DE SENTIMENT ET PREDICATEUR DE SUJETS🤖<small><br> Powered by An\'s Learning </h3></h1></h1>
        </div> 
        </div> 
        """
    
    st.markdown(html_titre, unsafe_allow_html = True)

    st.markdown('<p style="text-align: center;font-size:15px;" > <br><br><br><bold><center><h1 style="color:#D3F7F4"> <bold>ENTREZ LE LIEN DE LA VIDEO DONT VOUS VOULEZ TELECHARGER LES COMMENTAIRES<h1></bold><p>', unsafe_allow_html=True)
    
    video_url = st.text_input('Entrez le lien de la vidéo Youtube :')

    video_id = extract_video_id(video_url)  # Fonction pour extraire l'ID de la vidéo à partir de l'URL

    if len(video_id) != 11 and video_id.strip() != '':

        st.error('L\'ID de la vidéo doit comporter 11 caractères.')

    # Bouton submit pour récupérer les informations de la vidéo
    if st.button('Afficher les informations'):
        with st.spinner('Chargement des informations...'):
            api_key = st.secrets['youtube']['api_key']
            display_video_info(video_id, api_key)

            progress_text = "Operation in progress. Please wait."
            my_bar = st.progress(0, text=progress_text)

            for percent_complete in range(25):
                time.sleep(0.1)
                my_bar.progress(percent_complete + 1, text=progress_text)


    # Bouton de téléchargement des commentaires
    if st.button('Télécharger les commentaires'):
        with st.spinner('Téléchargement des commentaires...'):
            api_key = st.secrets['youtube']['api_key']
            df_comments = download_comments(video_id, api_key)
            video_title = display_video_info(video_id, api_key)

            # Créez les dossiers
            #create_folder('a')
            #create_folder('b')

            # Enregistrez les commentaires dans le dossier "comments"
            comments_path = os.path.join('comments', f"{video_title}.xlsx")
            df_comments.to_excel(comments_path, index=False)

            df_filtered = prediction(df_comments)

            # Enregistrez le fichier de prédiction dans le dossier "predict"
            predict_path = os.path.join('predict', f"{video_title}_PREDICTION.xlsx")
            df_filtered.to_excel(predict_path, index=False)

            # Préparation des fichiers pour téléchargement
            output_comments = io.BytesIO()
            writer_comments = pd.ExcelWriter(output_comments, engine='xlsxwriter')
            df_comments.to_excel(writer_comments, sheet_name='Sheet1')
            writer_comments.save()
            output_comments.seek(0)
            excel_file_comments = output_comments.getvalue()

            output_prediction = io.BytesIO()
            writer_prediction = pd.ExcelWriter(output_prediction, engine='xlsxwriter')
            df_filtered.to_excel(writer_prediction, sheet_name='Sheet1')
            writer_prediction.save()
            output_prediction.seek(0)
            excel_file_prediction = output_prediction.getvalue()

            st.markdown(f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{base64.b64encode(excel_file_comments).decode("utf-8")}" download="{video_title}.xlsx">Télécharger les commentaires</a>', unsafe_allow_html=True)
            st.markdown(f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{base64.b64encode(excel_file_prediction).decode("utf-8")}" download="{video_title}_PREDICTION.xlsx">Télécharger le fichier de commentaires predictif</a>', unsafe_allow_html=True)
           

           
            # Barre de progression
            progress_text = "Operation in progress. Please wait."
            my_bar = st.progress(0, text=progress_text)

            for percent_complete in range(100):
                time.sleep(0.1)
                my_bar.progress(percent_complete + 1, text=progress_text)





  



if __name__ == "__main__":
    main()
