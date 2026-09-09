import {
  describe,
  expect,
  it,
} from 'vitest'

import router from '../index'


describe(
  'SmartPark router',
  () => {
    it(
      'contains a catch-all 404 route',
      () => {
        const route =
          router
            .getRoutes()
            .find(
              (item) =>
                item.name ===
                'not-found'
            )

        expect(route).toBeDefined()

        expect(
          route.path
        ).toBe(
          '/:pathMatch(.*)*'
        )
      }
    )

    it(
      'protects every admin route',
      () => {
        const adminRoutes =
          router
            .getRoutes()
            .filter(
              (route) =>
                route.path.startsWith(
                  '/admin'
                )
            )

        expect(
          adminRoutes.length
        ).toBeGreaterThan(0)

        for (
          const route
          of adminRoutes
        ) {
          expect(
            route.meta.requiresAuth
          ).toBe(true)

          expect(
            route.meta.requiresAdmin
          ).toBe(true)
        }
      }
    )

    it(
      'protects authenticated user pages',
      () => {
        const protectedPaths = [
          '/dashboard',
          '/parking',
          '/prediction',
          '/reservations',
          '/wallet',
          '/profile',
          '/reviews',
        ]

        for (
          const path
          of protectedPaths
        ) {
          const route =
            router
              .getRoutes()
              .find(
                (item) =>
                  item.path === path
              )

          expect(route).toBeDefined()

          expect(
            route.meta.requiresAuth
          ).toBe(true)
        }
      }
    )
  }
)
