import axios from "axios"
const api = axios.create({ baseURL: "", timeout: 30000, headers: { "Content-Type": "application/json" } })
api.interceptors.response.use(r => r, e => {
  if (e.response?.status === 429) { alert("Rate limited. Please wait.") }
  return Promise.reject(e)
})
export default api
