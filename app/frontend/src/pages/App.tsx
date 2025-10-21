import { Routes, Route, Link, useNavigate } from 'react-router-dom'
import Home from './Home'
import EditReservation from './EditReservation'
import MenuPage from './MenuPage'
import ZenchefSettings from './ZenchefSettings'

export default function App() {
  const navigate = useNavigate()
  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-white shadow-soft">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-2xl font-semibold text-primary cursor-pointer" onClick={() => navigate('/')}>FicheCuisineManager</h1>
          <nav className="flex gap-2">
            <Link className="btn" to="/">Fiches</Link>
            <Link className="btn" to="/menu">Base de plats</Link>
            <Link className="btn" to="/settings">Paramètres</Link>
          </nav>
        </div>
      </header>
      <main className="max-w-6xl mx-auto w-full px-4 py-6 flex-1">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/reservation/new" element={<EditReservation />} />
          <Route path="/reservation/:id" element={<EditReservation />} />
          <Route path="/menu" element={<MenuPage />} />
          <Route path="/settings" element={<ZenchefSettings />} />
        </Routes>
      </main>
    </div>
  )
}
