<script setup>
import {
  computed,
  onMounted,
  ref,
} from 'vue'

import {
  Activity,
  BrainCircuit,
  Building2,
  CalendarDays,
  CircleDollarSign,
  Gauge,
  MapPinned,
  RefreshCw,
  Sparkles,
  Users,
} from '@lucide/vue'

import {
  Bar,
  Doughnut,
  Line,
} from 'vue-chartjs'

import {
  ArcElement,
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Filler,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  Tooltip,
} from 'chart.js'

import AppShell from '../components/AppShell.vue'
import api from '../services/api'

ChartJS.register(
  ArcElement,
  BarElement,
  CategoryScale,
  Filler,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  Tooltip
)

const loading = ref(true)
const errorMessage = ref('')

const overview = ref(null)
const locations = ref([])
const trends = ref([])
const aiDemand = ref(null)
const modelPerformance = ref(null)

const lastUpdated = ref(null)

async function loadAdminDashboard() {
  loading.value = true
  errorMessage.value = ''

  try {
    const [
      overviewResponse,
      locationsResponse,
      trendsResponse,
      aiDemandResponse,
      modelResponse,
    ] = await Promise.all([
      api.get(
        '/api/admin/analytics/overview'
      ),

      api.get(
        '/api/admin/analytics/locations'
      ),

      api.get(
        '/api/admin/analytics/reservation-trends?days=7'
      ),

      api.get(
        '/api/admin/analytics/ai-demand?limit=8'
      ),

      api.get(
        '/api/admin/analytics/model-performance'
      ),
    ])

    overview.value =
      overviewResponse.data

    locations.value =
      locationsResponse.data

    trends.value =
      trendsResponse.data

    aiDemand.value =
      aiDemandResponse.data

    modelPerformance.value =
      modelResponse.data

    lastUpdated.value =
      new Date()
  } catch (error) {
    if (
      error.response?.status === 403
    ) {
      errorMessage.value =
        'Administrator permission is required to view this dashboard.'
    } else {
      errorMessage.value =
        error.response?.data?.detail ||
        'Unable to load the admin analytics dashboard.'
    }
  } finally {
    loading.value = false
  }
}

function formatCurrency(value) {
  return new Intl.NumberFormat(
    'en-GB',
    {
      style: 'currency',
      currency: 'GBP',
    }
  ).format(
    Number(value || 0)
  )
}

function formatNumber(value) {
  return new Intl.NumberFormat(
    'en-GB'
  ).format(
    Number(value || 0)
  )
}

function formatPercent(value) {
  return `${Number(value || 0).toFixed(1)}%`
}

function formatMetric(value) {
  return Number(
    value || 0
  ).toFixed(4)
}

function formatTrendDate(value) {
  if (!value) {
    return ''
  }

  return new Intl.DateTimeFormat(
    'en-GB',
    {
      day: '2-digit',
      month: 'short',
    }
  ).format(
    new Date(
      `${value}T00:00:00`
    )
  )
}

function formatDateTime(value) {
  if (!value) {
    return '—'
  }

  return new Intl.DateTimeFormat(
    'en-GB',
    {
      day: '2-digit',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit',
    }
  ).format(
    new Date(value)
  )
}

function demandBadge(level) {
  const normalised =
    String(level || '')
      .toUpperCase()

  if (normalised === 'LOW') {
    return 'bg-emerald-100 text-emerald-700'
  }

  if (normalised === 'MEDIUM') {
    return 'bg-amber-100 text-amber-700'
  }

  if (normalised === 'HIGH') {
    return 'bg-orange-100 text-orange-700'
  }

  return 'bg-red-100 text-red-700'
}

