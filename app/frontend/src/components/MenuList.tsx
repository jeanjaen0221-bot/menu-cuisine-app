import { useEffect, useState } from 'react'
import { api } from '../lib/api'
import { MenuItem } from '../types'

export default function MenuList() {
  const [items, setItems] = useState<MenuItem[]>([])
  const [name, setName] = useState('')
  const [type, setType] = useState('plat')
  const [active, setActive] = useState(true)

  async function load() {
    const res = await api.get('/api/menu-items')
    setItems(res.data)
  }
  useEffect(() => { load() }, [])

  async function add() {
    if (!name) return
    await api.post('/api/menu-items', { name, type, active })
    setName(''); setType('plat'); setActive(true)
    await load()
  }

  async function toggleActive(it: MenuItem) {
    await api.put(`/api/menu-items/${it.id}`, { active: !it.active })
    await load()
  }

  async function remove(it: MenuItem) {
    if (!confirm('Supprimer cet élément ?')) return
    await api.delete(`/api/menu-items/${it.id}`)
    await load()
  }

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-primary mb-3">Base de plats</h3>

      <div className="grid grid-cols-12 gap-2">
        <input className="input col-span-6" placeholder="Nom du plat" value={name} onChange={e=>setName(e.target.value)} />
        <select className="input col-span-3" value={type} onChange={e=>setType(e.target.value)}>
          <option>entrée</option>
          <option>plat</option>
          <option>dessert</option>
        </select>
        <select className="input col-span-2" value={String(active)} onChange={e=>setActive(e.target.value==='true')}>
          <option value="true">Actif</option>
          <option value="false">Inactif</option>
        </select>
        <button className="btn col-span-1" onClick={add}>Ajouter</button>
      </div>

      <div className="mt-4 overflow-auto">
        <table className="min-w-full text-sm">
          <thead>
            <tr className="text-left text-gray-600">
              <th className="p-2">Nom</th>
              <th className="p-2">Type</th>
              <th className="p-2">Actif</th>
              <th className="p-2">Actions</th>
            </tr>
          </thead>
          <tbody>
            {items.map(it => (
              <tr key={it.id} className="border-t">
                <td className="p-2">{it.name}</td>
                <td className="p-2">{it.type}</td>
                <td className="p-2">{it.active ? 'Oui' : 'Non'}</td>
                <td className="p-2 flex gap-2">
                  <button className="btn" onClick={()=>toggleActive(it)}>{it.active ? 'Désactiver' : 'Activer'}</button>
                  <button className="btn" onClick={()=>remove(it)}>Supprimer</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
