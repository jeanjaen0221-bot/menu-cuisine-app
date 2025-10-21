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

  useEffect(() => {
    if (!id || id === 'new') {
      // prefill service_date from query ?date=YYYY-MM-DD
      const params = new URLSearchParams(location.search)
      const d = params.get('date')
      if (d) setData({
        // minimal shape to prefill form only
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
    api.get(`/api/reservations/${id}`).then(r=> setData(r.data))
  }, [id, location.search])

  async function save(payload: any) {
    if (id && id !== 'new') {
      await api.put(`/api/reservations/${id}`, payload)
    } else {
      const res = await api.post('/api/reservations', payload)
      navigate(`/reservation/${res.data.id}`)
    }
    if (id && id !== 'new') navigate('/')
  }

  async function duplicate() {
    if (!id || id === 'new') return
    const res = await api.post(`/api/reservations/${id}/duplicate`)
    navigate(`/reservation/${res.data.id}`)
  }

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <button className="btn" onClick={()=>navigate(-1)}>Retour</button>
        {id && id !== 'new' && (
          <>
            <button className="btn" onClick={duplicate}>Dupliquer fiche</button>
            <button className="btn" onClick={()=>fileDownload(`/api/reservations/${id}/pdf`)}>Exporter en PDF</button>
          </>
        )}
      </div>
      <ReservationForm initial={data || undefined} onSubmit={save} />
    </div>
  )
}
