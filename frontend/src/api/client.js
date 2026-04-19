import axios from "axios"
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "https://simguard-v1.onrender.com",
  timeout: 30000,
  headers: { "Content-Type": "application/json" }
})
export default api
