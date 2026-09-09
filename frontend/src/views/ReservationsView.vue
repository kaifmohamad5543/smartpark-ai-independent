<script setup>
import {
  computed,
  nextTick,
  onMounted,
  onUnmounted,
  ref,
} from 'vue'

import {
  CalendarDays,
  CarFront,
  CheckCircle2,
  Clock3,
  CreditCard,
  LogIn,
  LogOut,
  MapPin,
  RefreshCw,
  ScanLine,
  Timer,
  TicketCheck,
  WalletCards,
  X,
  XCircle,
} from '@lucide/vue'

import JsBarcode from 'jsbarcode'
import AppShell from '../components/AppShell.vue'
import api from '../services/api'

const reservations = ref([])
const locations = ref([])
const vehicles = ref([])

const loading = ref(true)
const actionId = ref(null)

const errorMessage = ref('')
const successMessage = ref('')

const checkoutMethods = ref({})

const filter = ref('all')

const currentTime = ref(Date.now())

const scannerOpen = ref(false)
const scannerVideo = ref(null)
const scannerReservation = ref(null)
const scannerMessage = ref('')
const scannerError = ref('')

let timerInterval = null
let scannerControls = null
let codeReader = null

function renderBarcode(element, value) {
  if (!element || !value) {
    return
  }

  JsBarcode(
    element,
    String(value),
    {
      format: 'CODE128',
      width: 2,
      height: 52,
      displayValue: true,
      fontSize: 13,
      margin: 8,
      background: '#ffffff',
      lineColor: '#0f172a',
    }
  )
}

const vBarcode = {
  mounted(element, binding) {
    renderBarcode(
      element,
      binding.value
    )
  },

  updated(element, binding) {
    if (
      binding.value !==
      binding.oldValue
    ) {
      renderBarcode(
        element,
        binding.value
      )
    }
  },
}

const filteredReservations = computed(() => {
  if (filter.value === 'all') {
    return reservations.value
  }

  return reservations.value.filter(
    (reservation) =>
      reservation.status === filter.value
  )
})

const stats = computed(() => ({
  total: reservations.value.length,

  confirmed:
    reservations.value.filter(
      (item) =>
        item.status === 'confirmed'
    ).length,

  active:
    reservations.value.filter(
      (item) =>
        item.status === 'checked_in'
    ).length,

  completed:
    reservations.value.filter(
      (item) =>
        item.status === 'completed'
    ).length,
}))

function formatDuration(milliseconds) {
  const totalSeconds = Math.max(
    0,
    Math.floor(
      milliseconds / 1000
    )
  )

  const hours = Math.floor(
    totalSeconds / 3600
  )

  const minutes = Math.floor(
    (totalSeconds % 3600) / 60
  )

  const seconds =
    totalSeconds % 60

  return [
    hours,
    minutes,
    seconds,
  ]
    .map(
      (value) =>
        String(value).padStart(
          2,
          '0'
        )
    )
    .join(':')
}

function timerFor(reservation) {
  const start = new Date(
    reservation.reserved_from
  ).getTime()

  const end = new Date(
    reservation.reserved_until
  ).getTime()

  const now = currentTime.value

  if (
    reservation.status ===
    'confirmed'
  ) {
    if (now < start) {
      return {
        label: 'Starts in',
        value: formatDuration(
          start - now
        ),
        overtime: false,
      }
    }

    if (now < end) {
      return {
        label: 'Time remaining',
        value: formatDuration(
          end - now
        ),
        overtime: false,
      }
    }

    return {
      label: 'Reservation expired',
      value: '00:00:00',
      overtime: true,
    }
  }

  if (
    reservation.status ===
    'checked_in'
  ) {
    if (now <= end) {
      return {
        label: 'Time remaining',
        value: formatDuration(
          end - now
        ),
        overtime: false,
      }
    }

    return {
      label: 'Overtime',
      value: formatDuration(
        now - end
      ),
      overtime: true,
    }
  }

  return null
}

function locationName(id) {
  return (
    locations.value.find(
      (location) =>
        location.id === id
    )?.name ||
    'Parking location'
  )
}

