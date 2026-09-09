<script setup>
import {
  computed,
  onMounted,
  ref,
} from 'vue'

import {
  RouterLink,
  useRouter,
} from 'vue-router'

import {
  Bell,
  CalendarCheck2,
  BrainCircuit,
  CarFront,
  CheckCheck,
  Clock3,
  LayoutDashboard,
  LogOut,
  MapPinned,
  MessageSquareText,
  ShieldCheck,
  ReceiptText,
  Settings2,
  Star,
  Menu,
  WalletCards,
  UserRound,
  UsersRound,
  X,
} from '@lucide/vue'

import { auth } from '../stores/auth'
import api from '../services/api'

const router = useRouter()

const mobileOpen = ref(false)

const notificationOpen = ref(false)
const notifications = ref([])
const unreadCount = ref(0)

const notificationsLoading = ref(false)
const notificationError = ref('')

const firstName = computed(() => {
  return (
    auth.state.user?.full_name
      ?.trim()
      ?.split(/\s+/)[0] ||
    'User'
  )
})

const initials = computed(() => {
  const name =
    auth.state.user?.full_name ||
    'SmartPark User'

  return name
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0])
    .join('')
    .toUpperCase()
})

const baseNavigation = [
  {
    label: 'Dashboard',
    to: '/dashboard',
    icon: LayoutDashboard,
  },
  {
    label: 'Find Parking',
    to: '/parking',
    icon: MapPinned,
  },
  {
    label: 'AI Prediction',
    to: '/prediction',
    icon: BrainCircuit,
  },
  {
    label: 'Reservations',
    to: '/reservations',
    icon: CarFront,
  },
  {
    label: 'Wallet',
    to: '/wallet',
    icon: WalletCards,
  },
  {
    label: 'Profile & Vehicles',
    to: '/profile',
    icon: UserRound,
  },
  {
    label: 'Reviews & Ratings',
    to: '/reviews',
    icon: Star,
  },
]

const navigation = computed(() => {
  const items = [
    ...baseNavigation,
  ]

  if (auth.isAdmin.value) {
    items.push({
      label: 'Admin Dashboard',
      to: '/admin',
      icon: ShieldCheck,
    })

    items.push({
      label: 'Parking Management',
      to: '/admin/parking',
      icon: Settings2,
    })

    items.push({
      label: 'Payments & Refunds',
      to: '/admin/payments',
      icon: ReceiptText,
    })

    items.push({
      label: 'User Management',
      to: '/admin/users',
      icon: UsersRound,
    })

    items.push({
      label: 'Reservation Management',
      to: '/admin/reservations',
      icon: CalendarCheck2,
    })

    items.push({
      label: 'Reviews Management',
      to: '/admin/reviews',
      icon: MessageSquareText,
    })

    items.push({
      label: 'Notifications Management',
      to: '/admin/notifications',
      icon: Bell,
    })
  }

  return items
})

function formatNotificationDate(value) {
  if (!value) {
    return ''
  }

  const date = new Date(value)

  const now = new Date()

  const difference =
    now.getTime() -
    date.getTime()

  const minutes =
    Math.floor(
      difference /
      60000
    )

  if (minutes < 1) {
    return 'Just now'
  }

  if (minutes < 60) {
    return `${minutes} min ago`
  }

  const hours =
    Math.floor(
      minutes / 60
    )

  if (hours < 24) {
    return `${hours} hr${hours === 1 ? '' : 's'} ago`
  }

  return new Intl.DateTimeFormat(
    'en-GB',
    {
      dateStyle: 'medium',
      timeStyle: 'short',
    }
  ).format(date)
}

function notificationTypeLabel(value) {
  if (!value) {
    return 'Notification'
  }

  return value
    .replaceAll('_', ' ')
    .replace(
      /\b\w/g,
      (letter) =>
        letter.toUpperCase()
    )
}

async function loadNotifications() {
  notificationsLoading.value = true
  notificationError.value = ''

  try {
    const [
      notificationResponse,
      countResponse,
    ] = await Promise.all([
      api.get(
        '/api/notifications'
      ),
      api.get(
        '/api/notifications/unread-count'
      ),
    ])

    notifications.value =
      notificationResponse.data

    unreadCount.value =
      countResponse.data.unread_count
  } catch (error) {
    notificationError.value =
      error.response?.data?.detail ||
      'Unable to load notifications.'
  } finally {
    notificationsLoading.value = false
  }
}

async function toggleNotifications() {
  notificationOpen.value =
    !notificationOpen.value

  if (notificationOpen.value) {
    await loadNotifications()
  }
}

