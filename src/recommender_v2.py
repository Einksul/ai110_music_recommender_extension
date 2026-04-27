import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from dataclasses import asdict
from features import SemanticFeatureExtractor

class KNNRecommender:
    def __init__(self, song_library_df):
        """
        Initialize with a library of available songs (the CSV database).
        Now supports Ensemble strategies (K-Means, Item-to-Item, TF-IDF).
        """
        self.library_df = song_library_df
        self.features = ['energy', 'tempo_bpm', 'valence', 'danceability', 'acousticness']
        self.scaler = MinMaxScaler()
        
        # 1. Numerical KNN Setup
        if not self.library_df.empty:
            lib_data = self.library_df[self.features].fillna(0.5)
            self.library_vectors = self.scaler.fit_transform(lib_data)
            self.nn_model = NearestNeighbors(n_neighbors=20, metric='cosine')
            self.nn_model.fit(self.library_vectors)
            
            # 2. Semantic Setup
            self.semantic_extractor = SemanticFeatureExtractor()
            # Convert library rows to something fit-able
            lib_songs = []
            for _, row in self.library_df.iterrows():
                lib_songs.append(row) # Semantic extractor handles dicts
            self.semantic_extractor.fit(lib_songs)
            self.library_semantic_vectors = self.semantic_extractor.transform(lib_songs)

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
        Ensemble Recommender: Item-to-Item + K-Means + TF-IDF.
        """
        if not seed_songs or self.library_df.empty:
            return []

        # Prepare Seed Vectors
        seed_data = []
        for s in seed_songs:
            seed_data.append({
                'energy': s.energy,
                'tempo_bpm': s.tempo,
                'valence': s.valence,
                'danceability': s.danceability,
                'acousticness': s.acousticness
            })
        seed_df = pd.DataFrame(seed_data)
        seed_vectors = self.scaler.transform(seed_df)
        
        candidate_pool = {} # song_id -> {row, score, reasons[]}

        # --- STRATEGY 1: Item-to-Item Similarity ---
        # Find matches for EACH seed song individually
        for i, s in enumerate(seed_songs):
            vec = seed_vectors[i].reshape(1, -1)
            dist, idx = self.nn_model.kneighbors(vec, n_neighbors=5)
            for d, i_lib in zip(dist[0], idx[0]):
                row = self.library_df.iloc[i_lib]
                sid = f"local_{row['id']}"
                if sid not in candidate_pool:
                    candidate_pool[sid] = {"row": row, "score": 1 - d, "reasons": [f"Matches the vibe of **{s.title}**"]}
                else:
                    candidate_pool[sid]["score"] += (1 - d)
                    candidate_pool[sid]["reasons"].append(f"Similar to **{s.title}**")

        # --- STRATEGY 2: Multi-Centroid (K-Means) ---
        if len(seed_songs) >= 3:
            n_clusters = min(3, len(seed_songs) - 1)
            kmeans = KMeans(n_clusters=n_clusters, n_init=10)
            clusters = kmeans.fit_predict(seed_vectors)
            for c_idx in range(n_clusters):
                cluster_centroid = kmeans.cluster_centers_[c_idx].reshape(1, -1)
                dist, idx = self.nn_model.kneighbors(cluster_centroid, n_neighbors=5)
                for d, i_lib in zip(dist[0], idx[0]):
                    row = self.library_df.iloc[i_lib]
                    sid = f"local_{row['id']}"
                    reason = f"Fits your **Cluster #{c_idx + 1}** vibe"
                    if sid not in candidate_pool:
                        candidate_pool[sid] = {"row": row, "score": 1 - d, "reasons": [reason]}
                    else:
                        candidate_pool[sid]["reasons"].append(reason)

        # --- STRATEGY 3: TF-IDF Semantic Matching ---
        seed_semantic = self.semantic_extractor.transform(seed_songs)
        if seed_semantic is not None:
            # Pairwise similarity between all library and all seeds
            sem_sim = cosine_similarity(self.library_semantic_vectors, seed_semantic)
            # Take max similarity to any seed for each library song
            max_sem_sim = np.max(sem_sim, axis=1)
            # Get top 10 semantic matches
            top_sem_idx = np.argsort(max_sem_sim)[-10:]
            for i_lib in top_sem_idx:
                row = self.library_df.iloc[i_lib]
                sid = f"local_{row['id']}"
                score = max_sem_sim[i_lib]
                if score > 0.3: # Only if it's a decent text match
                    reason = "Shared metadata keywords"
                    if sid not in candidate_pool:
                        candidate_pool[sid] = {"row": row, "score": score, "reasons": [reason]}
                    else:
                        candidate_pool[sid]["score"] += score
                        candidate_pool[sid]["reasons"].append(reason)

        # Filter out seeds from results
        seed_ids = [str(s.id) for s in seed_songs]
        final_list = []
        for sid, data in candidate_pool.items():
            if sid not in seed_ids and str(data['row']['id']) not in seed_ids:
                res = dict(data['row'])
                res['explanation'] = " | ".join(list(set(data['reasons']))[:2])
                res['ensemble_score'] = data['score']
                final_list.append(res)

        # Sort by ensemble score and return k
        final_list.sort(key=lambda x: x['ensemble_score'], reverse=True)
        return final_list[:k]

    def recommend_global(self, seed_songs, search_func, estimator_func, k=10):
        """
        Global RAG Ensemble: Item-to-Item + TF-IDF Semantic scoring.
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
        raw_candidates = search_func(search_query, limit=50)
        
        # 3. Process Candidates & Map Features
        candidates = []
        seed_ids = [str(s.id) for s in seed_songs]
        for item in raw_candidates:
            tid = f"web_{item.get('trackId')}"
            if tid in seed_ids:
                continue
                
            f = estimator_func(item.get('trackName', ''), item.get('artistName', ''), item.get('primaryGenreName', ''))
            candidates.append(SongInfo(
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
            ))

        if not candidates:
            return []

        # 4. ENSEMBLE SCORING
        # A) Numerical Similarity (Item-to-Item)
        cand_data = pd.DataFrame([asdict(c) for c in candidates])
        if 'tempo' in cand_data.columns:
            cand_data = cand_data.rename(columns={'tempo': 'tempo_bpm'})
        cand_vectors = self.scaler.transform(cand_data[self.features].fillna(0.5))

        seed_data = pd.DataFrame([asdict(s) for s in seed_songs])
        if 'tempo' in seed_data.columns:
            seed_data = seed_data.rename(columns={'tempo': 'tempo_bpm'})
        seed_vectors = self.scaler.transform(seed_data[self.features].fillna(0.5))

        # Pairwise similarity: rows=candidates, cols=seeds
        num_sim_matrix = cosine_similarity(cand_vectors, seed_vectors)
        # For each candidate, find its best match in history
        max_num_sim = np.max(num_sim_matrix, axis=1)
        best_seed_indices = np.argmax(num_sim_matrix, axis=1)

        # B) Semantic Similarity (TF-IDF)
        seed_semantic = self.semantic_extractor.transform(seed_songs)
        cand_semantic = self.semantic_extractor.transform(candidates)
        max_sem_sim = np.zeros(len(candidates))
        if seed_semantic is not None and cand_semantic is not None:
            sem_sim_matrix = cosine_similarity(cand_semantic, seed_semantic)
            max_sem_sim = np.max(sem_sim_matrix, axis=1)

        # 5. Blend & Rank
        final_recs = []
        for i, cand in enumerate(candidates):
            num_score = max_num_sim[i]
            sem_score = max_sem_sim[i]
            total_score = (num_score * 0.7) + (sem_score * 0.3)
            
            best_seed = seed_songs[best_seed_indices[i]]
            explanation = f"Matches your vibe for **{best_seed.title}**"
            if sem_score > 0.5:
                explanation += " (Strong text match)"
            
            res = asdict(cand)
            res['explanation'] = explanation
            res['ensemble_score'] = total_score
            final_recs.append(res)

        final_recs.sort(key=lambda x: x['ensemble_score'], reverse=True)
        return final_recs[:k]

from models import SongInfo # Needed for recommend_global
