<script setup>
import {
  computed,
  nextTick,
  onMounted,
  onUnmounted,
  ref,
} from 'vue'

import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

import { useRouter } from 'vue-router'

import {
  BrainCircuit,
  CalendarDays,
  CarFront,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  Clock3,
  Crosshair,
  Crown,
  Gauge,
  LocateFixed,
  MapPin,
  Navigation,
  PoundSterling,
  RefreshCw,
  Search,
  Sparkles,
  Star,
  Trophy,
  X,
  Zap,
} from '@lucide/vue'

import AppShell from '../components/AppShell.vue'
import api from '../services/api'

const router = useRouter()

const locations = ref([])
const availability = ref({})
const ratingSummaries = ref({})
const vehicles = ref([])
const recommendations = ref([])

const openDataBays = ref([])
const openDataStats = ref(null)
const showOpenData = ref(false)
const openDataLoading = ref(false)
const openDataError = ref('')

const loading = ref(true)
const recommending = ref(false)
const booking = ref(false)

const errorMessage = ref('')
const bookingError = ref('')
const successReservation = ref(null)

const searchQuery = ref('')
const selectedRecommendation = ref(null)
const expandedRecommendation = ref(null)

const bookingModalOpen = ref(false)

const mapElement = ref(null)

const destination = ref({
  latitude: 51.5074,
  longitude: -0.1278,
})

const recommendationForm = ref({
  hour: 18,
  day_of_week: 4,
  traffic_level: 1,
  weather: 0,
  event_level: 0,
  preference_mode: 'balanced',
})

const reservationForm = ref({
  vehicle_id: '',
  parking_location_id: '',
  reserved_from: '',
  reserved_until: '',
})

let map = null
let parkingLayer = null
let openDataLayer = null
let destinationMarker = null

const preferenceModes = [
  {
    value: 'balanced',
    label: 'Balanced',
    description: 'Best overall match',
  },
  {
    value: 'closest',
    label: 'Closest',
    description: 'Prioritise distance',
  },
  {
    value: 'cheapest',
    label: 'Cheapest',
    description: 'Prioritise price',
  },
  {
    value: 'most_available',
    label: 'Most Available',
    description: 'Prioritise free spaces',
  },
  {
    value: 'low_demand',
    label: 'Low Demand',
    description: 'Prioritise predicted demand',
  },
]

const filteredLocations = computed(() => {
  const query =
    searchQuery.value
      .trim()
      .toLowerCase()

  if (!query) {
    return locations.value
  }

  return locations.value.filter(
    (location) =>
      location.name
        .toLowerCase()
        .includes(query) ||
      location.address
        .toLowerCase()
        .includes(query) ||
      location.city
        .toLowerCase()
        .includes(query) ||
      location.postcode
        .toLowerCase()
        .includes(query)
  )
})

const topRecommendation = computed(
  () => recommendations.value[0] || null
)

function openingHours(location) {
  if (location.is_24_hours) {
    return '24 hours'
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
}

function occupancyStatus(value) {
  if (value < 40) {
    return {
      label: 'Low occupancy',
      class:
        'bg-emerald-50 text-emerald-700',
    }
  }

  if (value < 70) {
    return {
      label: 'Moderate',
      class:
        'bg-amber-50 text-amber-700',
    }
  }

  return {
    label: 'Busy',
    class:
      'bg-red-50 text-red-700',
  }
}

function recommendationScoreClass(score) {
  if (score >= 75) {
    return 'text-emerald-600'
  }

  if (score >= 55) {
    return 'text-amber-600'
  }

  return 'text-slate-600'
}

function ratingFor(locationId) {
  return (
    ratingSummaries.value[
      locationId
    ] || {
      average_rating: 0,
      review_count: 0,
    }
  )
}

function createMap() {
  if (
    map ||
    !mapElement.value
  ) {
    return
  }

  map = L.map(
    mapElement.value
  ).setView(
    [
      destination.value.latitude,
      destination.value.longitude,
    ],
    12
  )

  L.tileLayer(
    'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    {
      maxZoom: 19,
      attribution:
        '&copy; OpenStreetMap contributors',
    }
  ).addTo(map)

  parkingLayer =
    L.layerGroup().addTo(map)

  openDataLayer =
    L.layerGroup()

  map.on('click', (event) => {
    destination.value.latitude =
      Number(
        event.latlng.lat.toFixed(6)
      )

    destination.value.longitude =
      Number(
        event.latlng.lng.toFixed(6)
      )

    renderDestinationMarker()
  })

  map.on('moveend', () => {
    if (showOpenData.value) {
      loadOpenDataForMap()
    }
  })

  renderDestinationMarker()
}

function renderDestinationMarker() {
  if (!map) {
    return
  }

  if (destinationMarker) {
    destinationMarker.remove()
  }

  const icon = L.divIcon({
    className: '',
    html: `
      <div
        style="
          width:46px;
          height:46px;
          border-radius:50%;
          background:#0f172a;
          border:4px solid white;
          box-shadow:0 8px 24px rgba(15,23,42,.35);
          display:flex;
          align-items:center;
          justify-content:center;
          color:white;
          font-size:18px;
        "
      >
        ◎
      </div>
    `,
    iconSize: [46, 46],
    iconAnchor: [23, 23],
  })

  destinationMarker = L.marker(
    [
      destination.value.latitude,
      destination.value.longitude,
    ],
    {
      icon,
    }
  )
    .addTo(map)
    .bindPopup(
      '<strong>Destination</strong><br>AI recommendations are ranked relative to this point.'
    )
}

