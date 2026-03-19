import os
from neo4j import GraphDatabase
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

def get_actor_with_most_films():
    with driver.session(database=NEO4J_DATABASE) as session:
        query = """
        MATCH (a:Actor)-[:ACTED_IN]->(f:Film)
        RETURN a.name AS actor, count(f) AS film_count
        ORDER BY film_count DESC
        LIMIT 1
        """
        result = session.run(query)
        record = result.single()
        return {"actor": record["actor"], "film_count": record["film_count"]} if record else None

def get_actors_who_played_with_anne_hathaway():
    with driver.session(database=NEO4J_DATABASE) as session:
        query = """
        MATCH (anne:Actor {name: "Anne Hathaway"})-[:ACTED_IN]->(f:Film)<-[:ACTED_IN]-(coActor:Actor)
        WHERE coActor <> anne
        RETURN DISTINCT coActor.name AS actor
        ORDER BY actor
        """
        result = session.run(query)
        return [record["actor"] for record in result]

def get_actor_with_highest_total_revenue():
    with driver.session(database=NEO4J_DATABASE) as session:
        query = """
        MATCH (a:Actor)-[:ACTED_IN]->(f:Film)
        WHERE f.revenue IS NOT NULL AND f.revenue <> ""
        RETURN a.name AS actor, sum(toFloat(f.revenue)) AS total_revenue
        ORDER BY total_revenue DESC
        LIMIT 1
        """
        result = session.run(query)
        record = result.single()
        return {"actor": record["actor"], "total_revenue": round(record["total_revenue"], 2)} if record else None

def get_average_votes():
    with driver.session(database=NEO4J_DATABASE) as session:
        query = """
        MATCH (f:Film)
        WHERE f.votes IS NOT NULL AND f.votes <> ""
        RETURN avg(toFloat(f.votes)) AS avg_votes
        """
        result = session.run(query)
        record = result.single()
        return {"average_votes": round(record["avg_votes"], 2)} if record else None

def get_most_represented_genre():
    with driver.session(database=NEO4J_DATABASE) as session:
        # Assuming genres are comma-separated in f.genre
        query = """
        MATCH (f:Film)
        WHERE f.genre IS NOT NULL
        WITH split(f.genre, ',') AS genres
        UNWIND genres AS genre
        RETURN trim(genre) AS genre, count(*) AS count
        ORDER BY count DESC
        LIMIT 1
        """
        result = session.run(query)
        record = result.single()
        return {"genre": record["genre"], "count": record["count"]} if record else None

def get_films_of_coactors_hybrid(mongo_collection, my_name="Pierre Garat"):
    # 1. MongoDB: Trouver les co-acteurs (personnes qui ont joué dans les mêmes films que moi)
    my_movies = list(mongo_collection.find({"Actors": {"$regex": my_name, "$options": "i"}}))
    co_actors = set()
    for movie in my_movies:
        actors_str = movie.get("Actors", "")
        actors_list = [a.strip() for a in actors_str.split(",")]
        for actor in actors_list:
            if actor.lower() != my_name.lower():
                co_actors.add(actor)
    
    if not co_actors:
        return []

    # 2. Neo4j: Trouver les autres films de ces co-acteurs
    with driver.session(database=NEO4J_DATABASE) as session:
        query = """
        MATCH (a:Actor)-[:ACTED_IN]->(f:Film)
        WHERE a.name IN $co_actors
        RETURN DISTINCT f.title AS title
        ORDER BY title
        """
        result = session.run(query, co_actors=list(co_actors))
        return [record["title"] for record in result]

def get_director_with_most_distinct_actors():
    with driver.session(database=NEO4J_DATABASE) as session:
        query = """
        MATCH (d:Director)-[:DIRECTED]->(f:Film)<-[:ACTED_IN]-(a:Actor)
        RETURN d.name AS director, count(DISTINCT a) AS actor_count
        ORDER BY actor_count DESC
        LIMIT 1
        """
        result = session.run(query)
        record = result.single()
        return {"director": record["director"], "actor_count": record["actor_count"]} if record else None

def get_most_connected_films():
    with driver.session(database=NEO4J_DATABASE) as session:
        query = """
        MATCH (f1:Film)<-[:ACTED_IN]-(a:Actor)-[:ACTED_IN]->(f2:Film)
        WHERE f1 <> f2
        RETURN f1.title AS film1, f2.title AS film2, count(a) AS common_actors
        ORDER BY common_actors DESC
        LIMIT 10
        """
        result = session.run(query)
        return [{"film1": record["film1"], "film2": record["film2"], "common_actors": record["common_actors"]} for record in result]

def get_top_5_actors_with_most_different_directors():
    with driver.session(database=NEO4J_DATABASE) as session:
        query = """
        MATCH (a:Actor)-[:ACTED_IN]->(f:Film)<-[:DIRECTED]-(d:Director)
        RETURN a.name AS actor, count(DISTINCT d) AS director_count
        ORDER BY director_count DESC
        LIMIT 5
        """
        result = session.run(query)
        return [{"actor": record["actor"], "director_count": record["director_count"]} for record in result]

