<script setup>
import {
  computed,
  onMounted,
  ref,
} from 'vue'

import {
  Bell,
  CheckCircle2,
  Megaphone,
  RefreshCw,
  Search,
  Send,
  ShieldCheck,
  UsersRound,
  X,
} from '@lucide/vue'

import AppShell from '../components/AppShell.vue'
import api from '../services/api'

const notifications = ref([])
const users = ref([])

const loading = ref(true)
const sending = ref(false)

const errorMessage = ref('')
const successMessage = ref('')

const searchQuery = ref('')
const typeFilter = ref('all')
const readFilter = ref('all')

const confirmOpen = ref(false)

const form = ref({
  recipient_mode: 'single_user',
  user_id: '',
  title: '',
  message: '',
})

const totalNotifications = computed(
  () => notifications.value.length
)

const unreadNotifications = computed(
  () =>
    notifications.value.filter(
      (item) => !item.is_read
    ).length
)

const adminAnnouncements = computed(
  () =>
    notifications.value.filter(
      (item) =>
        item.notification_type ===
        'admin_announcement'
    ).length
)

const activeUsers = computed(
  () =>
    users.value.filter(
      (user) => user.is_active
    )
)

const filteredNotifications = computed(() => {
  const query =
    searchQuery.value
      .trim()
      .toLowerCase()

  return notifications.value.filter(
    (notification) => {
      const matchesSearch =
        !query ||
        notification.user_name
          ?.toLowerCase()
          .includes(query) ||
        notification.user_email
          ?.toLowerCase()
          .includes(query) ||
        notification.title
          ?.toLowerCase()
          .includes(query) ||
        notification.message
          ?.toLowerCase()
          .includes(query) ||
        notification.booking_code
          ?.toLowerCase()
          .includes(query)

      const matchesType =
        typeFilter.value === 'all' ||
        notification.notification_type ===
          typeFilter.value

      const matchesRead =
        readFilter.value === 'all' ||
        (
          readFilter.value === 'read' &&
          notification.is_read
        ) ||
        (
          readFilter.value === 'unread' &&
          !notification.is_read
        )

      return (
        matchesSearch &&
        matchesType &&
        matchesRead
      )
    }
  )
})

const notificationTypes = computed(() => {
  return [
    ...new Set(
      notifications.value.map(
        (item) =>
          item.notification_type
      )
    ),
  ].sort()
})

const selectedRecipientName = computed(() => {
  if (
    form.value.recipient_mode ===
    'all_active'
  ) {
    return `All active users (${activeUsers.value.length})`
  }

  const user =
    activeUsers.value.find(
      (item) =>
        item.id === form.value.user_id
    )

  return (
    user?.full_name ||
    'No user selected'
  )
})

function formatDate(value) {
  if (!value) {
    return '—'
  }

  return new Intl.DateTimeFormat(
    'en-GB',
    {
      dateStyle: 'medium',
      timeStyle: 'short',
    }
  ).format(
    new Date(value)
  )
}

function typeLabel(value) {
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

async function loadData() {
  loading.value = true
  errorMessage.value = ''

  try {
    const [
      notificationResponse,
      userResponse,
    ] = await Promise.all([
      api.get(
        '/api/admin/notifications'
      ),
      api.get(
        '/api/admin/users'
      ),
    ])

    notifications.value =
      notificationResponse.data

    users.value =
      userResponse.data

    if (
      !form.value.user_id &&
      activeUsers.value.length
    ) {
      form.value.user_id =
        activeUsers.value[0].id
    }
  } catch (error) {
    errorMessage.value =
      error.response?.data?.detail ||
      'Unable to load notification management data.'
  } finally {
    loading.value = false
  }
}

function prepareSend() {
  errorMessage.value = ''
  successMessage.value = ''

  if (
    form.value.recipient_mode ===
      'single_user' &&
    !form.value.user_id
  ) {
    errorMessage.value =
      'Please select a recipient.'

    return
  }

  if (
    form.value.title.trim().length < 2
  ) {
    errorMessage.value =
      'Please enter a notification title.'

    return
  }

  if (
    form.value.message.trim().length < 2
  ) {
    errorMessage.value =
      'Please enter a notification message.'

    return
  }

  confirmOpen.value = true
}

function closeConfirm() {
  if (sending.value) {
    return
  }

  confirmOpen.value = false
}

async function sendNotification() {
  sending.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    const payload = {
      recipient_mode:
        form.value.recipient_mode,

      user_id:
        form.value.recipient_mode ===
        'single_user'
          ? form.value.user_id
          : null,

      title:
        form.value.title.trim(),

      message:
        form.value.message.trim(),
    }

    const response =
      await api.post(
        '/api/admin/notifications/send',
        payload
      )

    successMessage.value =
      response.data.message

    confirmOpen.value = false

    form.value.title = ''
    form.value.message = ''

    await loadData()
  } catch (error) {
    errorMessage.value =
      error.response?.data?.detail ||
      'Unable to send notification.'
  } finally {
    sending.value = false
  }
}

