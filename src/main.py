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

    # Starter example profile
    user_prefs = {
        "genre": "pop", 
        "mood": "happy", 
        "energy": 0.8,
        "tempo": 120,
        "valence": 0.8
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\n" + "="*50)
    print(" 🎵  YOUR PERSONALIZED MUSIC RECOMMENDATIONS  🎵 ")
    print("="*50)
    print(f"Target Vibe: {user_prefs['genre'].title()} / {user_prefs['mood'].title()}\n")

    for i, rec in enumerate(recommendations, 1):
        song, score, explanation = rec
        
        print(f"{i}. {song['title'].upper()}")
        print(f"   Artist: {song['artist']}")
        print(f"   Score:  [{score:.2f} / 1.00]")
        print(f"   Reason: {explanation}")
        print("-" * 50)

    print("\nEnjoy your music!\n")


if __name__ == "__main__":
    main()
