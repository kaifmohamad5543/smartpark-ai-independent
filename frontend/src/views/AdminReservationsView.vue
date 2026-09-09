<script setup>
import {
  computed,
  onMounted,
  ref,
} from 'vue'

import {
  CalendarCheck2,
  CarFront,
  CheckCircle2,
  Clock3,
  Eye,
  MapPinned,
  RefreshCw,
  Search,
  ShieldCheck,
  X,
  XCircle,
} from '@lucide/vue'

import AppShell from '../components/AppShell.vue'
import api from '../services/api'

const reservations = ref([])
const loading = ref(true)
const errorMessage = ref('')

const searchQuery = ref('')
const statusFilter = ref('all')
const locationFilter = ref('all')

const selectedReservation = ref(null)
const detailOpen = ref(false)

const totalReservations = computed(
  () => reservations.value.length
)

const confirmedCount = computed(
  () =>
    reservations.value.filter(
      (item) =>
        item.status === 'confirmed'
    ).length
)

const completedCount = computed(
  () =>
    reservations.value.filter(
      (item) =>
        item.status === 'completed'
    ).length
)

const cancelledCount = computed(
  () =>
    reservations.value.filter(
      (item) =>
        item.status === 'cancelled'
    ).length
)

const checkedInCount = computed(
  () =>
    reservations.value.filter(
      (item) =>
        item.status === 'checked_in'
    ).length
)

const locations = computed(() => {
  return [
    ...new Set(
      reservations.value.map(
        (item) =>
          item.parking_location_name
      )
    ),
  ].sort()
})

const filteredReservations =
  computed(() => {
    const query =
      searchQuery.value
        .trim()
        .toLowerCase()

    return reservations.value.filter(
      (reservation) => {
        const matchesSearch =
          !query ||
          reservation.booking_code
            ?.toLowerCase()
            .includes(query) ||
          reservation.user_name
            ?.toLowerCase()
            .includes(query) ||
          reservation.user_email
            ?.toLowerCase()
            .includes(query) ||
          reservation.vehicle_registration
            ?.toLowerCase()
            .includes(query) ||
          reservation.parking_location_name
            ?.toLowerCase()
            .includes(query)

        const matchesStatus =
          statusFilter.value === 'all' ||
          reservation.status ===
            statusFilter.value

        const matchesLocation =
          locationFilter.value === 'all' ||
          reservation.parking_location_name ===
            locationFilter.value

        return (
          matchesSearch &&
          matchesStatus &&
          matchesLocation
        )
      }
    )
  })

function money(value) {
  if (
    value === null ||
    value === undefined
  ) {
    return '—'
  }

  return new Intl.NumberFormat(
    'en-GB',
    {
      style: 'currency',
      currency: 'GBP',
    }
  ).format(
    Number(value)
  )
}

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

function statusLabel(value) {
  return value
    ?.replaceAll('_', ' ')
    ?.replace(
      /\b\w/g,
      (letter) =>
        letter.toUpperCase()
    )
}

function statusClasses(value) {
  if (value === 'completed') {
    return (
      'bg-emerald-50 ' +
      'text-emerald-700 ' +
      'ring-emerald-600/20'
    )
  }

  if (value === 'confirmed') {
    return (
      'bg-blue-50 ' +
      'text-blue-700 ' +
      'ring-blue-600/20'
    )
  }

  if (value === 'checked_in') {
    return (
      'bg-violet-50 ' +
      'text-violet-700 ' +
      'ring-violet-600/20'
    )
  }

  if (value === 'cancelled') {
    return (
      'bg-rose-50 ' +
      'text-rose-700 ' +
      'ring-rose-600/20'
    )
  }

  return (
    'bg-slate-100 ' +
    'text-slate-700 ' +
    'ring-slate-600/20'
  )
}

async function loadReservations() {
  loading.value = true
  errorMessage.value = ''

  try {
    const response =
      await api.get(
        '/api/admin/reservations'
      )

    reservations.value =
      response.data
  } catch (error) {
    errorMessage.value =
      error.response?.data?.detail ||
      'Unable to load reservations.'
  } finally {
    loading.value = false
  }
}

function openDetails(reservation) {
  selectedReservation.value =
    reservation

  detailOpen.value = true
}

