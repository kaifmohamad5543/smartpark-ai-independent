<script setup>
import {
  computed,
  onMounted,
  ref,
} from 'vue'

import {
  RefreshCw,
  Search,
  ShieldCheck,
  UserCheck,
  UsersRound,
  UserX,
  X,
} from '@lucide/vue'

import AppShell from '../components/AppShell.vue'
import api from '../services/api'
import { auth } from '../stores/auth'

const users = ref([])
const loading = ref(true)
const errorMessage = ref('')
const successMessage = ref('')

const searchQuery = ref('')
const statusFilter = ref('all')
const roleFilter = ref('all')

const selectedUser = ref(null)
const statusModalOpen = ref(false)
const statusLoading = ref(false)

const totalUsers = computed(
  () => users.value.length
)

const activeUsers = computed(
  () =>
    users.value.filter(
      (user) => user.is_active
    ).length
)

const inactiveUsers = computed(
  () =>
    users.value.filter(
      (user) => !user.is_active
    ).length
)

const adminUsers = computed(
  () =>
    users.value.filter(
      (user) => user.role === 'admin'
    ).length
)

const filteredUsers = computed(() => {
  const query =
    searchQuery.value
      .trim()
      .toLowerCase()

  return users.value.filter(
    (user) => {
      const matchesSearch =
        !query ||
        user.full_name
          ?.toLowerCase()
          .includes(query) ||
        user.email
          ?.toLowerCase()
          .includes(query)

      const matchesStatus =
        statusFilter.value === 'all' ||
        (
          statusFilter.value === 'active' &&
          user.is_active
        ) ||
        (
          statusFilter.value === 'inactive' &&
          !user.is_active
        )

      const matchesRole =
        roleFilter.value === 'all' ||
        user.role === roleFilter.value

      return (
        matchesSearch &&
        matchesStatus &&
        matchesRole
      )
    }
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

function isCurrentAdmin(user) {
  return (
    user.id ===
    auth.state.user?.id
  )
}

async function loadUsers() {
  loading.value = true
  errorMessage.value = ''

  try {
    const response =
      await api.get(
        '/api/admin/users'
      )

    users.value =
      response.data
  } catch (error) {
    errorMessage.value =
      error.response?.data?.detail ||
      'Unable to load users.'
  } finally {
    loading.value = false
  }
}

function openStatusModal(user) {
  selectedUser.value = user
  statusModalOpen.value = true
  errorMessage.value = ''
  successMessage.value = ''
}

function closeStatusModal() {
  if (statusLoading.value) {
    return
  }

  statusModalOpen.value = false
  selectedUser.value = null
}

async function confirmStatusChange() {
  if (!selectedUser.value) {
    return
  }

  statusLoading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  const newStatus =
    !selectedUser.value.is_active

  try {
    const response =
      await api.patch(
        `/api/admin/users/${selectedUser.value.id}/status`,
        {
          is_active: newStatus,
        }
      )

    const index =
      users.value.findIndex(
        (user) =>
          user.id ===
          response.data.id
      )

    if (index !== -1) {
      users.value[index] =
        response.data
    }

    successMessage.value =
      `${response.data.full_name} was ${
        response.data.is_active
          ? 'activated'
          : 'deactivated'
      } successfully.`

    statusModalOpen.value = false
    selectedUser.value = null
  } catch (error) {
    errorMessage.value =
      error.response?.data?.detail ||
      'Unable to update user status.'
  } finally {
    statusLoading.value = false
  }
}

onMounted(
  loadUsers
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
              Administrator Control
            </div>

            <h1
              class="text-3xl font-black tracking-tight sm:text-4xl"
            >
              User Management
            </h1>

            <p
              class="mt-3 max-w-2xl text-sm leading-6 text-slate-300 sm:text-base"
            >
              Review registered SmartPark users and safely
              activate or deactivate user accounts.
            </p>
          </div>

          <button
            type="button"
            class="inline-flex items-center justify-center gap-2 rounded-xl bg-white px-4 py-3 text-sm font-bold text-slate-950 transition hover:bg-emerald-50 disabled:opacity-60"
            :disabled="loading"
            @click="loadUsers"
          >
            <RefreshCw
              :size="17"
              :class="
                loading
                  ? 'animate-spin'
                  : ''
              "
            />
            Refresh users
          </button>
        </div>
      </section>

      <div
        v-if="successMessage"
        class="mt-6 rounded-2xl border border-emerald-200 bg-emerald-50 p-4 text-sm font-semibold text-emerald-800"
      >
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
            Registered Users
          </p>

          <p class="mt-2 text-3xl font-black text-slate-950">
            {{ totalUsers }}
          </p>

          <p class="mt-3 text-xs text-slate-500">
            All SmartPark accounts
          </p>
        </article>

        <article
          class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
        >
          <p class="text-sm font-semibold text-slate-500">
            Active Users
          </p>

          <p class="mt-2 text-3xl font-black text-emerald-700">
            {{ activeUsers }}
          </p>

          <p class="mt-3 text-xs text-slate-500">
            Accounts allowed to sign in
          </p>
        </article>

        <article
          class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
        >
          <p class="text-sm font-semibold text-slate-500">
            Inactive Users
          </p>

          <p class="mt-2 text-3xl font-black text-rose-700">
            {{ inactiveUsers }}
          </p>

          <p class="mt-3 text-xs text-slate-500">
            Accounts currently disabled
          </p>
        </article>

        <article
          class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
        >
          <p class="text-sm font-semibold text-slate-500">
            Administrators
          </p>

          <p class="mt-2 text-3xl font-black text-violet-700">
            {{ adminUsers }}
          </p>

          <p class="mt-3 text-xs text-slate-500">
            Accounts with admin role
          </p>
        </article>
      </section>

      <section
        class="mt-6 overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm"
      >
        <div
          class="border-b border-slate-200 p-5 sm:p-6"
        >
          <div
            class="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between"
          >
            <div>
              <h2
                class="text-xl font-black text-slate-950"
              >
                Registered Accounts
              </h2>

              <p
                class="mt-1 text-sm text-slate-500"
              >
                {{ filteredUsers.length }}
                user{{ filteredUsers.length === 1 ? '' : 's' }}
                shown
              </p>
            </div>

            <div
              class="grid gap-3 sm:grid-cols-3"
            >
              <label class="relative">
                <Search
                  class="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
                  :size="17"
                />

                <input
                  v-model="searchQuery"
                  type="search"
                  placeholder="Search users..."
                  class="w-full rounded-xl border border-slate-200 py-2.5 pl-10 pr-3 text-sm font-medium outline-none focus:border-emerald-500"
                />
              </label>

              <select
                v-model="statusFilter"
                class="rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm font-semibold text-slate-700 outline-none"
              >
                <option value="all">
                  All statuses
                </option>

                <option value="active">
                  Active
                </option>

                <option value="inactive">
                  Inactive
                </option>
              </select>

              <select
                v-model="roleFilter"
                class="rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm font-semibold text-slate-700 outline-none"
              >
                <option value="all">
                  All roles
                </option>

                <option value="user">
                  User
                </option>

                <option value="admin">
                  Admin
                </option>
              </select>
            </div>
          </div>
        </div>

        <div
          v-if="loading"
          class="flex min-h-72 items-center justify-center"
        >
          <div class="text-center">
            <RefreshCw
              class="mx-auto animate-spin text-emerald-600"
              :size="28"
            />

            <p
              class="mt-3 text-sm font-semibold text-slate-500"
            >
              Loading users...
            </p>
          </div>
        </div>

        <div
          v-else-if="filteredUsers.length === 0"
          class="flex min-h-72 items-center justify-center p-8 text-center"
        >
          <div>
            <UsersRound
              class="mx-auto text-slate-300"
              :size="38"
            />

            <p
              class="mt-3 font-bold text-slate-700"
            >
              No matching users
            </p>
          </div>
        </div>

        <div
          v-else
          class="overflow-x-auto"
        >
          <table
            class="min-w-full divide-y divide-slate-200"
          >
            <thead class="bg-slate-50">
              <tr
                class="text-left text-xs font-bold uppercase tracking-wider text-slate-500"
              >
                <th class="px-6 py-4">
                  User
                </th>

                <th class="px-6 py-4">
                  Role
                </th>

                <th class="px-6 py-4">
                  Status
                </th>

                <th class="px-6 py-4">
                  Registered
                </th>

                <th class="px-6 py-4 text-right">
                  Action
                </th>
              </tr>
            </thead>

            <tbody
              class="divide-y divide-slate-100"
            >
              <tr
                v-for="user in filteredUsers"
                :key="user.id"
                class="transition hover:bg-slate-50"
              >
                <td class="px-6 py-4">
                  <div
                    class="flex items-center gap-3"
                  >
                    <div
                      class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-slate-100 text-sm font-black text-slate-700"
                    >
                      {{
                        user.full_name
                          .split(/\s+/)
                          .slice(0, 2)
                          .map((part) => part[0])
                          .join('')
                          .toUpperCase()
                      }}
                    </div>

                    <div>
                      <div
                        class="flex items-center gap-2"
                      >
                        <p
                          class="font-bold text-slate-900"
                        >
                          {{ user.full_name }}
                        </p>

                        <span
                          v-if="isCurrentAdmin(user)"
                          class="rounded-full bg-violet-50 px-2 py-0.5 text-[10px] font-black uppercase text-violet-700"
                        >
                          You
                        </span>
                      </div>

                      <p
                        class="mt-1 text-xs text-slate-500"
                      >
                        {{ user.email }}
                      </p>
                    </div>
                  </div>
                </td>

                <td
                  class="whitespace-nowrap px-6 py-4"
                >
                  <span
                    class="inline-flex rounded-full px-2.5 py-1 text-xs font-bold capitalize ring-1 ring-inset"
                    :class="
                      user.role === 'admin'
                        ? 'bg-violet-50 text-violet-700 ring-violet-600/20'
                        : 'bg-slate-100 text-slate-700 ring-slate-600/20'
                    "
                  >
                    {{ user.role }}
                  </span>
                </td>

                <td
                  class="whitespace-nowrap px-6 py-4"
                >
                  <span
                    class="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-bold ring-1 ring-inset"
                    :class="
                      user.is_active
                        ? 'bg-emerald-50 text-emerald-700 ring-emerald-600/20'
                        : 'bg-rose-50 text-rose-700 ring-rose-600/20'
                    "
                  >
                    <span
                      class="h-1.5 w-1.5 rounded-full"
                      :class="
                        user.is_active
                          ? 'bg-emerald-500'
                          : 'bg-rose-500'
                      "
                    />

                    {{
                      user.is_active
                        ? 'Active'
                        : 'Inactive'
                    }}
                  </span>
                </td>

                <td
                  class="whitespace-nowrap px-6 py-4 text-sm text-slate-500"
                >
                  {{ formatDate(user.created_at) }}
                </td>

                <td
                  class="whitespace-nowrap px-6 py-4 text-right"
                >
                  <span
                    v-if="isCurrentAdmin(user)"
                    class="text-xs font-semibold text-slate-400"
                  >
                    Protected account
                  </span>

                  <button
                    v-else
                    type="button"
                    class="inline-flex items-center gap-2 rounded-lg px-3 py-2 text-xs font-bold transition"
                    :class="
                      user.is_active
                        ? 'bg-rose-50 text-rose-700 hover:bg-rose-100'
                        : 'bg-emerald-50 text-emerald-700 hover:bg-emerald-100'
                    "
                    @click="openStatusModal(user)"
                  >
                    <UserX
                      v-if="user.is_active"
                      :size="14"
                    />

                    <UserCheck
                      v-else
                      :size="14"
                    />

                    {{
                      user.is_active
                        ? 'Deactivate'
                        : 'Activate'
                    }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </main>

    <Teleport to="body">
      <div
        v-if="statusModalOpen"
        class="fixed inset-0 z-[100] flex items-center justify-center bg-slate-950/60 p-4 backdrop-blur-sm"
        @click.self="closeStatusModal"
      >
        <div
          class="w-full max-w-md overflow-hidden rounded-3xl bg-white shadow-2xl"
        >
          <div
            class="flex items-start justify-between border-b border-slate-200 p-6"
          >
            <div>
              <div
                class="mb-3 flex h-11 w-11 items-center justify-center rounded-xl"
                :class="
                  selectedUser?.is_active
                    ? 'bg-rose-50 text-rose-700'
                    : 'bg-emerald-50 text-emerald-700'
                "
              >
                <UserX
                  v-if="selectedUser?.is_active"
                  :size="21"
                />

                <UserCheck
                  v-else
                  :size="21"
                />
              </div>

              <h3
                class="text-xl font-black text-slate-950"
              >
                {{
                  selectedUser?.is_active
                    ? 'Deactivate user'
                    : 'Activate user'
                }}
              </h3>
            </div>

            <button
              type="button"
              class="rounded-lg p-2 text-slate-400 hover:bg-slate-100"
              @click="closeStatusModal"
            >
              <X :size="20" />
            </button>
          </div>

          <div
            v-if="selectedUser"
            class="p-6"
          >
            <p
              class="text-sm leading-6 text-slate-600"
            >
              {{
                selectedUser.is_active
                  ? 'This user will no longer be able to sign in until their account is activated again.'
                  : 'This user will be able to sign in and use SmartPark AI again.'
              }}
            </p>

            <div
              class="mt-5 rounded-2xl bg-slate-50 p-4"
            >
              <p
                class="font-bold text-slate-900"
              >
                {{ selectedUser.full_name }}
              </p>

              <p
                class="mt-1 text-sm text-slate-500"
              >
                {{ selectedUser.email }}
              </p>
            </div>
          </div>

          <div
            class="flex gap-3 border-t border-slate-200 p-6"
          >
            <button
              type="button"
              class="flex-1 rounded-xl border border-slate-200 px-4 py-3 text-sm font-bold text-slate-700 hover:bg-slate-50"
              :disabled="statusLoading"
              @click="closeStatusModal"
            >
              Cancel
            </button>

            <button
              type="button"
              class="flex flex-1 items-center justify-center gap-2 rounded-xl px-4 py-3 text-sm font-bold text-white disabled:opacity-60"
              :class="
                selectedUser?.is_active
                  ? 'bg-rose-600 hover:bg-rose-700'
                  : 'bg-emerald-600 hover:bg-emerald-700'
              "
              :disabled="statusLoading"
              @click="confirmStatusChange"
            >
              <RefreshCw
                v-if="statusLoading"
                class="animate-spin"
                :size="16"
              />

              {{
                statusLoading
                  ? 'Updating...'
                  : selectedUser?.is_active
                    ? 'Confirm deactivation'
                    : 'Confirm activation'
              }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </AppShell>
</template>
