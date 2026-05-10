import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  withCredentials: true,
})

export const guestApi = {
  chat: (data) => api.post('/guest/chat', data),
}
