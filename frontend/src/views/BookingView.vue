<script setup>
import {
  computed,
  onMounted,
  ref,
} from 'vue'

import {
  ArrowLeft,
  CalendarDays,
  CarFront,
  CheckCircle2,
  Clock3,
  MapPin,
  PoundSterling,
  Sparkles,
  TicketCheck,
} from '@lucide/vue'

import {
  RouterLink,
  useRoute,
} from 'vue-router'

import AppShell from '../components/AppShell.vue'
import api from '../services/api'

const route = useRoute()

const parkingLocation = ref(null)
const vehicles = ref([])

const loading = ref(true)
const booking = ref(false)

const errorMessage = ref('')
const successReservation = ref(null)

const form = ref({
  vehicle_id: '',
  reserved_from: '',
  reserved_until: '',
})

const locationId = computed(
  () => String(
    route.params.locationId || ''
  )
)

const openingHours = computed(() => {
  const location = parkingLocation.value

  if (!location) {
    return '—'
  }

  if (location.is_24_hours) {
    return 'Open 24 hours'
  }

  if (
    !location.opening_time ||
    !location.closing_time
  ) {
    return 'Hours unavailable'
  }

  return `${location.opening_time.slice(
    0,
    5
  )} – ${location.closing_time.slice(
    0,
    5
  )}`
})

function toLocalInputValue(date) {
  const localDate = new Date(
    date.getTime() -
    date.getTimezoneOffset() *
    60000
  )

  return localDate
    .toISOString()
    .slice(0, 16)
}

function setDefaultTimes() {
  const start = new Date(
    Date.now() +
    10 * 60 * 1000
  )

  start.setSeconds(0, 0)

  const end = new Date(
    start.getTime() +
    60 * 60 * 1000
  )

  form.value.reserved_from =
    toLocalInputValue(start)

  form.value.reserved_until =
    toLocalInputValue(end)
}

async function loadBookingData() {
  loading.value = true
  errorMessage.value = ''

  try {
    const [
      locationResponse,
      vehicleResponse,
    ] = await Promise.all([
      api.get(
        `/api/parking/locations/${locationId.value}`
      ),
      api.get(
        '/api/vehicles'
      ),
    ])

    parkingLocation.value =
      locationResponse.data

    vehicles.value =
      vehicleResponse.data

    const defaultVehicle =
      vehicles.value.find(
        (vehicle) =>
          vehicle.is_default
      ) ||
      vehicles.value[0]

    if (defaultVehicle) {
      form.value.vehicle_id =
        defaultVehicle.id
    }

    setDefaultTimes()
  } catch (error) {
    errorMessage.value =
      error.response?.data?.detail ||
      'Unable to load booking information.'
  } finally {
    loading.value = false
  }
}

async function confirmReservation() {
  errorMessage.value = ''
  successReservation.value = null

  if (!form.value.vehicle_id) {
    errorMessage.value =
      'Please select a vehicle.'
    return
  }

  const start = new Date(
    form.value.reserved_from
  )

  const end = new Date(
    form.value.reserved_until
  )

  if (
    !Number.isFinite(start.getTime()) ||
    !Number.isFinite(end.getTime())
  ) {
    errorMessage.value =
      'Please enter valid reservation times.'
    return
  }

  if (end <= start) {
    errorMessage.value =
      'End time must be later than start time.'
    return
  }

  booking.value = true

  try {
    const response =
      await api.post(
        '/api/reservations',
        {
          vehicle_id:
            form.value.vehicle_id,

          parking_location_id:
            locationId.value,

          reserved_from:
            start.toISOString(),

          reserved_until:
            end.toISOString(),
        }
      )

    successReservation.value =
      response.data
  } catch (error) {
    errorMessage.value =
      error.response?.data?.detail ||
      'Unable to create reservation.'
  } finally {
    booking.value = false
  }
}

onMounted(loadBookingData)
</script>

