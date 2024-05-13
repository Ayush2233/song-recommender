import os
import random
import streamlit as st
import pandas as pd
import pickle
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from IPython.display import clear_output

def read_pickle_file(path: str):
    '''

    This function reads pickle files such as scalers, transformers, encoders or models 
    from a previsouly saved file using save_pickle_file.
    
    Input:
        path: the file's location with .pkl extension. i.e encoders/encoder.pkl
    
    Output:
        file: the file read at the directory
    
    '''
    
    with open(path, "rb") as file:
        file_read = pickle.load(file)

    return file_read


def save_pickle_file(path: str, file_name: str, file_to_save):
    '''

    This function saves pickle files such as scalers, transformers, encoders or models 
    to later retrieve them using the read_pickle_file function.
    
    Input:
        path: path to save the file. If the directory doesn't exist, it will create one. i.e 'encoders/'
        file_name: name of the pickle file. Must have .pkl extension. i.e encoder.pkl
        file_to_save: the .pkl file to save
    
    Output:
        It will save the file. If a directory is created it will notify via print.
    
    '''
    # Check whether the specified path exists or not
    isExist = os.path.exists(path)
    if not isExist:
      # Create a new directory because it does not exist
      os.makedirs(path)
      print("The new directory is created!")

    with open(path + file_name, "wb") as file:
        pickle.dump(file_to_save, file)


def searchbyid(id:str)->list:
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=st.secrets["Client_ID"], client_secret=st.secrets["Client_Secret"]))

    try:
        track=sp.track(track_id=id)
    except Exception as e:
            print("Error:", e)
    else:
        track=[]
    
    # clean_result = {    'track_id': track['id'],
    #                     'href': track['href'],
    #                     'track_link': track['external_urls']['spotify'],
    #                     'track_name': track['name'],
    #                     'artist': track['album']['artists'][0]['name'],
    #                     'album_name': track['album']['name'],
    #                     'album_release_year': track['album']['release_date'],
    #                     # 'track_duration': round(result['duration_ms']/1000),
    #                     'album_image': track['album']['images'][1]['url'],
    #     }
    # cleaned_data = []
    # cleaned_data.append(clean_result)
    return track
    

    




def search_song(title: str, artist: str) -> list:
    '''
    Given a song title and artist, this function returns up to 5 posible matches
    from Spotipy, Spotify's API.
    
    Input:
    title: song title as string
    artist: song artist as string
    
    Output:
    List of matches, each match is a dictionary
    
    '''
    
    # Initialize SpotiPy with user credentias
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=st.secrets["Client_ID"], client_secret=st.secrets["Client_Secret"]))

    # Create the query string
    query = ("track:"+title if title != "" else "")+" "+("artist:"+artist if artist != "" else "")

    # Search the requested song and artist if the input is not blank
    if len(query) > 0:
        try:
            raw_results = sp.search(q=query,type="track,artist",limit=5)
            raw_results = raw_results['tracks']['items'] # Parse first two dictionary levels
        except Exception as e:
            print("Error:", e)
    else:
        raw_results = []
    
    # Define result variable
    clean_results = []
    
    # Loop through results and store relevant data in clean_results as list of dictionaries
    for index, result in enumerate(raw_results):
        
        # Store each individual result in temporal dictionary             TO-DO: add -> song poopularity, artist nationality...
        clean_result = {'result_index': index,
                        'track_id': result['id'],
                        'href': result['href'],
                        'track_link': result['external_urls']['spotify'],
                        'track_name': result['name'],
                        'artist': result['album']['artists'][0]['name'],
                        'album_name': result['album']['name'],
                        'album_release_year': result['album']['release_date'],
                        'track_duration': round(result['duration_ms']/1000),
                        'album_image': result['album']['images'][1]['url'],
        }
        
        # Append each dictionary to results list
        clean_results.append(clean_result)
    
    return clean_results


