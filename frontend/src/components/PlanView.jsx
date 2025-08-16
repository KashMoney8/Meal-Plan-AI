import React, { useState } from 'react'
import api from '../lib/api.js'
export function PlanView({ token }){
  const [days, setDays] = useState(7)
  const [meals_per_day, setMeals] = useState(3)
  const [allow_repeats, setRepeats] = useState(true)
  const [plan, setPlan] = useState(null)
  return (<div>
    <div className='card'><h2>Create Plan</h2><div className='toolbar'>
      <label>Days <input type='number' value={days} onChange={e=>setDays(+e.target.value)} /></label>
      <label>Meals/day <input type='number' value={meals_per_day} onChange={e=>setMeals(+e.target.value)} /></label>
      <label><input type='checkbox' checked={allow_repeats} onChange={e=>setRepeats(e.target.checked)} /> Allow repeats</label>
      <button onClick={async()=>{const res=await api.post('/plans/generate',{days,meals_per_day,allow_repeats},token); setPlan(res)}}>Generate</button>
    </div></div>
    {plan && (<div className='card'><h2>Plan #{plan.id}</h2>
      <div className='grid week'>
        {Array.from({length: plan.days}).map((_, di) => (
          <div key={di} className='meal-slot'><strong>Day {di+1}</strong>
            {Array.from({length: plan.meals_per_day}).map((_, mi) => {
              const item = plan.items.find(x => x.day_index===di && x.meal_index===mi)
              return (<div key={mi} style={{marginTop:8,borderTop:'1px solid #eee',paddingTop:8}}>
                <div>Meal {mi+1} — recipe #{item?.recipe_id} — portion {item?.portion ?? 1.0}</div>
                <button onClick={async()=>{const r=await api.post(`/plans/${plan.id}/swap`,{day_index:di,meal_index:mi},token); setPlan(p=>({...p, items: p.items.map(it => (it.day_index===di && it.meal_index===mi) ? r : it)}))}}>Swap</button>
              </div>)
            })}
          </div>
        ))}
      </div>
      <p style={{marginTop:12,fontSize:12,color:'#666'}}>Disclaimer: This app does not provide medical advice. Consult a professional.</p>
    </div>)}
  </div>)
}