function renderParkingMarkers() {
  if (
    !map ||
    !parkingLayer
  ) {
    return
  }

  parkingLayer.clearLayers()

  const recommendationMap =
    new Map(
      recommendations.value.map(
        (item) => [
          item.parking_location_id,
          item,
        ]
      )
    )

  for (
    const location
    of filteredLocations.value
  ) {
    const lat =
      Number(location.latitude)

    const lng =
      Number(location.longitude)

    if (
      !Number.isFinite(lat) ||
      !Number.isFinite(lng)
    ) {
      continue
    }

    const recommendation =
      recommendationMap.get(
        location.id
      )

    const stats =
      availability.value[
        location.id
      ]

    const rank =
      recommendation
        ?.recommendation_rank

    const markerIcon = L.divIcon({
      className: '',
      html: `
        <div
          style="
            width:46px;
            height:46px;
            border-radius:14px;
            background:${
              rank === 1
                ? '#10b981'
                : '#0f172a'
            };
            color:white;
            display:flex;
            align-items:center;
            justify-content:center;
            font-weight:800;
            border:3px solid white;
            box-shadow:0 8px 20px rgba(15,23,42,.25);
            position:relative;
          "
        >
          ${
            rank
              ? `#${rank}`
              : 'P'
          }
        </div>
      `,
      iconSize: [46, 46],
      iconAnchor: [23, 46],
    })

    const marker = L.marker(
      [lat, lng],
      {
        icon: markerIcon,
      }
    )

    marker.bindPopup(`
      <div style="min-width:200px">
        <strong>${location.name}</strong>
        <br>
        ${location.address}
        <br><br>
        ${
          recommendation
            ? `<strong>AI rank #${recommendation.recommendation_rank}</strong>
               · ${recommendation.recommendation_score.toFixed(1)} score
               <br>
               ${recommendation.distance_km.toFixed(2)} km away
               <br>
               ${recommendation.predicted_available_spaces} predicted free spaces`
            : `${stats?.available_spaces ?? '—'} spaces available`
        }
        <br>
        £${Number(
          location.hourly_rate
        ).toFixed(2)}/hr

        ${
          Number(
            stats?.total_ev_chargers || 0
          ) > 0
            ? `
              <br><br>
              <strong>⚡ EV charging</strong>
              <br>
              ${stats?.available_ev_chargers ?? 0}
              /
              ${stats?.total_ev_chargers ?? 0}
              chargers available
              <br>
              ${stats?.occupied_ev_chargers ?? 0}
              occupied ·
              ${stats?.offline_ev_chargers ?? 0}
              offline ·
              ${stats?.maintenance_ev_chargers ?? 0}
              maintenance
            `
            : ''
        }
      </div>
    `)

    marker.addTo(parkingLayer)
  }
}


function escapePopupText(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;')
}

function renderOpenDataMarkers() {
  if (
    !map ||
    !openDataLayer
  ) {
    return
  }

  openDataLayer.clearLayers()

  for (
    const bay
    of openDataBays.value
  ) {
    const lat =
      Number(bay.latitude)

    const lng =
      Number(bay.longitude)

    if (
      !Number.isFinite(lat) ||
      !Number.isFinite(lng)
    ) {
      continue
    }

    const restriction =
      bay.restriction_type || ''

    const isEv =
      restriction ===
      'electric vehicle recharging'

    const isDisabled =
      restriction.startsWith(
        'disabled'
      )

    const marker =
      L.circleMarker(
        [lat, lng],
        {
          radius:
            isEv
              ? 8
              : 7,
          weight: 2,
          fillOpacity: 0.82,
          color:
            isEv
              ? '#059669'
              : isDisabled
                ? '#2563eb'
                : '#7c3aed',
          fillColor:
            isEv
              ? '#10b981'
              : isDisabled
                ? '#3b82f6'
                : '#8b5cf6',
        }
      )

    const tariff =
      bay.tariff
        ? `
          <br><br>
          <strong>Tariff</strong><br>
          ${escapePopupText(
            bay.tariff
          )}
        `
        : ''

    marker.bindPopup(`
      <div style="min-width:240px">
        <strong>
          ${escapePopupText(
            bay.road_name
          )}
        </strong>

        <br>
        ${escapePopupText(
          bay.postcode || 'Postcode unavailable'
        )}

        <br><br>

        <strong>Restriction</strong><br>
        ${escapePopupText(
          bay.restriction_type
        )}

        <br><br>

        <strong>Declared spaces</strong><br>
        ${
          bay.parking_spaces ??
          'Not specified'
        }

        <br><br>

        <strong>Operating times</strong><br>
        ${escapePopupText(
          bay.times_of_operation ||
          'Not specified'
        )}

        ${tariff}

        <br><br>

        <span
          style="
            font-size:11px;
            color:#475569;
          "
        >
          Camden Open Data<br>
          Source ID:
          ${escapePopupText(
            bay.source_identifier
          )}
          <br>
          Public parking infrastructure
          record — not live occupancy.
        </span>
      </div>
    `)

    marker.addTo(
      openDataLayer
    )
  }
}

async function loadOpenDataStats() {
  if (openDataStats.value) {
    return
  }

  try {
    const response =
      await api.get(
        '/api/open-data/parking-bays/stats'
      )

    openDataStats.value =
      response.data
  } catch (error) {
    openDataError.value =
      error.response?.data?.detail ||
      'Unable to load Camden dataset statistics.'
  }
}

async function loadOpenDataForMap() {
  if (
    !map ||
    !showOpenData.value
  ) {
    return
  }

  openDataLoading.value = true
  openDataError.value = ''

  try {
    const bounds =
      map.getBounds()

    const response =
      await api.get(
        '/api/open-data/parking-bays',
        {
          params: {
            min_lat:
              bounds.getSouth(),
            max_lat:
              bounds.getNorth(),
            min_lon:
              bounds.getWest(),
            max_lon:
              bounds.getEast(),
            limit: 500,
          },
        }
      )

    openDataBays.value =
      response.data

    renderOpenDataMarkers()
  } catch (error) {
    openDataError.value =
      error.response?.data?.detail ||
      'Unable to load Camden Open Data parking bays.'
  } finally {
    openDataLoading.value = false
  }
}

async function toggleOpenData() {
  showOpenData.value =
    !showOpenData.value

  openDataError.value = ''

  if (
    !map ||
    !openDataLayer
  ) {
    return
  }

  if (!showOpenData.value) {
    map.removeLayer(
      openDataLayer
    )

    return
  }

  openDataLayer.addTo(map)

  await Promise.all([
    loadOpenDataStats(),
    loadOpenDataForMap(),
  ])
}

function focusLocation(item) {
  if (!map) {
    return
  }

  const latitude =
    Number(
      item.latitude
    )

  const longitude =
    Number(
      item.longitude
    )

  map.flyTo(
    [
      latitude,
      longitude,
    ],
    16,
    {
      duration: 0.8,
    }
  )
}

function useMyLocation() {
  errorMessage.value = ''

  if (
    !navigator.geolocation
  ) {
    errorMessage.value =
      'Location services are not supported by this browser.'
    return
  }

  navigator.geolocation.getCurrentPosition(
    (position) => {
      destination.value.latitude =
        Number(
          position.coords.latitude
            .toFixed(6)
        )

      destination.value.longitude =
        Number(
          position.coords.longitude
            .toFixed(6)
        )

      renderDestinationMarker()

      map?.flyTo(
        [
          destination.value.latitude,
          destination.value.longitude,
        ],
        14
      )
    },
    () => {
      errorMessage.value =
        'Unable to access your current location.'
    }
  )
}

async function loadParkingData() {
  loading.value = true
  errorMessage.value = ''

  try {
    const [
      locationResponse,
      vehicleResponse,
    ] = await Promise.all([
      api.get(
        '/api/parking/locations'
      ),
      api.get(
        '/api/vehicles'
      ),
    ])

    locations.value =
      locationResponse.data.filter(
        (location) =>
          location.is_active
      )

    vehicles.value =
      vehicleResponse.data

    const defaultVehicle =
      vehicles.value.find(
        (vehicle) =>
          vehicle.is_default
      ) ||
      vehicles.value[0]

    if (defaultVehicle) {
      reservationForm.value
        .vehicle_id =
        defaultVehicle.id
    }

    const availabilityResults =
      await Promise.allSettled(
        locations.value.map(
          (location) =>
            api.get(
              `/api/parking/locations/${location.id}/availability`
            )
        )
      )

    const reviewResults =
      await Promise.allSettled(
        locations.value.map(
          (location) =>
            api.get(
              `/api/reviews/location/${location.id}/summary`
            )
        )
      )

    const availabilityMap = {}
    const reviewMap = {}

    availabilityResults.forEach(
      (result, index) => {
        if (
          result.status ===
          'fulfilled'
        ) {
          availabilityMap[
            locations.value[index].id
          ] = result.value.data
        }
      }
    )

    reviewResults.forEach(
      (result, index) => {
        if (
          result.status ===
          'fulfilled'
        ) {
          reviewMap[
            locations.value[index].id
          ] = result.value.data
        }
      }
    )

    availability.value =
      availabilityMap

    ratingSummaries.value =
      reviewMap

    await nextTick()

    createMap()
    renderParkingMarkers()
  } catch (error) {
    errorMessage.value =
      error.response?.data?.detail ||
      'Unable to load parking information.'
  } finally {
    loading.value = false
  }
}

async function generateRecommendations() {
  recommending.value = true
  errorMessage.value = ''

  try {
    const response =
      await api.post(
        '/api/recommendations',
        {
          destination_latitude:
            Number(
              destination.value.latitude
            ),
          destination_longitude:
            Number(
              destination.value.longitude
            ),
          hour:
            Number(
              recommendationForm.value
                .hour
            ),
          day_of_week:
            Number(
              recommendationForm.value
                .day_of_week
            ),
          traffic_level:
            Number(
              recommendationForm.value
                .traffic_level
            ),
          weather:
            Number(
              recommendationForm.value
                .weather
            ),
          event_level:
            Number(
              recommendationForm.value
                .event_level
            ),
          preference_mode:
            recommendationForm.value
              .preference_mode,
        }
      )

    recommendations.value =
      response.data.recommendations

    selectedRecommendation.value =
      recommendations.value[0] ||
      null

    await nextTick()

    renderParkingMarkers()

    if (
      topRecommendation.value &&
      map
    ) {
      const points =
        recommendations.value.map(
          (item) => [
            item.latitude,
            item.longitude,
          ]
        )

      points.push([
        destination.value.latitude,
        destination.value.longitude,
      ])

      map.fitBounds(
        points,
        {
          padding: [50, 50],
          maxZoom: 14,
        }
      )
    }
  } catch (error) {
    errorMessage.value =
      error.response?.data?.detail ||
      'Unable to generate parking recommendations.'
  } finally {
    recommending.value = false
  }
}

function setDefaultReservationTimes() {
  const start = new Date()

  start.setMinutes(
    0,
    0,
    0
  )

  start.setHours(
    start.getHours() + 1
  )

  const end =
    new Date(
      start.getTime() +
        60 * 60 * 1000
    )

  const toInputValue = (date) => {
    const local =
      new Date(
        date.getTime() -
          date.getTimezoneOffset() *
            60000
      )

    return local
      .toISOString()
      .slice(0, 16)
  }

  reservationForm.value
    .reserved_from =
    toInputValue(start)

  reservationForm.value
    .reserved_until =
    toInputValue(end)
}

async function openBooking(item) {
  const locationId =
    item.parking_location_id ||
    item.id

  if (!locationId) {
    errorMessage.value =
      'Parking location could not be determined.'
    return
  }

  await router.push({
    name: 'book-parking',
    params: {
      locationId,
    },
  })
}

function closeBooking() {
  bookingModalOpen.value = false
  bookingError.value = ''
}

async function createReservation() {
  booking.value = true
  bookingError.value = ''
  successReservation.value = null

  try {
    if (
      !reservationForm.value
        .vehicle_id
    ) {
      throw new Error(
        'Please select a vehicle.'
      )
    }

    const start =
      new Date(
        reservationForm.value
          .reserved_from
      )

    const end =
      new Date(
        reservationForm.value
          .reserved_until
      )

    if (
      !Number.isFinite(
        start.getTime()
      ) ||
      !Number.isFinite(
        end.getTime()
      )
    ) {
      throw new Error(
        'Please select valid reservation times.'
      )
    }

    if (end <= start) {
      throw new Error(
        'Reservation end time must be later than the start time.'
      )
    }

    const response =
      await api.post(
        '/api/reservations',
        {
          vehicle_id:
            reservationForm.value
              .vehicle_id,
          parking_location_id:
            reservationForm.value
              .parking_location_id,
          reserved_from:
            start.toISOString(),
          reserved_until:
            end.toISOString(),
        }
      )

    successReservation.value =
      response.data

    await loadParkingData()
  } catch (error) {
    bookingError.value =
      error.response?.data?.detail ||
      error.message ||
      'Unable to create reservation.'
  } finally {
    booking.value = false
  }
}

function toggleBreakdown(item) {
  expandedRecommendation.value =
    expandedRecommendation.value ===
    item.parking_location_id
      ? null
      : item.parking_location_id
}

onMounted(async () => {
  await loadParkingData()
})

onUnmounted(() => {
  if (map) {
    map.remove()
    map = null
  }
})
</script>

<template>
  <AppShell>
    <section class="mx-auto max-w-7xl">
      <div
        class="relative overflow-hidden rounded-[2rem] bg-slate-950 px-6 py-8 text-white shadow-2xl sm:px-8 lg:px-10"
      >
        <div
          class="absolute -right-20 -top-20 h-72 w-72 rounded-full bg-emerald-500/20 blur-3xl"
        />

        <div
          class="relative grid gap-8 lg:grid-cols-[1fr_auto] lg:items-center"
        >
          <div>
            <div
              class="inline-flex items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1.5 text-xs font-semibold text-emerald-300"
            >
              <BrainCircuit
                :size="15"
              />
              AI parking recommender
            </div>

            <h1
              class="mt-5 max-w-3xl text-3xl font-black tracking-tight sm:text-4xl lg:text-5xl"
            >
              Find the best parking,
              not just the nearest.
            </h1>

            <p
              class="mt-4 max-w-2xl text-sm leading-7 text-slate-300 sm:text-base"
            >
              SmartPark ranks locations
              using distance, price, live
              availability, predicted
              occupancy and user ratings.
            </p>
          </div>

          <div
            class="grid grid-cols-3 gap-3"
          >
            <div
              class="rounded-2xl border border-white/10 bg-white/5 p-4"
            >
              <Navigation
                :size="20"
                class="text-cyan-400"
              />

              <p
                class="mt-3 text-xs text-slate-400"
              >
                Distance
              </p>

              <p
                class="mt-1 font-bold"
              >
                Ranked
              </p>
            </div>

            <div
              class="rounded-2xl border border-white/10 bg-white/5 p-4"
            >
              <Gauge
                :size="20"
                class="text-emerald-400"
              />

              <p
                class="mt-3 text-xs text-slate-400"
              >
                Demand
              </p>

              <p
                class="mt-1 font-bold"
              >
                Predicted
              </p>
            </div>

            <div
              class="rounded-2xl border border-white/10 bg-white/5 p-4"
            >
              <Star
                :size="20"
                class="text-amber-400"
              />

              <p
                class="mt-3 text-xs text-slate-400"
              >
                Reviews
              </p>

              <p
                class="mt-1 font-bold"
              >
                Included
              </p>
            </div>
          </div>
        </div>
      </div>

      <div
        v-if="errorMessage"
        class="mt-6 rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-700"
      >
        {{ errorMessage }}
      </div>

      <div
        class="mt-7 grid gap-6 xl:grid-cols-[390px_1fr]"
      >
        <aside
          class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm"
        >
          <div
            class="flex items-center gap-3"
          >
            <div
              class="flex h-11 w-11 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600"
            >
              <Sparkles
                :size="20"
              />
            </div>

            <div>
              <h2
                class="font-bold text-slate-900"
              >
                Smart search
              </h2>

              <p
                class="text-xs text-slate-500"
              >
                Configure your destination
              </p>
            </div>
          </div>

          <div class="mt-6">
            <label
              class="text-sm font-semibold text-slate-700"
            >
              Destination
            </label>

            <p
              class="mt-1 text-xs leading-5 text-slate-400"
            >
              Click anywhere on the map
              to move the destination.
            </p>

            <div
              class="mt-3 grid grid-cols-2 gap-2"
            >
              <input
                v-model.number="
                  destination.latitude
                "
                type="number"
                step="0.000001"
                class="rounded-xl border border-slate-200 px-3 py-3 text-sm outline-none focus:border-emerald-500"
              >

              <input
                v-model.number="
                  destination.longitude
                "
                type="number"
                step="0.000001"
                class="rounded-xl border border-slate-200 px-3 py-3 text-sm outline-none focus:border-emerald-500"
              >
            </div>

            <button
              class="mt-3 flex w-full items-center justify-center gap-2 rounded-xl bg-slate-100 px-4 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-200"
              type="button"
              @click="useMyLocation"
            >
              <LocateFixed
                :size="17"
              />
              Use my location
            </button>
          </div>

          <div class="mt-6">
            <label
              class="text-sm font-semibold text-slate-700"
            >
              Recommendation priority
            </label>

            <div
              class="mt-3 space-y-2"
            >
              <button
                v-for="mode in preferenceModes"
                :key="mode.value"
                type="button"
                class="flex w-full items-center justify-between rounded-xl border p-3 text-left transition"
                :class="
                  recommendationForm.preference_mode ===
                  mode.value
                    ? 'border-emerald-500 bg-emerald-50'
                    : 'border-slate-200 hover:border-slate-300'
                "
                @click="
                  recommendationForm.preference_mode =
                    mode.value
                "
              >
                <div>
                  <p
                    class="text-sm font-semibold text-slate-800"
                  >
                    {{ mode.label }}
                  </p>

                  <p
                    class="mt-0.5 text-xs text-slate-400"
                  >
                    {{ mode.description }}
                  </p>
                </div>

                <CheckCircle2
                  v-if="
                    recommendationForm.preference_mode ===
                    mode.value
                  "
                  :size="19"
                  class="text-emerald-600"
                />
              </button>
            </div>
          </div>

          <div
            class="mt-6 grid grid-cols-2 gap-3"
          >
            <div>
              <label
                class="mb-2 block text-xs font-semibold text-slate-600"
              >
                Hour
              </label>

              <input
                v-model.number="
                  recommendationForm.hour
                "
                type="number"
                min="0"
                max="23"
                class="w-full rounded-xl border border-slate-200 px-3 py-3 text-sm outline-none focus:border-emerald-500"
              >
            </div>

            <div>
              <label
                class="mb-2 block text-xs font-semibold text-slate-600"
              >
                Day index
              </label>

              <select
                v-model.number="
                  recommendationForm.day_of_week
                "
                class="w-full rounded-xl border border-slate-200 bg-white px-3 py-3 text-sm outline-none focus:border-emerald-500"
              >
                <option
                  v-for="day in 7"
                  :key="day - 1"
                  :value="day - 1"
                >
                  {{ day - 1 }}
                </option>
              </select>
            </div>

            <div>
              <label
                class="mb-2 block text-xs font-semibold text-slate-600"
              >
                Traffic
              </label>

              <select
                v-model.number="
                  recommendationForm.traffic_level
                "
                class="w-full rounded-xl border border-slate-200 bg-white px-3 py-3 text-sm"
              >
                <option
                  v-for="level in 4"
                  :key="level - 1"
                  :value="level - 1"
                >
                  Level {{ level - 1 }}
                </option>
              </select>
            </div>

            <div>
              <label
                class="mb-2 block text-xs font-semibold text-slate-600"
              >
                Event
              </label>

              <select
                v-model.number="
                  recommendationForm.event_level
                "
                class="w-full rounded-xl border border-slate-200 bg-white px-3 py-3 text-sm"
              >
                <option
                  v-for="level in 4"
                  :key="level - 1"
                  :value="level - 1"
                >
                  Level {{ level - 1 }}
                </option>
              </select>
            </div>

            <div class="col-span-2">
              <label
                class="mb-2 block text-xs font-semibold text-slate-600"
              >
                Weather condition
              </label>

              <select
                v-model.number="
                  recommendationForm.weather
                "
                class="w-full rounded-xl border border-slate-200 bg-white px-3 py-3 text-sm"
              >
                <option
                  v-for="condition in 4"
                  :key="condition - 1"
                  :value="condition - 1"
                >
                  Condition
                  {{ condition - 1 }}
                </option>
              </select>
            </div>
          </div>

          <button
            class="mt-6 flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 px-5 py-4 font-bold text-white shadow-lg shadow-emerald-600/20 transition hover:-translate-y-0.5 disabled:opacity-60"
            :disabled="recommending"
            @click="
              generateRecommendations
            "
          >
            <BrainCircuit
              :size="19"
            />

            {{
              recommending
                ? 'Analysing locations...'
                : 'Generate smart recommendations'
            }}
          </button>
        </aside>

        <div class="space-y-6">
          <section
            class="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm"
          >
            <div
              class="flex flex-col gap-4 border-b border-slate-200 p-5 sm:flex-row sm:items-center sm:justify-between"
            >
              <div>
                <h2
                  class="font-bold text-slate-900"
                >
                  Intelligent parking map
                </h2>

                <p
                  class="mt-1 text-xs text-slate-500"
                >
                  Click the map to choose
                  your destination.
                </p>
              </div>

              <div
                class="flex flex-wrap gap-2"
              >
                <button
                  type="button"
                  class="inline-flex items-center gap-2 rounded-xl border px-4 py-2.5 text-xs font-semibold transition"
                  :class="
                    showOpenData
                      ? 'border-violet-300 bg-violet-50 text-violet-700'
                      : 'border-slate-200 text-slate-600 hover:bg-slate-50'
                  "
                  @click="
                    toggleOpenData
                  "
                >
                  <MapPin
                    :size="15"
                  />

                  {{
                    showOpenData
                      ? 'Hide Camden Open Data'
                      : 'Show Camden Open Data'
                  }}
                </button>

                <button
                  class="inline-flex items-center gap-2 rounded-xl border border-slate-200 px-4 py-2.5 text-xs font-semibold text-slate-600"
                  @click="
                    loadParkingData
                  "
                >
                  <RefreshCw
                    :size="15"
                  />
                  Refresh live data
                </button>
              </div>
            </div>

            <div
              v-if="showOpenData"
              class="border-b border-violet-100 bg-violet-50/70 px-5 py-4"
            >
              <div
                class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between"
              >
                <div>
                  <p
                    class="text-sm font-bold text-violet-900"
                  >
                    London Borough of Camden
                    Open Data
                  </p>

                  <p
                    class="mt-1 text-xs leading-5 text-violet-700"
                  >
                    Genuine public parking
                    infrastructure records.
                    These markers are not
                    real-time occupancy data.
                  </p>
                </div>

                <div
                  v-if="openDataStats"
                  class="flex flex-wrap gap-2 text-xs"
                >
                  <span
                    class="rounded-full bg-white px-3 py-1.5 font-semibold text-violet-700 shadow-sm"
                  >
                    {{
                      openDataStats.total_records.toLocaleString()
                    }}
                    records
                  </span>

                  <span
                    class="rounded-full bg-white px-3 py-1.5 font-semibold text-violet-700 shadow-sm"
                  >
                    {{
                      openDataStats.declared_parking_spaces.toLocaleString()
                    }}
                    spaces
                  </span>

                  <span
                    class="rounded-full bg-white px-3 py-1.5 font-semibold text-violet-700 shadow-sm"
                  >
                    {{
                      openDataStats.ev_charging_records.toLocaleString()
                    }}
                    EV bays
                  </span>
                </div>
              </div>

              <p
                v-if="openDataLoading"
                class="mt-3 text-xs font-semibold text-violet-600"
              >
                Loading visible Camden
                parking bays…
              </p>

              <p
                v-if="openDataError"
                class="mt-3 text-xs font-semibold text-red-600"
              >
                {{ openDataError }}
              </p>

              <p
                v-if="
                  !openDataLoading &&
                  !openDataError
                "
                class="mt-3 text-xs text-violet-600"
              >
                {{
                  openDataBays.length.toLocaleString()
                }}
                records currently displayed
                within the visible map area.
                Maximum 500 markers per
                request for performance.
              </p>
            </div>

            <div
              ref="mapElement"
              class="h-[520px] w-full bg-slate-100"
            />
          </section>

          <section
            v-if="recommendations.length"
          >
            <div
              class="flex items-end justify-between"
            >
              <div>
                <p
                  class="text-sm font-semibold text-emerald-600"
                >
                  AI ranking
                </p>

                <h2
                  class="mt-1 text-2xl font-bold text-slate-900"
                >
                  Recommended parking
                </h2>
              </div>

              <span
                class="rounded-full bg-slate-100 px-3 py-1.5 text-xs font-semibold text-slate-600"
              >
                {{
                  recommendations.length
                }}
                locations analysed
              </span>
            </div>

            <div
              class="mt-5 space-y-4"
            >
              <article
                v-for="item in recommendations"
                :key="
                  item.parking_location_id
                "
                class="overflow-hidden rounded-3xl border bg-white shadow-sm transition hover:-translate-y-0.5 hover:shadow-lg"
                :class="
                  item.recommendation_rank ===
                  1
                    ? 'border-emerald-300 ring-1 ring-emerald-100'
                    : 'border-slate-200'
                "
              >
                <div
                  v-if="
                    item.recommendation_rank ===
                    1
                  "
                  class="flex items-center gap-2 bg-emerald-600 px-5 py-2 text-xs font-bold text-white"
                >
                  <Crown
                    :size="15"
                  />
                  BEST MATCH
                </div>

                <div class="p-5">
                  <div
                    class="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between"
                  >
                    <div
                      class="flex gap-4"
                    >
                      <div
                        class="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-slate-950 text-lg font-black text-white"
                      >
                        #{{
                          item.recommendation_rank
                        }}
                      </div>

                      <div>
                        <h3
                          class="text-lg font-bold text-slate-900"
                        >
                          {{
                            item.parking_name
                          }}
                        </h3>

                        <div
                          class="mt-2 flex flex-wrap gap-3 text-xs text-slate-500"
                        >
                          <span
                            class="inline-flex items-center gap-1"
                          >
                            <Navigation
                              :size="14"
                            />
                            {{
                              item.distance_km.toFixed(
                                2
                              )
                            }}
                            km
                          </span>

                          <span
                            class="inline-flex items-center gap-1"
                          >
                            <PoundSterling
                              :size="14"
                            />
                            {{
                              item.hourly_rate.toFixed(
                                2
                              )
                            }}/hr
                          </span>

                          <span
                            class="inline-flex items-center gap-1"
                          >
                            <Star
                              :size="14"
                            />
                            {{
                              item.rating.toFixed(
                                1
                              )
                            }}/5
                            ({{
                              item.review_count
                            }})
                          </span>
                        </div>
                      </div>
                    </div>

                    <div
                      class="text-left lg:text-right"
                    >
                      <p
                        class="text-xs font-semibold uppercase tracking-wide text-slate-400"
                      >
                        AI score
                      </p>

                      <p
                        class="mt-1 text-3xl font-black"
                        :class="
                          recommendationScoreClass(
                            item.recommendation_score
                          )
                        "
                      >
                        {{
                          item.recommendation_score.toFixed(
                            1
                          )
                        }}
                      </p>
                    </div>
                  </div>

                  <div
                    class="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-4"
                  >
                    <div
                      class="rounded-xl bg-slate-50 p-3"
                    >
                      <p
                        class="text-xs text-slate-400"
                      >
                        Free now
                      </p>

                      <p
                        class="mt-1 text-lg font-bold text-slate-900"
                      >
                        {{
                          item.current_available_spaces
                        }}
                        /
                        {{
                          item.total_spaces
                        }}
                      </p>
                    </div>

                    <div
                      class="rounded-xl bg-slate-50 p-3"
                    >
                      <p
                        class="text-xs text-slate-400"
                      >
                        Predicted free
                      </p>

                      <p
                        class="mt-1 text-lg font-bold text-emerald-600"
                      >
                        {{
                          item.predicted_available_spaces
                        }}
                      </p>
                    </div>

                    <div
                      class="rounded-xl bg-slate-50 p-3"
                    >
                      <p
                        class="text-xs text-slate-400"
                      >
                        Current occupancy
                      </p>

                      <p
                        class="mt-1 text-lg font-bold text-slate-900"
                      >
                        {{
                          item.current_occupancy.toFixed(
                            1
                          )
                        }}%
                      </p>
                    </div>

                    <div
                      class="rounded-xl bg-slate-50 p-3"
                    >
                      <p
                        class="text-xs text-slate-400"
                      >
                        Predicted
                      </p>

                      <p
                        class="mt-1 text-lg font-bold"
                      >
                        {{
                          item.predicted_occupancy.toFixed(
                            1
                          )
                        }}%
                      </p>
                    </div>
                  </div>

                  <div
                    class="mt-4 flex flex-wrap gap-2"
                  >
                    <span
                      v-for="reason in item.recommendation_reasons.slice(
                        0,
                        3
                      )"
                      :key="reason"
                      class="rounded-full bg-emerald-50 px-3 py-1.5 text-xs font-medium text-emerald-700"
                    >
                      {{ reason }}
                    </span>
                  </div>

                  <button
                    class="mt-4 flex items-center gap-1 text-xs font-semibold text-slate-500 hover:text-slate-900"
                    @click="
                      toggleBreakdown(
                        item
                      )
                    "
                  >
                    <ChevronUp
                      v-if="
                        expandedRecommendation ===
                        item.parking_location_id
                      "
                      :size="15"
                    />

                    <ChevronDown
                      v-else
                      :size="15"
                    />

                    AI score breakdown
                  </button>

                  <div
                    v-if="
                      expandedRecommendation ===
                      item.parking_location_id
                    "
                    class="mt-4 grid grid-cols-2 gap-3 rounded-2xl bg-slate-50 p-4 sm:grid-cols-4"
                  >
                    <div
                      v-for="(
                        value,
                        key
                      ) in item.score_breakdown"
                      :key="key"
                    >
                      <p
                        class="text-[11px] capitalize text-slate-400"
                      >
                        {{
                          key.replaceAll(
                            '_',
                            ' '
                          )
                        }}
                      </p>

                      <p
                        class="mt-1 font-bold text-slate-800"
                      >
                        {{
                          Number(
                            value
                          ).toFixed(1)
                        }}
                      </p>
                    </div>
                  </div>

                  <div
                    class="mt-5 flex flex-col gap-2 sm:flex-row"
                  >
                    <button
                      class="flex flex-1 items-center justify-center gap-2 rounded-xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
                      @click="
                        focusLocation(
                          item
                        )
                      "
                    >
                      <MapPin
                        :size="17"
                      />
                      View on map
                    </button>

                    <button
                      class="flex flex-1 items-center justify-center gap-2 rounded-xl bg-emerald-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-emerald-700"
                      @click="
                        openBooking(
                          item
                        )
                      "
                    >
                      <CalendarDays
                        :size="17"
                      />
                      Reserve parking
                    </button>
                  </div>
                </div>
              </article>
            </div>
          </section>

          <section
            v-else
            class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm"
          >
            <div
              class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between"
            >
              <div>
                <h2
                  class="text-xl font-bold text-slate-900"
                >
                  Browse parking locations
                </h2>

                <p
                  class="mt-1 text-sm text-slate-500"
                >
                  Generate AI
                  recommendations for
                  intelligent ranking.
                </p>
              </div>

              <div class="relative">
                <Search
                  :size="17"
                  class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
                />

                <input
                  v-model="searchQuery"
                  placeholder="Search parking..."
                  class="rounded-xl border border-slate-200 py-2.5 pl-10 pr-3 text-sm outline-none focus:border-emerald-500"
                  @input="
                    nextTick(
                      renderParkingMarkers
                    )
                  "
                >
              </div>
            </div>

            <div
              class="mt-5 grid gap-4 md:grid-cols-2"
            >
              <article
                v-for="location in filteredLocations"
                :key="location.id"
                class="rounded-2xl border border-slate-200 p-5 transition hover:border-emerald-200 hover:shadow-md"
              >
                <div
                  class="flex items-start justify-between gap-4"
                >
                  <div>
                    <h3
                      class="font-bold text-slate-900"
                    >
                      {{ location.name }}
                    </h3>

                    <p
                      class="mt-1 text-xs leading-5 text-slate-500"
                    >
                      {{
                        location.address
                      }},
                      {{ location.city }}
                    </p>
                  </div>

                  <span
                    class="rounded-full px-3 py-1 text-xs font-semibold"
                    :class="
                      occupancyStatus(
                        availability[
                          location.id
                        ]
                          ?.occupancy_percentage ||
                          0
                      ).class
                    "
                  >
                    {{
                      availability[
                        location.id
                      ]
                        ?.available_spaces ??
                      '—'
                    }}
                    free
                  </span>
                </div>

                <div
                  class="mt-4 flex items-center justify-between text-xs text-slate-500"
                >
                  <span>
                    £{{
                      Number(
                        location.hourly_rate
                      ).toFixed(2)
                    }}/hr
                  </span>

                  <span>
                    {{
                      openingHours(
                        location
                      )
                    }}
                  </span>

                  <span
                    class="inline-flex items-center gap-1"
                  >
                    <Star
                      :size="13"
                    />
                    {{
                      ratingFor(
                        location.id
                      ).average_rating.toFixed(
                        1
                      )
                    }}
                  </span>
                </div>

                <div
                  v-if="
                    Number(
                      availability[
                        location.id
                      ]?.total_ev_chargers ||
                        0
                    ) > 0
                  "
                  class="mt-4 rounded-2xl border border-amber-200 bg-amber-50/60 p-4"
                >
                  <div
                    class="flex items-center justify-between gap-3"
                  >
                    <div
                      class="flex items-center gap-2"
                    >
                      <div
                        class="flex h-9 w-9 items-center justify-center rounded-xl bg-amber-100 text-amber-700"
                      >
                        <Zap :size="17" />
                      </div>

                      <div>
                        <p
                          class="text-sm font-bold text-slate-800"
                        >
                          EV Charging
                        </p>

                        <p
                          class="text-xs text-slate-500"
                        >
                          Live charger status
                        </p>
                      </div>
                    </div>

                    <div
                      class="text-right"
                    >
                      <p
                        class="text-base font-black text-emerald-700"
                      >
                        {{
                          availability[
                            location.id
                          ]
                            ?.available_ev_chargers ??
                          0
                        }}
                        /
                        {{
                          availability[
                            location.id
                          ]
                            ?.total_ev_chargers ??
                          0
                        }}
                      </p>

                      <p
                        class="text-[11px] font-semibold text-slate-500"
                      >
                        available
                      </p>
                    </div>
                  </div>

                  <div
                    class="mt-3 flex flex-wrap gap-2 text-[11px] font-semibold"
                  >
                    <span
                      class="rounded-full bg-white px-2.5 py-1 text-amber-700"
                    >
                      {{
                        availability[
                          location.id
                        ]
                          ?.occupied_ev_chargers ??
                        0
                      }}
                      occupied
                    </span>

                    <span
                      class="rounded-full bg-white px-2.5 py-1 text-red-600"
                    >
                      {{
                        availability[
                          location.id
                        ]
                          ?.offline_ev_chargers ??
                        0
                      }}
                      offline
                    </span>

                    <span
                      class="rounded-full bg-white px-2.5 py-1 text-violet-700"
                    >
                      {{
                        availability[
                          location.id
                        ]
                          ?.maintenance_ev_chargers ??
                        0
                      }}
                      maintenance
                    </span>
                  </div>
                </div>

                <button
                  class="mt-4 w-full rounded-xl bg-slate-100 px-4 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-200"
                  @click="
                    focusLocation(
                      location
                    )
                  "
                >
                  View location
                </button>
              </article>
            </div>
          </section>
        </div>
      </div>
    </section>

    <template>
      <div
        v-if="bookingModalOpen"
        class="fixed inset-0 z-[9999] flex items-center justify-center bg-slate-950/65 p-4 backdrop-blur-sm"
        @click.self="
          closeBooking
        "
      >
        <div
          class="w-full max-w-xl overflow-hidden rounded-3xl bg-white shadow-2xl"
        >
          <div
            class="flex items-center justify-between border-b border-slate-200 p-6"
          >
            <div>
              <p
                class="text-sm font-semibold text-emerald-600"
              >
                SmartPark reservation
              </p>

              <h2
                class="mt-1 text-xl font-bold text-slate-900"
              >
                Reserve your parking
              </h2>
            </div>

            <button
              class="rounded-xl p-2 text-slate-400 hover:bg-slate-100 hover:text-slate-700"
              @click="
                closeBooking
              "
            >
              <X :size="21" />
            </button>
          </div>

          <div class="p-6">
            <div
              v-if="successReservation"
              class="text-center"
            >
              <div
                class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-emerald-100 text-emerald-600"
              >
                <Trophy
                  :size="30"
                />
              </div>

              <h3
                class="mt-5 text-2xl font-bold text-slate-900"
              >
                Parking reserved
              </h3>

              <p
                class="mt-2 text-sm text-slate-500"
              >
                Your booking has been
                created successfully.
              </p>

              <div
                class="mt-6 rounded-2xl bg-slate-950 p-5 text-white"
              >
                <p
                  class="text-xs uppercase tracking-widest text-slate-400"
                >
                  Booking code
                </p>

                <p
                  class="mt-2 text-3xl font-black tracking-wider text-emerald-400"
                >
                  {{
                    successReservation.booking_code
                  }}
                </p>

                <p
                  class="mt-3 text-sm text-slate-300"
                >
                  Estimated cost:
                  £{{
                    Number(
                      successReservation.estimated_cost
                    ).toFixed(2)
                  }}
                </p>
              </div>

              <button
                class="mt-6 w-full rounded-xl bg-emerald-600 px-4 py-3 font-semibold text-white"
                @click="
                  closeBooking
                "
              >
                Done
              </button>
            </div>

            <form
              v-else
              class="space-y-5"
              @submit.prevent="
                createReservation
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
                    reservationForm.vehicle_id
                  "
                  required
                  class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 outline-none focus:border-emerald-500"
                >
                  <option
                    value=""
                    disabled
                  >
                    Select vehicle
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
                  v-if="
                    vehicles.length ===
                    0
                  "
                  class="mt-2 text-xs text-red-500"
                >
                  Add a vehicle before
                  creating a reservation.
                </p>
              </div>

              <div
                class="grid gap-4 sm:grid-cols-2"
              >
                <div>
                  <label
                    class="mb-2 block text-sm font-semibold text-slate-700"
                  >
                    Start time
                  </label>

                  <input
                    v-model="
                      reservationForm.reserved_from
                    "
                    type="datetime-local"
                    required
                    class="w-full rounded-xl border border-slate-200 px-4 py-3 outline-none focus:border-emerald-500"
                  >
                </div>

                <div>
                  <label
                    class="mb-2 block text-sm font-semibold text-slate-700"
                  >
                    End time
                  </label>

                  <input
                    v-model="
                      reservationForm.reserved_until
                    "
                    type="datetime-local"
                    required
                    class="w-full rounded-xl border border-slate-200 px-4 py-3 outline-none focus:border-emerald-500"
                  >
                </div>
              </div>

              <div
                v-if="bookingError"
                class="rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700"
              >
                {{ bookingError }}
              </div>

              <button
                type="submit"
                :disabled="
                  booking ||
                  vehicles.length === 0
                "
                class="flex w-full items-center justify-center gap-2 rounded-xl bg-emerald-600 px-5 py-4 font-bold text-white transition hover:bg-emerald-700 disabled:opacity-50"
              >
                <Zap
                  :size="18"
                />

                {{
                  booking
                    ? 'Creating reservation...'
                    : 'Confirm reservation'
                }}
              </button>
            </form>
          </div>
        </div>
      </div>
    </template>
  </AppShell>
</template>
