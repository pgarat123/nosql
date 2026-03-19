from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db import db, collection
from queries import (
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

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # en soutenance ok, sinon mets localhost:5173
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Movie analytics API is running"}

@app.get("/year-with-most-films")
def year_with_most_films():
    return get_year_with_most_films(collection)

@app.get("/films-count-after-year")
def films_count_after_year(year: int = 1999):
    return {"year": year, "count": get_films_count_after_year(collection, year)}

@app.get("/average-votes-by-year")
def average_votes_by_year(year: int = 2007):
    return {"year": year, "average_votes": get_average_votes_by_year(collection, year)}

@app.get("/films-per-year")
def films_per_year():
    return get_films_per_year(collection)

@app.get("/available-genres")
def available_genres():
    return get_available_genres(collection)

@app.get("/film-with-highest-revenue")
def film_with_highest_revenue():
    return get_film_with_highest_revenue(collection)

@app.get("/directors-more-than-n-films")
def directors_more_than_n_films(n: int = 5):
    return get_directors_with_more_than_n_films(collection, n)

@app.get("/genre-with-highest-average-revenue")
def genre_with_highest_average_revenue():
    return get_genre_with_highest_average_revenue(collection)

@app.get("/top-3-films-per-decade")
def top_3_films_per_decade():
    return get_top_3_films_per_decade(collection)

@app.get("/longest-film-per-genre")
def longest_film_per_genre():
    return get_longest_film_per_genre(collection)

@app.get("/high-rated-high-revenue-view")
def high_rated_high_revenue_view(metascore_threshold: int = 80, revenue_threshold: int = 50):
    return create_high_rated_high_revenue_view(
        collection,
        db,
        metascore_threshold=metascore_threshold,
        revenue_threshold=revenue_threshold
    )

@app.get("/runtime-revenue-correlation")
def runtime_revenue_correlation():
    return calculate_runtime_revenue_correlation(collection)

@app.get("/average-runtime-by-decade")
def average_runtime_by_decade():
    return get_average_runtime_by_decade(collection)


#TEST AREA
@app.get("/debug-directors")
def debug_directors():
    return list(collection.find({}, {"_id": 0, "Director": 1}).limit(20))

@app.get("/debug-ratings")
def debug_ratings():
    return list(collection.find({}, {"_id": 0, "title": 1, "rating": 1, "year": 1}).limit(20))