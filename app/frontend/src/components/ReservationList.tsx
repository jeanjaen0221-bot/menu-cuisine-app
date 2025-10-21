import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api, fileDownload } from '../lib/api'
import { Reservation } from '../types'

export default function ReservationList() {
  const [rows, setRows] = useState<Reservation[]>([])
  const [q, setQ] = useState('')
  const [date, setDate] = useState<string>('')

  async function load() {
    const params: any = {}
    if (q) params.q = q
    if (date) params.service_date = date
    const res = await api.get('/api/reservations', { params })
    setRows(res.data)
  }

  useEffect(() => { load() }, [])

  return (
    <div className="card">
      <div className="flex flex-col md:flex-row gap-2 md:items-center md:justify-between">
        <div className="flex gap-2 items-center">
          <input className="input" placeholder="Rechercher un client" value={q} onChange={e=>setQ(e.target.value)} />
          <input type="date" className="input" value={date} onChange={e=>setDate(e.target.value)} />
          <button className="btn" onClick={load}>Filtrer</button>
        </div>
        <div className="flex gap-2">
          <Link to="/reservation/new" className="btn">➕ Nouvelle fiche</Link>
          <button className="btn" onClick={() => {
            if (!date) { alert('Sélectionnez une date'); return }
            fileDownload(`/api/reservations/day/${date}/pdf`)
          }}>🖨️ Export PDF du jour</button>
        </div>
      </div>

      <div className="mt-4 overflow-auto">
        <table className="min-w-full text-sm">
          <thead>
            <tr className="text-left text-gray-600">
              <th className="p-2">Nom du client</th>
              <th className="p-2">Date</th>
              <th className="p-2">Heure</th>
              <th className="p-2">Couverts</th>
              <th className="p-2">Statut</th>
              <th className="p-2">Actions</th>
            </tr>
          </thead>
          <tbody>
            {rows.map(r => (
              <tr key={r.id} className="border-t">
                <td className="p-2">{r.client_name}</td>
                <td className="p-2">{r.service_date}</td>
                <td className="p-2">{r.arrival_time}</td>
                <td className="p-2">{r.pax}</td>
                <td className="p-2 capitalize">{r.status}</td>
                <td className="p-2 flex gap-2">
                  <Link className="btn" to={`/reservation/${r.id}`}>Modifier</Link>
                  <button className="btn" onClick={() => fileDownload(`/api/reservations/${r.id}/pdf`)}>🖨️ PDF</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
