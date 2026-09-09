import {
  computed,
  reactive,
} from 'vue'

import api from '../services/api'

const TOKEN_KEY =
  'smartpark_access_token'

const state = reactive({
  user: null,
  loading: false,
  initialized: false,
})

const token = () =>
  localStorage.getItem(
    TOKEN_KEY
  )

const isAuthenticated = computed(
  () =>
    Boolean(
      token() &&
      state.user
    )
)

const isAdmin = computed(
  () =>
    state.user?.role ===
    'admin'
)

async function loadUser(
  throwOnError = false
) {
  if (!token()) {
    state.user = null
    state.initialized = true
    return null
  }

  state.loading = true

  try {
    const response =
      await api.get(
        '/api/auth/me'
      )

    state.user =
      response.data

    return state.user
  } catch (error) {
    localStorage.removeItem(
      TOKEN_KEY
    )

    state.user = null

    if (throwOnError) {
      throw error
    }

    return null
  } finally {
    state.loading = false
    state.initialized = true
  }
}

async function login(
  email,
  password
) {
  state.loading = true

  try {
    const response =
      await api.post(
        '/api/auth/login',
        {
          email,
          password,
        }
      )

    const accessToken =
      response.data
        ?.access_token

    if (!accessToken) {
      throw new Error(
        'Login succeeded but no access token was returned.'
      )
    }

    localStorage.setItem(
      TOKEN_KEY,
      accessToken
    )

    const user =
      await loadUser(true)

    if (!user) {
      throw new Error(
        'Unable to load the signed-in user.'
      )
    }

    state.initialized = true

    return user
  } catch (error) {
    localStorage.removeItem(
      TOKEN_KEY
    )

    state.user = null

    throw error
  } finally {
    state.loading = false
  }
}

async function register(
  fullName,
  email,
  password
) {
  state.loading = true

  try {
    await api.post(
      '/api/auth/register',
      {
        full_name:
          fullName,
        email,
        password,
      }
    )

    return await login(
      email,
      password
    )
  } finally {
    state.loading = false
  }
}

function logout() {
  localStorage.removeItem(
    TOKEN_KEY
  )

  state.user = null
  state.initialized = true
}

async function initialize() {
  if (state.initialized) {
    return
  }

  await loadUser()
}

export const auth = {
  state,
  isAuthenticated,
  isAdmin,
  login,
  register,
  logout,
  loadUser,
  initialize,
}
