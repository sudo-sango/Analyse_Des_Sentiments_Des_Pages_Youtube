import streamlit as st
from googleapiclient.discovery import build
import pandas as pd
import os
#from streamlit_snowfall import snowfall
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
      
        background-image: url('https://media.istockphoto.com/id/2047220331/photo/generate-ai-technology-machine-learning-on-the-big-data-network-brain-data-creative-in-a.jpg?s=2048x2048&w=is&k=20&c=Iji3ku1dOwUkw8ByNajslpjDqt6GjgxdDJ1d6_OKFXY=');
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

# Création du dossier Data s'il n'existe pas
if not os.path.exists('Scrapping_Channel_Informations'):
    os.makedirs('Scrapping_Channel_Informations')
######################## ################################################################################################################################################################################



def get_channel_info(api_key, channel_name):
    youtube = build('youtube', 'v3', developerKey=api_key)

    request = youtube.search().list(
        part='snippet',
        q=channel_name,
        type='channel',
        maxResults=1
    )
    response = request.execute()

    if not response['items']:
        return None

    channel_id = response['items'][0]['id']['channelId']
    channel_title = response['items'][0]['snippet']['title']
    
    request = youtube.channels().list(
        part='statistics',
        id=channel_id
    )
    response = request.execute()

    if not response['items']:
        return None

    stats = response['items'][0]['statistics']
    return {
        'channel_title': channel_title,
        'channel_id': channel_id,
        'video_count': int(stats.get('videoCount', 'N/A')),
        'subscriber_count': int(stats.get('subscriberCount', 'N/A')),
        'view_count': int(stats.get('viewCount', 'N/A'))
    }

def get_upload_playlist_id(youtube, channel_id):
    request = youtube.channels().list(part='contentDetails', id=channel_id)
    response = request.execute()
    
    if not response['items']:
        st.error("Aucune vidéo trouvée pour cette chaîne.")
        return None
    
    playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    return playlist_id


######################## ################################################################################################################################################################################

def get_video_ids(api_key, playlist_id):
    youtube = build('youtube', 'v3', developerKey=api_key)

    video_ids = []
    request = youtube.playlistItems().list(part='contentDetails', playlistId=playlist_id, maxResults=50)
    response = request.execute()
    
    video_ids.extend([item['contentDetails']['videoId'] for item in response['items']])
    
    next_page_token = response.get('nextPageToken')
    while next_page_token:
        request = youtube.playlistItems().list(part='contentDetails', playlistId=playlist_id, maxResults=50, pageToken=next_page_token)
        response = request.execute()
        video_ids.extend([item['contentDetails']['videoId'] for item in response['items']])
        next_page_token = response.get('nextPageToken')
    
    return video_ids

######################## ################################################################################################################################################################################


def get_video_details(api_key, video_ids, channel_title):
    youtube = build('youtube', 'v3', developerKey=api_key)
    all_video_stats = []

    for i in range(0, len(video_ids), 50):
        request = youtube.videos().list(part='snippet,statistics', id=','.join(video_ids[i:i + 50]))
        response = request.execute()

        for video in response['items']:
            video_stats = {
                'Title': video['snippet']['title'],
                'PublishedDate': video['snippet']['publishedAt'],
                'Views': video['statistics'].get('viewCount', 0),
                'Likes': video['statistics'].get('likeCount', 0),
                'FavoriteCount': video['statistics'].get('favoriteCount', 0),
                'Comments': video['statistics'].get('commentCount', 0)
            }
            all_video_stats.append(video_stats)

    df = pd.DataFrame(all_video_stats)
    file_name = f"Scrapping_Channel_Informations/{channel_title}_All_Informations.xlsx"
    df.to_excel(file_name, index=False)

    return file_name


######################## ################################################################################################################################################################################

def main():
    #st.markdown('<p style="text-align: center;font-size:15px;"><bold><center><h1 style="color:#D3F7F4"><bold>Pour commencer entrez le nom de la chaine YouTube dont vous voulez les informations<h1></bold><p>', unsafe_allow_html=True)
    
   

    html_titre = """ 
        <div style="padding: 13px; background-color: #866ef0; border: 5px solid #0d0c0c; border-radius: 10px;">
        <h1 style="color:#0d0c0c; text-align: center; background: linear-gradient(to right, rgba(255, 255, 255, 0), rgba(255, 255, 255, 1));">🤖 ANALYSEUR DE SENTIMENT ET PREDICATEUR DE SUJETS🤖<small><br> Powered by An\'s Learning </h3></h1></h1>
        </div> 
        </div> 
        """
    
    st.markdown(html_titre, unsafe_allow_html = True)

    st.markdown('<p style="text-align: center;font-size:15px;" > <bold><center><h1 style="color:#f2f0f5"> <bold>Pour commencer entrez l\' ID de la video youtube dont vous voulez telecharger les commentaires<h1></bold><p>', unsafe_allow_html=True)
    
    channel_name = st.text_input("Nom de la chaîne YouTube")
    
    api_key = st.secrets['youtube']['api_key']

    if st.button("Obtenir les informations détaillées"):
        if not channel_name or not api_key:
            st.error("Veuillez entrer le nom de la chaîne et la clé API YouTube.")
        else:
            with st.spinner('Recherche des informations de la chaîne...'):
                channel_info = get_channel_info(api_key, channel_name)

                # Progress bar
                progress_text = "Operation in progress. Please wait."
                progress_bar = st.progress(0, text=progress_text)
                
                for percent_complete in range(100):
                    time.sleep(0.001)
                    progress_bar.progress(percent_complete + 1, text=progress_text)

            if channel_info:
                st.write(f"**Nom de la chaîne :** {channel_info['channel_title']}")
                st.write(f"**Nombre de vidéos :** {channel_info['video_count']}")
                st.write(f"**Nombre d'abonnés :** {channel_info['subscriber_count']}")
                st.write(f"**Nombre de vues :** {channel_info['view_count']}")
                st.snow()
            else:
                st.write("La chaîne n'a pas été trouvée ou une erreur s'est produite.")

    if st.button("Rechercher"):
        if not channel_name or not api_key:
            st.error("Veuillez entrer le nom de la chaîne et la clé API YouTube.")
        else:
            channel_info = get_channel_info(api_key, channel_name)
            if channel_info:
                playlist_id = get_upload_playlist_id(build('youtube', 'v3', developerKey=api_key), channel_info['channel_id'])
                video_ids = get_video_ids(api_key, playlist_id)

                # Progress bar
                progress_text = "Operation in progress. Please wait."
                progress_bar = st.progress(0, text=progress_text)
                
                for percent_complete in range(100):
                    time.sleep(0.01)
                    progress_bar.progress(percent_complete + 1, text=progress_text)

                file_name = get_video_details(api_key, video_ids, channel_info['channel_title'])

                # Display the snow effect
                st.snow()

                with open(file_name, "rb") as file:
                    st.download_button(
                        label="Download Excel File",
                        data=file,
                        file_name=file_name,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

if __name__ == "__main__":
    main()
