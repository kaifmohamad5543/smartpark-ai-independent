import {
  afterEach,
} from 'vitest'

function createStorage() {
  const data = new Map()

  return {
    get length() {
      return data.size
    },

    clear() {
      data.clear()
    },

    getItem(key) {
      const value =
        data.get(String(key))

      return value === undefined
        ? null
        : value
    },

    key(index) {
      return (
        Array.from(
          data.keys()
        )[index] ?? null
      )
    },

    removeItem(key) {
      data.delete(
        String(key)
      )
    },

    setItem(key, value) {
      data.set(
        String(key),
        String(value)
      )
    },
  }
}

const localStorageMock =
  createStorage()

const sessionStorageMock =
  createStorage()

Object.defineProperty(
  globalThis,
  'localStorage',
  {
    configurable: true,
    value:
      localStorageMock,
  }
)

Object.defineProperty(
  globalThis,
  'sessionStorage',
  {
    configurable: true,
    value:
      sessionStorageMock,
  }
)

if (
  typeof window !==
  'undefined'
) {
  Object.defineProperty(
    window,
    'localStorage',
    {
      configurable: true,
      value:
        localStorageMock,
    }
  )

  Object.defineProperty(
    window,
    'sessionStorage',
    {
      configurable: true,
      value:
        sessionStorageMock,
    }
  )
}

afterEach(() => {
  localStorageMock.clear()
  sessionStorageMock.clear()
})
