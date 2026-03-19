import './App.css'
import { useState } from 'react'

function App() {
  const [result, setResult] = useState("Clique sur un bouton pour afficher un résultat.")
  const [loading, setLoading] = useState(false)
  const [title, setTitle] = useState("Résultat")

  const btnStyle =
    "border border-white/20 rounded-xl p-3 bg-gray-800 hover:bg-gray-700 transition-all duration-200 text-center flex items-center justify-center min-h-[70px] text-xs"

  const callApi = async (endpoint, label) => {
    try {
      setLoading(true)
      setTitle(label)

      const response = await fetch(`http://127.0.0.1:8000${endpoint}`)
      const data = await response.json()

      console.log("API RESPONSE:", data)
      setResult(JSON.stringify(data, null, 2))
    } catch (error) {
      setResult(`Erreur lors de l'appel au backend : ${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-gray-800 min-h-screen w-full text-white font-sans">
      <div className="grid grid-cols-3 w-full h-20 border-b border-white/20 place-items-center px-4 bg-gray-900 sticky top-0 z-10">
        <h1 className="font-semibold text-2xl">No-SQL Analytics</h1>
        <h2 className="col-span-2 text-sm text-center text-gray-400">
          Acsel PARSY, Pierre GARAT, Arthur MENNESSIER, Théo LESTE, Clara LIMOUSIN
        </h2>
      </div>

      <div className="p-6 bg-gray-900 min-h-screen">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="space-y-6">
            <section>
              <h2 className="text-xl font-bold mb-4 text-green-400 border-b border-green-400/30 pb-2">MongoDB Queries</h2>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                <button className={btnStyle} onClick={() => callApi('/year-with-most-films', 'Year with the most release')}>
                  Year with most release
                </button>
                <button className={btnStyle} onClick={() => callApi('/films-count-after-year?year=1999', 'Films after 1999')}>
                  Films after 1999
                </button>
                <button className={btnStyle} onClick={() => callApi('/average-votes-by-year?year=2007', 'Votes mean 2007')}>
                  Avg votes 2007
                </button>
                <button className={btnStyle} onClick={() => callApi('/films-per-year', 'Histogram data')}>
                  Films per year
                </button>
                <button className={btnStyle} onClick={() => callApi('/available-genres', 'Genres')}>
                  All Genres
                </button>
                <button className={btnStyle} onClick={() => callApi('/film-with-highest-revenue', 'Top revenue movie')}>
                  Highest revenue
                </button>
                <button className={btnStyle} onClick={() => callApi('/directors-more-than-n-films?n=2', 'Directors (2+ films)')}>
                  Directors (2+ films)
                </button>
                <button className={btnStyle} onClick={() => callApi('/genre-with-highest-average-revenue', 'Best genre')}>
                  Best genre (revenue)
                </button>
                <button className={btnStyle} onClick={() => callApi('/top-3-films-per-decade', 'Top 3 by decade')}>
                  Top 3 per decade
                </button>
                <button className={btnStyle} onClick={() => callApi('/longest-film-per-genre', 'Longest films')}>
                  Longest per genre
                </button>
                <button className={btnStyle} onClick={() => callApi('/high-rated-high-revenue-view', 'Mongo view')}>
                  High rated view
                </button>
                <button className={btnStyle} onClick={() => callApi('/runtime-revenue-correlation', 'Correlation')}>
                  Runtime/Rev Corr
                </button>
                <button className={btnStyle} onClick={() => callApi('/average-runtime-by-decade', 'Runtime evolution')}>
                  Avg Runtime/Decade
                </button>
              </div>
            </section>

            <section>
              <h2 className="text-xl font-bold mb-4 text-blue-400 border-b border-blue-400/30 pb-2">Neo4j Queries</h2>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                <button className={btnStyle} onClick={() => callApi('/actor-with-most-films', 'Actor with most films')}>
                  Actor most films
                </button>
                <button className={btnStyle} onClick={() => callApi('/actors-with-anne-hathaway', 'Played with Anne Hathaway')}>
                  Anne Hathaway co-actors
                </button>
                <button className={btnStyle} onClick={() => callApi('/actor-highest-revenue', 'Actor highest revenue')}>
                  Actor total revenue
                </button>
                <button className={btnStyle} onClick={() => callApi('/average-votes-neo4j', 'Average votes')}>
                  Avg votes (Neo4j)
                </button>
                <button className={btnStyle} onClick={() => callApi('/most-represented-genre', 'Most represented genre')}>
                  Top Genre
                </button>
                <button className={btnStyle} onClick={() => callApi('/films-of-coactors', 'My co-actors films')}>
                  Co-actors films
                </button>
                <button className={btnStyle} onClick={() => callApi('/director-most-actors', 'Director most actors')}>
                  Dir. most actors
                </button>
                <button className={btnStyle} onClick={() => callApi('/most-connected-films', 'Most connected films')}>
                  Connected films
                </button>
                <button className={btnStyle} onClick={() => callApi('/top-5-actors-directors', 'Actors with most directors')}>
                  Actor/Directors count
                </button>
                <button className={btnStyle} onClick={() => callApi('/recommend-film', 'Recommendation')}>
                  Recommend film
                </button>
                <button className={btnStyle} onClick={() => callApi('/create-influence', 'Influence relation')}>
                  Create Influence
                </button>
                <button className={btnStyle} onClick={() => callApi('/shortest-path', 'Shortest Path')}>
                  Shortest Path
                </button>
                <button className={btnStyle} onClick={() => callApi('/analyze-communities', 'Communities')}>
                  Louvain Analysis
                </button>
              </div>
            </section>

            <section>
              <h2 className="text-xl font-bold mb-4 text-purple-400 border-b border-purple-400/30 pb-2">Transversal</h2>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                <button className={btnStyle} onClick={() => callApi('/films-common-genres-diff-directors', 'Common genres / Diff directors')}>
                  Common genres/Diff Dir
                </button>
                <button className={btnStyle} onClick={() => callApi('/create-competition', 'Competition relation')}>
                  Create Competition
                </button>
                <button className={btnStyle} onClick={() => callApi('/frequent-collaborations', 'Frequent Collabs')}>
                  Frequent Collabs
                </button>
              </div>
            </section>
          </div>

          <div className="sticky top-28 h-fit">
            <div className="border border-white/20 rounded-xl p-6 bg-gray-800 shadow-2xl">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-2xl font-semibold text-yellow-500">{title}</h3>
                {loading && <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>}
              </div>
              <div className="bg-black/40 rounded-lg p-4 max-h-[70vh] overflow-auto border border-white/10">
                {loading ? (
                  <p className="text-gray-400 animate-pulse">Chargement des données...</p>
                ) : (
                  <pre className="whitespace-pre-wrap break-words text-xs font-mono">
                    {result}
                  </pre>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App