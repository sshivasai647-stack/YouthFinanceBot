import axios from 'axios'

const api = axios.create({
  baseURL: '/api/auth',
  withCredentials: true,
})

export const authApi = {
  register: (data) =>
    api.post('/register', {
      name: data.full_name,          // map full_name → name
      email: data.email,
      phone: data.phone,
      age: data.age,
      password: data.password,
      role: 'citizen',
      captcha_token: 'dev-bypass',   // bypassed when HCAPTCHA_SECRET is empty
    }),

  verifyOtp: (data) =>
    api.post('/verify-otp', {
      email: data.email,
      otp: data.otp,
    }),

  login: (data) =>
    api.post('/login', {
      email: data.email,
      password: data.password,
      captcha_token: 'dev-bypass',   // bypassed when HCAPTCHA_SECRET is empty
    }),

  logout: () => api.post('/logout'),

  refresh: () => api.post('/refresh'),

  forgotPassword: (email) => api.post('/forgot-password', { email }),

  resetPassword: (token, password) =>
    api.post('/reset-password', { token, password }),
}