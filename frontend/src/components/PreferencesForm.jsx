import React, { useState } from 'react'
import api from '../lib/api.js'
export function PreferencesForm({ token, onDone }){
  const [calorie_target, setKcal] = useState(2000)
  const [protein_target, setProtein] = useState('')
  const [carb_target, setCarb] = useState('')
  const [fat_target, setFat] = useState('')
  const [diet_type, setDiet] = useState('No Restriction')
  const [allergens, setAllergens] = useState([])
  const [exclude_ingredients, setExclude] = useState([])
  const [units, setUnits] = useState('us')
  const [share, setShare] = useState(true)
  const toggleAllergen = (a) => setAllergens(x => x.includes(a) ? x.filter(y=>y!==a) : [...x, a])
  return (<form onSubmit={async e=>{e.preventDefault(); await api.post('/preferences',{calorie_target,protein_target:protein_target||null,carb_target:carb_target||null,fat_target:fat_target||null,diet_type,allergens,exclude_ingredients,units,share_anonymized:share},token); onDone()}}>
    <label>Calorie target<input type='number' value={calorie_target} onChange={e=>setKcal(e.target.value)} /></label>
    <div style={{display:'flex',gap:8}}>
      <label>Protein (g/day)<input type='number' value={protein_target} onChange={e=>setProtein(e.target.value)} /></label>
      <label>Carbs (g/day)<input type='number' value={carb_target} onChange={e=>setCarb(e.target.value)} /></label>
      <label>Fat (g/day)<input type='number' value={fat_target} onChange={e=>setFat(e.target.value)} /></label>
    </div>
    <label>Diet<select value={diet_type} onChange={e=>setDiet(e.target.value)}><option>No Restriction</option><option>Vegetarian</option><option>Vegan</option></select></label>
    <div><strong>Allergens</strong>{['dairy','eggs','peanuts','tree nuts','soy','gluten','shellfish','fish','sesame'].map(a=>(
      <label key={a} style={{display:'inline-flex',gap:6,marginRight:12}}><input type='checkbox' checked={allergens.includes(a)} onChange={()=>toggleAllergen(a)} />{a}</label>))}</div>
    <label>Exclude ingredients (comma-separated)<input value={exclude_ingredients.join(',')} onChange={e=>setExclude(e.target.value.split(',').map(s=>s.trim()).filter(Boolean))} /></label>
    <label>Units<select value={units} onChange={e=>setUnits(e.target.value)}><option value='us'>US</option><option value='metric'>Metric</option></select></label>
    <label><input type='checkbox' checked={share} onChange={e=>setShare(e.target.checked)} />Share anonymized ratings to improve global recommendations</label>
    <button>Continue</button></form>)
}