const reservationTrendChart =
  computed(() => ({
    labels:
      trends.value.map(
        (item) =>
          formatTrendDate(
            item.date
          )
      ),

    datasets: [
      {
        label:
          'Total Reservations',

        data:
          trends.value.map(
            (item) =>
              item.total_reservations
          ),

        borderColor:
          '#059669',

        backgroundColor:
          'rgba(5,150,105,0.12)',

        pointBackgroundColor:
          '#059669',

        tension: 0.35,
        fill: true,
      },

      {
        label: 'Completed',

        data:
          trends.value.map(
            (item) =>
              item.completed
          ),

        borderColor:
          '#0284c7',

        backgroundColor:
          'rgba(2,132,199,0.08)',

        pointBackgroundColor:
          '#0284c7',

        tension: 0.35,
      },

      {
        label: 'Cancelled',

        data:
          trends.value.map(
            (item) =>
              item.cancelled
          ),

        borderColor:
          '#e11d48',

        backgroundColor:
          'rgba(225,29,72,0.08)',

        pointBackgroundColor:
          '#e11d48',

        tension: 0.35,
      },
    ],
  }))

const trendOptions = {
  responsive: true,
  maintainAspectRatio: false,

  plugins: {
    legend: {
      position: 'bottom',
    },
  },

  scales: {
    y: {
      beginAtZero: true,

      ticks: {
        precision: 0,
      },

      grid: {
        color:
          'rgba(148,163,184,0.15)',
      },
    },

    x: {
      grid: {
        display: false,
      },
    },
  },
}

const demandChart =
  computed(() => ({
    labels: [
      'Low',
      'Medium',
      'High',
      'Very High',
    ],

    datasets: [
      {
        data: [
          aiDemand.value
            ?.low_demand_count || 0,

          aiDemand.value
            ?.medium_demand_count || 0,

          aiDemand.value
            ?.high_demand_count || 0,

          aiDemand.value
            ?.very_high_demand_count || 0,
        ],

        backgroundColor: [
          '#10b981',
          '#f59e0b',
          '#f97316',
          '#ef4444',
        ],

        borderWidth: 0,
        hoverOffset: 5,
      },
    ],
  }))

const demandOptions = {
  responsive: true,
  maintainAspectRatio: false,

  plugins: {
    legend: {
      position: 'bottom',
    },
  },
}

const featureImportanceChart =
  computed(() => {
    const features =
      modelPerformance.value
        ?.feature_importance || []

    return {
      labels:
        features.map(
          (item) =>
            item.display_name
        ),

      datasets: [
        {
          label:
            'Importance %',

          data:
            features.map(
              (item) =>
                item.importance_percentage
            ),

          backgroundColor:
            '#0f766e',

          borderRadius: 7,
        },
      ],
    }
  })

const featureImportanceOptions = {
  responsive: true,
  maintainAspectRatio: false,

  indexAxis: 'y',

  plugins: {
    legend: {
      display: false,
    },
  },

  scales: {
    x: {
      beginAtZero: true,

      ticks: {
        callback(value) {
          return `${value}%`
        },
      },

      grid: {
        color:
          'rgba(148,163,184,0.14)',
      },
    },

    y: {
      grid: {
        display: false,
      },
    },
  },
}

const locationRows =
  computed(() =>
    [...locations.value].sort(
      (a, b) =>
        Number(
          b.total_revenue
        ) -
        Number(
          a.total_revenue
        )
    )
  )

