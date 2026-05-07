// In dev: Vite proxy forwards /api → localhost:8080
// In production: VITE_API_URL must be set to the Railway backend URL (no trailing slash)
const BASE = (import.meta.env.VITE_API_URL || '') + '/api'

async function req(method, path, body) {
  const opts = { method, headers: { 'Content-Type': 'application/json' } }
  if (body !== undefined) opts.body = JSON.stringify(body)
  const res = await fetch(BASE + path, opts)
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'Request failed')
  }
  // 204 No Content or empty body
  const text = await res.text()
  return text ? JSON.parse(text) : null
}

const get  = (path)        => req('GET',    path)
const post = (path, body)  => req('POST',   path, body)
const put  = (path, body)  => req('PUT',    path, body)
const del  = (path)        => req('DELETE', path)

export const api = {
  // Dashboard
  dashboard: ()                     => get('/dashboard'),

  // User
  getUser: ()                       => get('/user'),
  saveUser: (body)                  => put('/user', body),

  // Goals
  getGoals: ()                      => get('/goals'),
  createGoal: (body)                => post('/goals', body),
  updateGoal: (id, body)            => put(`/goals/${id}`, body),
  deleteGoal: (id)                  => del(`/goals/${id}`),

  // Tasks
  getTasks: (date)                  => get(date ? `/tasks?date=${date}` : '/tasks'),
  getTasksToday: ()                 => get('/tasks/today'),
  createTask: (body)                => post('/tasks', body),
  updateTask: (id, body)            => put(`/tasks/${id}`, body),
  deleteTask: (id)                  => del(`/tasks/${id}`),
  addNote: (id, text)               => post(`/tasks/${id}/notes`, { text }),
  deleteNote: (id, index)           => del(`/tasks/${id}/notes/${index}`),
  postponeTask: (id, new_date, new_time) => post(`/tasks/${id}/postpone`, { new_date, new_time }),

  // Journal
  getJournal: ()                    => get('/journal'),
  getTodaysJournal: ()              => get('/journal/today'),
  createJournal: (body)             => post('/journal', body),
  updateJournal: (id, body)         => put(`/journal/${id}`, body),
  deleteJournal: (id)               => del(`/journal/${id}`),

  // Analytics
  getAnalytics: ()                  => get('/analytics'),
}
