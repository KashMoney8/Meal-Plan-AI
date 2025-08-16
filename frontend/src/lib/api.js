import axios from 'axios'
const base = import.meta.env.VITE_API_BASE || 'http://localhost:8000'
export default {
  async post(path, body, token){
    const res = await axios.post(base + path, body, { headers: token ? { Authorization: 'Bearer ' + token } : {} })
    return res.data
  },
  async get(path, token){
    const res = await axios.get(base + path, { headers: token ? { Authorization: 'Bearer ' + token } : {} })
    return res.data
  }
}
