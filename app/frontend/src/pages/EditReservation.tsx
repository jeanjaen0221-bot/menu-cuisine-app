import { useLocation, useNavigate, useParams } from 'react-router-dom'
import ReservationForm from '../components/ReservationForm'
import { useEffect, useState } from 'react'
import { api, fileDownload } from '../lib/api'
import { Reservation } from '../types'

export default function EditReservation() {
  const { id } = useParams()
  const navigate = useNavigate()
  const location = useLocation()
  const [data, setData] = useState<Reservation | null>(null)
  const [error, setError] = useState<string | null>(null)
  const isNew = id === 'new'

  useEffect(() => {
    if (isNew) {
      // Prefill from query or use sensible defaults
      const params = new URLSearchParams(location.search)
      const d = params.get('date') || new Date().toISOString().slice(0,10)
      setData({
        id: '' as any,
        client_name: '',
        pax: 2,
        service_date: d,
        arrival_time: '',
        drink_formula: 'Sans alcool',
        notes: '',
        status: 'draft',
        created_at: '' as any,
        updated_at: '' as any,
        items: []
      } as Reservation)
      return
    }
    // Existing reservation: load then render
    setData(null)
    api.get(`/api/reservations/${id}`)
      .then(r=> setData(r.data))
      .catch((e:any)=> setError(e?.userMessage || e?.response?.data?.detail || e?.message || 'Erreur de chargement'))
  }, [id, isNew, location.search])

  async function save(payload: any) {
    setError(null)
    try {
      if (id && id !== 'new') {
        await api.put(`/api/reservations/${id}`, payload)
        navigate('/')
      } else {
        const res = await api.post('/api/reservations', payload)
        navigate(`/reservation/${res.data.id}`)
      }
    } catch (e: any) {
      setError(e?.userMessage || e?.response?.data?.detail || e?.message || 'Erreur lors de l\'enregistrement')
    }
  }

  async function duplicate() {
    if (!id || id === 'new') return
    setError(null)
    try {
      const res = await api.post(`/api/reservations/${id}/duplicate`)
      navigate(`/reservation/${res.data.id}`)
    } catch (e: any) {
      setError(e?.userMessage || e?.response?.data?.detail || e?.message || 'Erreur lors du doublon')
    }
  }

  return (
    <div className="space-y-4">
      {error && (
        <div className="p-3 rounded-md bg-red-50 border border-red-200 text-red-700">{error}</div>
      )}
      <div className="flex gap-2">
        <button className="btn" onClick={()=>navigate(-1)}>Retour</button>
        {id && id !== 'new' && (
          <>
            <button className="btn" onClick={duplicate}>Dupliquer fiche</button>
            <button className="btn" onClick={()=>fileDownload(`/api/reservations/${id}/pdf`)}>Exporter en PDF</button>
          </>
        )}
      </div>
      {(!isNew && !data) ? (
        <div className="text-gray-600">Chargement…</div>
      ) : (
        <ReservationForm initial={data || undefined} onSubmit={save} />
      )}
    </div>
  )
}