onMounted(
  loadData
)
</script>

<template>
  <AppShell>
    <main
      class="mx-auto w-full max-w-7xl px-4 py-8 sm:px-6 lg:px-8"
    >
      <section
        class="overflow-hidden rounded-3xl bg-slate-950 px-6 py-8 text-white shadow-xl sm:px-8"
      >
        <div
          class="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between"
        >
          <div>
            <div
              class="mb-4 inline-flex items-center gap-2 rounded-full bg-emerald-400/10 px-3 py-1 text-xs font-bold uppercase tracking-[0.18em] text-emerald-300 ring-1 ring-inset ring-emerald-400/20"
            >
              <ShieldCheck :size="15" />
              Communication Centre
            </div>

            <h1
              class="text-3xl font-black tracking-tight sm:text-4xl"
            >
              Notifications Management
            </h1>

            <p
              class="mt-3 max-w-2xl text-sm leading-6 text-slate-300 sm:text-base"
            >
              Monitor SmartPark system notifications and send
              administrative announcements to active users.
            </p>
          </div>

          <button
            type="button"
            class="inline-flex items-center justify-center gap-2 rounded-xl bg-white px-4 py-3 text-sm font-bold text-slate-950 transition hover:bg-emerald-50 disabled:opacity-60"
            :disabled="loading"
            @click="loadData"
          >
            <RefreshCw
              :size="17"
              :class="
                loading
                  ? 'animate-spin'
                  : ''
              "
            />

            Refresh
          </button>
        </div>
      </section>

      <div
        v-if="successMessage"
        class="mt-6 flex items-center gap-3 rounded-2xl border border-emerald-200 bg-emerald-50 p-4 text-sm font-semibold text-emerald-800"
      >
        <CheckCircle2 :size="19" />
        {{ successMessage }}
      </div>

      <div
        v-if="errorMessage"
        class="mt-6 rounded-2xl border border-rose-200 bg-rose-50 p-4 text-sm font-semibold text-rose-700"
      >
        {{ errorMessage }}
      </div>

      <section
        class="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4"
      >
        <article
          class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
        >
          <p class="text-sm font-semibold text-slate-500">
            Total Notifications
          </p>

          <p class="mt-2 text-3xl font-black text-slate-950">
            {{ totalNotifications }}
          </p>

          <Bell
            class="mt-3 text-slate-400"
            :size="20"
          />
        </article>

        <article
          class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
        >
          <p class="text-sm font-semibold text-slate-500">
            Unread
          </p>

          <p class="mt-2 text-3xl font-black text-amber-600">
            {{ unreadNotifications }}
          </p>

          <p class="mt-3 text-xs text-slate-500">
            Awaiting user attention
          </p>
        </article>

        <article
          class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
        >
          <p class="text-sm font-semibold text-slate-500">
            Admin Announcements
          </p>

          <p class="mt-2 text-3xl font-black text-violet-700">
            {{ adminAnnouncements }}
          </p>

          <Megaphone
            class="mt-3 text-violet-500"
            :size="20"
          />
        </article>

        <article
          class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
        >
          <p class="text-sm font-semibold text-slate-500">
            Active Recipients
          </p>

          <p class="mt-2 text-3xl font-black text-emerald-700">
            {{ activeUsers.length }}
          </p>

          <UsersRound
            class="mt-3 text-emerald-500"
            :size="20"
          />
        </article>
      </section>

      <section
        class="mt-6 grid gap-6 xl:grid-cols-[0.9fr_1.6fr]"
      >
        <article
          class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm"
        >
          <div
            class="flex items-center gap-3"
          >
            <div
              class="flex h-11 w-11 items-center justify-center rounded-xl bg-emerald-50 text-emerald-700"
            >
              <Send :size="20" />
            </div>

            <div>
              <h2
                class="text-xl font-black text-slate-950"
              >
                Send Announcement
              </h2>

              <p
                class="mt-1 text-sm text-slate-500"
              >
                Send to one user or all active users.
              </p>
            </div>
          </div>

          <div class="mt-6 space-y-5">
            <div>
              <label
                class="text-sm font-bold text-slate-700"
              >
                Recipient
              </label>

              <div
                class="mt-2 grid grid-cols-2 gap-2"
              >
                <button
                  type="button"
                  class="rounded-xl border px-3 py-3 text-sm font-bold transition"
                  :class="
                    form.recipient_mode === 'single_user'
                      ? 'border-emerald-500 bg-emerald-50 text-emerald-800'
                      : 'border-slate-200 text-slate-600 hover:bg-slate-50'
                  "
                  @click="
                    form.recipient_mode =
                      'single_user'
                  "
                >
                  Single User
                </button>

                <button
                  type="button"
                  class="rounded-xl border px-3 py-3 text-sm font-bold transition"
                  :class="
                    form.recipient_mode === 'all_active'
                      ? 'border-emerald-500 bg-emerald-50 text-emerald-800'
                      : 'border-slate-200 text-slate-600 hover:bg-slate-50'
                  "
                  @click="
                    form.recipient_mode =
                      'all_active'
                  "
                >
                  All Active
                </button>
              </div>
            </div>

            <div
              v-if="
                form.recipient_mode ===
                'single_user'
              "
            >
              <label
                class="text-sm font-bold text-slate-700"
              >
                User
              </label>

              <select
                v-model="form.user_id"
                class="mt-2 w-full rounded-xl border border-slate-200 bg-white px-3 py-3 text-sm font-semibold text-slate-700 outline-none focus:border-emerald-500"
              >
                <option
                  v-for="user in activeUsers"
                  :key="user.id"
                  :value="user.id"
                >
                  {{ user.full_name }}
                  — {{ user.email }}
                </option>
              </select>
            </div>

            <div>
              <label
                class="text-sm font-bold text-slate-700"
              >
                Title
              </label>

              <input
                v-model="form.title"
                maxlength="150"
                type="text"
                placeholder="e.g. Parking service update"
                class="mt-2 w-full rounded-xl border border-slate-200 px-3 py-3 text-sm outline-none focus:border-emerald-500"
              />
            </div>

            <div>
              <label
                class="text-sm font-bold text-slate-700"
              >
                Message
              </label>

              <textarea
                v-model="form.message"
                maxlength="2000"
                rows="6"
                placeholder="Write the announcement..."
                class="mt-2 w-full resize-none rounded-xl border border-slate-200 px-3 py-3 text-sm leading-6 outline-none focus:border-emerald-500"
              />

              <p
                class="mt-2 text-right text-xs text-slate-400"
              >
                {{ form.message.length }}/2000
              </p>
            </div>

            <button
              type="button"
              class="flex w-full items-center justify-center gap-2 rounded-xl bg-emerald-600 px-4 py-3 text-sm font-black text-white transition hover:bg-emerald-700"
              @click="prepareSend"
            >
              <Send :size="17" />
              Review & Send
            </button>
          </div>
        </article>

        <article
          class="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm"
        >
          <div
            class="border-b border-slate-200 p-5 sm:p-6"
          >
            <div
              class="flex flex-col gap-4"
            >
              <div>
                <h2
                  class="text-xl font-black text-slate-950"
                >
                  Notification History
                </h2>

                <p
                  class="mt-1 text-sm text-slate-500"
                >
                  {{ filteredNotifications.length }}
                  notification{{ filteredNotifications.length === 1 ? '' : 's' }}
                  shown
                </p>
              </div>

              <div
                class="grid gap-3 md:grid-cols-3"
              >
                <label class="relative">
                  <Search
                    class="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
                    :size="17"
                  />

                  <input
                    v-model="searchQuery"
                    type="search"
                    placeholder="Search..."
                    class="w-full rounded-xl border border-slate-200 py-2.5 pl-10 pr-3 text-sm outline-none focus:border-emerald-500"
                  />
                </label>

                <select
                  v-model="typeFilter"
                  class="rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm font-semibold text-slate-700"
                >
                  <option value="all">
                    All types
                  </option>

                  <option
                    v-for="type in notificationTypes"
                    :key="type"
                    :value="type"
                  >
                    {{ typeLabel(type) }}
                  </option>
                </select>

                <select
                  v-model="readFilter"
                  class="rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm font-semibold text-slate-700"
                >
                  <option value="all">
                    All statuses
                  </option>

                  <option value="unread">
                    Unread
                  </option>

                  <option value="read">
                    Read
                  </option>
                </select>
              </div>
            </div>
          </div>

          <div
            v-if="loading"
            class="flex min-h-96 items-center justify-center"
          >
            <RefreshCw
              class="animate-spin text-emerald-600"
              :size="28"
            />
          </div>

          <div
            v-else-if="
              filteredNotifications.length === 0
            "
            class="flex min-h-96 items-center justify-center p-8 text-center"
          >
            <div>
              <Bell
                class="mx-auto text-slate-300"
                :size="40"
              />

              <p
                class="mt-3 font-bold text-slate-700"
              >
                No matching notifications
              </p>
            </div>
          </div>

          <div
            v-else
            class="max-h-[720px] divide-y divide-slate-100 overflow-y-auto"
          >
            <article
              v-for="notification in filteredNotifications"
              :key="notification.id"
              class="p-5"
            >
              <div
                class="flex items-start gap-4"
              >
                <div
                  class="mt-1 flex h-10 w-10 shrink-0 items-center justify-center rounded-xl"
                  :class="
                    notification.notification_type ===
                    'admin_announcement'
                      ? 'bg-violet-50 text-violet-700'
                      : 'bg-emerald-50 text-emerald-700'
                  "
                >
                  <Megaphone
                    v-if="
                      notification.notification_type ===
                      'admin_announcement'
                    "
                    :size="18"
                  />

                  <Bell
                    v-else
                    :size="18"
                  />
                </div>

                <div class="min-w-0 flex-1">
                  <div
                    class="flex flex-wrap items-center gap-2"
                  >
                    <p
                      class="font-black text-slate-900"
                    >
                      {{ notification.title }}
                    </p>

                    <span
                      class="rounded-full px-2 py-0.5 text-[10px] font-black uppercase"
                      :class="
                        notification.is_read
                          ? 'bg-slate-100 text-slate-500'
                          : 'bg-amber-50 text-amber-700'
                      "
                    >
                      {{
                        notification.is_read
                          ? 'Read'
                          : 'Unread'
                      }}
                    </span>
                  </div>

                  <p
                    class="mt-1 text-xs font-semibold text-emerald-700"
                  >
                    {{ notification.user_name }}
                    · {{ notification.user_email }}
                  </p>

                  <p
                    class="mt-3 text-sm leading-6 text-slate-600"
                  >
                    {{ notification.message }}
                  </p>

                  <div
                    class="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-xs text-slate-400"
                  >
                    <span>
                      {{ typeLabel(notification.notification_type) }}
                    </span>

                    <span>
                      {{ formatDate(notification.created_at) }}
                    </span>

                    <span
                      v-if="notification.booking_code"
                    >
                      {{ notification.booking_code }}
                    </span>
                  </div>
                </div>
              </div>
            </article>
          </div>
        </article>
      </section>
    </main>

    <Teleport to="body">
      <div
        v-if="confirmOpen"
        class="fixed inset-0 z-[100] flex items-center justify-center bg-slate-950/60 p-4 backdrop-blur-sm"
        @click.self="closeConfirm"
      >
        <div
          class="w-full max-w-md overflow-hidden rounded-3xl bg-white shadow-2xl"
        >
          <div
            class="flex items-start justify-between border-b border-slate-200 p-6"
          >
            <div>
              <div
                class="mb-3 flex h-11 w-11 items-center justify-center rounded-xl bg-emerald-50 text-emerald-700"
              >
                <Megaphone :size="21" />
              </div>

              <h3
                class="text-xl font-black text-slate-950"
              >
                Confirm announcement
              </h3>
            </div>

            <button
              type="button"
              class="rounded-lg p-2 text-slate-400 hover:bg-slate-100"
              @click="closeConfirm"
            >
              <X :size="20" />
            </button>
          </div>

          <div class="space-y-4 p-6">
            <div
              class="rounded-2xl bg-slate-50 p-4"
            >
              <p
                class="text-xs font-bold uppercase text-slate-400"
              >
                Recipient
              </p>

              <p
                class="mt-1 font-bold text-slate-900"
              >
                {{ selectedRecipientName }}
              </p>
            </div>

            <div
              class="rounded-2xl bg-slate-50 p-4"
            >
              <p
                class="font-black text-slate-900"
              >
                {{ form.title }}
              </p>

              <p
                class="mt-2 text-sm leading-6 text-slate-600"
              >
                {{ form.message }}
              </p>
            </div>

            <p
              v-if="
                form.recipient_mode ===
                'all_active'
              "
              class="text-sm font-semibold text-amber-700"
            >
              This announcement will be sent to every active user.
            </p>
          </div>

          <div
            class="flex gap-3 border-t border-slate-200 p-6"
          >
            <button
              type="button"
              class="flex-1 rounded-xl border border-slate-200 px-4 py-3 text-sm font-bold text-slate-700 hover:bg-slate-50"
              :disabled="sending"
              @click="closeConfirm"
            >
              Cancel
            </button>

            <button
              type="button"
              class="flex flex-1 items-center justify-center gap-2 rounded-xl bg-emerald-600 px-4 py-3 text-sm font-bold text-white hover:bg-emerald-700 disabled:opacity-60"
              :disabled="sending"
              @click="sendNotification"
            >
              <RefreshCw
                v-if="sending"
                class="animate-spin"
                :size="16"
              />

              <Send
                v-else
                :size="16"
              />

              {{
                sending
                  ? 'Sending...'
                  : 'Send announcement'
              }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </AppShell>
</template>
