<script setup>
import {
  computed,
  onMounted,
  ref,
} from 'vue'

import {
  Activity,
  BarChart3,
  BrainCircuit,
  CalendarDays,
  CarFront,
  Clock3,
  Cpu,
  Gauge,
  History,
  Info,
  MapPin,
  RefreshCw,
  Sparkles,
  TrendingUp,
  WandSparkles,
  Zap,
} from '@lucide/vue'

import {
  Bar,
  Line,
} from 'vue-chartjs'

import {
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Filler,
  Legend,
  LineElement,
  LinearScale,
  PointElement,
  Title,
  Tooltip,
} from 'chart.js'

import AppShell from '../components/AppShell.vue'
import api from '../services/api'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Filler,
  Title,
  Tooltip,
  Legend
)

const locations = ref([])
const history = ref([])
const featureImportance = ref([])
const modelInformation = ref(null)

const loading = ref(true)
const predicting = ref(false)
const errorMessage = ref('')
const result = ref(null)

const form = ref({
  parking_location_id: '',
  hour: 18,
  day_of_week: 4,
  previous_occupancy: 65,
  traffic_level: 2,
  weather: 1,
  event_level: 1,
})

const selectedLocation = computed(() =>
  locations.value.find(
    (location) =>
      location.id ===
      form.value.parking_location_id
  )
)

const predictedOccupancy = computed(() =>
  Number(
    result.value?.predicted_occupancy ?? 0
  )
)

const predictedAvailability = computed(() =>
  Number(
    result.value?.predicted_availability ?? 0
  )
)

const currentOccupancy = computed(() =>
  Number(
    result.value?.current_occupancy ?? 0
  )
)

const occupancyDifference = computed(() => {
  if (!result.value) {
    return 0
  }

  return (
    predictedOccupancy.value -
    currentOccupancy.value
  )
})

const estimatedOccupiedSpaces = computed(() => {
  const capacity =
    Number(result.value?.total_spaces)

  if (!capacity) {
    return null
  }

  return Math.round(
    capacity *
      predictedOccupancy.value /
      100
  )
})

const estimatedFreeSpaces = computed(() => {
  const capacity =
    Number(result.value?.total_spaces)

  if (!capacity) {
    return null
  }

  return Math.max(
    0,
    capacity -
      estimatedOccupiedSpaces.value
  )
})

const gaugeDegrees = computed(() => {
  const percentage = Math.min(
    100,
    Math.max(
      0,
      predictedOccupancy.value
    )
  )

  return percentage * 3.6
})

const demandLevel = computed(() => {
  const occupancy =
    predictedOccupancy.value

  if (occupancy < 40) {
    return {
      label: 'Low demand',
      description:
        'Parking demand is expected to remain relatively low.',
      class:
        'bg-emerald-400/15 text-emerald-300 border-emerald-400/20',
      dot: 'bg-emerald-400',
    }
  }

  if (occupancy < 70) {
    return {
      label: 'Moderate demand',
      description:
        'Demand is increasing but parking availability should remain reasonable.',
      class:
        'bg-amber-400/15 text-amber-300 border-amber-400/20',
      dot: 'bg-amber-400',
    }
  }

  if (occupancy < 90) {
    return {
      label: 'High demand',
      description:
        'Parking demand is expected to be high. Earlier arrival may be preferable.',
      class:
        'bg-orange-400/15 text-orange-300 border-orange-400/20',
      dot: 'bg-orange-400',
    }
  }

  return {
    label: 'Very high demand',
    description:
      'The selected parking location is predicted to operate near capacity.',
    class:
      'bg-red-400/15 text-red-300 border-red-400/20',
    dot: 'bg-red-400',
  }
})

const comparisonData = computed(() => ({
  labels: [
    'Current occupancy',
    'Predicted occupancy',
    'Predicted availability',
  ],
  datasets: [
    {
      label: 'Percentage',
      data: [
        currentOccupancy.value,
        predictedOccupancy.value,
        predictedAvailability.value,
      ],
      borderRadius: 10,
    },
  ],
}))

const comparisonOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false,
    },
  },
  scales: {
    y: {
      beginAtZero: true,
      max: 100,
      ticks: {
        callback: (value) =>
          `${value}%`,
      },
    },
    x: {
      grid: {
        display: false,
      },
    },
  },
}

const featureImportanceData = computed(() => ({
  labels:
    featureImportance.value
      .slice(0, 7)
      .map(
        (item) =>
          item.display_name
      ),
  datasets: [
    {
      label: 'Importance',
      data:
        featureImportance.value
          .slice(0, 7)
          .map(
            (item) =>
              item.importance_percentage
          ),
      borderRadius: 8,
    },
  ],
}))

const featureImportanceOptions = {
  responsive: true,
  maintainAspectRatio: false,
  indexAxis: 'y',
  plugins: {
    legend: {
      display: false,
    },
    tooltip: {
      callbacks: {
        label: (context) =>
          `${context.raw.toFixed(2)}% importance`,
      },
    },
  },
  scales: {
    x: {
      beginAtZero: true,
      ticks: {
        callback: (value) =>
          `${value}%`,
      },
    },
    y: {
      grid: {
        display: false,
      },
    },
  },
}

const historyChartData = computed(() => {
  const recent = history.value
    .slice(0, 8)
    .reverse()

  return {
    labels: recent.map(
      (item) =>
        `${String(item.hour).padStart(
          2,
          '0'
        )}:00`
    ),
    datasets: [
      {
        label: 'Predicted occupancy',
        data: recent.map(
          (item) =>
            Number(
              item.predicted_occupancy
            )
        ),
        tension: 0.35,
        fill: true,
      },
    ],
  }
})

const historyChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false,
    },
  },
  scales: {
    y: {
      beginAtZero: true,
      max: 100,
      ticks: {
        callback: (value) =>
          `${value}%`,
      },
    },
    x: {
      grid: {
        display: false,
      },
    },
  },
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

function applyScenario(type) {
  if (type === 'quiet') {
    form.value.previous_occupancy = 25
    form.value.traffic_level = 0
    form.value.event_level = 0
    return
  }

  if (type === 'normal') {
    form.value.previous_occupancy = 55
    form.value.traffic_level = 1
    form.value.event_level = 1
    return
  }

  if (type === 'busy') {
    form.value.previous_occupancy = 80
    form.value.traffic_level = 3
    form.value.event_level = 3
  }
}

async function loadInitialData() {
  loading.value = true
  errorMessage.value = ''

  try {
    const [
      locationsResponse,
      historyResponse,
      importanceResponse,
    ] = await Promise.all([
      api.get(
        '/api/parking/locations'
      ),
      api.get(
        '/api/predictions'
      ),
      api.get(
        '/api/predictions/feature-importance'
      ),
    ])

    locations.value =
      locationsResponse.data.filter(
        (location) =>
          location.is_active
      )

    history.value =
      historyResponse.data

    featureImportance.value =
      importanceResponse.data.features

    modelInformation.value = {
      name:
        importanceResponse.data
          .model_name,
      explanation:
        importanceResponse.data
          .explanation_type,
    }

    if (
      locations.value.length &&
      !form.value.parking_location_id
    ) {
      form.value.parking_location_id =
        locations.value[0].id
    }
  } catch (error) {
    errorMessage.value =
      error.response?.data?.detail ||
      'Unable to load AI prediction data.'
  } finally {
    loading.value = false
  }
}