const overviewCards =
  computed(() => [
    {
      label:
        'Total Users',

      value:
        formatNumber(
          overview.value
            ?.total_users
        ),

      detail:
        `${
          overview.value
            ?.active_users || 0
        } active users`,

      icon: Users,

      iconClass:
        'bg-violet-100 text-violet-700',
    },

    {
      label:
        'Reservations',

      value:
        formatNumber(
          overview.value
            ?.total_reservations
        ),

      detail:
        `${
          overview.value
            ?.completed_reservations || 0
        } completed`,

      icon: CalendarDays,

      iconClass:
        'bg-blue-100 text-blue-700',
    },

    {
      label:
        'Net Revenue',

      value:
        formatCurrency(
          overview.value
            ?.total_revenue
        ),

      detail:
        `${
          overview.value
            ?.completed_parking_sessions || 0
        } completed sessions`,

      icon: CircleDollarSign,

      iconClass:
        'bg-emerald-100 text-emerald-700',
    },

    {
      label:
        'Live Occupancy',

      value:
        formatPercent(
          overview.value
            ?.overall_occupancy_percentage
        ),

      detail:
        `${
          overview.value
            ?.available_parking_spaces || 0
        } spaces available`,

      icon: Gauge,

      iconClass:
        'bg-amber-100 text-amber-700',
    },

    {
      label:
        'Parking Network',

      value:
        formatNumber(
          overview.value
            ?.total_parking_locations
        ),

      detail:
        `${
          overview.value
            ?.total_parking_spaces || 0
        } total spaces`,

      icon: Building2,

      iconClass:
        'bg-cyan-100 text-cyan-700',
    },

    {
      label:
        'AI Predictions',

      value:
        formatNumber(
          overview.value
            ?.total_predictions
        ),

      detail:
        `${formatPercent(
          overview.value
            ?.average_predicted_occupancy
        )} avg predicted occupancy`,

      icon: BrainCircuit,

      iconClass:
        'bg-fuchsia-100 text-fuchsia-700',
    },
  ])

onMounted(
  loadAdminDashboard
)
</script>