def get_audio_features(track_ids: list) -> pd.DataFrame:
    '''
    Given a list of track IDs, this function returns 
    track audio features such as danceability, energy or tempo
    using Spotipy, Spotify's API.
    
    Input:
    track_ids: list of Spotipy track_ids
    
    Output:
    DataFrame with the track_ids and audio features
    
    '''
    
    # Define loop pauses to avoid API server blockage by overflow
    sleep_time = 30 # seconds of sleep time
    loop_count = 50 # tracks per sleep loop
    
    # Initialize SpotiPy with user credentias
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=st.secrets["Client_ID"], client_secret=st.secrets["Client_Secret"]))

    # Define result variable
    clean_results = []
    
    loop_counter = 0 # counter to track loop
    counter = 0 # counter to track progress
    fail_counter = 0 # counter to track failed matches
    
    # Loop through track_ids to get relevant audio features
    for index, track_id in enumerate(track_ids):
        
        counter += 1 # Add 1 to global counter
        clear_output(wait=True) # Clear print output to update progress
        print('Downloading audio features...', round(((index + 1) / len(track_ids))*100), '%') # Print progress
        
        #try:
            # Get audio features from Spotipy
        api_result = sp.audio_features(track_id)[0]
        #print(sp.audio_features(track_id))

        # Add features to track variable
        track = {'track_id': track_id,
                 'acousticness': api_result['acousticness'],
                 'danceability': api_result['danceability'],
                 'energy': api_result['energy'],
                 'instrumentalness': api_result['instrumentalness'],
                 'key': api_result['key'],
                 'liveness': api_result['liveness'],
                 'loudness': api_result['loudness'],
                 'mode': api_result['mode'],
                 'speechiness': api_result['speechiness'],
                 'tempo': api_result['tempo'],
                 'time_signature': api_result['time_signature'],
                 'valence': api_result['valence'],
        }

        # Append track results to results list
        clean_results.append(track)

        #except Exception as e:
            # If there is an error:
        #    print("Error:", e)
        #    fail_counter += 1
        
        # Sleep to avoid API overflow...
        loop_counter += 1
        if loop_counter >= loop_count:
            loop_counter = 0
            # Generate a random sleep timer based on sleep_time
            random_sleep_timer = random.randint(int(sleep_time*0.5), int(sleep_time*1.5))
            print('Sleeping for', random_sleep_timer, 's...')
            time.sleep(random_sleep_timer) # Sleep
            
    
    clear_output(wait=True)
    print("Audio features download complete.", "Success rate:", round(((counter-fail_counter)/counter)*100), "%")
    print("Succesful downloads:",counter-fail_counter,"Failed downloads:",fail_counter)
    
    # Convert list of dictionaries to DataFrame
    clean_results_df = pd.DataFrame(clean_results)

    return clean_results_df


def is_song_hot(df: pd.DataFrame, track_id: str) -> bool:
    '''
    '''
    
    if len(df[(df['track_id'] == track_id)]['is_hot']) == 0:
        return False 
    else:
        return df[(df['track_id'] == track_id)]['is_hot'][:1].item()


def scale_user_song(X: pd.DataFrame) -> pd.DataFrame:
    '''
    '''
    scaler = read_pickle_file('./scalers/scaler1.pkl')
    
    # Transform dataset
    X_scaled = scaler.transform(X)

    # Convert numpy array into pandas dataframe
    X_scaled_df = pd.DataFrame(X_scaled, columns = X.columns)
    
    return X_scaled_df


def convert_seconds_to_min_seconds(seconds):
    '''
    '''
    
    minutes = seconds // 60
    seconds %= 60
    
    return f"{minutes:02d}:{seconds:02d}"

def recommend_song(track_id: str, min_popularity: int, max_popularity: int) -> list:
    '''
    '''

    # Load data
    df = pd.read_csv('./data/clustered_dataset1.csv')

    # Define selected features
    selected_features = ['energy','danceability','mode', 'speechiness', 
                         'tempo', 'acousticness', 'instrumentalness', 'valence']

    # Load model
    model = read_pickle_file('./clustermodels1/kmeans_8.pkl')

    sp_song_audio_features = get_audio_features([track_id])[selected_features]
    
    # Work around while max retries ban
    # sp_song_audio_features = df[df['track_id'] == '59uQI0PADDKeE6UZDTJEe8'][selected_features]

    sp_song_audio_features_scaled = scale_user_song(sp_song_audio_features)
    
    # Predict cluster of user song
    recommended_cluster = model.predict(sp_song_audio_features_scaled)[:1].item()
    
    # Get a song from database using recommended cluster + is hot / not hot
    recommended_songs = df[(df['cluster'] == recommended_cluster) & 
                           (df['popularity'] >= min_popularity) &
                           (df['popularity'] <= max_popularity) &
                           (df['track_id'] != track_id)
                           ]
    min_results = 5
    # Check if df has a minimum of 5 songs
    if recommended_songs.shape[0] < min_results:
        recommended_songs = recommended_songs.sample(n=recommended_songs.shape[0])
    else:
        recommended_songs = recommended_songs.sample(n=min_results)
    
    return recommended_songs
    
