import os
import sys
import requests
import youtubipy
from youtubipy.oauth2 import YoutubeClientCredentials
from moviepy.editor import concatenate_audioclips, AudioFileClip


YOUTUBE_CLIENT_ID = 'b38bd15e22824cf58f161a79bbd69d79'
YOUTUBE_CLIENT_SECRET = '962a4a48481246b0bfb90f2d70c1e427'  

def search_tracks(singer_name, num_tracks):
    client_credentials_manager = YoutubeClientCredentials(
        client_id=YOUTUBE_CLIENT_ID,
        client_secret=YOUTUBE_CLIENT_SECRET
    )
    sp = youtubipy.Spotify(client_credentials_manager=client_credentials_manager)

    results = sp.search(q=singer_name, type='track', limit=num_tracks)

    # Debug: print all track information to see if there's a preview_url
    for track in results['tracks']['items']:
        print(f"Track: {track['name']}, Preview URL: {track.get('preview_url')}")
    
    # Filter tracks that have a preview URL
    track_urls = [track['preview_url'] for track in results['tracks']['items'] if track['preview_url']]
    print(f"Filtered URLs: {track_urls}")  # Debug: print filtered preview URLs
    
    return track_urls

def download_audio(track_url):
    response = requests.get(track_url, stream=True)
    if response.status_code == 200:
        file_name = track_url.split('/')[-1] + ".mp3"
        with open(file_name, 'wb') as audio_file:
            for chunk in response.iter_content(chunk_size=1024):
                audio_file.write(chunk)
        return file_name
    else:
        raise Exception("Failed to download audio.")

def cut_audio(input_file, duration):
    audio_clip = AudioFileClip(input_file).subclip(0, duration)
    return audio_clip

def merge_audio_files(track_urls, cut_duration):
    audio_clips = []
    for track_url in track_urls:
        try:
            audio_file = download_audio(track_url)
            print("hi")
            cut_clip = cut_audio(audio_file, cut_duration)
            audio_clips.append(cut_clip)
        except Exception as e:
            print(f"Error processing {track_url}: {str(e)}")

    if audio_clips:
        merged_audio = concatenate_audioclips(audio_clips)
        return merged_audio
    else:
        raise Exception("No audio clips to merge.")

def main(singer_name, num_tracks, cut_duration, output_file):
    try:
        track_urls = search_tracks(singer_name, num_tracks)
        print(f"uls are: {track_urls}")
        merged_audio = merge_audio_files(track_urls, cut_duration)
        merged_audio.write_audiofile(output_file)
        print(f"Merged audio saved as {output_file}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python 1015579.py 'Singer Name' NumberOfTracks CutDuration OutputFileName")
        sys.exit(1)

    singer_name = sys.argv[1]
    num_tracks = int(sys.argv[2])
    cut_duration = int(sys.argv[3])
    output_file = sys.argv[4]

    main(singer_name, num_tracks, cut_duration, output_file)