function vehicleName(id) {
  const vehicle =
    vehicles.value.find(
      (item) =>
        item.id === id
    )

  if (!vehicle) {
    return 'Vehicle'
  }

  return `${vehicle.registration_number} · ${vehicle.make} ${vehicle.model}`
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

function statusStyle(status) {
  const styles = {
    confirmed:
      'bg-blue-50 text-blue-700',
    checked_in:
      'bg-emerald-50 text-emerald-700',
    completed:
      'bg-slate-100 text-slate-700',
    cancelled:
      'bg-red-50 text-red-700',
  }

  return (
    styles[status] ||
    'bg-slate-100 text-slate-700'
  )
}

function statusLabel(status) {
  return status
    .replaceAll('_', ' ')
    .replace(
      /\b\w/g,
      (letter) =>
        letter.toUpperCase()
    )
}

async function closeScanner() {
  scannerControls?.stop?.()
  scannerControls = null
  codeReader = null

  if (
    scannerVideo.value?.srcObject
  ) {
    for (
      const track
      of scannerVideo.value
        .srcObject.getTracks()
    ) {
      track.stop()
    }

    scannerVideo.value.srcObject =
      null
  }

  scannerOpen.value = false
  scannerReservation.value = null
  scannerMessage.value = ''
  scannerError.value = ''
}

async function openScanner(reservation) {
  scannerReservation.value =
    reservation

  scannerMessage.value =
    'Point the camera at the booking barcode.'

  scannerError.value = ''
  scannerOpen.value = true

  await nextTick()

  try {
    const {
      BrowserMultiFormatOneDReader,
    } = await import(
      '@zxing/browser'
    )

    codeReader =
      new BrowserMultiFormatOneDReader()

    scannerControls =
      await codeReader.decodeFromVideoDevice(
        undefined,
        scannerVideo.value,
        async (
          result,
          error,
          controls
        ) => {
          if (!result) {
            return
          }

          const scannedCode =
            result
              .getText()
              .trim()
              .toUpperCase()

          const expectedCode =
            reservation
              .booking_code
              .trim()
              .toUpperCase()

          if (
            scannedCode !==
            expectedCode
          ) {
            scannerError.value =
              `Wrong barcode: ${scannedCode}`

            return
          }

          scannerError.value = ''
          scannerMessage.value =
            `Booking ${scannedCode} verified.`

          controls?.stop?.()
          scannerControls?.stop?.()

          if (
            reservation.status ===
            'confirmed'
          ) {
            await checkIn(
              reservation
            )

            await closeScanner()
          }
        }
      )
  } catch (error) {
    scannerError.value =
      error?.message ||
      'Unable to access the camera.'
  }
}

async function loadReservations() {
  loading.value = true
  errorMessage.value = ''

  try {
    const [
      reservationResponse,
      locationResponse,
      vehicleResponse,
    ] = await Promise.all([
      api.get(
        '/api/reservations'
      ),
      api.get(
        '/api/parking/locations'
      ),
      api.get(
        '/api/vehicles'
      ),
    ])

    reservations.value =
      reservationResponse.data

    locations.value =
      locationResponse.data

    vehicles.value =
      vehicleResponse.data

    for (
      const reservation
      of reservations.value
    ) {
      if (
        !checkoutMethods.value[
          reservation.id
        ]
      ) {
        checkoutMethods.value[
          reservation.id
        ] = 'card'
      }
    }
  } catch (error) {
    errorMessage.value =
      error.response?.data?.detail ||
      'Unable to load reservations.'
  } finally {
    loading.value = false
  }
}

async function cancelReservation(
  reservation
) {
  if (
    !window.confirm(
      `Cancel booking ${reservation.booking_code}?`
    )
  ) {
    return
  }

  actionId.value =
    reservation.id

  errorMessage.value = ''
  successMessage.value = ''

  try {
    await api.patch(
      `/api/reservations/${reservation.id}/cancel`
    )

    successMessage.value =
      `Booking ${reservation.booking_code} was cancelled.`

    await loadReservations()
  } catch (error) {
    errorMessage.value =
      error.response?.data?.detail ||
      'Unable to cancel reservation.'
  } finally {
    actionId.value = null
  }
}

async function checkIn(
  reservation
) {
  actionId.value =
    reservation.id

  errorMessage.value = ''
  successMessage.value = ''

  try {
    await api.post(
      '/api/reservations/check-in',
      {
        booking_code:
          reservation.booking_code,
      }
    )

    successMessage.value =
      `Checked in successfully with booking ${reservation.booking_code}.`

    await loadReservations()
  } catch (error) {
    errorMessage.value =
      error.response?.data?.detail ||
      'Unable to check in.'
  } finally {
    actionId.value = null
  }
}

async function checkOut(
  reservation
) {
  actionId.value =
    reservation.id

  errorMessage.value = ''
  successMessage.value = ''

  try {
    const response =
      await api.post(
        `/api/reservations/${reservation.id}/check-out`,
        {
          payment_method:
            checkoutMethods.value[
              reservation.id
            ] || 'card',
        }
      )

    successMessage.value =
      `Checkout completed. Final cost £${Number(
        response.data.final_cost
      ).toFixed(2)} · Payment ${response.data.payment_reference}.`

    await loadReservations()
  } catch (error) {
    errorMessage.value =
      error.response?.data?.detail ||
      'Unable to check out.'
  } finally {
    actionId.value = null
  }
}

onMounted(() => {
  loadReservations()

  timerInterval =
    window.setInterval(
      () => {
        currentTime.value =
          Date.now()
      },
      1000
    )
})

onUnmounted(() => {
  if (timerInterval) {
    window.clearInterval(
      timerInterval
    )
  }

  scannerControls?.stop?.()

  if (
    scannerVideo.value?.srcObject
  ) {
    for (
      const track
      of scannerVideo.value
        .srcObject.getTracks()
    ) {
      track.stop()
    }
  }
})
</script>

<template>
  <AppShell>
    <section
      class="mx-auto max-w-7xl"
    >
      <div
        class="relative overflow-hidden rounded-[2rem] bg-slate-950 p-7 text-white shadow-xl sm:p-9"
      >
        <div
          class="absolute -right-20 -top-20 h-64 w-64 rounded-full bg-emerald-500/20 blur-3xl"
        />

        <div class="relative">
          <div
            class="inline-flex items-center gap-2 rounded-full bg-emerald-400/10 px-3 py-1.5 text-xs font-semibold text-emerald-300"
          >
            <TicketCheck
              :size="15"
            />
            Reservation management
          </div>

          <h1
            class="mt-5 text-3xl font-black tracking-tight sm:text-4xl"
          >
            Your parking journey
          </h1>

          <p
            class="mt-3 max-w-2xl text-sm leading-7 text-slate-300"
          >
            Manage upcoming bookings,
            check in when you arrive,
            complete parking sessions and
            track your reservation history.
          </p>

          <div
            class="mt-7 grid grid-cols-2 gap-3 sm:grid-cols-4"
          >
            <div
              class="rounded-2xl border border-white/10 bg-white/5 p-4"
            >
              <p class="text-xs text-slate-400">
                Total
              </p>

              <p class="mt-1 text-2xl font-black">
                {{ stats.total }}
              </p>
            </div>

            <div
              class="rounded-2xl border border-white/10 bg-white/5 p-4"
            >
              <p class="text-xs text-slate-400">
                Confirmed
              </p>

              <p
                class="mt-1 text-2xl font-black text-blue-300"
              >
                {{ stats.confirmed }}
              </p>
            </div>

            <div
              class="rounded-2xl border border-white/10 bg-white/5 p-4"
            >
              <p class="text-xs text-slate-400">
                Checked in
              </p>

              <p
                class="mt-1 text-2xl font-black text-emerald-300"
              >
                {{ stats.active }}
              </p>
            </div>

            <div
              class="rounded-2xl border border-white/10 bg-white/5 p-4"
            >
              <p class="text-xs text-slate-400">
                Completed
              </p>

              <p class="mt-1 text-2xl font-black">
                {{ stats.completed }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div
        class="mt-7 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between"
      >
        <div
          class="flex flex-wrap gap-2"
        >
          <button
            v-for="option in [
              ['all', 'All'],
              ['confirmed', 'Confirmed'],
              ['checked_in', 'Checked in'],
              ['completed', 'Completed'],
              ['cancelled', 'Cancelled'],
            ]"
            :key="option[0]"
            class="rounded-xl px-4 py-2.5 text-sm font-semibold transition"
            :class="
              filter === option[0]
                ? 'bg-slate-950 text-white'
                : 'border border-slate-200 bg-white text-slate-600 hover:bg-slate-50'
            "
            @click="
              filter = option[0]
            "
          >
            {{ option[1] }}
          </button>
        </div>

        <button
          class="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-700 shadow-sm"
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

          Refresh
        </button>
      </div>

      <div
        v-if="successMessage"
        class="mt-5 flex items-start gap-3 rounded-2xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-700"
      >
        <CheckCircle2
          :size="19"
          class="mt-0.5 shrink-0"
        />

        {{ successMessage }}
      </div>

      <div
        v-if="errorMessage"
        class="mt-5 rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-700"
      >
        {{ errorMessage }}
      </div>

      <div
        v-if="loading"
        class="mt-7 rounded-3xl border border-slate-200 bg-white p-12 text-center text-slate-500"
      >
        Loading reservations...
      </div>

      <div
        v-else-if="
          filteredReservations.length ===
          0
        "
        class="mt-7 rounded-3xl border border-slate-200 bg-white p-12 text-center shadow-sm"
      >
        <div
          class="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-emerald-50 text-emerald-600"
        >
          <CalendarDays :size="30" />
        </div>

        <h2
          class="mt-5 text-xl font-bold text-slate-900"
        >
          No reservations found
        </h2>

        <p
          class="mt-2 text-sm text-slate-500"
        >
          There are no reservations matching this status.
        </p>

        <RouterLink
          to="/parking"
          class="mt-6 inline-flex rounded-xl bg-emerald-600 px-5 py-3 text-sm font-semibold text-white"
        >
          Find parking
        </RouterLink>
      </div>

      <div
        v-else
        class="mt-7 grid gap-5 xl:grid-cols-2"
      >
        <article
          v-for="reservation in filteredReservations"
          :key="reservation.id"
          class="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm"
        >
          <div class="p-6">
            <div
              class="flex items-start justify-between gap-4"
            >
              <div
                class="flex items-center gap-4"
              >
                <div
                  class="flex h-13 w-13 shrink-0 items-center justify-center rounded-2xl bg-emerald-50 p-3 text-emerald-600"
                >
                  <CarFront
                    :size="24"
                  />
                </div>

                <div>
                  <p
                    class="text-xs font-semibold uppercase tracking-wider text-slate-400"
                  >
                    Booking code
                  </p>

                  <p
                    class="mt-1 text-xl font-black tracking-wide text-slate-900"
                  >
                    {{
                      reservation.booking_code
                    }}
                  </p>
                </div>
              </div>

              <span
                class="rounded-full px-3 py-1.5 text-xs font-bold"
                :class="
                  statusStyle(
                    reservation.status
                  )
                "
              >
                {{
                  statusLabel(
                    reservation.status
                  )
                }}
              </span>
            </div>

            <div
              class="mt-5 rounded-2xl bg-slate-50 p-4"
            >
              <div
                class="flex items-center gap-2"
              >
                <MapPin
                  :size="17"
                  class="text-emerald-600"
                />

                <p
                  class="font-bold text-slate-800"
                >
                  {{
                    locationName(
                      reservation.parking_location_id
                    )
                  }}
                </p>
              </div>

              <p
                class="mt-2 text-sm text-slate-500"
              >
                {{
                  vehicleName(
                    reservation.vehicle_id
                  )
                }}
              </p>
            </div>

            <div
              class="mt-4 grid grid-cols-2 gap-3"
            >
              <div
                class="rounded-xl border border-slate-100 p-4"
              >
                <div
                  class="flex items-center gap-2 text-xs text-slate-400"
                >
                  <Clock3
                    :size="14"
                  />
                  Starts
                </div>

                <p
                  class="mt-2 text-sm font-semibold text-slate-800"
                >
                  {{
                    formatDate(
                      reservation.reserved_from
                    )
                  }}
                </p>
              </div>

              <div
                class="rounded-xl border border-slate-100 p-4"
              >
                <div
                  class="flex items-center gap-2 text-xs text-slate-400"
                >
                  <Clock3
                    :size="14"
                  />
                  Ends
                </div>

                <p
                  class="mt-2 text-sm font-semibold text-slate-800"
                >
                  {{
                    formatDate(
                      reservation.reserved_until
                    )
                  }}
                </p>
              </div>
            </div>

            <div
              class="mt-4 flex items-center justify-between rounded-2xl bg-slate-950 p-4 text-white"
            >
              <span
                class="text-sm text-slate-400"
              >
                Estimated cost
              </span>

              <span
                class="text-xl font-black"
              >
                £{{
                  Number(
                    reservation.estimated_cost
                  ).toFixed(2)
                }}
              </span>
            </div>

            <div
              v-if="
                reservation.status ===
                  'confirmed' ||
                reservation.status ===
                  'checked_in'
              "
              class="mt-4 grid gap-3 lg:grid-cols-[1.35fr_0.85fr]"
            >
              <div
                class="overflow-hidden rounded-2xl border border-slate-200 bg-white p-4"
              >
                <div
                  class="flex items-start justify-between gap-3"
                >
                  <div>
                    <p
                      class="text-xs font-bold uppercase tracking-wider text-slate-400"
                    >
                      Entry barcode
                    </p>

                    <p
                      class="mt-1 text-xs text-slate-500"
                    >
                      Present this barcode at
                      the parking entrance.
                    </p>
                  </div>

                  <div
                    class="flex h-9 w-9 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600"
                  >
                    <ScanLine :size="18" />
                  </div>
                </div>

                <div
                  class="mt-3 overflow-x-auto rounded-xl border border-slate-100 bg-white p-2"
                >
                  <svg
                    v-barcode="
                      reservation.booking_code
                    "
                    class="mx-auto max-w-full"
                  />
                </div>

                <button
                  type="button"
                  class="mt-3 flex w-full items-center justify-center gap-2 rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-xs font-bold text-slate-700 transition hover:bg-slate-100"
                  @click="
                    openScanner(
                      reservation
                    )
                  "
                >
                  <ScanLine :size="16" />
                  Scan reservation barcode
                </button>
              </div>

              <div
                v-if="
                  timerFor(
                    reservation
                  )
                "
                class="flex min-h-[180px] flex-col justify-between rounded-2xl border p-4"
                :class="
                  timerFor(
                    reservation
                  ).overtime
                    ? 'border-red-200 bg-red-50'
                    : 'border-emerald-200 bg-emerald-50'
                "
              >
                <div
                  class="flex items-center gap-2"
                >
                  <Timer
                    :size="18"
                    :class="
                      timerFor(
                        reservation
                      ).overtime
                        ? 'text-red-600'
                        : 'text-emerald-600'
                    "
                  />

                  <span
                    class="text-xs font-black uppercase tracking-wider"
                    :class="
                      timerFor(
                        reservation
                      ).overtime
                        ? 'text-red-700'
                        : 'text-emerald-700'
                    "
                  >
                    {{
                      timerFor(
                        reservation
                      ).label
                    }}
                  </span>
                </div>

                <p
                  class="my-5 font-mono text-3xl font-black tracking-tight"
                  :class="
                    timerFor(
                      reservation
                    ).overtime
                      ? 'text-red-700'
                      : 'text-slate-950'
                  "
                >
                  {{
                    timerFor(
                      reservation
                    ).value
                  }}
                </p>

                <p
                  class="text-xs leading-5 text-slate-500"
                >
                  {{
                    reservation.status ===
                    'checked_in'
                      ? 'Live parking session timer'
                      : 'Live reservation timer'
                  }}
                </p>
              </div>
            </div>

            <div
              v-if="
                reservation.status ===
                'confirmed'
              "
              class="mt-4 grid gap-2 sm:grid-cols-2"
            >
              <button
                class="flex items-center justify-center gap-2 rounded-xl bg-emerald-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-emerald-700 disabled:opacity-50"
                :disabled="
                  actionId ===
                  reservation.id
                "
                @click="
                  checkIn(
                    reservation
                  )
                "
              >
                <LogIn
                  :size="17"
                />

                Check in
              </button>

              <button
                class="flex items-center justify-center gap-2 rounded-xl border border-red-200 px-4 py-3 text-sm font-semibold text-red-600 transition hover:bg-red-50 disabled:opacity-50"
                :disabled="
                  actionId ===
                  reservation.id
                "
                @click="
                  cancelReservation(
                    reservation
                  )
                "
              >
                <XCircle
                  :size="17"
                />

                Cancel booking
              </button>
            </div>

            <div
              v-if="
                reservation.status ===
                'checked_in'
              "
              class="mt-4 rounded-2xl border border-emerald-200 bg-emerald-50 p-4"
            >
              <p
                class="text-sm font-bold text-emerald-800"
              >
                Parking session active
              </p>

              <p
                class="mt-1 text-xs text-emerald-700"
              >
                Choose your payment method
                before checking out.
              </p>

              <div
                class="mt-4 grid gap-3 sm:grid-cols-[1fr_auto]"
              >
                <select
                  v-model="
                    checkoutMethods[
                      reservation.id
                    ]
                  "
                  class="rounded-xl border border-emerald-200 bg-white px-4 py-3 text-sm outline-none"
                >
                  <option value="card">
                    Card payment
                  </option>

                  <option value="wallet">
                    SmartPark wallet
                  </option>
                </select>

                <button
                  class="flex items-center justify-center gap-2 rounded-xl bg-slate-950 px-5 py-3 text-sm font-semibold text-white disabled:opacity-50"
                  :disabled="
                    actionId ===
                    reservation.id
                  "
                  @click="
                    checkOut(
                      reservation
                    )
                  "
                >
                  <LogOut
                    :size="17"
                  />

                  Check out
                </button>
              </div>
            </div>

            <div
              v-if="
                reservation.status ===
                'completed'
              "
              class="mt-4 flex items-center gap-3 rounded-xl bg-emerald-50 p-4 text-sm font-semibold text-emerald-700"
            >
              <CheckCircle2
                :size="19"
              />

              Parking session completed
            </div>

            <div
              v-if="
                reservation.status ===
                'cancelled'
              "
              class="mt-4 flex items-center gap-3 rounded-xl bg-red-50 p-4 text-sm font-semibold text-red-600"
            >
              <XCircle
                :size="19"
              />

              Reservation cancelled
            </div>
          </div>
        </article>
      </div>
    </section>
    <Teleport to="body">
      <div
        v-if="scannerOpen"
        class="fixed inset-0 z-[12000] flex items-center justify-center bg-slate-950/80 p-4 backdrop-blur-sm"
        @click.self="
          closeScanner
        "
      >
        <div
          class="w-full max-w-xl overflow-hidden rounded-3xl bg-white shadow-2xl"
        >
          <div
            class="flex items-center justify-between border-b border-slate-200 p-5"
          >
            <div>
              <p
                class="text-xs font-bold uppercase tracking-wider text-emerald-600"
              >
                SmartPark scanner
              </p>

              <h2
                class="mt-1 text-xl font-black text-slate-900"
              >
                Scan reservation barcode
              </h2>
            </div>

            <button
              type="button"
              class="rounded-xl p-2 text-slate-400 hover:bg-slate-100"
              @click="
                closeScanner
              "
            >
              <X :size="21" />
            </button>
          </div>

          <div class="p-5">
            <div
              class="relative overflow-hidden rounded-2xl bg-slate-950"
            >
              <video
                ref="scannerVideo"
                autoplay
                muted
                playsinline
                class="aspect-video w-full object-cover"
              />

              <div
                class="pointer-events-none absolute inset-0 flex items-center justify-center"
              >
                <div
                  class="h-28 w-4/5 rounded-xl border-2 border-emerald-400"
                />
              </div>

              <div
                class="pointer-events-none absolute left-[10%] right-[10%] top-1/2 h-0.5 bg-emerald-400"
              />
            </div>

            <div
              class="mt-4 rounded-2xl bg-slate-50 p-4"
            >
              <p
                class="text-xs font-semibold text-slate-500"
              >
                Expected booking code
              </p>

              <p
                class="mt-1 font-mono text-lg font-black tracking-wide text-slate-900"
              >
                {{
                  scannerReservation
                    ?.booking_code
                }}
              </p>
            </div>

            <p
              v-if="scannerMessage"
              class="mt-4 rounded-xl border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-700"
            >
              {{ scannerMessage }}
            </p>

            <p
              v-if="scannerError"
              class="mt-4 rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700"
            >
              {{ scannerError }}
            </p>

            <p
              class="mt-4 text-xs leading-5 text-slate-500"
            >
              Allow camera permission and
              position the barcode inside
              the scanning frame.
            </p>

            <button
              type="button"
              class="mt-5 w-full rounded-xl bg-slate-950 px-5 py-3 text-sm font-bold text-white"
              @click="
                closeScanner
              "
            >
              Close scanner
            </button>
          </div>
        </div>
      </div>
    </Teleport>

  </AppShell>
</template>