function closeDetails() {
  detailOpen.value = false
  selectedReservation.value = null
}

onMounted(
  loadReservations
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
              Reservation Control
            </div>

            <h1
              class="text-3xl font-black tracking-tight sm:text-4xl"
            >
              Reservation Management
            </h1>

            <p
              class="mt-3 max-w-2xl text-sm leading-6 text-slate-300 sm:text-base"
            >
              Review reservations across the SmartPark network,
              including customers, vehicles, parking spaces,
              booking status and costs.
            </p>
          </div>

          <button
            type="button"
            class="inline-flex items-center justify-center gap-2 rounded-xl bg-white px-4 py-3 text-sm font-bold text-slate-950 transition hover:bg-emerald-50 disabled:opacity-60"
            :disabled="loading"
            @click="loadReservations"
          >
            <RefreshCw
              :size="17"
              :class="
                loading
                  ? 'animate-spin'
                  : ''
              "
            />
            Refresh reservations
          </button>
        </div>
      </section>

      <div
        v-if="errorMessage"
        class="mt-6 rounded-2xl border border-rose-200 bg-rose-50 p-4 text-sm font-semibold text-rose-700"
      >
        {{ errorMessage }}
      </div>

      <section
        class="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-5"
      >
        <article
          class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
        >
          <p class="text-sm font-semibold text-slate-500">
            Total Reservations
          </p>

          <p class="mt-2 text-3xl font-black text-slate-950">
            {{ totalReservations }}
          </p>

          <CalendarCheck2
            class="mt-3 text-slate-400"
            :size="20"
          />
        </article>

        <article
          class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
        >
          <p class="text-sm font-semibold text-slate-500">
            Confirmed
          </p>

          <p class="mt-2 text-3xl font-black text-blue-700">
            {{ confirmedCount }}
          </p>

          <Clock3
            class="mt-3 text-blue-500"
            :size="20"
          />
        </article>

        <article
          class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
        >
          <p class="text-sm font-semibold text-slate-500">
            Checked In
          </p>

          <p class="mt-2 text-3xl font-black text-violet-700">
            {{ checkedInCount }}
          </p>

          <CarFront
            class="mt-3 text-violet-500"
            :size="20"
          />
        </article>

        <article
          class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
        >
          <p class="text-sm font-semibold text-slate-500">
            Completed
          </p>

          <p class="mt-2 text-3xl font-black text-emerald-700">
            {{ completedCount }}
          </p>

          <CheckCircle2
            class="mt-3 text-emerald-500"
            :size="20"
          />
        </article>

        <article
          class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
        >
          <p class="text-sm font-semibold text-slate-500">
            Cancelled
          </p>

          <p class="mt-2 text-3xl font-black text-rose-700">
            {{ cancelledCount }}
          </p>

          <XCircle
            class="mt-3 text-rose-500"
            :size="20"
          />
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
                All Reservations
              </h2>

              <p
                class="mt-1 text-sm text-slate-500"
              >
                {{ filteredReservations.length }}
                reservation{{ filteredReservations.length === 1 ? '' : 's' }}
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
                  placeholder="Search booking..."
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

                <option value="confirmed">
                  Confirmed
                </option>

                <option value="checked_in">
                  Checked In
                </option>

                <option value="completed">
                  Completed
                </option>

                <option value="cancelled">
                  Cancelled
                </option>
              </select>

              <select
                v-model="locationFilter"
                class="rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm font-semibold text-slate-700 outline-none"
              >
                <option value="all">
                  All locations
                </option>

                <option
                  v-for="location in locations"
                  :key="location"
                  :value="location"
                >
                  {{ location }}
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
              Loading reservations...
            </p>
          </div>
        </div>

        <div
          v-else-if="filteredReservations.length === 0"
          class="flex min-h-72 items-center justify-center p-8 text-center"
        >
          <div>
            <CalendarCheck2
              class="mx-auto text-slate-300"
              :size="38"
            />

            <p
              class="mt-3 font-bold text-slate-700"
            >
              No matching reservations
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
                  Booking
                </th>

                <th class="px-6 py-4">
                  Customer
                </th>

                <th class="px-6 py-4">
                  Vehicle
                </th>

                <th class="px-6 py-4">
                  Parking
                </th>

                <th class="px-6 py-4">
                  Reservation
                </th>

                <th class="px-6 py-4">
                  Cost
                </th>

                <th class="px-6 py-4">
                  Status
                </th>

                <th class="px-6 py-4 text-right">
                  Details
                </th>
              </tr>
            </thead>

            <tbody
              class="divide-y divide-slate-100"
            >
              <tr
                v-for="reservation in filteredReservations"
                :key="reservation.id"
                class="transition hover:bg-slate-50"
              >
                <td
                  class="whitespace-nowrap px-6 py-4"
                >
                  <p
                    class="font-black text-slate-900"
                  >
                    {{ reservation.booking_code }}
                  </p>

                  <p
                    class="mt-1 text-xs text-slate-400"
                  >
                    {{ formatDate(reservation.created_at) }}
                  </p>
                </td>

                <td class="px-6 py-4">
                  <p
                    class="font-semibold text-slate-800"
                  >
                    {{ reservation.user_name }}
                  </p>

                  <p
                    class="mt-1 text-xs text-slate-500"
                  >
                    {{ reservation.user_email }}
                  </p>
                </td>

                <td
                  class="whitespace-nowrap px-6 py-4"
                >
                  <p
                    class="font-bold text-slate-800"
                  >
                    {{ reservation.vehicle_registration }}
                  </p>

                  <p
                    class="mt-1 text-xs text-slate-500"
                  >
                    {{ reservation.vehicle_make }}
                    {{ reservation.vehicle_model }}
                  </p>
                </td>

                <td class="px-6 py-4">
                  <div
                    class="flex items-start gap-2"
                  >
                    <MapPinned
                      class="mt-0.5 shrink-0 text-emerald-600"
                      :size="16"
                    />

                    <div>
                      <p
                        class="font-semibold text-slate-800"
                      >
                        {{ reservation.parking_location_name }}
                      </p>

                      <p
                        class="mt-1 text-xs text-slate-500"
                      >
                        Space
                        {{ reservation.parking_space_number }}
                        ·
                        {{ reservation.parking_space_type }}
                      </p>
                    </div>
                  </div>
                </td>

                <td
                  class="whitespace-nowrap px-6 py-4 text-sm text-slate-600"
                >
                  <p>
                    {{ formatDate(reservation.reserved_from) }}
                  </p>

                  <p
                    class="mt-1 text-xs text-slate-400"
                  >
                    to
                    {{ formatDate(reservation.reserved_until) }}
                  </p>
                </td>

                <td
                  class="whitespace-nowrap px-6 py-4"
                >
                  <p
                    class="text-sm font-black text-slate-900"
                  >
                    {{
                      reservation.final_cost !== null
                        ? money(reservation.final_cost)
                        : money(reservation.estimated_cost)
                    }}
                  </p>

                  <p
                    class="mt-1 text-xs text-slate-500"
                  >
                    {{
                      reservation.final_cost !== null
                        ? 'Final cost'
                        : 'Estimated'
                    }}
                  </p>
                </td>

                <td
                  class="whitespace-nowrap px-6 py-4"
                >
                  <span
                    class="inline-flex rounded-full px-2.5 py-1 text-xs font-bold ring-1 ring-inset"
                    :class="statusClasses(reservation.status)"
                  >
                    {{ statusLabel(reservation.status) }}
                  </span>
                </td>

                <td
                  class="whitespace-nowrap px-6 py-4 text-right"
                >
                  <button
                    type="button"
                    class="inline-flex items-center gap-2 rounded-lg bg-slate-100 px-3 py-2 text-xs font-bold text-slate-700 transition hover:bg-slate-200"
                    @click="openDetails(reservation)"
                  >
                    <Eye :size="14" />
                    View
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
        v-if="detailOpen"
        class="fixed inset-0 z-[100] flex items-center justify-center bg-slate-950/60 p-4 backdrop-blur-sm"
        @click.self="closeDetails"
      >
        <div
          v-if="selectedReservation"
          class="max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-3xl bg-white shadow-2xl"
        >
          <div
            class="flex items-start justify-between border-b border-slate-200 p-6"
          >
            <div>
              <p
                class="text-xs font-bold uppercase tracking-wider text-emerald-700"
              >
                Reservation Details
              </p>

              <h3
                class="mt-1 text-2xl font-black text-slate-950"
              >
                {{ selectedReservation.booking_code }}
              </h3>
            </div>

            <button
              type="button"
              class="rounded-lg p-2 text-slate-400 hover:bg-slate-100"
              @click="closeDetails"
            >
              <X :size="20" />
            </button>
          </div>

          <div
            class="grid gap-4 p-6 sm:grid-cols-2"
          >
            <div class="rounded-2xl bg-slate-50 p-4">
              <p class="text-xs font-bold uppercase text-slate-400">
                Customer
              </p>

              <p class="mt-2 font-bold text-slate-900">
                {{ selectedReservation.user_name }}
              </p>

              <p class="mt-1 text-sm text-slate-500">
                {{ selectedReservation.user_email }}
              </p>
            </div>

            <div class="rounded-2xl bg-slate-50 p-4">
              <p class="text-xs font-bold uppercase text-slate-400">
                Vehicle
              </p>

              <p class="mt-2 font-bold text-slate-900">
                {{ selectedReservation.vehicle_registration }}
              </p>

              <p class="mt-1 text-sm text-slate-500">
                {{ selectedReservation.vehicle_make }}
                {{ selectedReservation.vehicle_model }}
              </p>
            </div>

            <div class="rounded-2xl bg-slate-50 p-4 sm:col-span-2">
              <p class="text-xs font-bold uppercase text-slate-400">
                Parking
              </p>

              <p class="mt-2 font-bold text-slate-900">
                {{ selectedReservation.parking_location_name }}
              </p>

              <p class="mt-1 text-sm text-slate-500">
                Space
                {{ selectedReservation.parking_space_number }}
                ·
                {{ selectedReservation.parking_space_type }}
              </p>
            </div>

            <div class="rounded-2xl bg-slate-50 p-4">
              <p class="text-xs font-bold uppercase text-slate-400">
                Reserved From
              </p>

              <p class="mt-2 text-sm font-semibold text-slate-800">
                {{ formatDate(selectedReservation.reserved_from) }}
              </p>
            </div>

            <div class="rounded-2xl bg-slate-50 p-4">
              <p class="text-xs font-bold uppercase text-slate-400">
                Reserved Until
              </p>

              <p class="mt-2 text-sm font-semibold text-slate-800">
                {{ formatDate(selectedReservation.reserved_until) }}
              </p>
            </div>

            <div class="rounded-2xl bg-slate-50 p-4">
              <p class="text-xs font-bold uppercase text-slate-400">
                Estimated Cost
              </p>

              <p class="mt-2 font-black text-slate-900">
                {{ money(selectedReservation.estimated_cost) }}
              </p>
            </div>

            <div class="rounded-2xl bg-slate-50 p-4">
              <p class="text-xs font-bold uppercase text-slate-400">
                Final Cost
              </p>

              <p class="mt-2 font-black text-slate-900">
                {{ money(selectedReservation.final_cost) }}
              </p>
            </div>

            <div class="rounded-2xl bg-slate-50 p-4">
              <p class="text-xs font-bold uppercase text-slate-400">
                Check In
              </p>

              <p class="mt-2 text-sm font-semibold text-slate-800">
                {{ formatDate(selectedReservation.checked_in_at) }}
              </p>
            </div>

            <div class="rounded-2xl bg-slate-50 p-4">
              <p class="text-xs font-bold uppercase text-slate-400">
                Check Out
              </p>

              <p class="mt-2 text-sm font-semibold text-slate-800">
                {{ formatDate(selectedReservation.checked_out_at) }}
              </p>
            </div>

            <div
              v-if="selectedReservation.cancelled_at"
              class="rounded-2xl bg-rose-50 p-4 sm:col-span-2"
            >
              <p class="text-xs font-bold uppercase text-rose-500">
                Cancelled At
              </p>

              <p class="mt-2 text-sm font-semibold text-rose-800">
                {{ formatDate(selectedReservation.cancelled_at) }}
              </p>
            </div>
          </div>

          <div
            class="border-t border-slate-200 p-6"
          >
            <button
              type="button"
              class="w-full rounded-xl bg-slate-950 px-4 py-3 text-sm font-bold text-white hover:bg-slate-800"
              @click="closeDetails"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </AppShell>
</template>
