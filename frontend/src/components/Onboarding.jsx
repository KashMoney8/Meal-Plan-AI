import React, { useEffect, useState } from 'react'
import api from '../lib/api.js'
export function Onboarding({ token, onDone }){
  const [cards, setCards] = useState([])
  const [ratings, setRatings] = useState({})
  const diet = 'No Restriction'
  useEffect(()=>{(async()=>{const res=await api.get('/onboarding/cards?diet_type='+encodeURIComponent(diet), token); setCards(res.cards||[])})()},[])
  const allRated = cards.length===12 && cards.every(c=>ratings[c.recipe_id])
  return (<div className='card'><h2>Rate 12 recipes</h2><p>No skips. You can edit before finalizing.</p>
    {cards.map(c=>(<div key={c.recipe_id} className='card'><strong>{c.title}</strong> — {Math.round(c.kcal||0)} kcal
      <div>Diet: {c.diet_type}</div><div style={{display:'flex',gap:6,marginTop:8}}>
      {Array.from({length:10}).map((_,i)=>{const v=i+1; return <button key={v} onClick={()=>setRatings(r=>({...r,[c.recipe_id]:v}))} style={{background:ratings[c.recipe_id]===v?'#0ea5e9':'#eee'}}>{v}</button>})}
    </div></div>))}
    <button disabled={!allRated} onClick={async()=>{const payload={ratings:cards.map(c=>({recipe_id:c.recipe_id,rating:ratings[c.recipe_id]}))}; await api.post('/onboarding/ratings', payload, token); onDone()}}>Finish</button></div>)
}
