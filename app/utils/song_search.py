import webbrowser
import requests
import urllib.parse

def find_song_from_lyrics(lyrics):
    """
    Finds a song from partial lyrics using YouTube search.
    Optionally can integrate with Genius API or Spotify for more accuracy.
    """
    if len(lyrics.strip()) < 3:
        print("❌ Please provide a longer lyric snippet.")
        return None

    print("🔎 Searching for the song on YouTube...")
    query = urllib.parse.quote_plus(f"{lyrics} song")
    youtube_search_url = f"https://www.youtube.com/results?search_query={query}"

    # Directly open YouTube search page in browser
    webbrowser.open(youtube_search_url)

    print(f"🎶 Showing results for: {lyrics}")
    print(f"➡️ Opening YouTube: {youtube_search_url}")
    return youtube_search_url
