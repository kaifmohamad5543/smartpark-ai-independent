import {
  beforeEach,
  describe,
  expect,
  it,
  vi,
} from 'vitest'

vi.mock(
  '../../services/api',
  () => ({
    default: {
      get: vi.fn(),
      post: vi.fn(),
    },
  })
)

import api from '../../services/api'
import { auth } from '../auth'

const TOKEN_KEY =
  'smartpark_access_token'

function resetAuth() {
  localStorage.clear()

  auth.state.user = null
  auth.state.loading = false
  auth.state.initialized = false

  api.get.mockReset()
  api.post.mockReset()
}

describe(
  'authentication store',
  () => {
    beforeEach(() => {
      resetAuth()
    })

    it(
      'logs in, stores the token and loads the user',
      async () => {
        api.post.mockResolvedValue({
          data: {
            access_token:
              'test-access-token',
          },
        })

        api.get.mockResolvedValue({
          data: {
            id: 'user-1',
            full_name:
              'SmartPark User',
            email:
              'user@smartpark.com',
            role: 'user',
            is_active: true,
          },
        })

        const user =
          await auth.login(
            'user@smartpark.com',
            'Password123!'
          )

        expect(
          api.post
        ).toHaveBeenCalledWith(
          '/api/auth/login',
          {
            email:
              'user@smartpark.com',
            password:
              'Password123!',
          }
        )

        expect(
          localStorage.getItem(
            TOKEN_KEY
          )
        ).toBe(
          'test-access-token'
        )

        expect(
          api.get
        ).toHaveBeenCalledWith(
          '/api/auth/me'
        )

        expect(
          user.email
        ).toBe(
          'user@smartpark.com'
        )

        expect(
          auth.isAuthenticated.value
        ).toBe(true)
      }
    )

    it(
      'detects an administrator account',
      async () => {
        localStorage.setItem(
          TOKEN_KEY,
          'admin-token'
        )

        api.get.mockResolvedValue({
          data: {
            id: 'admin-1',
            full_name:
              'SmartPark Administrator',
            email:
              'admin@smartpark.com',
            role: 'admin',
            is_active: true,
          },
        })

        await auth.loadUser()

        expect(
          auth.isAdmin.value
        ).toBe(true)

        expect(
          auth.isAuthenticated.value
        ).toBe(true)
      }
    )

    it(
      'clears authentication when loading the user fails',
      async () => {
        localStorage.setItem(
          TOKEN_KEY,
          'expired-token'
        )

        api.get.mockRejectedValue(
          new Error(
            'Unauthorized'
          )
        )

        const result =
          await auth.loadUser()

        expect(result).toBeNull()

        expect(
          localStorage.getItem(
            TOKEN_KEY
          )
        ).toBeNull()

        expect(
          auth.state.user
        ).toBeNull()

        expect(
          auth.state.initialized
        ).toBe(true)
      }
    )

    it(
      'logs the current user out',
      () => {
        localStorage.setItem(
          TOKEN_KEY,
          'active-token'
        )

        auth.state.user = {
          id: 'user-1',
          role: 'user',
        }

        auth.logout()

        expect(
          localStorage.getItem(
            TOKEN_KEY
          )
        ).toBeNull()

        expect(
          auth.state.user
        ).toBeNull()

        expect(
          auth.isAuthenticated.value
        ).toBe(false)

        expect(
          auth.state.initialized
        ).toBe(true)
      }
    )
  }
)
