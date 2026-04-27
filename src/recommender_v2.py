import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler
from dataclasses import asdict

class KNNRecommender:
    def __init__(self, song_library_df):
        """
        Initialize with a library of available songs (the CSV database).
        """
        self.library_df = song_library_df
        self.features = ['energy', 'tempo_bpm', 'valence', 'danceability', 'acousticness']
        self.scaler = MinMaxScaler()
        
        # Prepare the library vectors
        if not self.library_df.empty:
            lib_data = self.library_df[self.features].fillna(0.5)
            self.library_vectors = self.scaler.fit_transform(lib_data)
            self.nn_model = NearestNeighbors(n_neighbors=10, metric='cosine')
            self.nn_model.fit(self.library_vectors)

    def get_song_vector(self, song_info):
        """Convert a SongInfo object to a normalized vector."""
        data = {
            'energy': [song_info.energy],
            'tempo_bpm': [song_info.tempo],
            'valence': [song_info.valence],
            'danceability': [song_info.danceability],
            'acousticness': [song_info.acousticness]
        }
        df = pd.DataFrame(data)
        return self.scaler.transform(df)

    def recommend(self, seed_songs, k=10):
        """
        Recommend songs based on a list of seed SongInfo objects.
        Now with a much larger variety pool (60 neighbors).
        """
        if not seed_songs or self.library_df.empty:
            return []

        # 1. Create a 'Centroid' vector of the seed songs
        seed_vectors = []
        for s in seed_songs:
            data = {
                'energy': [s.energy],
                'tempo_bpm': [s.tempo],
                'valence': [s.valence],
                'danceability': [s.danceability],
                'acousticness': [s.acousticness]
            }
            df = pd.DataFrame(data)
            seed_vectors.append(self.scaler.transform(df))
        
        centroid = np.mean(seed_vectors, axis=0)

        # 2. Find a much larger pool of neighbors (60)
        pool_size = min(60, len(self.library_df))
        distances, indices = self.nn_model.kneighbors(centroid, n_neighbors=pool_size)
        
        # 3. Filter out songs already in the seed list
        seed_ids = [str(s.id) for s in seed_songs]
        candidate_rows = []
        
        for idx in indices[0]:
            row = self.library_df.iloc[idx]
            if str(row['id']) not in seed_ids and f"local_{row['id']}" not in seed_ids:
                candidate_rows.append(row)
        
        # 4. Sample randomly for high variety
        if not candidate_rows:
            return []
        
        import random
        random.shuffle(candidate_rows)
        return candidate_rows[:k]

    def recommend_global(self, seed_songs, search_func, estimator_func, k=10):
        """
        RAG Mode: Describe vibe -> Query Web -> Map Features -> Rank.
        Now with a larger sampling pool (top 25).
        """
        if not seed_songs:
            return []

        # 1. Describe the Vibe
        genres = [s.genre for s in seed_songs if s.genre]
        artists = [s.artist for s in seed_songs if s.artist]
        top_genre = max(set(genres), key=genres.count) if genres else ""
        top_artist = max(set(artists), key=artists.count) if artists else ""
        
        search_query = f"{top_genre} {top_artist}".strip()
        if not search_query:
            search_query = "popular songs"

        # 2. Retrieval (Query iTunes)
        raw_candidates = search_func(search_query, limit=50) # Even larger retrieval
        
        # 3. Map features & Convert to SongInfo
        candidates = []
        for item in raw_candidates:
            tid = f"web_{item.get('trackId')}"
            if tid in [str(s.id) for s in seed_songs]:
                continue
                
            f = estimator_func(item.get('trackName', ''), item.get('artistName', ''), item.get('primaryGenreName', ''))
            candidates.append(asdict(SongInfo(
                id=tid,
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
            )))

        if not candidates:
            return []

        # 4. Rank using Centroid distance
        seed_vectors = []
        for s in seed_songs:
            data = {
                'energy': [s.energy],
                'tempo_bpm': [s.tempo],
                'valence': [s.valence],
                'danceability': [s.danceability],
                'acousticness': [s.acousticness]
            }
            df = pd.DataFrame(data)
            seed_vectors.append(self.scaler.transform(df))
        centroid = np.mean(seed_vectors, axis=0)

        cand_df = pd.DataFrame(candidates)
        if 'tempo' in cand_df.columns:
            cand_df = cand_df.rename(columns={'tempo': 'tempo_bpm'})
            
        cand_data = cand_df[self.features].fillna(0.5)
        cand_vectors = self.scaler.transform(cand_data)

        from sklearn.metrics.pairwise import cosine_similarity
        similarities = cosine_similarity(centroid, cand_vectors)[0]
        
        # 5. Take top 25 and sample k for high variety
        top_pool_indices = np.argsort(similarities)[::-1][:25]
        
        import random
        selected_indices = random.sample(list(top_pool_indices), min(k, len(top_pool_indices)))
        
        top_recs = []
        for idx in selected_indices:
            top_recs.append(candidates[idx])
            
        return top_recs

from models import SongInfo # Needed for recommend_global
