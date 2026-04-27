import streamlit as st
import pandas as pd
import os
from models import UserProfile, SongInfo, Playlist, list_profiles

# Load song database for autocomplete
@st.cache_data
def load_song_db():
    df = pd.read_csv("data/songs.csv")
    return df

SONG_DB = load_song_db()

def main():
    st.set_page_config(page_title="Music Recommender UI", layout="wide")
    st.title("🎵 Music Recommender & Playlist Manager")

    # 1. Profile Loading / Creation
    if 'profile' not in st.session_state:
        st.session_state.profile = None

    if st.session_state.profile is None:
        st.subheader("Welcome! Please select or create a profile.")
        existing_profiles = list_profiles()
        
        col1, col2 = st.columns(2)
        
        with col1:
            if existing_profiles:
                selected_profile = st.selectbox("Load Profile", [""] + existing_profiles)
                if selected_profile:
                    st.session_state.profile = UserProfile.load(selected_profile)
                    st.rerun()
            else:
                st.info("No profiles found. Create one to get started.")

        with col2:
            new_profile_name = st.text_input("New Profile Name")
            if st.button("Create Profile"):
                if new_profile_name:
                    st.session_state.profile = UserProfile(name=new_profile_name)
                    st.session_state.profile.save()
                    st.success(f"Profile '{new_profile_name}' created!")
                    st.rerun()
                else:
                    st.error("Please enter a name.")
        return

    # Sidebar for Profile Info and Session Management
    profile = st.session_state.profile
    st.sidebar.header(f"👤 {profile.name}")
    if st.sidebar.button("Logout/Switch Profile"):
        st.session_state.profile = None
        st.rerun()

    # Log interaction for model learning
    def log_interaction(action, details):
        profile.user_metadata["interaction_history"].append({
            "action": action,
            "details": details
        })
        profile.save()

    # UI Tabs
    tab1, tab2, tab3 = st.tabs(["Playlists", "Search & Add", "Liked Songs"])

    with tab1:
        st.header("My Playlists")
        new_pl_name = st.text_input("New Playlist Name", key="new_pl")
        if st.button("Create Playlist"):
            if new_pl_name and new_pl_name not in profile.playlists:
                profile.playlists[new_pl_name] = Playlist(name=new_pl_name)
                log_interaction("create_playlist", {"name": new_pl_name})
                st.success(f"Playlist '{new_pl_name}' created!")
                st.rerun()

        if profile.playlists:
            selected_pl = st.selectbox("View Playlist", list(profile.playlists.keys()))
            if selected_pl:
                pl = profile.playlists[selected_pl]
                st.subheader(f"Playlist: {pl.name}")
                if not pl.songs:
                    st.write("No songs in this playlist yet.")
                else:
                    for song in pl.songs:
                        st.write(f"• **{song.title}** by {song.artist} ({song.album if hasattr(song, 'album') else 'N/A'})")
        else:
            st.write("No playlists created yet.")

    with tab2:
        st.header("Search & Add Songs")
        
        search_type = st.radio("Search By", ["Song Title", "Artist", "Album"], horizontal=True)
        query = st.text_input(f"Start typing {search_type}...")

        if query:
            # Simple autocomplete/filtering
            if search_type == "Song Title":
                results = SONG_DB[SONG_DB['title'].str.contains(query, case=False, na=False)]
            elif search_type == "Artist":
                results = SONG_DB[SONG_DB['artist'].str.contains(query, case=False, na=False)]
            else: # Album
                # In current CSV, we don't have 'album', let's simulate or fallback to genre
                if 'album' in SONG_DB.columns:
                    results = SONG_DB[SONG_DB['album'].str.contains(query, case=False, na=False)]
                else:
                    st.warning("Album data not in database yet. Searching Genre as fallback.")
                    results = SONG_DB[SONG_DB['genre'].str.contains(query, case=False, na=False)]

            if not results.empty:
                for _, row in results.iterrows():
                    col_a, col_b, col_c = st.columns([3, 1, 1])
                    song_obj = SongInfo(
                        id=str(row['id']),
                        title=row['title'],
                        artist=row['artist'],
                        album="Unknown", # Placeholder
                        genre=row['genre'],
                        mood=row['mood']
                    )
                    
                    col_a.write(f"**{row['title']}** - {row['artist']} ({row['genre']})")
                    
                    # Improved Add to Playlist logic with explicit button
                    if profile.playlists:
                        with col_b:
                            pl_options = ["Add to..."] + list(profile.playlists.keys())
                            selected_target = st.selectbox(
                                "Playlist", 
                                options=pl_options, 
                                key=f"sel_{row['id']}",
                                label_visibility="collapsed"
                            )
                            if selected_target != "Add to...":
                                if st.button("Confirm", key=f"conf_{row['id']}"):
                                    existing_ids = [s.id for s in profile.playlists[selected_target].songs]
                                    if song_obj.id not in existing_ids:
                                        profile.playlists[selected_target].songs.append(song_obj)
                                        log_interaction("add_to_playlist", {
                                            "playlist": selected_target, 
                                            "song": asdict(song_obj)
                                        })
                                        st.success(f"Added!")
                                        st.rerun()
                                    else:
                                        st.info("Already in!")
                    else:
                        col_b.info("No playlists")

                    if col_c.button("❤️ Like", key=f"like_{row['id']}"):
                        liked_ids = [s.id for s in profile.liked_songs]
                        if song_obj.id not in liked_ids:
                            profile.liked_songs.append(song_obj)
                            log_interaction("like_song", {"song": asdict(song_obj)})
                            st.success("Liked!")
                        else:
                            st.info("Already liked")
            else:
                st.write("No results found.")

    with tab3:
        st.header("Liked Songs")
        if profile.liked_songs:
            for song in profile.liked_songs:
                st.write(f"❤️ **{song.title}** by {song.artist}")
        else:
            st.write("No liked songs yet.")

if __name__ == "__main__":
    from dataclasses import asdict
    main()
