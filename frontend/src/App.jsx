import React, { useEffect, useState } from 'react'
import { Login } from './components/Login.jsx'
import { Signup } from './components/Signup.jsx'
import { PreferencesForm } from './components/PreferencesForm.jsx'
import { Onboarding } from './components/Onboarding.jsx'
import { PlanView } from './components/PlanView.jsx'
import api from './lib/api.js'

export default function App(){
  const [token, setToken] = useState(localStorage.getItem('token'))
  const [stage, setStage] = useState('auth')
  useEffect(() => {
    if(!token){ setStage('auth'); return }
    ;(async () => {
      try{ await api.get('/me', token); setStage('prefs') }catch{ setStage('auth') }
    })()
  }, [token])
  if(stage === 'auth') return (<div className='container'><h1>RAG Meal Planner (Vertex)</h1><div className='card'><Signup onAuthed={t=>{localStorage.setItem('token',t);setToken(t)}}/></div><div className='card'><Login onAuthed={t=>{localStorage.setItem('token',t);setToken(t)}}/></div></div>)
  if(stage === 'prefs') return (<div className='container'><h1>Set Preferences</h1><div className='card'><PreferencesForm token={token} onDone={()=>setStage('onboarding')} /></div></div>)
  if(stage === 'onboarding') return (<div className='container'><Onboarding token={token} onDone={()=>setStage('plan')} /></div>)
  return (<div className='container'><PlanView token={token} /></div>)
}