def recommend_film_for_actor(actor_name):
    with driver.session(database=NEO4J_DATABASE) as session:
        query = """
        MATCH (a:Actor {name: $name})-[:ACTED_IN]->(f:Film)
        WITH a, split(f.genre, ',') AS genres
        UNWIND genres AS genre
        WITH a, trim(genre) AS fav_genre, count(*) AS genre_count
        ORDER BY genre_count DESC
        LIMIT 3
        WITH a, collect(fav_genre) AS top_genres
        MATCH (rec:Film)
        WHERE NOT (a)-[:ACTED_IN]->(rec)
        AND any(g IN split(rec.genre, ',') WHERE trim(g) IN top_genres)
        RETURN rec.title AS title, rec.genre AS genre, rec.rating AS rating
        ORDER BY rec.rating DESC
        LIMIT 5
        """
        result = session.run(query, name=actor_name)
        return [{"title": record["title"], "genre": record["genre"], "rating": record["rating"]} for record in result]

def create_influence_relationship():
    with driver.session(database=NEO4J_DATABASE) as session:
        # This query creates relationships based on sharing at least 2 common genres
        query = """
        MATCH (d1:Director)-[:DIRECTED]->(f1:Film)
        MATCH (d2:Director)-[:DIRECTED]->(f2:Film)
        WHERE d1 <> d2
        WITH d1, d2, split(f1.genre, ',') AS g1, split(f2.genre, ',') AS g2
        UNWIND g1 AS genre1
        UNWIND g2 AS genre2
        WITH d1, d2, trim(genre1) AS tg1, trim(genre2) AS tg2
        WHERE tg1 = tg2
        WITH d1, d2, count(DISTINCT tg1) AS common_genres
        WHERE common_genres >= 5
        MERGE (d1)-[r:INFLUENCE_PAR]-(d2)
        SET r.common_genres = common_genres
        RETURN count(r) AS rel_count
        """
        result = session.run(query)
        record = result.single()
        return {"relationships_created": record["rel_count"]}

def get_shortest_path(actor1, actor2):
    with driver.session(database=NEO4J_DATABASE) as session:
        query = """
        MATCH (a1:Actor {name: $name1}), (a2:Actor {name: $name2})
        MATCH p = shortestPath((a1)-[:ACTED_IN*]-(a2))
        RETURN p
        """
        result = session.run(query, name1=actor1, name2=actor2)
        record = result.single()
        if record:
            path = record["p"]
            nodes = [node["name"] if "name" in node else node["title"] for node in path.nodes]
            return {"path": nodes, "length": len(nodes) // 2}
        return None

def analyze_communities():
    with driver.session(database=NEO4J_DATABASE) as session:
        # Version simplifiée : Groupes d'acteurs travaillant souvent ensemble
        query = """
        MATCH (a1:Actor)-[:ACTED_IN]->(f:Film)<-[:ACTED_IN]-(a2:Actor)
        WHERE id(a1) < id(a2)
        WITH a1, a2, count(f) AS common_films
        WHERE common_films >= 2
        RETURN a1.name AS actor1, a2.name AS actor2, common_films
        ORDER BY common_films DESC
        LIMIT 10
        """
        result = session.run(query)
        return [{"actor1": record["actor1"], "actor2": record["actor2"], "common_films": record["common_films"]} for record in result]

# Transversal
def get_films_common_genres_different_directors():
    with driver.session(database=NEO4J_DATABASE) as session:
        query = """
        MATCH (f1:Film)<-[:DIRECTED]-(d1:Director)
        MATCH (f2:Film)<-[:DIRECTED]-(d2:Director)
        WHERE f1 <> f2 AND d1 <> d2
        WITH f1, f2, split(f1.genre, ',') AS g1, split(f2.genre, ',') AS g2
        WHERE any(x IN g1 WHERE trim(x) IN g2)
        RETURN f1.title AS film1, f2.title AS film2, f1.genre AS genre
        LIMIT 10
        """
        result = session.run(query)
        return [{"film1": record["film1"], "film2": record["film2"], "genre": record["genre"]} for record in result]

def create_competition_relationship():
    with driver.session(database=NEO4J_DATABASE) as session:
        query = """
        MATCH (d1:Director)-[:DIRECTED]->(f1:Film)
        MATCH (d2:Director)-[:DIRECTED]->(f2:Film)
        WHERE d1 <> d2 AND f1.year = f2.year
        WITH d1, d2, f1.year AS year, split(f1.genre, ',') AS g1, split(f2.genre, ',') AS g2
        WHERE any(x IN g1 WHERE trim(x) IN g2)
        MERGE (d1)-[c:CONCURRENCE {year: year}]-(d2)
        RETURN count(c) AS rel_count
        """
        result = session.run(query)
        record = result.single()
        return {"competition_relationships": record["rel_count"]}

def get_frequent_collaborations():
    with driver.session(database=NEO4J_DATABASE) as session:
        query = """
        MATCH (d:Director)-[:DIRECTED]->(f:Film)<-[:ACTED_IN]-(a:Actor)
        WITH d, a, count(f) AS collab_count, avg(toFloat(f.revenue)) AS avg_revenue, avg(toFloat(f.rating)) AS avg_rating
        WHERE collab_count > 1
        RETURN d.name AS director, a.name AS actor, collab_count, round(avg_revenue, 2) AS avg_revenue, round(avg_rating, 2) AS avg_rating
        ORDER BY collab_count DESC
        LIMIT 10
        """
        result = session.run(query)
        return [dict(record) for record in result]
