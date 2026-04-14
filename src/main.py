"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv") 

    test_profiles = [
        {
            "name": "The High-Energy Classical (Adversarial)",
            "genre": "classical", "mood": "intense", "energy": 0.95, "tempo": 150, "valence": 0.1, "likes_acoustic": False
        },
        {
            "name": "The Acoustic Metalhead (Edge Case)",
            "genre": "metal", "mood": "chill", "energy": 0.2, "tempo": 70, "valence": 0.5, "likes_acoustic": True
        },
        {
            "name": "The Minimalist (Edge Case)",
            "genre": "", "mood": "", "energy": 0.5, "tempo": 100, "valence": 0.5, "likes_acoustic": False
        },
        {
            "name": "The Ultra-Specific Niche",
            "genre": "reggae", "mood": "sad", "energy": 0.3, "tempo": 75, "valence": 0.2, "likes_acoustic": True
        }
    ]

    for profile in test_profiles:
        name = profile.pop("name")
        recommendations = recommend_songs(profile, songs, k=5)

        print("\n" + "="*60)
        print(f" PROFILE: {name} ")
        print("="*60)
        print(f"Params: {profile}\n")

        for i, rec in enumerate(recommendations, 1):
            song, score, explanation = rec
            print(f"{i}. {song['title'].upper()} ({song['genre']} / {song['mood']})")
            print(f"   Score:  [{score:.2f} / 1.00]")
            print(f"   Reason: {explanation}")
            print("-" * 60)


if __name__ == "__main__":
    main()
