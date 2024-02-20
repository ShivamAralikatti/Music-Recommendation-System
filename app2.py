import joblib
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Get CLIENT_ID and CLIENT_SECRET from Spotify for Developers
CLIENT_ID = "7de0b8750b9e4fc1b9bc025720******"
CLIENT_SECRET = "de495b43a406464681f3bc3239******"

# Initialize the Spotify client
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def get_song_album_cover_url(song_name, artist_name):
    search_query = f"track:{song_name} artist:{artist_name}"
    results = sp.search(q=search_query, type="track")

    if results and results["tracks"]["items"]:
        track = results["tracks"]["items"][0]
        album_cover_url = track["album"]["images"][0]["url"]
        spotify_url = track["external_urls"]["spotify"]
        return album_cover_url, spotify_url
    else:
        return "https://i.postimg.cc/0QNxYz4V/social.png", None


def batch_process_data(data, batch_size=100):
    """
    Process data in batches to reduce memory usage.
    """
    for i in range(0, len(data), batch_size):
        yield data[i:i+batch_size]

def recommend(song, music, similarity):
    index = music[music['song'] == song].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_music_names = []
    recommended_music_urls = []

    for batch_distances in batch_process_data(distances[1:6]):
        for i in batch_distances:
            artist = music.iloc[i[0]].artist
            recommended_music_names.append(music.iloc[i[0]].song)
            recommended_music_urls.append(get_song_album_cover_url(music.iloc[i[0]].song, artist))

    return recommended_music_names, recommended_music_urls

# Songs from the same artist recommender
def artist_recommender(artist_name, music_df):
    """
    Recommends songs from the same artist.
    
    Parameters:
        artist_name (str): The name of the artist.
        music_df (pd.DataFrame): The DataFrame containing music data.
    
    Returns:
        list: A list of recommended songs from the same artist.
    """
    # Filter the DataFrame to get songs by the specified artist
    artist_df = music_df[music_df['artist'] == artist_name].head(5)
    
    # Get the list of recommended songs by the same artist
    songs_by_artist = artist_df['song'].tolist()
    
    return songs_by_artist

# Function to create clickable links
def create_spotify_link(name, artist):
    search_query = f"track:{name} artist:{artist}"
    results = sp.search(q=search_query, type="track")
    if results and results["tracks"]["items"]:
        track = results["tracks"]["items"][0]
        spotify_url = track["external_urls"]["spotify"]
        return f'<a href="{spotify_url}" target="_blank">{name}</a>'
    else:
        return name

st.header('Music Recommender System')
music = joblib.load(open('df.joblib', 'rb'))
similarity = joblib.load(open('similarity.joblib', 'rb'))

music_list = music['song'].values
selected_music = st.selectbox(
    "Type or select a song from the dropdown",
    music_list
)

if st.button('Show Recommendation'):
    recommended_music_names, recommended_music_urls = recommend(selected_music, music, similarity)
    col1, col2, col3, col4, col5 = st.columns(5)
    for i, name in enumerate(recommended_music_names):
        with col1 if i == 0 else col2 if i == 1 else col3 if i == 2 else col4 if i == 3 else col5:
            st.markdown(create_spotify_link(name, selected_music), unsafe_allow_html=True)
            st.image(recommended_music_urls[i][0])


# Modify the artist recommendation display
st.header('Songs from the Same Artist Recommender')
selected_artist = st.selectbox('Select an artist for recommendations', music['artist'].unique())
if st.button('Show Artist Recommendations'):
    artist_recommendations = artist_recommender(selected_artist, music)
    
    # Create a row layout for artist recommendations with 5 columns
    cols_artist = st.columns(5)
    for i, song_name in enumerate(artist_recommendations):
        cols_artist[i].markdown(create_spotify_link(song_name, selected_artist), unsafe_allow_html=True)
        artist_image_url = get_song_album_cover_url(song_name, selected_artist)[0]
        cols_artist[i].image(artist_image_url)