async function submitPrediction() {
  errorMessage.value = ''
  predicting.value = true

  try {
    const response = await api.post(
      '/api/predictions',
      {
        parking_location_id:
          form.value
            .parking_location_id,
        hour:
          Number(form.value.hour),
        day_of_week:
          Number(
            form.value.day_of_week
          ),
        previous_occupancy:
          Number(
            form.value
              .previous_occupancy
          ),
        traffic_level:
          Number(
            form.value
              .traffic_level
          ),
        weather:
          Number(
            form.value.weather
          ),
        event_level:
          Number(
            form.value
              .event_level
          ),
      }
    )

    result.value =
      response.data

    history.value = [
      response.data,
      ...history.value.filter(
        (item) =>
          item.id !==
          response.data.id
      ),
    ]
  } catch (error) {
    errorMessage.value =
      error.response?.data?.detail ||
      'Unable to generate prediction.'
  } finally {
    predicting.value = false
  }
}

onMounted(loadInitialData)
</script>

<template>
  <AppShell>
    <section class="mx-auto max-w-7xl">
      <div
        class="relative overflow-hidden rounded-[2rem] bg-slate-950 px-6 py-8 text-white shadow-2xl sm:px-8 lg:px-10"
      >
        <div
          class="absolute -right-24 -top-24 h-72 w-72 rounded-full bg-emerald-500/20 blur-3xl"
        />

        <div
          class="absolute bottom-0 left-1/3 h-48 w-48 rounded-full bg-cyan-500/10 blur-3xl"
        />

        <div
          class="relative flex flex-col gap-8 lg:flex-row lg:items-center lg:justify-between"
        >
          <div class="max-w-3xl">
            <div
              class="inline-flex items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1.5 text-xs font-semibold text-emerald-300"
            >
              <span
                class="h-2 w-2 animate-pulse rounded-full bg-emerald-400"
              />
              AI engine online
            </div>

            <h1
              class="mt-5 text-3xl font-black tracking-tight sm:text-4xl lg:text-5xl"
            >
              Intelligent Parking
              Demand Forecast
            </h1>

            <p
              class="mt-4 max-w-2xl text-sm leading-7 text-slate-300 sm:text-base"
            >
              Analyse live parking
              conditions and contextual
              inputs using SmartPark's
              tuned XGBoost prediction
              model.
            </p>
          </div>

          <div
            class="grid grid-cols-2 gap-3 sm:grid-cols-3"
          >
            <div
              class="rounded-2xl border border-white/10 bg-white/5 p-4 backdrop-blur"
            >
              <Cpu
                :size="20"
                class="text-emerald-400"
              />

              <p
                class="mt-3 text-xs text-slate-400"
              >
                Model
              </p>

              <p
                class="mt-1 text-sm font-bold"
              >
                XGBoost V2
              </p>
            </div>

            <div
              class="rounded-2xl border border-white/10 bg-white/5 p-4 backdrop-blur"
            >
              <Zap
                :size="20"
                class="text-amber-400"
              />

              <p
                class="mt-3 text-xs text-slate-400"
              >
                Prediction
              </p>

              <p
                class="mt-1 text-sm font-bold"
              >
                Real-time
              </p>
            </div>

            <div
              class="col-span-2 rounded-2xl border border-white/10 bg-white/5 p-4 backdrop-blur sm:col-span-1"
            >
              <BarChart3
                :size="20"
                class="text-cyan-400"
              />

              <p
                class="mt-3 text-xs text-slate-400"
              >
                Explainability
              </p>

              <p
                class="mt-1 text-sm font-bold"
              >
                Feature importance
              </p>
            </div>
          </div>
        </div>
      </div>

      <div
        class="mt-7 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between"
      >
        <div>
          <p
            class="text-sm font-semibold text-emerald-600"
          >
            Prediction workspace
          </p>

          <p
            class="mt-1 text-sm text-slate-500"
          >
            Configure a parking-demand
            scenario and analyse the result.
          </p>
        </div>

        <button
          class="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50"
          :disabled="loading"
          @click="loadInitialData"
        >
          <RefreshCw
            :size="17"
            :class="
              loading
                ? 'animate-spin'
                : ''
            "
          />

          Refresh AI data
        </button>
      </div>

      <div
        v-if="errorMessage"
        class="mt-6 rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-700"
      >
        {{ errorMessage }}
      </div>

      <div
        class="mt-6 grid gap-6 xl:grid-cols-[0.95fr_1.05fr]"
      >
        <section
          class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm sm:p-7"
        >
          <div
            class="flex items-center justify-between gap-4"
          >
            <div
              class="flex items-center gap-3"
            >
              <div
                class="flex h-12 w-12 items-center justify-center rounded-2xl bg-emerald-50 text-emerald-600"
              >
                <WandSparkles
                  :size="22"
                />
              </div>

              <div>
                <h2
                  class="font-bold text-slate-900"
                >
                  Scenario builder
                </h2>

                <p
                  class="text-xs text-slate-500"
                >
                  Configure model inputs
                </p>
              </div>
            </div>
          </div>

          <div
            class="mt-6 grid grid-cols-3 gap-2"
          >
            <button
              type="button"
              class="rounded-xl border border-slate-200 px-3 py-2.5 text-xs font-semibold text-slate-600 transition hover:border-emerald-300 hover:bg-emerald-50 hover:text-emerald-700"
              @click="
                applyScenario('quiet')
              "
            >
              Quiet scenario
            </button>

            <button
              type="button"
              class="rounded-xl border border-slate-200 px-3 py-2.5 text-xs font-semibold text-slate-600 transition hover:border-emerald-300 hover:bg-emerald-50 hover:text-emerald-700"
              @click="
                applyScenario('normal')
              "
            >
              Normal scenario
            </button>

            <button
              type="button"
              class="rounded-xl border border-slate-200 px-3 py-2.5 text-xs font-semibold text-slate-600 transition hover:border-emerald-300 hover:bg-emerald-50 hover:text-emerald-700"
              @click="
                applyScenario('busy')
              "
            >
              Busy scenario
            </button>
          </div>

          <form
            class="mt-6 space-y-5"
            @submit.prevent="
              submitPrediction
            "
          >
            <div>
              <label
                class="mb-2 flex items-center gap-2 text-sm font-semibold text-slate-700"
              >
                <MapPin :size="16" />
                Parking location
              </label>

              <select
                v-model="
                  form.parking_location_id
                "
                required
                class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3.5 outline-none transition focus:border-emerald-500 focus:ring-4 focus:ring-emerald-100"
              >
                <option
                  value=""
                  disabled
                >
                  Select parking location
                </option>

                <option
                  v-for="location in locations"
                  :key="location.id"
                  :value="location.id"
                >
                  {{ location.name }}
                </option>
              </select>

              <div
                v-if="selectedLocation"
                class="mt-3 grid grid-cols-2 gap-3 rounded-xl bg-slate-50 p-4 text-xs"
              >
                <div>
                  <p
                    class="text-slate-400"
                  >
                    Price
                  </p>

                  <p
                    class="mt-1 font-bold text-slate-700"
                  >
                    £{{
                      Number(
                        selectedLocation.hourly_rate
                      ).toFixed(2)
                    }}/hr
                  </p>
                </div>

                <div>
                  <p
                    class="text-slate-400"
                  >
                    Capacity
                  </p>

                  <p
                    class="mt-1 font-bold text-slate-700"
                  >
                    {{
                      selectedLocation.total_spaces
                    }}
                    spaces
                  </p>
                </div>
              </div>
            </div>

            <div
              class="grid gap-4 sm:grid-cols-2"
            >
              <div>
                <label
                  class="mb-2 flex items-center gap-2 text-sm font-semibold text-slate-700"
                >
                  <Clock3 :size="16" />
                  Hour
                </label>

                <input
                  v-model.number="
                    form.hour
                  "
                  type="number"
                  min="0"
                  max="23"
                  required
                  class="w-full rounded-xl border border-slate-200 px-4 py-3 outline-none transition focus:border-emerald-500 focus:ring-4 focus:ring-emerald-100"
                >
              </div>

              <div>
                <label
                  class="mb-2 flex items-center gap-2 text-sm font-semibold text-slate-700"
                >
                  <CalendarDays
                    :size="16"
                  />
                  Day index
                </label>

                <select
                  v-model.number="
                    form.day_of_week
                  "
                  class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 outline-none transition focus:border-emerald-500 focus:ring-4 focus:ring-emerald-100"
                >
                  <option
                    v-for="day in 7"
                    :key="day - 1"
                    :value="day - 1"
                  >
                    Day {{ day - 1 }}
                  </option>
                </select>
              </div>
            </div>

            <div
              class="rounded-2xl border border-slate-200 p-4"
            >
              <div
                class="flex items-center justify-between"
              >
                <div>
                  <p
                    class="text-sm font-semibold text-slate-700"
                  >
                    Previous occupancy
                  </p>

                  <p
                    class="mt-1 text-xs text-slate-400"
                  >
                    Historical occupancy input
                  </p>
                </div>

                <span
                  class="rounded-full bg-emerald-50 px-3 py-1.5 text-sm font-bold text-emerald-700"
                >
                  {{
                    form.previous_occupancy
                  }}%
                </span>
              </div>

              <input
                v-model.number="
                  form.previous_occupancy
                "
                type="range"
                min="0"
                max="100"
                step="1"
                class="mt-4 w-full accent-emerald-600"
              >
            </div>

            <div
              class="grid gap-4 sm:grid-cols-3"
            >
              <div>
                <label
                  class="mb-2 block text-xs font-semibold text-slate-600"
                >
                  Traffic level
                </label>

                <select
                  v-model.number="
                    form.traffic_level
                  "
                  class="w-full rounded-xl border border-slate-200 bg-white px-3 py-3 text-sm outline-none focus:border-emerald-500"
                >
                  <option :value="0">
                    Level 0
                  </option>
                  <option :value="1">
                    Level 1
                  </option>
                  <option :value="2">
                    Level 2
                  </option>
                  <option :value="3">
                    Level 3
                  </option>
                </select>
              </div>

              <div>
                <label
                  class="mb-2 block text-xs font-semibold text-slate-600"
                >
                  Event level
                </label>

                <select
                  v-model.number="
                    form.event_level
                  "
                  class="w-full rounded-xl border border-slate-200 bg-white px-3 py-3 text-sm outline-none focus:border-emerald-500"
                >
                  <option :value="0">
                    Level 0
                  </option>
                  <option :value="1">
                    Level 1
                  </option>
                  <option :value="2">
                    Level 2
                  </option>
                  <option :value="3">
                    Level 3
                  </option>
                </select>
              </div>

              <div>
                <label
                  class="mb-2 block text-xs font-semibold text-slate-600"
                >
                  Weather code
                </label>

                <select
                  v-model.number="
                    form.weather
                  "
                  class="w-full rounded-xl border border-slate-200 bg-white px-3 py-3 text-sm outline-none focus:border-emerald-500"
                >
                  <option :value="0">
                    Condition 0
                  </option>
                  <option :value="1">
                    Condition 1
                  </option>
                  <option :value="2">
                    Condition 2
                  </option>
                  <option :value="3">
                    Condition 3
                  </option>
                </select>
              </div>
            </div>

            <div
              class="flex gap-2 rounded-xl bg-blue-50 p-3 text-xs leading-5 text-blue-700"
            >
              <Info
                :size="17"
                class="mt-0.5 shrink-0"
              />

              <span>
                Context values use the
                same encoded 0–3 inputs
                used when training the
                prototype ML model.
              </span>
            </div>

            <button
              type="submit"
              :disabled="
                predicting ||
                !form.parking_location_id
              "
              class="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 px-5 py-4 font-bold text-white shadow-lg shadow-emerald-600/20 transition hover:-translate-y-0.5 hover:shadow-xl disabled:cursor-not-allowed disabled:opacity-60"
            >
              <BrainCircuit
                :size="20"
              />

              {{
                predicting
                  ? 'Running XGBoost model...'
                  : 'Generate AI prediction'
              }}
            </button>
          </form>
        </section>

        <section
          class="overflow-hidden rounded-3xl bg-slate-950 p-6 text-white shadow-xl sm:p-7"
        >
          <div
            class="flex items-start justify-between"
          >
            <div
              class="flex items-center gap-3"
            >
              <div
                class="flex h-12 w-12 items-center justify-center rounded-2xl bg-emerald-500 text-slate-950"
              >
                <Gauge :size="23" />
              </div>

              <div>
                <h2 class="font-bold">
                  AI forecast
                </h2>

                <p
                  class="text-xs text-slate-400"
                >
                  Occupancy intelligence
                </p>
              </div>
            </div>

            <span
              v-if="result"
              class="rounded-full border px-3 py-1.5 text-xs font-semibold"
              :class="
                demandLevel.class
              "
            >
              <span
                class="mr-2 inline-block h-2 w-2 rounded-full"
                :class="
                  demandLevel.dot
                "
              />

              {{ demandLevel.label }}
            </span>
          </div>

          <div
            v-if="!result"
            class="flex min-h-[500px] flex-col items-center justify-center text-center"
          >
            <div
              class="relative flex h-32 w-32 items-center justify-center rounded-full border border-white/10 bg-white/5"
            >
              <div
                class="absolute inset-3 animate-pulse rounded-full border border-emerald-400/20"
              />

              <BrainCircuit
                :size="46"
                class="text-emerald-400"
              />
            </div>

            <h3
              class="mt-6 text-xl font-bold"
            >
              Ready to predict
            </h3>

            <p
              class="mt-3 max-w-sm text-sm leading-6 text-slate-400"
            >
              Configure a scenario and
              SmartPark AI will estimate
              future parking occupancy.
            </p>
          </div>

          <div
            v-else
            class="mt-8"
          >
            <div
              class="grid gap-6 sm:grid-cols-[220px_1fr] sm:items-center"
            >
              <div
                class="mx-auto"
              >
                <div
                  class="relative flex h-48 w-48 items-center justify-center rounded-full"
                  :style="{
                    background:
                      `conic-gradient(
                        #10b981 ${gaugeDegrees}deg,
                        rgba(255,255,255,.08) ${gaugeDegrees}deg
                      )`,
                  }"
                >
                  <div
                    class="flex h-40 w-40 flex-col items-center justify-center rounded-full bg-slate-950"
                  >
                    <p
                      class="text-4xl font-black"
                    >
                      {{
                        predictedOccupancy.toFixed(
                          1
                        )
                      }}%
                    </p>

                    <p
                      class="mt-1 text-xs text-slate-400"
                    >
                      predicted occupancy
                    </p>
                  </div>
                </div>
              </div>

              <div>
                <p
                  class="text-sm font-semibold text-slate-300"
                >
                  {{
                    locationName(
                      result.parking_location_id
                    )
                  }}
                </p>

                <p
                  class="mt-3 text-sm leading-6 text-slate-400"
                >
                  {{
                    demandLevel.description
                  }}
                </p>

                <div
                  class="mt-5 flex items-center gap-2"
                >
                  <TrendingUp
                    :size="18"
                    :class="
                      occupancyDifference >= 0
                        ? 'text-amber-400'
                        : 'rotate-180 text-emerald-400'
                    "
                  />

                  <span
                    class="text-sm font-semibold"
                  >
                    {{
                      Math.abs(
                        occupancyDifference
                      ).toFixed(1)
                    }}
                    percentage points
                    {{
                      occupancyDifference >= 0
                        ? 'above'
                        : 'below'
                    }}
                    current occupancy
                  </span>
                </div>
              </div>
            </div>

            <div
              class="mt-7 grid grid-cols-2 gap-3 lg:grid-cols-4"
            >
              <div
                class="rounded-2xl border border-white/10 bg-white/5 p-4"
              >
                <p
                  class="text-xs text-slate-400"
                >
                  Current
                </p>

                <p
                  class="mt-2 text-xl font-bold"
                >
                  {{
                    currentOccupancy.toFixed(
                      1
                    )
                  }}%
                </p>
              </div>

              <div
                class="rounded-2xl border border-white/10 bg-white/5 p-4"
              >
                <p
                  class="text-xs text-slate-400"
                >
                  Available
                </p>

                <p
                  class="mt-2 text-xl font-bold text-emerald-400"
                >
                  {{
                    predictedAvailability.toFixed(
                      1
                    )
                  }}%
                </p>
              </div>

              <div
                class="rounded-2xl border border-white/10 bg-white/5 p-4"
              >
                <p
                  class="text-xs text-slate-400"
                >
                  Est. free
                </p>

                <p
                  class="mt-2 text-xl font-bold"
                >
                  {{
                    estimatedFreeSpaces ??
                    '—'
                  }}
                </p>
              </div>

              <div
                class="rounded-2xl border border-white/10 bg-white/5 p-4"
              >
                <p
                  class="text-xs text-slate-400"
                >
                  Capacity
                </p>

                <p
                  class="mt-2 text-xl font-bold"
                >
                  {{
                    result.total_spaces ??
                    '—'
                  }}
                </p>
              </div>
            </div>

            <div
              class="mt-6 h-60 rounded-2xl bg-white p-4"
            >
              <Bar
                :data="
                  comparisonData
                "
                :options="
                  comparisonOptions
                "
              />
            </div>

            <div
              class="mt-4 flex flex-wrap gap-2"
            >
              <span
                class="rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-xs text-slate-300"
              >
                Model:
                {{
                  result.model_version ||
                  'V2'
                }}
              </span>

              <span
                class="rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-xs text-slate-300"
              >
                Live spaces:
                {{
                  result.available_spaces
                }}
              </span>

              <span
                class="rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-xs text-slate-300"
              >
                Est. occupied:
                {{
                  estimatedOccupiedSpaces ??
                  '—'
                }}
              </span>
            </div>
          </div>
        </section>
      </div>

      <div
        class="mt-7 grid gap-6 xl:grid-cols-2"
      >
        <section
          class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm"
        >
          <div
            class="flex items-center justify-between"
          >
            <div
              class="flex items-center gap-3"
            >
              <div
                class="flex h-11 w-11 items-center justify-center rounded-xl bg-violet-50 text-violet-600"
              >
                <BarChart3
                  :size="21"
                />
              </div>

              <div>
                <h2
                  class="font-bold text-slate-900"
                >
                  AI explainability
                </h2>

                <p
                  class="text-xs text-slate-500"
                >
                  Global model feature
                  importance
                </p>
              </div>
            </div>
          </div>

          <div
            v-if="
              featureImportance.length
            "
            class="mt-6 h-80"
          >
            <Bar
              :data="
                featureImportanceData
              "
              :options="
                featureImportanceOptions
              "
            />
          </div>

          <div
            v-if="modelInformation"
            class="mt-5 rounded-2xl bg-slate-50 p-4"
          >
            <p
              class="text-xs font-semibold uppercase tracking-wide text-slate-400"
            >
              Model
            </p>

            <p
              class="mt-1 font-bold text-slate-800"
            >
              {{
                modelInformation.name
              }}
            </p>

            <p
              class="mt-1 text-xs text-slate-500"
            >
              {{
                modelInformation.explanation
              }}
            </p>
          </div>
        </section>

        <section
          class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm"
        >
          <div
            class="flex items-center gap-3"
          >
            <div
              class="flex h-11 w-11 items-center justify-center rounded-xl bg-cyan-50 text-cyan-600"
            >
              <Activity :size="21" />
            </div>

            <div>
              <h2
                class="font-bold text-slate-900"
              >
                Prediction trend
              </h2>

              <p
                class="text-xs text-slate-500"
              >
                Recent model outputs
              </p>
            </div>
          </div>

          <div
            v-if="history.length"
            class="mt-6 h-80"
          >
            <Line
              :data="
                historyChartData
              "
              :options="
                historyChartOptions
              "
            />
          </div>

          <div
            v-else
            class="mt-6 flex h-80 items-center justify-center rounded-2xl bg-slate-50 text-sm text-slate-500"
          >
            Generate predictions to
            display the trend.
          </div>
        </section>
      </div>

      <section
        class="mt-7 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm"
      >
        <div
          class="flex items-center gap-3"
        >
          <div
            class="flex h-11 w-11 items-center justify-center rounded-xl bg-slate-100 text-slate-700"
          >
            <History :size="21" />
          </div>

          <div>
            <h2
              class="font-bold text-slate-900"
            >
              Prediction history
            </h2>

            <p
              class="text-xs text-slate-500"
            >
              Most recent AI forecasts
              stored for your account.
            </p>
          </div>
        </div>

        <div
          v-if="history.length === 0"
          class="mt-6 rounded-2xl bg-slate-50 p-8 text-center text-sm text-slate-500"
        >
          No prediction history yet.
        </div>

        <div
          v-else
          class="mt-6 overflow-x-auto"
        >
          <table
            class="w-full min-w-[900px] text-left text-sm"
          >
            <thead
              class="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-400"
            >
              <tr>
                <th class="pb-3 pr-4">
                  Location
                </th>

                <th class="pb-3 pr-4">
                  Time
                </th>

                <th class="pb-3 pr-4">
                  Previous
                </th>

                <th class="pb-3 pr-4">
                  Current
                </th>

                <th class="pb-3 pr-4">
                  Predicted
                </th>

                <th class="pb-3 pr-4">
                  Availability
                </th>

                <th class="pb-3">
                  Generated
                </th>
              </tr>
            </thead>

            <tbody>
              <tr
                v-for="item in history.slice(0, 10)"
                :key="item.id"
                class="border-b border-slate-100 transition hover:bg-slate-50"
              >
                <td
                  class="py-4 pr-4 font-semibold text-slate-800"
                >
                  {{
                    locationName(
                      item.parking_location_id
                    )
                  }}
                </td>

                <td
                  class="py-4 pr-4 text-slate-500"
                >
                  {{
                    String(
                      item.hour
                    ).padStart(
                      2,
                      '0'
                    )
                  }}:00
                </td>

                <td
                  class="py-4 pr-4 text-slate-500"
                >
                  {{
                    Number(
                      item.previous_occupancy
                    ).toFixed(1)
                  }}%
                </td>

                <td
                  class="py-4 pr-4 text-slate-500"
                >
                  {{
                    item.current_occupancy !==
                    null
                      ? `${Number(
                          item.current_occupancy
                        ).toFixed(1)}%`
                      : '—'
                  }}
                </td>

                <td
                  class="py-4 pr-4 font-bold text-slate-900"
                >
                  {{
                    Number(
                      item.predicted_occupancy
                    ).toFixed(1)
                  }}%
                </td>

                <td
                  class="py-4 pr-4 font-bold text-emerald-600"
                >
                  {{
                    Number(
                      item.predicted_availability
                    ).toFixed(1)
                  }}%
                </td>

                <td
                  class="py-4 text-slate-500"
                >
                  {{
                    formatDate(
                      item.created_at
                    )
                  }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </section>
  </AppShell>
</template>
