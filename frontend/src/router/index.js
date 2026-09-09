import {
  createRouter,
  createWebHistory,
} from 'vue-router'

import { auth } from '../stores/auth'


const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('../views/HomeView.vue'),
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/LoginView.vue'),
    meta: {
      guestOnly: true,
    },
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('../views/RegisterView.vue'),
    meta: {
      guestOnly: true,
    },
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('../views/DashboardView.vue'),
    meta: {
      requiresAuth: true,
    },
  },
  {
    path: '/parking',
    name: 'parking',
    component: () => import('../views/ParkingView.vue'),
    meta: {
      requiresAuth: true,
    },
  },
  {
    path: '/parking/:locationId/book',
    name: 'book-parking',
    component: () => import('../views/BookingView.vue'),
    meta: {
      requiresAuth: true,
    },
  },
  {
    path: '/prediction',
    name: 'prediction',
    component: () => import('../views/PredictionView.vue'),
    meta: {
      requiresAuth: true,
    },
  },
  {
    path: '/reservations',
    name: 'reservations',
    component: () => import('../views/ReservationsView.vue'),
    meta: {
      requiresAuth: true,
    },
  },
  {
    path: '/wallet',
    name: 'wallet',
    component: () => import('../views/WalletView.vue'),
    meta: {
      requiresAuth: true,
    },
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('../views/ProfileView.vue'),
    meta: {
      requiresAuth: true,
    },
  },
  {
    path: '/admin',
    name: 'admin-dashboard',
    component: () =>
      import(
        '../views/AdminDashboardView.vue'
      ),
    meta: {
      requiresAuth: true,
      requiresAdmin: true,
    },
  },

  {
    path: '/admin/parking',
    name: 'admin-parking',
    component: () =>
      import(
        '../views/AdminParkingView.vue'
      ),
    meta: {
      requiresAuth: true,
      requiresAdmin: true,
    },
  },

  {
    path: '/admin/notifications',
    name: 'admin-notifications',
    component: () =>
      import(
        '../views/AdminNotificationsView.vue'
      ),
    meta: {
      requiresAuth: true,
      requiresAdmin: true,
    },
  },

  {
    path: '/admin/reviews',
    name: 'admin-reviews',
    component: () =>
      import(
        '../views/AdminReviewsView.vue'
      ),
    meta: {
      requiresAuth: true,
      requiresAdmin: true,
    },
  },

  {
    path: '/admin/reservations',
    name: 'admin-reservations',
    component: () =>
      import(
        '../views/AdminReservationsView.vue'
      ),
    meta: {
      requiresAuth: true,
      requiresAdmin: true,
    },
  },

  {
    path: '/admin/users',
    name: 'admin-users',
    component: () =>
      import(
        '../views/AdminUsersView.vue'
      ),
    meta: {
      requiresAuth: true,
      requiresAdmin: true,
    },
  },

  {
    path: '/admin/payments',
    name: 'admin-payments',
    component: () =>
      import(
        '../views/AdminPaymentsView.vue'
      ),
    meta: {
      requiresAuth: true,
      requiresAdmin: true,
    },
  },

  {
    path: '/reviews',
    name: 'reviews',
    component: () =>
      import(
        '../views/ReviewsView.vue'
      ),
    meta: {
      requiresAuth: true,
    },
  },

  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () =>
      import(
        '../views/NotFoundView.vue'
      ),
  },

]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(
  async (to) => {
    await auth.initialize()

    if (
      to.meta.requiresAuth &&
      !auth.isAuthenticated.value
    ) {
      return {
        name: 'login',
        query: {
          redirect: to.fullPath,
        },
      }
    }

    if (
      to.meta.requiresAdmin &&
      !auth.isAdmin.value
    ) {
      return {
        name: 'dashboard',
      }
    }

    if (
      to.meta.guestOnly &&
      auth.isAuthenticated.value
    ) {
      return {
        name: 'dashboard',
      }
    }

    return true
  }
)

export default router
