import { useEffect, useMemo, useState } from 'react'
import { api } from '../lib/api'
import { Reservation, ReservationCreate, ReservationItem } from '../types'

const DRINKS = [
  'Sans alcool', 'Vin au verre', 'Accords mets & vins', 'Soft + Café', 'Eau + Café'
]

type Props = {
  initial?: Partial<Reservation>
  onSubmit: (payload: Partial<ReservationCreate>) => Promise<void>
}

export default function ReservationForm({ initial, onSubmit }: Props) {
  const [client_name, setClient] = useState(initial?.client_name || '')
  const [service_date, setDate] = useState(initial?.service_date || '')
  const [arrival_time, setTime] = useState(initial?.arrival_time || '')
  const [pax, setPax] = useState(initial?.pax || 2)
  const [drink_formula, setDrink] = useState(initial?.drink_formula || DRINKS[0])
  const [notes, setNotes] = useState(initial?.notes || '')
  const [status, setStatus] = useState<Reservation['status']>(initial?.status || 'draft')
  const [items, setItems] = useState<ReservationItem[]>(initial?.items || [])
  const [openRow, setOpenRow] = useState<number | null>(null)

  useEffect(() => {
    if (!items.length) {
      setItems([
        { type: 'entrée', name: '', quantity: 0 },
        { type: 'plat', name: '', quantity: 0 },
        { type: 'dessert', name: '', quantity: 0 },
      ])
    }
  }, [])

  function updateItem(idx: number, patch: Partial<ReservationItem>) {
    setItems(prev => prev.map((it, i) => i===idx ? { ...it, ...patch } : it))
  }

  function addItem() {
    setItems(prev => [...prev, { type: 'plat', name: '', quantity: 1 }])
  }

  async function submit() {
    const d = service_date || new Date().toISOString().slice(0,10)
    const t = arrival_time && arrival_time.length >= 4 ? arrival_time : '00:00'
    const name = (client_name || '').trim() || 'Client'
    const validItems = (items || []).filter(it => (it.name || '').trim() && (it.quantity || 0) > 0)
    await onSubmit({ client_name: name, service_date: d, arrival_time: t, pax: Number(pax) || 1, drink_formula, notes, status, items: validItems })
  }

  return (
    <div className="card">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="label">Nom du client</label>
          <input className="input" value={client_name} onChange={e=>setClient(e.target.value)} />
        </div>
        <div>
          <label className="label">Date du service</label>
          <input type="date" className="input" value={service_date} onChange={e=>setDate(e.target.value)} />
        </div>
        <div>
          <label className="label">Heure d’arrivée</label>
          <input type="time" className="input" value={arrival_time} onChange={e=>setTime(e.target.value)} />
        </div>
        <div>
          <label className="label">Nombre de couverts</label>
          <input type="number" min={1} className="input" value={pax} onChange={e=>setPax(Number(e.target.value))} />
        </div>
        <div>
          <label className="label">Formule boisson</label>
          <select className="input" value={drink_formula} onChange={e=>setDrink(e.target.value)}>
            {DRINKS.map(d => <option key={d} value={d}>{d}</option>)}
          </select>
        </div>
        <div>
          <label className="label">Statut</label>
          <select className="input" value={status} onChange={e=>setStatus(e.target.value as Reservation['status'])}>
            <option value="draft">Brouillon</option>
            <option value="confirmed">Confirmée</option>
            <option value="printed">Imprimée</option>
          </select>
        </div>
        <div className="md:col-span-2">
          <label className="label">Notes cuisine</label>
          <textarea className="input min-h-[100px]" value={notes} onChange={e=>setNotes(e.target.value)} />
        </div>
      </div>

      <div className="mt-6">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-primary">Plats</h3>
          <button className="btn" onClick={addItem}>+ Ajouter un plat</button>
        </div>
        <div className="mt-3 space-y-2">
          {items.map((it, idx) => (
            <div key={idx}>
              <ItemRow
                item={it}
                open={openRow === idx}
                onFocus={()=>setOpenRow(idx)}
                onClose={()=>setOpenRow(prev => prev === idx ? null : prev)}
                onChange={(p)=>updateItem(idx,p)}
              />
            </div>
          ))}
        </div>
      </div>

      <div className="mt-6 flex gap-2">
        <button className="btn" onClick={submit}>Sauvegarder</button>
      </div>
    </div>
  )
}

function ItemRow({ item, onChange, open, onFocus, onClose }: { item: ReservationItem, onChange: (p: Partial<ReservationItem>)=>void, open: boolean, onFocus: ()=>void, onClose: ()=>void }) {
  const [suggest, setSuggest] = useState<{name:string,type:string}[]>([])
  const [q, setQ] = useState('')

  async function loadDefault() {
    const res = await api.get('/api/menu-items/search', { params: { type: item.type } })
    setSuggest(res.data)
  }

  useEffect(() => {
    const t = setTimeout(async () => {
      if (!q) { await loadDefault(); return }
      const res = await api.get('/api/menu-items/search', { params: { q, type: item.type } })
      setSuggest(res.data)
    }, 200)
    return () => clearTimeout(t)
  }, [q, item.type])

  return (
    <div className="grid grid-cols-12 gap-2" onBlur={(e)=>{ if (!e.currentTarget.contains(e.relatedTarget as Node)) onClose() }}>
      <select className="input col-span-2" value={item.type} onChange={e=>{ onChange({ type: e.target.value }); setQ(''); }}>
        <option>entrée</option>
        <option>plat</option>
        <option>dessert</option>
      </select>
      <div className="col-span-8 relative">
        <input className="input w-full" placeholder="Nom du plat" value={item.name} onFocus={()=>{ onFocus(); if (!q) loadDefault() }} onChange={e=>{ onChange({ name: e.target.value }); setQ(e.target.value) }} />
        {open && suggest.length>0 && (
          <div className="absolute z-10 bg-white border rounded-md mt-1 max-h-48 overflow-auto w-full">
            {suggest.map((s, i) => (
              <div key={i} className="px-3 py-2 hover:bg-gray-100 cursor-pointer" onMouseDown={(e)=>{ e.preventDefault(); onChange({ name: s.name, type: s.type }); setSuggest([]); onClose(); }}>{s.name}</div>
            ))}
          </div>
        )}
      </div>
      <input type="number" min={0} className="input col-span-2" value={item.quantity} onChange={e=>onChange({ quantity: parseInt(e.target.value || '0', 10) })} />
    </div>
  )
}
