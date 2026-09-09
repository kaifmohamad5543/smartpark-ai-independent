import axios from 'axios'

const TOKEN_KEY =
  'smartpark_access_token'

const api = axios.create({
  baseURL:
    import.meta.env.VITE_API_BASE_URL ||
    'http://127.0.0.1:8000',

  headers: {
    'Content-Type':
      'application/json',
  },

  timeout: 10000,
})

api.interceptors.request.use(
  (config) => {
    const token =
      localStorage.getItem(
        TOKEN_KEY
      )

    if (token) {
      config.headers.Authorization =
        `Bearer ${token}`
    }

    return config
  }
)

api.interceptors.response.use(
  (response) => response,

  (error) => {
    const status =
      error.response?.status

    const requestUrl =
      error.config?.url || ''

    const hadToken =
      Boolean(
        localStorage.getItem(
          TOKEN_KEY
        )
      )

    const isLoginRequest =
      requestUrl.includes(
        '/api/auth/login'
      )

    if (
      status === 401 &&
      hadToken &&
      !isLoginRequest
    ) {
      localStorage.removeItem(
        TOKEN_KEY
      )

      const currentPath =
        `${window.location.pathname}${window.location.search}`

      const alreadyOnLogin =
        window.location.pathname ===
        '/login'

      if (!alreadyOnLogin) {
        const redirect =
          encodeURIComponent(
            currentPath
          )

        window.location.replace(
          `/login?reason=session-expired&redirect=${redirect}`
        )
      }
    }

    return Promise.reject(error)
  }
)

export default api
