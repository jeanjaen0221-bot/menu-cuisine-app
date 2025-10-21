import { useNavigate, useParams } from 'react-router-dom'
import ReservationForm from '../components/ReservationForm'
import { useEffect, useState } from 'react'
import { api, fileDownload } from '../lib/api'
import { Reservation } from '../types'

export default function EditReservation() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [data, setData] = useState<Reservation | null>(null)

  useEffect(() => {
    if (!id || id === 'new') return
    api.get(`/api/reservations/${id}`).then(r=> setData(r.data))
  }, [id])

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