<template>
  <AppShell>
    <section
      class="mx-auto max-w-5xl"
    >
      <RouterLink
        to="/parking"
        class="inline-flex items-center gap-2 text-sm font-semibold text-emerald-600 hover:text-emerald-700"
      >
        <ArrowLeft :size="17" />
        Back to parking
      </RouterLink>

      <div
        v-if="loading"
        class="mt-6 rounded-3xl border border-slate-200 bg-white p-12 text-center text-slate-500"
      >
        Loading booking information...
      </div>

      <div
        v-else-if="successReservation"
        class="mt-6 overflow-hidden rounded-[2rem] border border-emerald-200 bg-white shadow-xl"
      >
        <div
          class="bg-gradient-to-br from-emerald-600 to-teal-600 p-8 text-center text-white"
        >
          <div
            class="mx-auto flex h-20 w-20 items-center justify-center rounded-full bg-white/15"
          >
            <CheckCircle2 :size="40" />
          </div>

          <h1
            class="mt-5 text-3xl font-black"
          >
            Parking reserved
          </h1>

          <p
            class="mt-2 text-emerald-50"
          >
            Your SmartPark booking has
            been confirmed.
          </p>
        </div>

        <div class="p-7 sm:p-9">
          <div
            class="rounded-3xl bg-slate-950 p-7 text-center text-white"
          >
            <p
              class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400"
            >
              Booking code
            </p>

            <p
              class="mt-3 text-4xl font-black tracking-wider text-emerald-400"
            >
              {{
                successReservation.booking_code
              }}
            </p>

            <p
              class="mt-4 text-sm text-slate-300"
            >
              Estimated cost:
              £{{
                Number(
                  successReservation.estimated_cost
                ).toFixed(2)
              }}
            </p>
          </div>

          <div
            v-if="
              successReservation.applied_hourly_rate != null
            "
            class="mt-5 rounded-3xl border border-slate-200 bg-slate-50 p-5 text-left"
          >
            <div
              class="flex items-center justify-between gap-4"
            >
              <div
                class="flex items-center gap-2"
              >
                <Sparkles
                  :size="18"
                  class="text-emerald-600"
                />

                <p
                  class="font-bold text-slate-900"
                >
                  {{
                    successReservation.pricing_model_version ===
                    'fixed-v1'
                      ? 'Fixed booking price'
                      : 'Locked AI pricing'
                  }}
                </p>
              </div>

              <span
                class="rounded-full px-3 py-1 text-xs font-bold"
                :class="
                  successReservation.pricing_model_version ===
                  'fixed-v1'
                    ? 'bg-slate-200 text-slate-600'
                    : 'bg-emerald-100 text-emerald-700'
                "
              >
                {{
                  successReservation.pricing_model_version ===
                  'fixed-v1'
                    ? 'Fixed'
                    : 'AI Dynamic'
                }}
              </span>
            </div>

            <div
              class="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-4"
            >
              <div
                class="rounded-2xl bg-white p-4"
              >
                <p
                  class="text-[11px] font-bold uppercase tracking-wide text-slate-400"
                >
                  Base rate
                </p>

                <p
                  class="mt-2 font-black text-slate-900"
                >
                  £{{
                    Number(
                      successReservation.base_hourly_rate ||
                      0
                    ).toFixed(2)
                  }}/hr
                </p>
              </div>

              <div
                class="rounded-2xl bg-white p-4"
              >
                <p
                  class="text-[11px] font-bold uppercase tracking-wide text-slate-400"
                >
                  Locked rate
                </p>

                <p
                  class="mt-2 font-black text-emerald-700"
                >
                  £{{
                    Number(
                      successReservation.applied_hourly_rate ||
                      0
                    ).toFixed(2)
                  }}/hr
                </p>
              </div>

              <div
                class="rounded-2xl bg-white p-4"
              >
                <p
                  class="text-[11px] font-bold uppercase tracking-wide text-slate-400"
                >
                  Price factor
                </p>

                <p
                  class="mt-2 font-black text-slate-900"
                >
                  ×{{
                    Number(
                      successReservation.pricing_multiplier ||
                      1
                    ).toFixed(2)
                  }}
                </p>
              </div>

              <div
                class="rounded-2xl bg-white p-4"
              >
                <p
                  class="text-[11px] font-bold uppercase tracking-wide text-slate-400"
                >
                  AI demand
                </p>

                <p
                  class="mt-2 font-black text-slate-900"
                >
                  {{
                    successReservation
                      .predicted_occupancy_at_booking != null
                      ? Number(
                          successReservation
                            .predicted_occupancy_at_booking
                        ).toFixed(1) + '%'
                      : '—'
                  }}
                </p>
              </div>
            </div>

            <div
              class="mt-3 flex items-center justify-between rounded-2xl bg-slate-950 px-4 py-3 text-white"
            >
              <span
                class="text-sm text-slate-300"
              >
                Estimated total
              </span>

              <span
                class="text-lg font-black text-emerald-400"
              >
                £{{
                  Number(
                    successReservation.estimated_cost
                  ).toFixed(2)
                }}
              </span>
            </div>
          </div>

          <div
            class="mt-6 grid gap-3 sm:grid-cols-2"
          >
            <RouterLink
              to="/reservations"
              class="flex items-center justify-center gap-2 rounded-xl bg-emerald-600 px-5 py-4 font-semibold text-white"
            >
              <TicketCheck :size="19" />
              View reservations
            </RouterLink>

            <RouterLink
              to="/parking"
              class="flex items-center justify-center rounded-xl border border-slate-200 px-5 py-4 font-semibold text-slate-700"
            >
              Find more parking
            </RouterLink>
          </div>
        </div>
      </div>

      <div
        v-else
        class="mt-6 grid gap-6 lg:grid-cols-[0.9fr_1.1fr]"
      >
        <section
          class="rounded-3xl bg-slate-950 p-7 text-white shadow-xl"
        >
          <div
            class="flex h-14 w-14 items-center justify-center rounded-2xl bg-emerald-500 text-slate-950"
          >
            <MapPin :size="26" />
          </div>

          <p
            class="mt-6 text-xs font-semibold uppercase tracking-[0.2em] text-emerald-400"
          >
            Selected parking
          </p>

          <h1
            class="mt-3 text-3xl font-black"
          >
            {{
              parkingLocation?.name
            }}
          </h1>

          <p
            class="mt-3 text-sm leading-6 text-slate-400"
          >
            {{
              parkingLocation?.address
            }},
            {{
              parkingLocation?.city
            }}
            {{
              parkingLocation?.postcode
            }}
          </p>

          <div
            class="mt-7 grid grid-cols-2 gap-3"
          >
            <div
              class="rounded-2xl border border-white/10 bg-white/5 p-4"
            >
              <PoundSterling
                :size="18"
                class="text-emerald-400"
              />

              <p
                class="mt-3 text-xs text-slate-400"
              >
                Hourly rate
              </p>

              <p
                class="mt-1 text-xl font-bold"
              >
                £{{
                  Number(
                    parkingLocation?.hourly_rate ||
                    0
                  ).toFixed(2)
                }}
              </p>
            </div>

            <div
              class="rounded-2xl border border-white/10 bg-white/5 p-4"
            >
              <CarFront
                :size="18"
                class="text-cyan-400"
              />

              <p
                class="mt-3 text-xs text-slate-400"
              >
                Capacity
              </p>

              <p
                class="mt-1 text-xl font-bold"
              >
                {{
                  parkingLocation?.total_spaces
                }}
              </p>
            </div>
          </div>

          <div
            class="mt-4 rounded-2xl border border-white/10 bg-white/5 p-4"
          >
            <div
              class="flex items-center gap-2"
            >
              <Clock3
                :size="17"
                class="text-emerald-400"
              />

              <span
                class="text-sm font-semibold"
              >
                {{ openingHours }}
              </span>
            </div>
          </div>

          <div
            v-if="
              parkingLocation?.dynamic_pricing_enabled
            "
            class="mt-4 rounded-2xl border border-emerald-400/20 bg-emerald-400/10 p-4"
          >
            <div
              class="flex items-start gap-3"
            >
              <Sparkles
                :size="19"
                class="mt-0.5 shrink-0 text-emerald-400"
              />

              <div>
                <p
                  class="text-sm font-bold text-emerald-300"
                >
                  AI Dynamic Pricing is active
                </p>

                <p
                  class="mt-1 text-xs leading-5 text-slate-300"
                >
                  The hourly rate shown above is
                  the base rate. Your booking rate
                  will be calculated using the
                  reservation time, current occupancy
                  and AI-predicted parking demand.
                </p>

                <p
                  class="mt-2 text-xs font-semibold text-emerald-300"
                >
                  Your calculated hourly rate is
                  locked when the reservation is
                  confirmed.
                </p>
              </div>
            </div>
          </div>

        </section>

        <section
          class="rounded-3xl border border-slate-200 bg-white p-7 shadow-sm"
        >
          <div
            class="flex items-center gap-3"
          >
            <div
              class="flex h-12 w-12 items-center justify-center rounded-2xl bg-emerald-50 text-emerald-600"
            >
              <CalendarDays
                :size="22"
              />
            </div>

            <div>
              <h2
                class="text-xl font-bold text-slate-900"
              >
                Reserve parking
              </h2>

              <p
                class="text-xs text-slate-500"
              >
                Select your vehicle and
                parking times.
              </p>
            </div>
          </div>

          <form
            class="mt-7 space-y-5"
            @submit.prevent="
              confirmReservation
            "
          >
            <div>
              <label
                class="mb-2 block text-sm font-semibold text-slate-700"
              >
                Vehicle
              </label>

              <select
                v-model="
                  form.vehicle_id
                "
                required
                class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3.5 outline-none focus:border-emerald-500 focus:ring-4 focus:ring-emerald-100"
              >
                <option
                  value=""
                  disabled
                >
                  Select a vehicle
                </option>

                <option
                  v-for="vehicle in vehicles"
                  :key="vehicle.id"
                  :value="vehicle.id"
                >
                  {{
                    vehicle.registration_number
                  }}
                  —
                  {{ vehicle.make }}
                  {{ vehicle.model }}
                  {{
                    vehicle.is_default
                      ? '(Default)'
                      : ''
                  }}
                </option>
              </select>

              <p
                v-if="vehicles.length === 0"
                class="mt-2 text-xs text-red-600"
              >
                No vehicle is registered
                on this account.
              </p>
            </div>

            <div>
              <label
                class="mb-2 block text-sm font-semibold text-slate-700"
              >
                Reservation start
              </label>

              <input
                v-model="
                  form.reserved_from
                "
                type="datetime-local"
                required
                class="w-full rounded-xl border border-slate-200 px-4 py-3.5 outline-none focus:border-emerald-500 focus:ring-4 focus:ring-emerald-100"
              >
            </div>

            <div>
              <label
                class="mb-2 block text-sm font-semibold text-slate-700"
              >
                Reservation end
              </label>

              <input
                v-model="
                  form.reserved_until
                "
                type="datetime-local"
                required
                class="w-full rounded-xl border border-slate-200 px-4 py-3.5 outline-none focus:border-emerald-500 focus:ring-4 focus:ring-emerald-100"
              >
            </div>

            <div
              v-if="errorMessage"
              class="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700"
            >
              {{ errorMessage }}
            </div>

            <button
              type="submit"
              :disabled="
                booking ||
                vehicles.length === 0
              "
              class="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 px-5 py-4 font-bold text-white shadow-lg shadow-emerald-600/20 transition hover:-translate-y-0.5 disabled:opacity-50"
            >
              <TicketCheck
                :size="19"
              />

              {{
                booking
                  ? 'Creating reservation...'
                  : 'Confirm reservation'
              }}
            </button>
          </form>
        </section>
      </div>
    </section>
  </AppShell>
</template>
