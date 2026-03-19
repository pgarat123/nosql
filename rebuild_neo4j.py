import json
import os
from neo4j import GraphDatabase
from dotenv import load_dotenv
from pathlib import Path

# Charger les variables d'environnement
load_dotenv()

URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")
DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

if not all([URI, USERNAME, PASSWORD]):
    print("Erreur: Identifiants Neo4j manquants dans le .env")
    exit(1)

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

def rebuild():
    with driver.session(database=DATABASE) as session:
        print("--- Nettoyage de la base existante ---")
        session.run("MATCH (n) DETACH DELETE n")

        print("--- Importation des Films depuis movies.json ---")
        # On remonte d'un cran si on est dans le dossier MongoDB
        json_path = Path("movies.json")
        if not json_path.exists():
            json_path = Path("../movies.json")

        with open(json_path, 'r', encoding='utf-8') as f:
            for line in f:
                movie = json.loads(line)
                if "title" not in movie: continue
                
                session.run("""
                MERGE (f:Film {id: $id})
                SET f.title = $title,
                    f.year = $year,
                    f.votes = $votes,
                    f.revenue = $revenue,
                    f.rating = $rating,
                    f.director = $director,
                    f.actors = $actors,
                    f.genre = $genre,
                    f.runtime = $runtime
                """, 
                id=str(movie["_id"]),
                title=movie.get("title"),
                year=movie.get("year"),
                votes=movie.get("Votes"),
                revenue=movie.get("Revenue (Millions)"),
                rating=movie.get("rating"),
                director=movie.get("Director"),
                actors=movie.get("Actors"),
                genre=movie.get("genre"),
                runtime=movie.get("Runtime (Minutes)")
                )

        print("--- Création des nœuds Actors et relations ACTED_IN ---")
        session.run("""
        MATCH (f:Film)
        WHERE f.actors IS NOT NULL
        WITH f, split(f.actors, ",") AS actors
        UNWIND actors AS actor
        MERGE (a:Actor {name: trim(actor)})
        MERGE (a)-[:ACTED_IN]->(f)
        """)

        print("--- Création des nœuds Director et relations DIRECTED ---")
        session.run("""
        MATCH (f:Film)
        WHERE f.director IS NOT NULL
        MERGE (d:Director {name: trim(f.director)})
        MERGE (d)-[:DIRECTED]->(f)
        """)

        print("--- Ajout des membres du projet dans 'The Departed' ---")
        members = ["Pierre Garat", "Théo Leste", "Clara Limousin", "Arthur Mennessier", "Acsel Parsy"]
        for member in members:
            session.run("""
            MERGE (a:Actor {name: $name})
            WITH a
            MATCH (f:Film {title: 'The Departed'})
            MERGE (a)-[:ACTED_IN]->(f)
            """, name=member)

        print("--- Création des relations complexes (INFLUENCE_PAR, etc.) ---")
        # On crée quelques relations pour que les questions transversales fonctionnent
        session.run("""
        MATCH (d1:Director)-[:DIRECTED]->(f1:Film)
        MATCH (d2:Director)-[:DIRECTED]->(f2:Film)
        WHERE d1 <> d2 AND f1.year = f2.year
        WITH d1, d2, f1.year AS yr, split(f1.genre, ',') AS g1, split(f2.genre, ',') AS g2
        WHERE any(x IN g1 WHERE trim(x) IN g2)
        MERGE (d1)-[:CONCURRENCE {year: yr}]-(d2)
        """)

        print("\nBase Neo4j reconstruite avec succès !")

if __name__ == "__main__":
    try:
        rebuild()
    finally:
        driver.close()
