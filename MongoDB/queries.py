import pandas as pd
from scipy import stats
from pymongo.mongo_client import MongoClient


def get_year_with_most_films(collection):
    """
    Récupère l'année où le plus grand nombre de films ont été sortis.
    
    Args:
        collection: Collection MongoDB des films
        
    Returns:
        dict: {'year': int, 'count': int}
    """
    pipeline = [
        {"$group": {"_id": "$year", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 1}
    ]
    result = list(collection.aggregate(pipeline))
    if result:
        return {"year": result[0]["_id"], "count": result[0]["count"]}
    return None


def get_films_count_after_year(collection, year=1999):
    """
    Compte le nombre de films sortis après une année donnée.
    
    Args:
        collection: Collection MongoDB des films
        year: Année de référence (défaut: 1999)
        
    Returns:
        int: Nombre de films
    """
    return collection.count_documents({"year": {"$gt": year}})


def get_average_votes_by_year(collection, year=2007):
    """
    Calcule la moyenne des votes des films sortis une année donnée.
    
    Args:
        collection: Collection MongoDB des films
        year: Année cible (défaut: 2007)
        
    Returns:
        float: Moyenne des votes, ou None si aucun film
    """
    pipeline = [
        {"$match": {"year": year}},
        {"$group": {"_id": None, "avg_votes": {"$avg": "$Votes"}}}
    ]
    result = list(collection.aggregate(pipeline))
    if result:
        return result[0]["avg_votes"]
    return None


def get_films_per_year(collection):
    """
    Récupère le nombre de films pour chaque année.
    
    Args:
        collection: Collection MongoDB des films
        
    Returns:
        list: Liste de dicts {'year': int, 'count': int} triée par année
    """
    pipeline = [
        {"$group": {"_id": "$year", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]
    result = list(collection.aggregate(pipeline))
    return [{"year": doc["_id"], "count": doc["count"]} for doc in result]


def get_available_genres(collection):
    """
    Récupère tous les genres de films disponibles dans la base.
    
    Args:
        collection: Collection MongoDB des films
        
    Returns:
        list: Liste unique des genres, triée
    """
    genres = collection.distinct("genre")
    return sorted([g for g in genres if g])


def get_film_with_highest_revenue(collection):
    """
    Trouve le film qui a généré le plus de revenu.
    
    Args:
        collection: Collection MongoDB des films
        
    Returns:
        dict: Film avec les champs Title, Revenue, year, Director
    """
    pipeline = [
        {"$match": {"Revenue (Millions)": {"$exists": True, "$nin": [None, ""]}}},
        {"$sort": {"Revenue (Millions)": -1}},
        {"$limit": 1},
        {"$project": {
            "Title": "$title",
            "Revenue": "$Revenue (Millions)",
            "year": 1,
            "Director": 1,
            "_id": 0
        }}
    ]
    result = list(collection.aggregate(pipeline))
    return result[0] if result else None


def get_directors_with_more_than_n_films(collection, n=5):
    """
    Récupère les réalisateurs ayant réalisé plus de n films.
    
    Args:
        collection: Collection MongoDB des films
        n: Seuil minimum de films (défaut: 5)
        
    Returns:
        list: Liste de dicts {'director': str, 'film_count': int}
    """
    pipeline = [
        {"$group": {"_id": "$Director", "film_count": {"$sum": 1}}},
        {"$match": {"film_count": {"$gt": n}}},
        {"$sort": {"film_count": -1}},
        {"$project": {"director": "$_id", "film_count": 1, "_id": 0}}
    ]
    return list(collection.aggregate(pipeline))


def get_genre_with_highest_average_revenue(collection):
    """
    Identifie le genre de film qui rapporte en moyenne le plus de revenus.
    
    Args:
        collection: Collection MongoDB des films
        
    Returns:
        dict: {'genre': str, 'avg_revenue': float}
    """
    pipeline = [
        {"$match": {"Revenue (Millions)": {"$exists": True, "$ne": None}}},
        {"$group": {"_id": "$genre", "avg_revenue": {"$avg": "$Revenue (Millions)"}}},
        {"$sort": {"avg_revenue": -1}},
        {"$limit": 1}
    ]
    result = list(collection.aggregate(pipeline))
    if result:
        return {"genre": result[0]["_id"], "avg_revenue": result[0]["avg_revenue"]}
    return None


def get_top_3_films_per_decade(collection):
    """
    Récupère les 3 films les mieux notés (rating) pour chaque décennie.
    
    Args:
        collection: Collection MongoDB des films
        
    Returns:
        dict: {decade_range: [film1, film2, film3], ...}
    """
    pipeline = [
        {"$match": {"rating": {"$exists": True, "$ne": None}}},
        {"$addFields": {"decade": {"$floor": {"$divide": ["$year", 10]}}}},
        {"$sort": {"decade": 1, "rating": -1}},
        {"$group": {
            "_id": "$decade",
            "films": {"$push": {"title": "$title", "rating": "$rating", "year": "$year"}}
        }},
        {"$sort": {"_id": 1}}
    ]
    
    result = list(collection.aggregate(pipeline))
    output = {}
    for doc in result:
        decade_start = int(doc["_id"] * 10)
        decade_end = decade_start + 9
        decade_range = f"{decade_start}-{decade_end}"
        output[decade_range] = doc["films"][:3]
    
    return output


def get_longest_film_per_genre(collection):
    """
    Identifie le film le plus long (Runtime) pour chaque genre.
    
    Args:
        collection: Collection MongoDB des films
        
    Returns:
        list: Liste de dicts {'genre': str, 'film': dict}
    """
    pipeline = [
        {"$match": {"Runtime (Minutes)": {"$exists": True, "$ne": None}}},
        {"$sort": {"genre": 1, "Runtime (Minutes)": -1}},
        {"$group": {
            "_id": "$genre",
            "film": {"$first": {"title": "$title", "runtime": "$Runtime (Minutes)", "year": "$year"}}
        }},
        {"$sort": {"_id": 1}}
    ]
    
    result = list(collection.aggregate(pipeline))
    return [{"genre": doc["_id"], "film": doc["film"]} for doc in result]


def create_high_rated_high_revenue_view(collection, db, metascore_threshold=80, revenue_threshold=50):
    """
    Crée une vue MongoDB affichant les films avec Metascore > seuil et Revenue > seuil.
    
    Args:
        collection: Collection MongoDB des films
        db: Base de données MongoDB
        metascore_threshold: Seuil Metascore (défaut: 80)
        revenue_threshold: Seuil Revenue en millions (défaut: 50M)
        
    Returns:
        list: Documents correspondant aux critères
    """
    query = {
        "Metascore": {"$exists": True, "$gt": metascore_threshold},
        "Revenue (Millions)": {"$exists": True, "$gt": revenue_threshold}
    }
    
    projection = {"title": 1, "year": 1, "Director": 1, "Metascore": 1, "Revenue (Millions)": 1}
    
    result = list(collection.find(query, projection))
    
    try:
        db.command({
            "create": "high_rated_high_revenue_films",
            "viewOn": collection.name,
            "pipeline": [
                {"$match": query},
                {"$project": projection}
            ]
        })
    except Exception:
        pass
    
    return result


def calculate_runtime_revenue_correlation(collection):
    """
    Calcule la corrélation entre la durée des films (Runtime) et leur revenu (Revenue).
    Réalise une analyse statistique complète.
    
    Args:
        collection: Collection MongoDB des films
        
    Returns:
        dict: {
            'correlation': float,
            'p_value': float,
            'r_squared': float,
            'sample_size': int,
            'interpretation': str
        }
    """
    pipeline = [
        {"$match": {
            "Runtime (Minutes)": {"$exists": True, "$ne": None},
            "Revenue (Millions)": {"$exists": True, "$ne": None, "$gt": 0}
        }},
        {"$project": {"Runtime (Minutes)": 1, "Revenue (Millions)": 1}}
    ]
    
    data = list(collection.aggregate(pipeline))
    
    if len(data) < 2:
        return {"error": "Insufficient data for correlation analysis"}
    
    df = pd.DataFrame(data)
    runtime = df["Runtime (Minutes)"].astype(float)
    revenue = df["Revenue (Millions)"].astype(float)
    
    correlation, p_value = stats.pearsonr(runtime, revenue)
    r_squared = correlation ** 2
    
    interpretation = "Strong positive" if correlation > 0.7 else \
                     "Moderate positive" if correlation > 0.4 else \
                     "Weak positive" if correlation > 0.2 else \
                     "Very weak" if correlation >= 0 else \
                     "Negative"
    
    return {
        "correlation": round(correlation, 4),
        "p_value": round(p_value, 6),
        "r_squared": round(r_squared, 4),
        "sample_size": len(data),
        "interpretation": f"{interpretation} correlation"
    }


def get_average_runtime_by_decade(collection):
    """
    Calcule la durée moyenne des films par décennie.
    
    Args:
        collection: Collection MongoDB des films
        
    Returns:
        list: Liste de dicts {'decade': str, 'avg_runtime': float}
    """
    pipeline = [
        {"$match": {"Runtime (Minutes)": {"$exists": True, "$ne": None}}},
        {"$addFields": {"decade": {"$floor": {"$divide": ["$year", 10]}}}},
        {"$group": {
            "_id": "$decade",
            "avg_runtime": {"$avg": "$Runtime (Minutes)"}
        }},
        {"$sort": {"_id": 1}}
    ]
    
    result = list(collection.aggregate(pipeline))
    output = []
    for doc in result:
        decade_start = int(doc["_id"] * 10)
        decade_end = decade_start + 9
        output.append({
            "decade": f"{decade_start}-{decade_end}",
            "avg_runtime": round(doc["avg_runtime"], 2)
        })
    
    return output
