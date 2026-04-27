import streamlit as st
import pandas as pd
import os
from models import UserProfile, SongInfo, Playlist, list_profiles
from features import LocalFeatureEstimator
from recommender_v2 import KNNRecommender

import requests

# Load song database for autocomplete
@st.cache_data
def load_song_db():
    df = pd.read_csv("data/songs.csv")
    return df

SONG_DB = load_song_db()

def search_itunes(query, limit=10, entity="song"):
    url = f"https://itunes.apple.com/search?term={query}&limit={limit}&entity={entity}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get('results', [])
    except Exception as e:
        st.error(f"Error searching iTunes: {e}")
    return []

def lookup_itunes(id, entity="song"):
    # lookup uses IDs to find all children (e.g., songs in an album)
    url = f"https://itunes.apple.com/lookup?id={id}&entity={entity}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get('results', [])
    except Exception as e:
        st.error(f"Error looking up iTunes: {e}")
    return []

def main():
    st.set_page_config(page_title="Music Recommender UI", layout="wide")
    st.title("🎵 Music Recommender & Playlist Manager")

    # 1. Session State for Exploration and Search Persistence
    if 'view_context' not in st.session_state:
        st.session_state.view_context = None
    if 'search_query' not in st.session_state:
        st.session_state.search_query = ""
    if 'search_type' not in st.session_state:
        st.session_state.search_type = "Song Title"
    if 'local_only' not in st.session_state:
        st.session_state.local_only = False
    
    # Existing Profile Loading logic...
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
    tab1, tab2, tab3, tab4 = st.tabs(["Playlists", "Search & Add", "Liked Songs", "Discovery & Recs"])

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
                col_title, col_del = st.columns([4, 1])
                with col_title:
                    st.subheader(f"Playlist: {pl.name}")
                with col_del:
                    if st.button("🗑️ Delete Playlist", key=f"del_pl_{pl.name}"):
                        del profile.playlists[selected_pl]
                        log_interaction("delete_playlist", {"name": selected_pl})
                        st.success(f"Playlist deleted!")
                        st.rerun()

                if not pl.songs:
                    st.write("No songs in this playlist yet.")
                else:
                    for i, song in enumerate(pl.songs):
                        p_col1, p_col2, p_col3 = st.columns([1, 4, 1])
                        with p_col1:
                            if hasattr(song, 'artwork_url') and song.artwork_url:
                                st.image(song.artwork_url, width=100)
                            else:
                                st.write("🖼️")
                        with p_col2:
                            st.write(f"### {song.title}")
                            st.write(f"by **{song.artist}**  \n*{song.album}*")
                            if hasattr(song, 'preview_url') and song.preview_url:
                                st.audio(song.preview_url, format="audio/mp4")
                        with p_col3:
                            if st.button("❌", key=f"rm_{pl.name}_{i}"):
                                pl.songs.pop(i)
                                log_interaction("remove_from_playlist", {"playlist": pl.name, "song": song.title})
                                st.success("Removed!")
                                st.rerun()
        else:
            st.write("No playlists created yet.")

    with tab2:
        # Exploration View (Artist/Album)
        if st.session_state.view_context:
            ctx = st.session_state.view_context
            if st.button("⬅️ Back to Search"):
                st.session_state.view_context = None
                st.rerun()

            # Fetch data
            raw_data = lookup_itunes(ctx['id'], entity="song")
            if not raw_data:
                st.error("Could not find data for this item.")
            else:
                # Separate header (metadata) from tracks
                header_info = raw_data[0]
                # Filter tracks (ensure wrapperType is 'track')
                tracks = [item for item in raw_data if item.get('wrapperType') == 'track']

                # Display Header with Image
                h_col1, h_col2 = st.columns([2, 5])
                with h_col1:
                    img_url = header_info.get('artworkUrl100') or header_info.get('artworkUrl60')
                    if img_url:
                        big_img = img_url.replace("100x100", "600x600").replace("60x60", "600x600")
                        st.image(big_img, width=300)
                    else:
                        st.write("👤" if ctx['type'] == 'artist' else "📁")
                with h_col2:
                    st.title(ctx['name'])
                    if ctx['type'] == 'album':
                        st.write(f"**Artist:** {header_info.get('artistName')} | **Genre:** {header_info.get('primaryGenreName')}")
                    else:
                        st.write(f"**Genre:** {header_info.get('primaryGenreName', 'Various')}")

                st.divider()

                if tracks:
                    for item in tracks:
                        # Estimate features
                        f = LocalFeatureEstimator.estimate_features(
                            item.get('trackName', ''), 
                            item.get('artistName', ''), 
                            item.get('primaryGenreName', '')
                        )

                        song_obj = SongInfo(
                            id=f"web_{item.get('trackId')}",
                            title=item.get('trackName', 'Unknown'),
                            artist=item.get('artistName', 'Unknown'),
                            album=item.get('collectionName', 'Unknown'),
                            genre=item.get('primaryGenreName', 'Unknown'),
                            mood=f['mood'],
                            artwork_url=item.get('artworkUrl100', ''),
                            energy=f['energy'],
                            tempo=f['tempo'],
                            valence=f['valence'],
                            danceability=f['danceability'],
                            acousticness=f['acousticness']
                        )

                        col_img, col_a, col_b, col_c = st.columns([1, 3, 1, 1])
                        with col_img:
                            if song_obj.artwork_url:
                                img_res = song_obj.artwork_url.replace("100x100", "200x200")
                                st.image(img_res, width=100)
                        with col_a:
                            st.markdown(f"**{song_obj.title}**")
                            if item.get('previewUrl'):
                                st.audio(item.get('previewUrl'), format="audio/mp4")

                        with col_b:
                            if profile.playlists:
                                pl_options = ["Add to..."] + list(profile.playlists.keys())
                                selected_target = st.selectbox("Playlist", options=pl_options, key=f"ctx_sel_{song_obj.id}", label_visibility="collapsed")
                                if selected_target != "Add to...":
                                    if st.button("Confirm", key=f"ctx_conf_{song_obj.id}"):
                                        if song_obj.id not in [s.id for s in profile.playlists[selected_target].songs]:
                                            profile.playlists[selected_target].songs.append(song_obj)
                                            log_interaction("add_to_playlist", {"playlist": selected_target, "song": asdict(song_obj), "source": "Global"})
                                            st.success("Added!")
                                            st.rerun()
                            else: st.info("No playlists")
                        with col_c:
                            if st.button("❤️ Like", key=f"ctx_like_{song_obj.id}"):
                                if song_obj.id not in [s.id for s in profile.liked_songs]:
                                    profile.liked_songs.append(song_obj)
                                    log_interaction("like_song", {"song": asdict(song_obj), "source": "Global"})
                                    st.success("Liked!")
                else:
                    st.write("No tracks found.")
        else:
            # Main Search UI
            st.header("Search & Add Songs")

            col_s1, col_s2 = st.columns([2, 1])
            with col_s1:
                st.session_state.search_type = st.radio(
                    "Search By", 
                    ["Song Title", "Artist", "Album"], 
                    index=["Song Title", "Artist", "Album"].index(st.session_state.search_type),
                    horizontal=True
                )
                st.session_state.search_query = st.text_input(
                    f"Start typing {st.session_state.search_type}...",
                    value=st.session_state.search_query
                )
            with col_s2:
                st.write("") # Spacing
                st.session_state.local_only = st.checkbox(
                    "Search Local Library Only", 
                    value=st.session_state.local_only
                )

            query = st.session_state.search_query
            search_type = st.session_state.search_type
            local_only = st.session_state.local_only

            if query:
                all_results = []

                # 1. Global Search (iTunes) - Now the default
                if not local_only and len(query) > 2:
                    itunes_data = search_itunes(query)
                    for item in itunes_data:
                        # Estimate features
                        f = LocalFeatureEstimator.estimate_features(
                            item.get('trackName', ''), 
                            item.get('artistName', ''), 
                            item.get('primaryGenreName', '')
                        )

                        all_results.append({
                            "source": "Global",
                            "song": SongInfo(
                                id=f"web_{item.get('trackId')}",
                                title=item.get('trackName', 'Unknown'),
                                artist=item.get('artistName', 'Unknown'),
                                album=item.get('collectionName', 'Unknown'),
                                genre=item.get('primaryGenreName', 'Unknown'),
                                mood=f['mood'],
                                artwork_url=item.get('artworkUrl100', ''),
                                energy=f['energy'],
                                tempo=f['tempo'],
                                valence=f['valence'],
                                danceability=f['danceability'],
                                acousticness=f['acousticness'],
                                preview_url=item.get('previewUrl', '')
                                ),

                            "preview": item.get('previewUrl'),
                            "raw": item
                        })

                # 2. Local Search
                if local_only:
                    if search_type == "Song Title":
                        local_results = SONG_DB[SONG_DB['title'].str.contains(query, case=False, na=False)]
                    elif search_type == "Artist":
                        local_results = SONG_DB[SONG_DB['artist'].str.contains(query, case=False, na=False)]
                    else:
                        local_results = SONG_DB[SONG_DB['genre'].str.contains(query, case=False, na=False)]

                    for _, row in local_results.iterrows():
                        all_results.append({
                            "source": "Local",
                            "song": SongInfo(
                                id=f"local_{row['id']}",
                                title=row['title'],
                                artist=row['artist'],
                                album="Library",
                                genre=row['genre'],
                                mood=row['mood'],
                                artwork_url="",
                                energy=row.get('energy', 0.5),
                                tempo=row.get('tempo_bpm', 110.0),
                                valence=row.get('valence', 0.5),
                                danceability=row.get('danceability', 0.5),
                                acousticness=row.get('acousticness', 0.5)
                            ),
                            "preview": None,
                            "raw": None
                        })

                if all_results:
                    for res in all_results:
                        song_obj = res['song']
                        source_label = f"[{res['source']}]"

                        st.divider()
                        col_img, col_a, col_b, col_c = st.columns([1, 3, 1, 1])

                        with col_img:
                            if song_obj.artwork_url:
                                search_img = song_obj.artwork_url.replace("100x100", "300x300")
                                st.image(search_img, width=180)
                            else:
                                st.write("🖼️")

                        with col_a:
                            st.markdown(f"**{song_obj.title}** - {song_obj.artist}  \n*{song_obj.album} | {song_obj.genre}* {source_label}")
                            if res['preview']:
                                st.audio(res['preview'], format="audio/mp4")

                            # Drill-down Buttons
                            if res['source'] == "Global" and res['raw']:
                                sub_col1, sub_col2 = st.columns(2)
                                if sub_col1.button("📁 View Album", key=f"alb_{song_obj.id}"):
                                    st.session_state.view_context = {
                                        "type": "album", 
                                        "id": res['raw'].get('collectionId'),
                                        "name": song_obj.album
                                    }
                                    st.rerun()
                                if sub_col2.button("👤 View Artist", key=f"art_{song_obj.id}"):
                                    st.session_state.view_context = {
                                        "type": "artist", 
                                        "id": res['raw'].get('artistId'),
                                        "name": song_obj.artist
                                    }
                                    st.rerun()

                        # Add to Playlist logic
                        if profile.playlists:
                            with col_b:
                                pl_options = ["Add to..."] + list(profile.playlists.keys())
                                selected_target = st.selectbox(
                                    "Playlist", 
                                    options=pl_options, 
                                    key=f"sel_{song_obj.id}",
                                    label_visibility="collapsed"
                                )
                                if selected_target != "Add to...":
                                    if st.button("Confirm", key=f"conf_{song_obj.id}"):
                                        existing_ids = [s.id for s in profile.playlists[selected_target].songs]
                                        if song_obj.id not in existing_ids:
                                            profile.playlists[selected_target].songs.append(song_obj)
                                            log_interaction("add_to_playlist", {
                                                "playlist": selected_target, 
                                                "song": asdict(song_obj),
                                                "source": res['source']
                                            })
                                            st.success(f"Added!")
                                            st.rerun()
                                        else:
                                            st.info("Already in!")
                        else:
                            col_b.info("No playlists")

                        if col_c.button("❤️ Like", key=f"like_{song_obj.id}"):
                            liked_ids = [s.id for s in profile.liked_songs]
                            if song_obj.id not in liked_ids:
                                profile.liked_songs.append(song_obj)
                                log_interaction("like_song", {"song": asdict(song_obj), "source": res['source']})
                                st.success("Liked!")
                            else:
                                st.info("Already liked")
                else:
                    st.write("No results found.")
    with tab3:
        st.header("Liked Songs")
        if profile.liked_songs:
            for i, song in enumerate(profile.liked_songs):
                l_col1, l_col2, l_col3 = st.columns([1, 4, 1])
                with l_col1:
                    if hasattr(song, 'artwork_url') and song.artwork_url:
                        st.image(song.artwork_url, width=100)
                    else:
                        st.write("🖼️")
                with l_col2:
                    st.write(f"### {song.title}")
                    st.write(f"by **{song.artist}**")
                    if hasattr(song, 'preview_url') and song.preview_url:
                        st.audio(song.preview_url, format="audio/mp4")
                with l_col3:
                    if st.button("❌", key=f"unlike_{i}"):
                        profile.liked_songs.pop(i)
                        log_interaction("unlike_song", {"song": song.title})
                        st.success("Removed!")
                        st.rerun()
        else:
            st.write("No liked songs yet.")

    with tab4:
        st.header("Tailored Recommendations")
        rec_engine = KNNRecommender(SONG_DB)
        
        r_col1, r_col2, r_col3 = st.columns([2, 2, 1])
        with r_col1:
            mode = st.radio("Recommendation Basis", ["Playlist-Specific", "General Discovery"], horizontal=True)
        with r_col2:
            source = st.radio("Discovery Source", ["Local Library", "Global RAG (Internet)"], horizontal=True)
        with r_col3:
            rec_count = st.slider("Count", 5, 50, 10)
        
        seeds = []
        if mode == "Playlist-Specific":
            if profile.playlists:
                target_pl = st.selectbox("Choose Playlist as Vibe Seed", list(profile.playlists.keys()))
                seeds = profile.playlists[target_pl].songs
            else:
                st.warning("Create a playlist first!")
        else: # Discovery
            seeds = profile.liked_songs
            if not seeds:
                st.warning("Like some songs first so we can learn your taste!")

        if seeds:
            if st.button("Generate Recommendations"):
                if source == "Local Library":
                    recs = rec_engine.recommend(seeds, k=rec_count)
                    # Convert DF rows to dicts for consistent display
                    st.session_state.current_recs = [dict(row) for _, row in pd.DataFrame(recs).iterrows()]
                else: # Global RAG
                    recs = rec_engine.recommend_global(
                        seeds, 
                        search_itunes, 
                        LocalFeatureEstimator.estimate_features, 
                        k=rec_count
                    )
                    st.session_state.current_recs = recs
                
                log_interaction("generate_recommendations", {"mode": mode, "source": source, "seed_count": len(seeds), "requested_count": rec_count})

        if 'current_recs' in st.session_state and st.session_state.current_recs:
            st.subheader(f"New {source} Matches:")
            for row in st.session_state.current_recs:
                st.divider()
                col_img, col_info, col_act = st.columns([1, 3, 2])
                
                # Normalize song_id and object for display
                is_web = str(row.get('id', '')).startswith('web_')
                song_id = row.get('id') if is_web else f"local_{row.get('id')}"
                artwork = row.get('artwork_url', "")
                
                with col_img:
                    if artwork:
                        st.image(artwork, width=100)
                    else:
                        st.markdown("### 🎵")
                
                with col_info:
                    st.markdown(f"**{row['title']}** by {row['artist']}  \n*Vibe: {row['genre']} ({row['mood']})*")
                    # Play preview for recommendations
                    purl = row.get('preview_url')
                    if purl:
                        st.audio(purl, format="audio/mp4")

                with col_act:
                    # Explanatory Popover
                    with st.popover("ℹ️ Why this?"):
                        st.write(row.get('explanation', "Matches your recent listening vibe!"))
                        st.caption(f"Features: E:{row.get('energy'):.1f} | T:{row.get('tempo'):.0f} | V:{row.get('valence'):.1f}")

                    rating = st.feedback("stars", key=f"rate_{song_id}")
                    if rating is not None:
                        real_rating = rating + 1
                        log_interaction("rate_recommendation", {"song": row['title'], "rating": real_rating})
                        
                        # DYNAMIC REACTION: 
                        # If user gives 5 stars, temporarily add this song to seeds to influence next generation
                        if real_rating == 5:
                            st.toast(f"Model tuned! Finding more like '{row['title']}'...")
                            new_seed = SongInfo(
                                id=str(song_id),
                                title=row['title'],
                                artist=row['artist'],
                                album=row.get('album', 'Unknown'),
                                genre=row['genre'],
                                mood=row['mood'],
                                artwork_url=artwork,
                                energy=row.get('energy', 0.5),
                                tempo=row.get('tempo', row.get('tempo_bpm', 110.0)),
                                valence=row.get('valence', 0.5),
                                danceability=row.get('danceability', 0.5),
                                acousticness=row.get('acousticness', 0.5)
                            )
                            # Add to liked_songs for the session to shift the centroid
                            if new_seed.id not in [s.id for s in profile.liked_songs]:
                                profile.liked_songs.append(new_seed)
                        
                        st.success("Feedback saved!")

if __name__ == "__main__":
    from dataclasses import asdict
    main()
