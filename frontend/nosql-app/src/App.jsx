import './App.css'
import { useState } from 'react'

function App() {
  const [result, setResult] = useState("Clique sur un bouton pour afficher un résultat.")
  const [loading, setLoading] = useState(false)
  const [title, setTitle] = useState("Résultat")

  const btnStyle =
    "border border-white/20 rounded-xl p-4 bg-gray-800 hover:bg-gray-700 transition-all duration-200 text-center flex items-center justify-center min-h-[90px]"

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
    <div className="bg-gray-800 min-h-screen w-full text-white">
      <div className="grid grid-cols-3 w-full h-20 border border-white/20 place-items-center px-4">
        <h1 className="font-semibold text-3xl">Projet No-SQL</h1>
        <h2 className="col-span-2 text-xl text-center">
          Acsel PARSY, Pierre GARAT, Arthur MENNESSIER, Théo LESTE, Clara LIMOUSIN
        </h2>
      </div>

      <div className="pt-6 bg-gray-900 min-h-screen p-6">
        <div className="grid grid-cols-4 gap-4 mb-4">
          <button className={btnStyle} onClick={() => callApi('/year-with-most-films', 'Year with the most release')}>
            Year with the most release
          </button>
          <button className={btnStyle} onClick={() => callApi('/films-count-after-year?year=1999', 'Films after 1999')}>
            Number of films out after 1999
          </button>
          <button className={btnStyle} onClick={() => callApi('/average-votes-by-year?year=2007', 'Votes mean 2007')}>
            Vote mean of movies released in 2007
          </button>
          <button className={btnStyle} onClick={() => callApi('/films-per-year', 'Histogram')}>
            Histogram of movies release per year
          </button>
        </div>

        <div className="grid grid-cols-4 gap-4 mb-4">
          <button className={btnStyle} onClick={() => callApi('/available-genres', 'Genres')}>
            Movies categories
          </button>
          <button className={btnStyle} onClick={() => callApi('/film-with-highest-revenue', 'Top revenue movie')}>
            Most valuable movie
          </button>
          <button className={btnStyle} onClick={() => callApi('/directors-more-than-n-films?n=5', 'Directors')}>
            Realisators with more than 5 movies
          </button>
          <button className={btnStyle} onClick={() => callApi('/genre-with-highest-average-revenue', 'Best genre')}>
            Category with the most revenue
          </button>
        </div>

        <div className="grid grid-cols-3 gap-4 mb-4">
          <button className={btnStyle} onClick={() => callApi('/top-3-films-per-decade', 'Top 3 by decade')}>
            3 most rated film from each decade
          </button>
          <button className={btnStyle} onClick={() => callApi('/longest-film-per-genre', 'Longest films')}>
            Longest film per genre
          </button>
          <button className={btnStyle} onClick={() => callApi('/high-rated-high-revenue-view', 'Mongo view')}>
            Mongo View
          </button>
        </div>

        <div className="grid grid-cols-2 gap-4 mb-6">
          <button className={btnStyle} onClick={() => callApi('/runtime-revenue-correlation', 'Correlation')}>
            Runtime / Revenue correlation
          </button>
          <button className={btnStyle} onClick={() => callApi('/average-runtime-by-decade', 'Runtime evolution')}>
            Runtime evolution by decade
          </button>
        </div>

        <div className="border border-white/20 rounded-xl p-6 bg-gray-800">
          <h3 className="text-2xl font-semibold mb-4">{title}</h3>
          {loading ? (
            <p>Chargement...</p>
          ) : (
            <pre className="whitespace-pre-wrap break-words text-sm">
              {result}
            </pre>
          )}
        </div>
      </div>
    </div>
  )
}

export default App