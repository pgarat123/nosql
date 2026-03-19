# NoSQL Movie Analytics Project

Ce projet est une plateforme d'analyse de données cinématographiques utilisant deux types de bases de données NoSQL : **MongoDB** (orientée document) et **Neo4j** (orientée graphe). L'application permet de répondre à 30 questions complexes allant de simples statistiques à des analyses de relations entre acteurs et réalisateurs.

---

## Architecture

- **Backend** : FastAPI (Python 3.13)
- **Base de données 1** : MongoDB Atlas (Données brutes des films)
- **Base de données 2** : Neo4j Aura (Relations Acteurs/Réalisateurs/Films)
- **Frontend** : React (Vite + Tailwind CSS)

---

## Installation et lancement

### 1. Prérequis
Avoir un fichier `.env` à la racine avec les accès suivants :
```env
MONGO_URI="ton_uri_mongodb"
DB_NAME=entertainment
COLLECTION_NAME=films

NEO4J_URI=neo4j+s://ton_instance.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=ton_password
NEO4J_DATABASE=neo4j
```

### 2. Lancer le Backend (FastAPI)
Le backend doit être lancé depuis la **racine du projet** pour que les chemins de fichiers et les packages soient correctement détectés.

```bash
# 1. Activer l'environnement virtuel (si besoin)
source venv/bin/activate 

# 2. Définir le chemin de recherche Python et lancer le serveur
PYTHONPATH=. uvicorn MongoDB.main:app --reload
```
> **Note sur le PYTHONPATH** : Le `.` indique à Python que le dossier actuel est la racine des modules. Cela permet à `main.py` de trouver le dossier `MongoDB` comme un package (`from MongoDB.db import ...`).

### 3. Lancer le Frontend (React)
Dans un nouveau terminal :
```bash
cd frontend/nosql-app
npm install  # Si ce n'est pas déjà fait
npm run dev
```
L'interface sera disponible sur `http://localhost:5173`.

---

## Fonctionnement

### Requêtes Hybrides 
Certaines questions (comme la **Question 19**) utilisent une approche hybride :
1. **MongoDB** : On récupère les films d'un utilisateur et on en extrait la liste des co-acteurs.
2. **Neo4j** : On utilise cette liste pour trouver tous les autres films où ces co-acteurs ont joué.
Cette méthode permet de profiter de la rapidité de recherche de texte de Mongo et de la puissance relationnelle de Neo4j.

### Nettoyage des données
Le projet inclut des filtres automatiques pour garantir la qualité des résultats :
- **MongoDB** : Les documents de configuration (`_design`) sont exclus des agrégations via un filtre `$match`.
- **Neo4j** : Les données numériques (revenus, votes) sont converties à la volée avec `toFloat()` dans les requêtes Cypher pour éviter les erreurs de calcul si les données sont stockées en texte.

### Analyse de communauté
Comme la bibliothèque GDS (Graph Data Science) n'est pas toujours disponible sur le cloud, une version simplifiée de la détection de communauté a été implémentée. Elle identifie les "cliques" d'acteurs travaillant fréquemment ensemble (cliques de collaboration).

---

## Structure des fichiers python
- `MongoDB/main.py` : Les endpoints de l'API FastAPI.
- `MongoDB/queries.py` : Fonctions de calculs et agrégations MongoDB.
- `MongoDB/neo4j_queries.py` : Requêtes Cypher pour l'analyse de graphes.
- `MongoDB/db.py` : Connexion à MongoDB Atlas.
- `rebuild_neo4j.py` : Script pour réinitialiser et importer les données dans Neo4j.
- `movies.json` : La source de données (100 films).

---
*Projet réalisé dans le cadre du cours NoSQL - ESIEA 4A.*
