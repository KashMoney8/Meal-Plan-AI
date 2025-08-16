import React, { useState } from 'react'
import api from '../lib/api.js'
export function Login({ onAuthed }){
  const [email, setEmail] = useState(''); const [password, setPassword] = useState('')
  return (<form onSubmit={async e=>{e.preventDefault(); const r=await api.post('/auth/login',{email,password}); onAuthed(r.token)}}>
    <h2>Login</h2><label>Email<input value={email} onChange={e=>setEmail(e.target.value)} /></label>
    <label>Password<input type='password' value={password} onChange={e=>setPassword(e.target.value)} /></label>
    <button>Login</button></form>)
}
