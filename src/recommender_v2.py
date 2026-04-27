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
        Expanded to 8 numerical dimensions for better variety.
        """
        self.library_df = song_library_df
        # Expanded features list
        self.features = ['energy', 'tempo_bpm', 'valence', 'danceability', 'acousticness', 'instrumentalness', 'speechiness', 'liveness']
        self.scaler = MinMaxScaler()
        
        # 1. Numerical KNN Setup
        if not self.library_df.empty:
            # Ensure all required features exist in the DF (or fill with default)
            for f in self.features:
                if f not in self.library_df.columns:
                    # Map common column names or use default
                    if f == 'tempo_bpm' and 'tempo' in self.library_df.columns:
                        self.library_df = self.library_df.rename(columns={'tempo': 'tempo_bpm'})
                    else:
                        self.library_df[f] = 0.5 if f != 'tempo_bpm' else 110.0
            
            lib_data = self.library_df[self.features].fillna(0.5)
            self.library_vectors = self.scaler.fit_transform(lib_data)
            self.nn_model = NearestNeighbors(n_neighbors=20, metric='cosine')
            self.nn_model.fit(self.library_vectors)
            
            # 2. Semantic Setup
            self.semantic_extractor = SemanticFeatureExtractor()
            lib_songs = []
            for _, row in self.library_df.iterrows():
                lib_songs.append(row)
            self.semantic_extractor.fit(lib_songs)
            self.library_semantic_vectors = self.semantic_extractor.transform(lib_songs)

    def get_song_vector(self, song_info):
        """Convert a SongInfo object to a normalized vector."""
        data = {
            'energy': [song_info.energy],
            'tempo_bpm': [song_info.tempo],
            'valence': [song_info.valence],
            'danceability': [song_info.danceability],
            'acousticness': [song_info.acousticness],
            'instrumentalness': [song_info.instrumentalness],
            'speechiness': [song_info.speechiness],
            'liveness': [song_info.liveness]
        }
        df = pd.DataFrame(data)
        return self.scaler.transform(df)

    def recommend(self, seed_songs, k=10):
        """
        Ensemble Recommender with MMR Ranking for high diversity.
        """
        if not seed_songs or self.library_df.empty:
            return []

        # 1. Prepare Seed Vectors
        seed_data = []
        for s in seed_songs:
            seed_data.append({
                'energy': s.energy, 
                'tempo_bpm': s.tempo, 
                'valence': s.valence, 
                'danceability': s.danceability, 
                'acousticness': s.acousticness,
                'instrumentalness': s.instrumentalness,
                'speechiness': s.speechiness,
                'liveness': s.liveness
            })
        seed_df = pd.DataFrame(seed_data)
        seed_vectors = self.scaler.transform(seed_df)
        
        candidate_pool = {} # song_id -> {row, score, reason_data}

        # --- STRATEGY 1: Item-to-Item ---
        for i, s in enumerate(seed_songs):
            vec = seed_vectors[i].reshape(1, -1)
            dist, idx = self.nn_model.kneighbors(vec, n_neighbors=15)
            for d, i_lib in zip(dist[0], idx[0]):
                row = self.library_df.iloc[i_lib]
                sid = f"local_{row['id']}"
                sim = 1 - d
                if sid not in candidate_pool:
                    candidate_pool[sid] = {"row": row, "num_score": sim, "sem_score": 0, "source_seed": s.title}
                else:
                    if sim > candidate_pool[sid]["num_score"]:
                        candidate_pool[sid]["num_score"] = sim
                        candidate_pool[sid]["source_seed"] = s.title

        # --- STRATEGY 2: Semantic TF-IDF ---
        seed_semantic = self.semantic_extractor.transform(seed_songs)
        if seed_semantic is not None:
            sem_sim = cosine_similarity(self.library_semantic_vectors, seed_semantic)
            for i_lib in range(len(self.library_df)):
                max_sim = np.max(sem_sim[i_lib])
                if max_sim > 0.3:
                    row = self.library_df.iloc[i_lib]
                    sid = f"local_{row['id']}"
                    if sid not in candidate_pool:
                        candidate_pool[sid] = {"row": row, "num_score": 0, "sem_score": max_sim, "source_seed": seed_songs[np.argmax(sem_sim[i_lib])].title}
                    else:
                        candidate_pool[sid]["sem_score"] = max_sim

        # 2. Convert to MMR-ready list
        candidates = []
        seed_ids = [str(s.id) for s in seed_songs]
        for sid, data in candidate_pool.items():
            if sid not in seed_ids and str(data['row']['id']) not in seed_ids:
                total_relevance = (data['num_score'] * 0.6) + (data['sem_score'] * 0.4)
                
                row = data['row']
                # Create vector with all 8 features
                vec_data = {
                    'energy': [row.get('energy', 0.5)], 
                    'tempo_bpm': [row.get('tempo_bpm', 110.0)], 
                    'valence': [row.get('valence', 0.5)], 
                    'danceability': [row.get('danceability', 0.5)], 
                    'acousticness': [row.get('acousticness', 0.5)],
                    'instrumentalness': [row.get('instrumentalness', 0.0)],
                    'speechiness': [row.get('speechiness', 0.0)],
                    'liveness': [row.get('liveness', 0.0)]
                }
                vec = self.scaler.transform(pd.DataFrame(vec_data))
                
                candidates.append({
                    "row": row,
                    "relevance": total_relevance,
                    "vector": vec,
                    "num_score": data['num_score'],
                    "sem_score": data['sem_score'],
                    "source_seed": data['source_seed']
                })

        return self._apply_mmr(candidates, seed_vectors, k)

    def recommend_global(self, seed_songs, search_func, estimator_func, k=10):
        """
        Sophisticated RAG: Multi-Query discovery + MMR Ranking.
        """
        if not seed_songs:
            return []

        # 1. ADVANCED MULTI-QUERY RAG
        genres = list(set([s.genre for s in seed_songs if s.genre]))
        artists = list(set([s.artist for s in seed_songs if s.artist]))
        import random

        top_artist = max(set([s.artist for s in seed_songs]), key=artists.count) if artists else ""
        top_genre = random.choice(genres) if genres else "pop"
        wildcard_seed = random.choice(seed_songs)
        
        queries = [top_artist, f"{top_genre} music", f"songs like {wildcard_seed.title} {wildcard_seed.artist}"]
        
        raw_candidates = []
        for q in queries:
            if q:
                raw_candidates.extend(search_func(q, limit=40))

        # 2. Process & Dedup
        candidates = []
        seen_ids = set([str(s.id) for s in seed_songs])
        for item in raw_candidates:
            tid = f"web_{item.get('trackId')}"
            if tid in seen_ids: continue
            seen_ids.add(tid)
                
            f = estimator_func(item.get('trackName', ''), item.get('artistName', ''), item.get('primaryGenreName', ''))
            candidates.append(SongInfo(
                id=tid, title=item.get('trackName', 'Unknown'), artist=item.get('artistName', 'Unknown'),
                album=item.get('collectionName', 'Unknown'), genre=item.get('primaryGenreName', 'Unknown'),
                mood=f['mood'], artwork_url=item.get('artworkUrl100', ''),
                energy=f['energy'], tempo=f['tempo'], valence=f['valence'], 
                danceability=f['danceability'], acousticness=f['acousticness'],
                instrumentalness=f['instrumentalness'], speechiness=f['speechiness'],
                liveness=f['liveness'], preview_url=item.get('previewUrl', '')
            ))

        if not candidates: return []

        # 3. SCORE CANDIDATES
        cand_data_list = []
        for c in candidates:
            d = asdict(c)
            # Standardize column for scaler
            d['tempo_bpm'] = d.get('tempo', 110.0)
            cand_data_list.append(d)
            
        cand_df = pd.DataFrame(cand_data_list)
        cand_vectors = self.scaler.transform(cand_df[self.features].fillna(0.5))

        seed_data_list = []
        for s in seed_songs:
            d = asdict(s)
            d['tempo_bpm'] = d.get('tempo', 110.0)
            seed_data_list.append(d)
        seed_df = pd.DataFrame(seed_data_list)
        seed_vectors = self.scaler.transform(seed_df[self.features].fillna(0.5))

        num_sim_matrix = cosine_similarity(cand_vectors, seed_vectors)
        seed_semantic = self.semantic_extractor.transform(seed_songs)
        cand_semantic = self.semantic_extractor.transform(candidates)
        sem_sim_matrix = cosine_similarity(cand_semantic, seed_semantic) if seed_semantic is not None else np.zeros((len(candidates), len(seed_songs)))

        mmr_candidates = []
        for i, cand in enumerate(candidates):
            max_num = np.max(num_sim_matrix[i])
            max_sem = np.max(sem_sim_matrix[i])
            best_seed_idx = np.argmax(num_sim_matrix[i])
            
            mmr_candidates.append({
                "song_info": cand,
                "relevance": (max_num * 0.6) + (max_sem * 0.4),
                "vector": cand_vectors[i].reshape(1, -1),
                "num_score": max_num,
                "sem_score": max_sem,
                "source_seed": seed_songs[best_seed_idx].title
            })

        return self._apply_mmr(mmr_candidates, seed_vectors, k, is_global=True)

    def _apply_mmr(self, candidates, seed_vectors, k, lambda_param=0.5, is_global=False):
        """
        Maximal Marginal Relevance: Balances relevance to seeds vs diversity from already selected items.
        """
        selected_indices = []
        remaining_indices = list(range(len(candidates)))
        
        while len(selected_indices) < k and remaining_indices:
            best_mmr = -np.inf
            next_selected = -1
            
            for i in remaining_indices:
                relevance = candidates[i]["relevance"]
                
                if not selected_indices:
                    redundancy = 0
                else:
                    selected_vecs = np.vstack([candidates[idx]["vector"] for idx in selected_indices])
                    redundancy = np.max(cosine_similarity(candidates[i]["vector"], selected_vecs))
                
                mmr_score = lambda_param * relevance - (1 - lambda_param) * redundancy
                
                if mmr_score > best_mmr:
                    best_mmr = mmr_score
                    next_selected = i
            
            if next_selected == -1: break
            selected_indices.append(next_selected)
            remaining_indices.remove(next_selected)

        # 4. Generate GRANULAR EXPLANATIONS
        final_recs = []
        for idx in selected_indices:
            c = candidates[idx]
            
            # Extract features for explanation
            if is_global:
                info = c["song_info"]
                f_data = asdict(info)
            else:
                info = c["row"]
                f_data = dict(info)
            
            # Find strongest matching feature among the 8
            # (Note: This is an approximation for the explanation)
            reasons = []
            if c["sem_score"] > c["num_score"] + 0.2:
                reasons.append(f"Thematically similar to **{c['source_seed']}**")
            
            if f_data.get('speechiness', 0) > 0.7:
                reasons.append("Matches your interest in spoken word/ASMR")
            if f_data.get('instrumentalness', 0) > 0.8:
                reasons.append("Matches your preference for instrumental tracks")
            if f_data.get('liveness', 0) > 0.7:
                reasons.append("Feels like a live concert recording")
                
            if not reasons:
                if c["num_score"] > 0.8:
                    reasons.append(f"Perfectly matches the energy of **{c['source_seed']}**")
                else:
                    reasons.append(f"Fits the broader vibe of your **{c['source_seed']}** discovery")
            
            if is_global:
                res = asdict(c["song_info"])
            else:
                res = dict(c["row"])
                
            res['explanation'] = " | ".join(reasons[:2])
            res['ensemble_score'] = c["relevance"]
            final_recs.append(res)
            
        return final_recs

from models import SongInfo # Needed for recommend_global
