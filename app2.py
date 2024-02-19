import joblib
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Get CLIENT_ID and CLIENT_SECRET code from Spotify for Developers
CLIENT_ID = "7de0b8750b9e4fc1b9bc02572011****"
CLIENT_SECRET = "de495b43a406464681f3bc3239d0****"

# Initialize the Spotify client
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def get_song_album_cover_url(song_name, artist_name):
    search_query = f"track:{song_name} artist:{artist_name}"
    results = sp.search(q=search_query, type="track")

    if results and results["tracks"]["items"]:
        track = results["tracks"]["items"][0]
        album_cover_url = track["album"]["images"][0]["url"]
        return album_cover_url
    else:
        return "https://i.postimg.cc/0QNxYz4V/social.png"

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
    recommended_music_posters = []

    # Process distances in batches
    for batch_distances in batch_process_data(distances[1:6]):
        for i in batch_distances:
            artist = music.iloc[i[0]].artist
            recommended_music_posters.append(get_song_album_cover_url(music.iloc[i[0]].song, artist))
            recommended_music_names.append(music.iloc[i[0]].song)

    return recommended_music_names, recommended_music_posters

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

st.header('Music Recommender System')
music = joblib.load(open('df.joblib', 'rb'))
similarity = joblib.load(open('similarity.joblib', 'rb'))

music_list = music['song'].values
selected_movie = st.selectbox(
    "Type or select a song from the dropdown",
    music_list
)

if st.button('Show Recommendation'):
    recommended_music_names, recommended_music_posters = recommend(selected_movie, music, similarity)
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.text(recommended_music_names[0])
        st.image(recommended_music_posters[0])
    with col2:
        st.text(recommended_music_names[1])
        st.image(recommended_music_posters[1])

    with col3:
        st.text(recommended_music_names[2])
        st.image(recommended_music_posters[2])
    with col4:
        st.text(recommended_music_names[3])
        st.image(recommended_music_posters[3])
    with col5:
        st.text(recommended_music_names[4])
        st.image(recommended_music_posters[4])

# Artist Recommender Section
st.header('Songs from the Same Artist Recommender')
selected_artist = st.text_input('Enter artist name:')
if st.button('Show Artist Recommendations'):
    artist_recommendations = artist_recommender(selected_artist, music)
    
    # Create a row layout for artist recommendations with 5 columns
    cols_artist = st.columns(5)
    for i, song_name in enumerate(artist_recommendations):
        cols_artist[i].text(song_name)
        artist_image_url = get_song_album_cover_url(song_name, selected_artist)
        cols_artist[i].image(artist_image_url)
