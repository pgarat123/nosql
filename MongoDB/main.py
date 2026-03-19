from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from MongoDB.db import db, collection
from MongoDB.queries import (
    get_year_with_most_films,
    get_films_count_after_year,
    get_average_votes_by_year,
    get_films_per_year,
    get_available_genres,
    get_film_with_highest_revenue,
    get_directors_with_more_than_n_films,
    get_genre_with_highest_average_revenue,
    get_top_3_films_per_decade,
    get_longest_film_per_genre,
    create_high_rated_high_revenue_view,
    calculate_runtime_revenue_correlation,
    get_average_runtime_by_decade
)

from MongoDB.neo4j_queries import (
    get_actor_with_most_films,
    get_actors_who_played_with_anne_hathaway,
    get_actor_with_highest_total_revenue,
    get_average_votes,
    get_most_represented_genre,
    get_films_of_coactors_hybrid,
    get_director_with_most_distinct_actors,
    get_most_connected_films,
    get_top_5_actors_with_most_different_directors,
    recommend_film_for_actor,
    create_influence_relationship,
    get_shortest_path,
    analyze_communities,
    get_films_common_genres_different_directors,
    create_competition_relationship,
    get_frequent_collaborations
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Movie analytics API is running"}

# --- MONGODB ENDPOINTS ---

@app.get("/year-with-most-films")
def year_with_most_films_route():
    return get_year_with_most_films(collection)

@app.get("/films-count-after-year")
def films_count_after_year_route(year: int = 1999):
    return {"year": year, "count": get_films_count_after_year(collection, year)}

@app.get("/average-votes-by-year")
def average_votes_by_year_route(year: int = 2007):
    return {"year": year, "average_votes": get_average_votes_by_year(collection, year)}

@app.get("/films-per-year")
def films_per_year_route():
    return get_films_per_year(collection)

@app.get("/available-genres")
def available_genres_route():
    return get_available_genres(collection)

@app.get("/film-with-highest-revenue")
def film_with_highest_revenue_route():
    return get_film_with_highest_revenue(collection)

@app.get("/directors-more-than-n-films")
def directors_more_than_n_films_route(n: int = 5):
    return get_directors_with_more_than_n_films(collection, n)

@app.get("/genre-with-highest-average-revenue")
def genre_with_highest_average_revenue_route():
    return get_genre_with_highest_average_revenue(collection)

@app.get("/top-3-films-per-decade")
def top_3_films_per_decade_route():
    return get_top_3_films_per_decade(collection)

@app.get("/longest-film-per-genre")
def longest_film_per_genre_route():
    return get_longest_film_per_genre(collection)

@app.get("/high-rated-high-revenue-view")
def high_rated_high_revenue_view_route(metascore_threshold: int = 80, revenue_threshold: int = 50):
    return create_high_rated_high_revenue_view(
        collection,
        db,
        metascore_threshold=metascore_threshold,
        revenue_threshold=revenue_threshold
    )

@app.get("/runtime-revenue-correlation")
def runtime_revenue_correlation_route():
    return calculate_runtime_revenue_correlation(collection)

@app.get("/average-runtime-by-decade")
def average_runtime_by_decade_route():
    return get_average_runtime_by_decade(collection)

# --- NEO4J ENDPOINTS ---

@app.get("/actor-with-most-films")
def actor_with_most_films_route():
    return get_actor_with_most_films()

@app.get("/actors-with-anne-hathaway")
def actors_with_anne_hathaway_route():
    return get_actors_who_played_with_anne_hathaway()

@app.get("/actor-highest-revenue")
def actor_highest_revenue_route():
    return get_actor_with_highest_total_revenue()

@app.get("/average-votes-neo4j")
def average_votes_neo4j_route():
    return get_average_votes()

@app.get("/most-represented-genre")
def most_represented_genre_route():
    return get_most_represented_genre()

@app.get("/films-of-coactors")
def films_of_coactors_route(name: str = "Pierre Garat"):
    return get_films_of_coactors_hybrid(collection, name)

@app.get("/director-most-actors")
def director_most_actors_route():
    return get_director_with_most_distinct_actors()

@app.get("/most-connected-films")
def most_connected_films_route():
    return get_most_connected_films()

@app.get("/top-5-actors-directors")
def top_5_actors_directors_route():
    return get_top_5_actors_with_most_different_directors()

@app.get("/recommend-film")
def recommend_film_route(actor: str = "Christian Bale"):
    return recommend_film_for_actor(actor)

@app.get("/create-influence")
def create_influence_route():
    return create_influence_relationship()

@app.get("/shortest-path")
def shortest_path_route(a1: str = "Tom Hanks", a2: str = "Scarlett Johansson"):
    return get_shortest_path(a1, a2)

@app.get("/analyze-communities")
def analyze_communities_route():
    return analyze_communities()

# --- TRANSVERSAL ENDPOINTS ---

@app.get("/films-common-genres-diff-directors")
def films_common_genres_diff_directors_route():
    return get_films_common_genres_different_directors()

@app.get("/create-competition")
def create_competition_route():
    return create_competition_relationship()

@app.get("/frequent-collaborations")
def frequent_collaborations_route():
    return get_frequent_collaborations()