async function markNotificationRead(
  notification
) {
  if (notification.is_read) {
    return
  }

  try {
    const response =
      await api.patch(
        `/api/notifications/${notification.id}/read`
      )

    const index =
      notifications.value.findIndex(
        (item) =>
          item.id ===
          notification.id
      )

    if (index !== -1) {
      notifications.value[index] =
        response.data
    }

    unreadCount.value =
      Math.max(
        0,
        unreadCount.value - 1
      )
  } catch (error) {
    notificationError.value =
      error.response?.data?.detail ||
      'Unable to update notification.'
  }
}

async function markAllRead() {
  if (
    unreadCount.value === 0
  ) {
    return
  }

  try {
    await api.patch(
      '/api/notifications/read-all'
    )

    notifications.value =
      notifications.value.map(
        (notification) => ({
          ...notification,
          is_read: true,
        })
      )

    unreadCount.value = 0
  } catch (error) {
    notificationError.value =
      error.response?.data?.detail ||
      'Unable to mark notifications as read.'
  }
}

async function logout() {
  notificationOpen.value = false
  auth.logout()

  await router.replace(
    '/login'
  )
}

onMounted(
  loadNotifications
)
</script>

<template>
  <div class="min-h-screen bg-slate-50">
    <div
      v-if="mobileOpen"
      class="fixed inset-0 z-40 bg-slate-950/50 backdrop-blur-sm lg:hidden"
      @click="mobileOpen = false"
    />

    <aside
      class="fixed inset-y-0 left-0 z-50 flex w-72 flex-col bg-slate-950 text-white transition-transform duration-300 lg:translate-x-0"
      :class="
        mobileOpen
          ? 'translate-x-0'
          : '-translate-x-full'
      "
    >
      <div
        class="flex h-20 items-center justify-between border-b border-white/10 px-6"
      >
        <RouterLink
          to="/dashboard"
          class="flex items-center gap-3"
          @click="mobileOpen = false"
        >
          <div
            class="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-500 font-black text-slate-950"
          >
            P
          </div>

          <div>
            <p class="text-lg font-bold">
              SmartPark AI
            </p>

            <p class="text-xs text-slate-400">
              Intelligent Parking
            </p>
          </div>
        </RouterLink>

        <button
          class="rounded-lg p-2 text-slate-400 hover:bg-white/10 hover:text-white lg:hidden"
          @click="mobileOpen = false"
        >
          <X :size="20" />
        </button>
      </div>

      <nav
        class="flex-1 space-y-2 overflow-y-auto px-4 py-6"
      >
        <RouterLink
          v-for="item in navigation"
          :key="item.label"
          :to="item.to"
          class="flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium text-slate-300 transition hover:bg-white/10 hover:text-white"
          active-class="bg-emerald-500 text-slate-950 hover:bg-emerald-500 hover:text-slate-950"
          @click="mobileOpen = false"
        >
          <component
            :is="item.icon"
            :size="20"
          />

          {{ item.label }}
        </RouterLink>
      </nav>

      <div
        class="border-t border-white/10 p-4"
      >
        <div
          class="mb-4 flex items-center gap-3 rounded-xl bg-white/5 p-3"
        >
          <div
            class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-emerald-500 font-bold text-slate-950"
          >
            {{ initials }}
          </div>

          <div class="min-w-0">
            <p
              class="truncate text-sm font-semibold text-white"
            >
              {{
                auth.state.user?.full_name
              }}
            </p>

            <p
              class="truncate text-xs text-slate-400"
            >
              {{
                auth.state.user?.email
              }}
            </p>
          </div>
        </div>

        <button
          class="flex w-full items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium text-slate-300 transition hover:bg-red-500/10 hover:text-red-300"
          @click="logout"
        >
          <LogOut :size="19" />
          Sign out
        </button>
      </div>
    </aside>

    <div class="lg:pl-72">
      <header
        class="sticky top-0 z-30 flex h-20 items-center justify-between border-b border-slate-200 bg-white/90 px-4 backdrop-blur sm:px-6 lg:px-8"
      >
        <div class="flex items-center gap-4">
          <button
            class="rounded-xl border border-slate-200 p-2.5 text-slate-600 lg:hidden"
            @click="mobileOpen = true"
          >
            <Menu :size="21" />
          </button>

          <div>
            <p
              class="text-sm text-slate-500"
            >
              Welcome back,
            </p>

            <p
              class="font-semibold text-slate-900"
            >
              {{ firstName }}
            </p>
          </div>
        </div>

        <div class="flex items-center gap-3">
          <div
            class="relative z-50"
          >
            <button
              class="relative rounded-xl border border-slate-200 bg-white p-2.5 text-slate-600 transition hover:bg-slate-50"
              @click.stop="
                toggleNotifications
              "
            >
              <Bell :size="20" />

              <span
                v-if="unreadCount > 0"
                class="absolute -right-1.5 -top-1.5 flex min-h-5 min-w-5 items-center justify-center rounded-full bg-emerald-500 px-1 text-[10px] font-black text-white ring-2 ring-white"
              >
                {{
                  unreadCount > 99
                    ? '99+'
                    : unreadCount
                }}
              </span>
            </button>

            <div
              v-if="notificationOpen"
              class="absolute right-0 top-14 w-[360px] max-w-[calc(100vw-2rem)] overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-2xl"
            >
              <div
                class="flex items-center justify-between border-b border-slate-100 p-5"
              >
                <div>
                  <h2
                    class="font-bold text-slate-900"
                  >
                    Notifications
                  </h2>

                  <p
                    class="mt-1 text-xs text-slate-500"
                  >
                    {{
                      unreadCount
                    }}
                    unread
                  </p>
                </div>

                <button
                  v-if="unreadCount > 0"
                  class="inline-flex items-center gap-1.5 text-xs font-semibold text-emerald-600 hover:text-emerald-700"
                  @click.stop="
                    markAllRead
                  "
                >
                  <CheckCheck
                    :size="16"
                  />
                  Mark all read
                </button>
              </div>

              <div
                v-if="notificationError"
                class="m-4 rounded-xl border border-red-200 bg-red-50 p-3 text-xs text-red-700"
              >
                {{ notificationError }}
              </div>

              <div
                v-if="notificationsLoading"
                class="p-8 text-center text-sm text-slate-500"
              >
                Loading notifications...
              </div>

              <div
                v-else-if="
                  notifications.length ===
                  0
                "
                class="p-8 text-center"
              >
                <div
                  class="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-100 text-slate-500"
                >
                  <Bell :size="22" />
                </div>

                <p
                  class="mt-4 font-semibold text-slate-800"
                >
                  You're all caught up
                </p>

                <p
                  class="mt-1 text-xs text-slate-500"
                >
                  No notifications yet.
                </p>
              </div>

              <div
                v-else
                class="max-h-[480px] overflow-y-auto"
              >
                <button
                  v-for="notification in notifications.slice(
                    0,
                    12
                  )"
                  :key="notification.id"
                  class="flex w-full gap-3 border-b border-slate-100 p-4 text-left transition last:border-b-0 hover:bg-slate-50"
                  :class="
                    notification.is_read
                      ? 'bg-white'
                      : 'bg-emerald-50/60'
                  "
                  @click.stop="
                    markNotificationRead(
                      notification
                    )
                  "
                >
                  <div
                    class="mt-1 flex h-9 w-9 shrink-0 items-center justify-center rounded-xl"
                    :class="
                      notification.is_read
                        ? 'bg-slate-100 text-slate-500'
                        : 'bg-emerald-100 text-emerald-700'
                    "
                  >
                    <Bell :size="17" />
                  </div>

                  <div class="min-w-0 flex-1">
                    <div
                      class="flex items-start justify-between gap-2"
                    >
                      <p
                        class="text-sm font-bold text-slate-900"
                      >
                        {{
                          notification.title
                        }}
                      </p>

                      <span
                        v-if="
                          !notification.is_read
                        "
                        class="mt-1 h-2 w-2 shrink-0 rounded-full bg-emerald-500"
                      />
                    </div>

                    <p
                      class="mt-1 text-xs font-medium text-emerald-600"
                    >
                      {{
                        notificationTypeLabel(
                          notification.notification_type
                        )
                      }}
                    </p>

                    <p
                      class="mt-2 text-xs leading-5 text-slate-500"
                    >
                      {{
                        notification.message
                      }}
                    </p>

                    <p
                      class="mt-2 flex items-center gap-1 text-[11px] text-slate-400"
                    >
                      <Clock3
                        :size="12"
                      />

                      {{
                        formatNotificationDate(
                          notification.created_at
                        )
                      }}
                    </p>
                  </div>
                </button>
              </div>
            </div>
          </div>

          <div
            class="hidden rounded-full bg-slate-900 px-4 py-2 text-xs font-semibold uppercase tracking-wide text-white sm:block"
          >
            {{
              auth.state.user?.role ||
              'user'
            }}
          </div>
        </div>
      </header>

      <div
        v-if="notificationOpen"
        class="fixed inset-0 z-40"
        @click="
          notificationOpen = false
        "
      />

      <main class="p-4 sm:p-6 lg:p-8">
        <slot />
      </main>
    </div>
  </div>
</template>