<template>
  <AppShell>
    <section
      class="mx-auto max-w-[1500px]"
    >
      <div
        class="relative overflow-hidden rounded-[2rem] bg-slate-950 p-7 text-white shadow-2xl sm:p-9"
      >
        <div
          class="absolute -right-20 -top-28 h-80 w-80 rounded-full bg-emerald-500/20 blur-3xl"
        />

        <div
          class="absolute bottom-0 left-1/2 h-64 w-64 rounded-full bg-cyan-500/10 blur-3xl"
        />

        <div
          class="relative flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between"
        >
          <div>
            <div
              class="inline-flex items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1.5 text-xs font-bold text-emerald-300"
            >
              <Sparkles :size="15" />
              SmartPark Control Centre
            </div>

            <h1
              class="mt-5 text-3xl font-black tracking-tight sm:text-4xl"
            >
              Admin Analytics Dashboard
            </h1>

            <p
              class="mt-3 max-w-3xl text-sm leading-7 text-slate-300"
            >
              Monitor users, parking activity,
              revenue, live occupancy, AI demand
              forecasts and machine-learning
              evaluation evidence.
            </p>
          </div>

          <div
            class="flex flex-col items-start gap-3 sm:flex-row sm:items-center"
          >
            <div
              v-if="lastUpdated"
              class="text-xs text-slate-400"
            >
              Updated
              {{
                lastUpdated.toLocaleTimeString(
                  'en-GB',
                  {
                    hour: '2-digit',
                    minute: '2-digit',
                  }
                )
              }}
            </div>

            <button
              class="inline-flex items-center gap-2 rounded-xl border border-white/10 bg-white/10 px-4 py-3 text-sm font-bold transition hover:bg-white/15 disabled:opacity-50"
              :disabled="loading"
              @click="
                loadAdminDashboard
              "
            >
              <RefreshCw
                :size="17"
                :class="{
                  'animate-spin':
                    loading,
                }"
              />

              Refresh
            </button>
          </div>
        </div>
      </div>

      <div
        v-if="errorMessage"
        class="mt-6 rounded-2xl border border-red-200 bg-red-50 p-5 text-sm font-medium text-red-700"
      >
        {{ errorMessage }}
      </div>

      <div
        v-if="loading"
        class="mt-7 rounded-3xl border border-slate-200 bg-white p-14 text-center shadow-sm"
      >
        <RefreshCw
          :size="30"
          class="mx-auto animate-spin text-emerald-600"
        />

        <p
          class="mt-4 font-bold text-slate-800"
        >
          Loading admin analytics...
        </p>

        <p
          class="mt-2 text-sm text-slate-500"
        >
          Fetching live SmartPark data.
        </p>
      </div>

      <template
        v-else-if="
          !errorMessage
        "
      >
        <div
          class="mt-7 grid gap-4 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-6"
        >
          <article
            v-for="
              card in overviewCards
            "
            :key="card.label"
            class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm"
          >
            <div
              :class="[
                'flex h-11 w-11 items-center justify-center rounded-2xl',
                card.iconClass,
              ]"
            >
              <component
                :is="card.icon"
                :size="21"
              />
            </div>

            <p
              class="mt-5 text-xs font-bold uppercase tracking-wider text-slate-400"
            >
              {{ card.label }}
            </p>

            <p
              class="mt-2 text-2xl font-black tracking-tight text-slate-950"
            >
              {{ card.value }}
            </p>

            <p
              class="mt-2 text-xs leading-5 text-slate-500"
            >
              {{ card.detail }}
            </p>
          </article>
        </div>

        <div
          class="mt-7 grid gap-6 xl:grid-cols-[1.55fr_0.75fr]"
        >
          <section
            class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm"
          >
            <div
              class="flex items-start justify-between gap-4"
            >
              <div>
                <p
                  class="text-xs font-bold uppercase tracking-wider text-emerald-600"
                >
                  Reservations
                </p>

                <h2
                  class="mt-1 text-xl font-black text-slate-900"
                >
                  7-Day Reservation Trend
                </h2>
              </div>

              <Activity
                :size="22"
                class="text-slate-400"
              />
            </div>

            <div
              class="mt-6 h-[330px]"
            >
              <Line
                :data="
                  reservationTrendChart
                "
                :options="
                  trendOptions
                "
              />
            </div>
          </section>

          <section
            class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm"
          >
            <div>
              <p
                class="text-xs font-bold uppercase tracking-wider text-fuchsia-600"
              >
                AI Demand
              </p>

              <h2
                class="mt-1 text-xl font-black text-slate-900"
              >
                Demand Distribution
              </h2>

              <p
                class="mt-2 text-sm text-slate-500"
              >
                {{
                  aiDemand
                    ?.total_predictions || 0
                }}
                predictions analysed
              </p>
            </div>

            <div
              class="mt-4 h-[280px]"
            >
              <Doughnut
                :data="
                  demandChart
                "
                :options="
                  demandOptions
                "
              />
            </div>

            <div
              class="mt-4 rounded-2xl bg-slate-50 p-4"
            >
              <p
                class="text-xs font-semibold uppercase tracking-wider text-slate-400"
              >
                Average Predicted Occupancy
              </p>

              <p
                class="mt-2 text-2xl font-black text-slate-900"
              >
                {{
                  formatPercent(
                    aiDemand
                      ?.average_predicted_occupancy
                  )
                }}
              </p>
            </div>
          </section>
        </div>

        <section
          class="mt-7 overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm"
        >
          <div
            class="flex flex-col gap-3 border-b border-slate-200 p-6 sm:flex-row sm:items-center sm:justify-between"
          >
            <div>
              <p
                class="text-xs font-bold uppercase tracking-wider text-cyan-600"
              >
                Parking Network
              </p>

              <h2
                class="mt-1 text-xl font-black text-slate-900"
              >
                Location Performance
              </h2>
            </div>

            <MapPinned
              :size="23"
              class="text-slate-400"
            />
          </div>

          <div
            class="overflow-x-auto"
          >
            <table
              class="min-w-[1050px] w-full text-left"
            >
              <thead
                class="bg-slate-50 text-xs uppercase tracking-wider text-slate-500"
              >
                <tr>
                  <th
                    class="px-6 py-4 font-bold"
                  >
                    Location
                  </th>

                  <th
                    class="px-4 py-4 font-bold"
                  >
                    Spaces
                  </th>

                  <th
                    class="px-4 py-4 font-bold"
                  >
                    Occupancy
                  </th>

                  <th
                    class="px-4 py-4 font-bold"
                  >
                    Reservations
                  </th>

                  <th
                    class="px-4 py-4 font-bold"
                  >
                    Completed
                  </th>

                  <th
                    class="px-4 py-4 font-bold"
                  >
                    Revenue
                  </th>

                  <th
                    class="px-4 py-4 font-bold"
                  >
                    Predicted
                  </th>

                  <th
                    class="px-4 py-4 font-bold"
                  >
                    Rating
                  </th>
                </tr>
              </thead>

              <tbody
                class="divide-y divide-slate-100 text-sm"
              >
                <tr
                  v-for="
                    location in locationRows
                  "
                  :key="
                    location.parking_location_id
                  "
                  class="hover:bg-slate-50/70"
                >
                  <td
                    class="px-6 py-5"
                  >
                    <p
                      class="font-bold text-slate-900"
                    >
                      {{
                        location.parking_name
                      }}
                    </p>

                    <p
                      class="mt-1 text-xs text-slate-400"
                    >
                      {{
                        location.parking_location_id.slice(
                          0,
                          8
                        )
                      }}
                    </p>
                  </td>

                  <td
                    class="px-4 py-5"
                  >
                    <span
                      class="font-bold text-slate-800"
                    >
                      {{
                        location.available_spaces
                      }}
                    </span>

                    <span
                      class="text-slate-400"
                    >
                      /
                      {{
                        location.total_spaces
                      }}
                    </span>
                  </td>

                  <td
                    class="px-4 py-5 font-semibold text-slate-700"
                  >
                    {{
                      formatPercent(
                        location.current_occupancy_percentage
                      )
                    }}
                  </td>

                  <td
                    class="px-4 py-5 text-slate-700"
                  >
                    {{
                      location.total_reservations
                    }}
                  </td>

                  <td
                    class="px-4 py-5 text-slate-700"
                  >
                    {{
                      location.completed_reservations
                    }}
                  </td>

                  <td
                    class="px-4 py-5 font-bold text-emerald-700"
                  >
                    {{
                      formatCurrency(
                        location.total_revenue
                      )
                    }}
                  </td>

                  <td
                    class="px-4 py-5 text-slate-700"
                  >
                    {{
                      formatPercent(
                        location.average_predicted_occupancy
                      )
                    }}
                  </td>

                  <td
                    class="px-4 py-5"
                  >
                    <span
                      class="font-bold text-amber-600"
                    >
                      {{
                        Number(
                          location.average_rating || 0
                        ).toFixed(1)
                      }}
                    </span>

                    <span
                      class="ml-1 text-xs text-slate-400"
                    >
                      ({{
                        location.review_count
                      }})
                    </span>
                  </td>
                </tr>

                <tr
                  v-if="
                    locationRows.length === 0
                  "
                >
                  <td
                    colspan="8"
                    class="px-6 py-10 text-center text-slate-500"
                  >
                    No parking location analytics available.
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <div
          class="mt-7 grid gap-6 xl:grid-cols-[1.1fr_0.9fr]"
        >
          <section
            class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm"
          >
            <div
              class="flex items-start justify-between gap-4"
            >
              <div>
                <p
                  class="text-xs font-bold uppercase tracking-wider text-emerald-600"
                >
                  Machine Learning
                </p>

                <h2
                  class="mt-1 text-xl font-black text-slate-900"
                >
                  Model Performance
                </h2>
              </div>

              <BrainCircuit
                :size="24"
                class="text-emerald-600"
              />
            </div>

            <div
              class="mt-6 rounded-2xl bg-slate-950 p-5 text-white"
            >
              <div
                class="flex flex-wrap items-center justify-between gap-4"
              >
                <div>
                  <p
                    class="text-xs font-bold uppercase tracking-wider text-emerald-400"
                  >
                    Selected Model
                  </p>

                  <p
                    class="mt-2 text-xl font-black"
                  >
                    {{
                      modelPerformance
                        ?.selected_model
                    }}
                  </p>
                </div>

                <span
                  class="rounded-full bg-emerald-400/10 px-3 py-1.5 text-xs font-bold text-emerald-300"
                >
                  v{{
                    modelPerformance
                      ?.model_version
                  }}
                </span>
              </div>
            </div>

            <div
              class="mt-5 grid gap-3 sm:grid-cols-3"
            >
              <div
                class="rounded-2xl bg-slate-50 p-4"
              >
                <p
                  class="text-xs font-bold uppercase tracking-wide text-slate-400"
                >
                  Evaluation MAE
                </p>

                <p
                  class="mt-2 text-xl font-black text-slate-900"
                >
                  {{
                    formatMetric(
                      modelPerformance
                        ?.evaluation_mae
                    )
                  }}
                </p>
              </div>

              <div
                class="rounded-2xl bg-slate-50 p-4"
              >
                <p
                  class="text-xs font-bold uppercase tracking-wide text-slate-400"
                >
                  Evaluation RMSE
                </p>

                <p
                  class="mt-2 text-xl font-black text-slate-900"
                >
                  {{
                    formatMetric(
                      modelPerformance
                        ?.evaluation_rmse
                    )
                  }}
                </p>
              </div>

              <div
                class="rounded-2xl bg-slate-50 p-4"
              >
                <p
                  class="text-xs font-bold uppercase tracking-wide text-slate-400"
                >
                  Evaluation R²
                </p>

                <p
                  class="mt-2 text-xl font-black text-emerald-700"
                >
                  {{
                    formatMetric(
                      modelPerformance
                        ?.evaluation_r2
                    )
                  }}
                </p>
              </div>
            </div>

            <div
              class="mt-5 grid gap-3 sm:grid-cols-3"
            >
              <div
                class="rounded-2xl border border-slate-200 p-4"
              >
                <p
                  class="text-xs text-slate-500"
                >
                  Development rows
                </p>

                <p
                  class="mt-2 font-black text-slate-900"
                >
                  {{
                    formatNumber(
                      modelPerformance
                        ?.development_rows
                    )
                  }}
                </p>
              </div>

              <div
                class="rounded-2xl border border-slate-200 p-4"
              >
                <p
                  class="text-xs text-slate-500"
                >
                  Evaluation rows
                </p>

                <p
                  class="mt-2 font-black text-slate-900"
                >
                  {{
                    formatNumber(
                      modelPerformance
                        ?.evaluation_rows
                    )
                  }}
                </p>
              </div>

              <div
                class="rounded-2xl border border-slate-200 p-4"
              >
                <p
                  class="text-xs text-slate-500"
                >
                  Best CV RMSE
                </p>

                <p
                  class="mt-2 font-black text-slate-900"
                >
                  {{
                    formatMetric(
                      modelPerformance
                        ?.best_cross_validation_rmse
                    )
                  }}
                </p>
              </div>
            </div>

            <div
              class="mt-5 rounded-2xl border border-amber-200 bg-amber-50 p-4"
            >
              <p
                class="text-xs font-bold uppercase tracking-wider text-amber-700"
              >
                Evaluation Scope
              </p>

              <p
                class="mt-2 text-sm leading-6 text-amber-900"
              >
                {{
                  modelPerformance
                    ?.evaluation_scope
                }}
              </p>
            </div>
          </section>

          <section
            class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm"
          >
            <div>
              <p
                class="text-xs font-bold uppercase tracking-wider text-teal-600"
              >
                Explainability
              </p>

              <h2
                class="mt-1 text-xl font-black text-slate-900"
              >
                Global Feature Importance
              </h2>
            </div>

            <div
              class="mt-6 h-[430px]"
            >
              <Bar
                :data="
                  featureImportanceChart
                "
                :options="
                  featureImportanceOptions
                "
              />
            </div>
          </section>
        </div>

        <div
          class="mt-7 grid gap-6 xl:grid-cols-2"
        >
          <section
            class="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm"
          >
            <div
              class="border-b border-slate-200 p-6"
            >
              <p
                class="text-xs font-bold uppercase tracking-wider text-violet-600"
              >
                Comparative Evaluation
              </p>

              <h2
                class="mt-1 text-xl font-black text-slate-900"
              >
                Baseline Model Comparison
              </h2>
            </div>

            <div
              class="overflow-x-auto"
            >
              <table
                class="w-full min-w-[620px] text-left text-sm"
              >
                <thead
                  class="bg-slate-50 text-xs uppercase tracking-wider text-slate-500"
                >
                  <tr>
                    <th
                      class="px-6 py-4"
                    >
                      Rank
                    </th>

                    <th
                      class="px-4 py-4"
                    >
                      Model
                    </th>

                    <th
                      class="px-4 py-4"
                    >
                      MAE
                    </th>

                    <th
                      class="px-4 py-4"
                    >
                      RMSE
                    </th>

                    <th
                      class="px-4 py-4"
                    >
                      R²
                    </th>
                  </tr>
                </thead>

                <tbody
                  class="divide-y divide-slate-100"
                >
                  <tr
                    v-for="
                      item in modelPerformance
                        ?.model_comparison || []
                    "
                    :key="
                      item.model
                    "
                  >
                    <td
                      class="px-6 py-4 font-black text-slate-800"
                    >
                      #{{ item.rank }}
                    </td>

                    <td
                      class="px-4 py-4 font-bold text-slate-800"
                    >
                      {{ item.model }}
                    </td>

                    <td
                      class="px-4 py-4 text-slate-600"
                    >
                      {{
                        formatMetric(
                          item.mae
                        )
                      }}
                    </td>

                    <td
                      class="px-4 py-4 text-slate-600"
                    >
                      {{
                        formatMetric(
                          item.rmse
                        )
                      }}
                    </td>

                    <td
                      class="px-4 py-4 font-bold text-emerald-700"
                    >
                      {{
                        formatMetric(
                          item.r2
                        )
                      }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>

          <section
            class="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm"
          >
            <div
              class="border-b border-slate-200 p-6"
            >
              <p
                class="text-xs font-bold uppercase tracking-wider text-fuchsia-600"
              >
                Live Prediction Activity
              </p>

              <h2
                class="mt-1 text-xl font-black text-slate-900"
              >
                Recent AI Predictions
              </h2>
            </div>

            <div
              class="divide-y divide-slate-100"
            >
              <article
                v-for="
                  prediction in aiDemand
                    ?.recent_predictions || []
                "
                :key="
                  prediction.prediction_id
                "
                class="flex items-center justify-between gap-5 px-6 py-4"
              >
                <div
                  class="min-w-0"
                >
                  <p
                    class="truncate font-bold text-slate-900"
                  >
                    {{
                      prediction.parking_name
                    }}
                  </p>

                  <p
                    class="mt-1 text-xs text-slate-400"
                  >
                    {{
                      formatDateTime(
                        prediction.created_at
                      )
                    }}
                  </p>
                </div>

                <div
                  class="shrink-0 text-right"
                >
                  <p
                    class="font-black text-slate-900"
                  >
                    {{
                      formatPercent(
                        prediction.predicted_occupancy
                      )
                    }}
                  </p>

                  <span
                    :class="[
                      'mt-1 inline-flex rounded-full px-2.5 py-1 text-[10px] font-black',
                      demandBadge(
                        prediction.demand_level
                      ),
                    ]"
                  >
                    {{
                      prediction.demand_level
                    }}
                  </span>
                </div>
              </article>

              <div
                v-if="
                  !aiDemand
                    ?.recent_predictions
                    ?.length
                "
                class="p-10 text-center text-sm text-slate-500"
              >
                No AI predictions available.
              </div>
            </div>
          </section>
        </div>
      </template>
    </section>
  </AppShell>
</template>
