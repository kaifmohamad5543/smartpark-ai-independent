<script setup>
import {
  computed,
  onMounted,
  ref,
} from 'vue'

import {
  Accessibility,
  Building2,
  CarFront,
  CheckCircle2,
  Clock3,
  MapPin,
  Pencil,
  Plus,
  Power,
  RefreshCw,
  Save,
  Settings2,
  ShieldCheck,
  Sparkles,
  X,
  Zap,
} from '@lucide/vue'

import AppShell from '../components/AppShell.vue'
import api from '../services/api'

const locations = ref([])
const spaces = ref([])

const loading = ref(true)
const spacesLoading = ref(false)
const saving = ref(false)

const errorMessage = ref('')
const successMessage = ref('')

const locationFormOpen = ref(false)
const editingLocationId = ref(null)

const spacesOpen = ref(false)
const selectedLocation = ref(null)

const spaceFormOpen = ref(false)
const editingSpaceId = ref(null)

const locationForm = ref({
  name: '',
  address: '',
  city: '',
  postcode: '',
  latitude: 51.5074,
  longitude: -0.1278,
  initial_spaces: 10,
  hourly_rate: 4,
  opening_time: '08:00',
  closing_time: '22:00',
  is_24_hours: false,
  dynamic_pricing_enabled: false,
  is_active: true,
})

const spaceForm = ref({
  space_number: '',
  space_type: 'standard',
  has_ev_charging: false,
  is_accessible: false,
  is_available: true,
  is_active: true,
})

const activeLocations = computed(
  () =>
    locations.value.filter(
      (location) =>
        location.is_active
    ).length
)

const totalSpaces = computed(
  () =>
    locations.value.reduce(
      (total, location) =>
        total +
        Number(
          location.total_spaces || 0
        ),
      0
    )
)

const activeSpaces = computed(
  () =>
    spaces.value.filter(
      (space) =>
        space.is_active
    ).length
)

const availableSpaces = computed(
  () =>
    spaces.value.filter(
      (space) =>
        space.is_active &&
        space.is_available
    ).length
)

function clearMessages() {
  errorMessage.value = ''
  successMessage.value = ''
}

function apiError(
  error,
  fallback
) {
  const detail =
    error.response?.data?.detail

  if (Array.isArray(detail)) {
    return detail
      .map(
        (item) =>
          item.msg ||
          'Validation error'
      )
      .join(' ')
  }

  return detail || fallback
}

function formatMoney(value) {
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

function formatTime(value) {
  if (!value) {
    return '—'
  }

  return String(value).slice(
    0,
    5
  )
}

function resetLocationForm() {
  locationForm.value = {
    name: '',
    address: '',
    city: '',
    postcode: '',
    latitude: 51.5074,
    longitude: -0.1278,
    initial_spaces: 10,
    hourly_rate: 4,
    opening_time: '08:00',
    closing_time: '22:00',
    is_24_hours: false,
    dynamic_pricing_enabled: false,
    is_active: true,
  }

  editingLocationId.value = null
}

function openCreateLocation() {
  clearMessages()
  resetLocationForm()

  locationFormOpen.value = true
}

function openEditLocation(
  location
) {
  clearMessages()

  editingLocationId.value =
    location.id

  locationForm.value = {
    name:
      location.name,

    address:
      location.address,

    city:
      location.city,

    postcode:
      location.postcode,

    latitude:
      Number(
        location.latitude
      ),

    longitude:
      Number(
        location.longitude
      ),

    initial_spaces:
      location.total_spaces,

    hourly_rate:
      Number(
        location.hourly_rate
      ),

    opening_time:
      location.opening_time
        ? String(
            location.opening_time
          ).slice(0, 5)
        : '08:00',

    closing_time:
      location.closing_time
        ? String(
            location.closing_time
          ).slice(0, 5)
        : '22:00',

    is_24_hours:
      location.is_24_hours,

    dynamic_pricing_enabled:
      Boolean(
        location.dynamic_pricing_enabled
      ),

    is_active:
      location.is_active,
  }

  locationFormOpen.value = true
}

function closeLocationForm() {
  locationFormOpen.value = false
  resetLocationForm()
}

async function loadLocations() {
  loading.value = true
  errorMessage.value = ''

  try {
    const response =
      await api.get(
        '/api/admin/parking/locations'
      )

    locations.value =
      response.data
  } catch (error) {
    errorMessage.value =
      apiError(
        error,
        'Unable to load parking locations.'
      )
  } finally {
    loading.value = false
  }
}

async function saveLocation() {
  clearMessages()
  saving.value = true

  try {
    if (
      !locationForm.value
        .is_24_hours &&
      (
        !locationForm.value
          .opening_time ||
        !locationForm.value
          .closing_time
      )
    ) {
      throw new Error(
        'Opening and closing times are required.'
      )
    }

    if (
      !locationForm.value
        .is_24_hours &&
      locationForm.value
        .opening_time ===
        locationForm.value
          .closing_time
    ) {
      throw new Error(
        'Opening and closing times cannot be identical.'
      )
    }

    const commonPayload = {
      name:
        locationForm.value
          .name
          .trim(),

      address:
        locationForm.value
          .address
          .trim(),

      city:
        locationForm.value
          .city
          .trim(),

      postcode:
        locationForm.value
          .postcode
          .trim()
          .toUpperCase(),

      latitude:
        Number(
          locationForm.value
            .latitude
        ),

      longitude:
        Number(
          locationForm.value
            .longitude
        ),

      hourly_rate:
        Number(
          locationForm.value
            .hourly_rate
        ),

      opening_time:
        locationForm.value
          .is_24_hours
          ? null
          : locationForm.value
              .opening_time,

      closing_time:
        locationForm.value
          .is_24_hours
          ? null
          : locationForm.value
              .closing_time,

      is_24_hours:
        Boolean(
          locationForm.value
            .is_24_hours
        ),

      dynamic_pricing_enabled:
        Boolean(
          locationForm.value
            .dynamic_pricing_enabled
        ),
    }

    if (
      editingLocationId.value
    ) {
      await api.patch(
        `/api/admin/parking/locations/${editingLocationId.value}`,
        commonPayload
      )

      successMessage.value =
        'Parking location updated successfully.'
    } else {
      await api.post(
        '/api/admin/parking/locations',
        {
          ...commonPayload,

          initial_spaces:
            Number(
              locationForm.value
                .initial_spaces
            ),

          is_active:
            Boolean(
              locationForm.value
                .is_active
            ),
        }
      )

      successMessage.value =
        'Parking location created successfully.'
    }

    closeLocationForm()
    await loadLocations()
  } catch (error) {
    errorMessage.value =
      error.response
        ? apiError(
            error,
            'Unable to save parking location.'
          )
        : error.message
  } finally {
    saving.value = false
  }
}

async function toggleLocationStatus(
  location
) {
  clearMessages()

  const newStatus =
    !location.is_active

  try {
    await api.patch(
      `/api/admin/parking/locations/${location.id}/status`,
      {
        is_active:
          newStatus,
      }
    )

    successMessage.value =
      `${location.name} ${
        newStatus
          ? 'activated'
          : 'deactivated'
      } successfully.`

    await loadLocations()

    if (
      selectedLocation.value
        ?.id === location.id
    ) {
      selectedLocation.value =
        locations.value.find(
          (item) =>
            item.id ===
            location.id
        ) || null
    }
  } catch (error) {
    errorMessage.value =
      apiError(
        error,
        'Unable to change parking location status.'
      )
  }
}

function resetSpaceForm() {
  spaceForm.value = {
    space_number: '',
    space_type: 'standard',
    has_ev_charging: false,
    is_accessible: false,
    is_available: true,
    is_active: true,
  }

  editingSpaceId.value = null
}

async function openSpaces(
  location
) {
  clearMessages()

  selectedLocation.value =
    location

  spacesOpen.value = true

  await loadSpaces()
}

function closeSpaces() {
  spacesOpen.value = false
  selectedLocation.value = null
  spaces.value = []

  resetSpaceForm()
  spaceFormOpen.value = false
}

async function loadSpaces() {
  if (!selectedLocation.value) {
    return
  }

  spacesLoading.value = true

  try {
    const response =
      await api.get(
        `/api/admin/parking/locations/${selectedLocation.value.id}/spaces`
      )

    spaces.value =
      response.data
  } catch (error) {
    errorMessage.value =
      apiError(
        error,
        'Unable to load parking spaces.'
      )
  } finally {
    spacesLoading.value = false
  }
}

function openCreateSpace() {
  clearMessages()
  resetSpaceForm()

  spaceFormOpen.value = true
}

function openEditSpace(
  space
) {
  clearMessages()

  editingSpaceId.value =
    space.id

  spaceForm.value = {
    space_number:
      space.space_number,

    space_type:
      space.space_type,

    has_ev_charging:
      space.has_ev_charging,

    is_accessible:
      space.is_accessible,

    is_available:
      space.is_available,

    is_active:
      space.is_active,
  }

  spaceFormOpen.value = true
}

function closeSpaceForm() {
  spaceFormOpen.value = false
  resetSpaceForm()
}

async function saveSpace() {
  if (!selectedLocation.value) {
    return
  }

  clearMessages()
  saving.value = true

  const payload = {
    space_number:
      spaceForm.value
        .space_number
        .trim()
        .toUpperCase(),

    space_type:
      spaceForm.value
        .space_type,

    has_ev_charging:
      Boolean(
        spaceForm.value
          .has_ev_charging
      ),

    is_accessible:
      Boolean(
        spaceForm.value
          .is_accessible
      ),

    is_available:
      Boolean(
        spaceForm.value
          .is_available
      ),

    is_active:
      Boolean(
        spaceForm.value
          .is_active
      ),
  }

  try {
    if (
      editingSpaceId.value
    ) {
      await api.patch(
        `/api/admin/parking/spaces/${editingSpaceId.value}`,
        payload
      )

      successMessage.value =
        'Parking space updated successfully.'
    } else {
      await api.post(
        `/api/admin/parking/locations/${selectedLocation.value.id}/spaces`,
        payload
      )

      successMessage.value =
        'Parking space created successfully.'
    }

    closeSpaceForm()
    await loadSpaces()
    await loadLocations()
  } catch (error) {
    errorMessage.value =
      apiError(
        error,
        'Unable to save parking space.'
      )
  } finally {
    saving.value = false
  }
}

async function toggleSpaceAvailability(
  space
) {
  clearMessages()

  try {
    await api.patch(
      `/api/admin/parking/spaces/${space.id}`,
      {
        is_available:
          !space.is_available,
      }
    )

    successMessage.value =
      `Space ${space.space_number} availability updated.`

    await loadSpaces()
  } catch (error) {
    errorMessage.value =
      apiError(
        error,
        'Unable to update space availability.'
      )
  }
}

async function toggleSpaceStatus(
  space
) {
  clearMessages()

  try {
    await api.patch(
      `/api/admin/parking/spaces/${space.id}`,
      {
        is_active:
          !space.is_active,
      }
    )

    successMessage.value =
      `Space ${space.space_number} status updated.`

    await loadSpaces()
    await loadLocations()
  } catch (error) {
    errorMessage.value =
      apiError(
        error,
        'Unable to update parking space status.'
      )
  }
}

onMounted(
  loadLocations
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
          class="absolute -right-24 -top-24 h-80 w-80 rounded-full bg-emerald-500/20 blur-3xl"
        />

        <div
          class="relative flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between"
        >
          <div>
            <div
              class="inline-flex items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1.5 text-xs font-bold text-emerald-300"
            >
              <ShieldCheck
                :size="15"
              />
              Administrator controls
            </div>

            <h1
              class="mt-5 text-3xl font-black tracking-tight sm:text-4xl"
            >
              Parking Management
            </h1>

            <p
              class="mt-3 max-w-3xl text-sm leading-7 text-slate-300"
            >
              Create parking locations,
              manage parking spaces,
              control availability and
              maintain the live SmartPark
              parking network.
            </p>
          </div>

          <div
            class="flex flex-wrap gap-3"
          >
            <button
              class="inline-flex items-center gap-2 rounded-xl border border-white/10 bg-white/10 px-4 py-3 text-sm font-bold transition hover:bg-white/15"
              @click="
                loadLocations
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

            <button
              class="inline-flex items-center gap-2 rounded-xl bg-emerald-500 px-4 py-3 text-sm font-black text-slate-950 transition hover:bg-emerald-400"
              @click="
                openCreateLocation
              "
            >
              <Plus :size="18" />
              New location
            </button>
          </div>
        </div>
      </div>

      <div
        v-if="successMessage"
        class="mt-6 flex items-center gap-3 rounded-2xl border border-emerald-200 bg-emerald-50 p-4 text-sm font-medium text-emerald-700"
      >
        <CheckCircle2
          :size="18"
        />
        {{ successMessage }}
      </div>

      <div
        v-if="errorMessage"
        class="mt-6 rounded-2xl border border-red-200 bg-red-50 p-4 text-sm font-medium text-red-700"
      >
        {{ errorMessage }}
      </div>

      <div
        class="mt-7 grid gap-4 sm:grid-cols-3"
      >
        <div
          class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm"
        >
          <div
            class="flex h-11 w-11 items-center justify-center rounded-2xl bg-cyan-100 text-cyan-700"
          >
            <Building2
              :size="21"
            />
          </div>

          <p
            class="mt-4 text-xs font-bold uppercase tracking-wider text-slate-400"
          >
            Parking Locations
          </p>

          <p
            class="mt-2 text-3xl font-black text-slate-950"
          >
            {{ locations.length }}
          </p>
        </div>

        <div
          class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm"
        >
          <div
            class="flex h-11 w-11 items-center justify-center rounded-2xl bg-emerald-100 text-emerald-700"
          >
            <Power :size="21" />
          </div>

          <p
            class="mt-4 text-xs font-bold uppercase tracking-wider text-slate-400"
          >
            Active Locations
          </p>

          <p
            class="mt-2 text-3xl font-black text-slate-950"
          >
            {{ activeLocations }}
          </p>
        </div>

        <div
          class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm"
        >
          <div
            class="flex h-11 w-11 items-center justify-center rounded-2xl bg-violet-100 text-violet-700"
          >
            <CarFront
              :size="21"
            />
          </div>

          <p
            class="mt-4 text-xs font-bold uppercase tracking-wider text-slate-400"
          >
            Total Spaces
          </p>

          <p
            class="mt-2 text-3xl font-black text-slate-950"
          >
            {{ totalSpaces }}
          </p>
        </div>
      </div>

      <div
        v-if="loading"
        class="mt-7 rounded-3xl border border-slate-200 bg-white p-14 text-center shadow-sm"
      >
        <RefreshCw
          :size="28"
          class="mx-auto animate-spin text-emerald-600"
        />

        <p
          class="mt-4 font-bold text-slate-800"
        >
          Loading parking network...
        </p>
      </div>

      <div
        v-else
        class="mt-7 grid gap-5 xl:grid-cols-2"
      >
        <article
          v-for="location in locations"
          :key="location.id"
          class="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm"
        >
          <div
            class="p-6"
          >
            <div
              class="flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between"
            >
              <div
                class="flex gap-4"
              >
                <div
                  class="flex h-13 w-13 shrink-0 items-center justify-center rounded-2xl bg-slate-950 p-3 text-emerald-400"
                >
                  <Building2
                    :size="25"
                  />
                </div>

                <div>
                  <div
                    class="flex flex-wrap items-center gap-2"
                  >
                    <h2
                      class="text-lg font-black text-slate-900"
                    >
                      {{ location.name }}
                    </h2>

                    <span
                      :class="[
                        'rounded-full px-2.5 py-1 text-[10px] font-black uppercase',
                        location.is_active
                          ? 'bg-emerald-100 text-emerald-700'
                          : 'bg-slate-200 text-slate-600',
                      ]"
                    >
                      {{
                        location.is_active
                          ? 'Active'
                          : 'Inactive'
                      }}
                    </span>
                  </div>

                  <div
                    class="mt-2 flex items-start gap-2 text-sm text-slate-500"
                  >
                    <MapPin
                      :size="15"
                      class="mt-0.5 shrink-0"
                    />

                    <span>
                      {{ location.address }},
                      {{ location.city }}
                      {{ location.postcode }}
                    </span>
                  </div>
                </div>
              </div>

              <div
                class="flex gap-2"
              >
                <button
                  class="rounded-xl border border-slate-200 p-2.5 text-slate-600 transition hover:bg-slate-50"
                  title="Edit location"
                  @click="
                    openEditLocation(
                      location
                    )
                  "
                >
                  <Pencil
                    :size="17"
                  />
                </button>

                <button
                  :class="[
                    'rounded-xl border p-2.5 transition',
                    location.is_active
                      ? 'border-red-200 text-red-600 hover:bg-red-50'
                      : 'border-emerald-200 text-emerald-700 hover:bg-emerald-50',
                  ]"
                  :title="
                    location.is_active
                      ? 'Deactivate'
                      : 'Activate'
                  "
                  @click="
                    toggleLocationStatus(
                      location
                    )
                  "
                >
                  <Power
                    :size="17"
                  />
                </button>
              </div>
            </div>

            <div
              class="mt-5 flex flex-wrap items-center gap-2"
            >
              <span
                v-if="
                  location.dynamic_pricing_enabled
                "
                class="inline-flex items-center gap-1.5 rounded-full bg-emerald-100 px-3 py-1.5 text-xs font-bold text-emerald-700"
              >
                <Sparkles :size="14" />
                AI Dynamic Pricing
              </span>

              <span
                v-else
                class="inline-flex items-center rounded-full bg-slate-100 px-3 py-1.5 text-xs font-bold text-slate-500"
              >
                Fixed Pricing
              </span>
            </div>

            <div
              class="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-4"
            >
              <div
                class="rounded-2xl bg-slate-50 p-4"
              >
                <p
                  class="text-[11px] font-bold uppercase tracking-wide text-slate-400"
                >
                  Spaces
                </p>

                <p
                  class="mt-2 text-lg font-black text-slate-900"
                >
                  {{ location.total_spaces }}
                </p>
              </div>

              <div
                class="rounded-2xl bg-slate-50 p-4"
              >
                <p
                  class="text-[11px] font-bold uppercase tracking-wide text-slate-400"
                >
                  Rate
                </p>

                <p
                  class="mt-2 text-lg font-black text-slate-900"
                >
                  {{
                    formatMoney(
                      location.hourly_rate
                    )
                  }}
                </p>
              </div>

              <div
                class="rounded-2xl bg-slate-50 p-4"
              >
                <p
                  class="text-[11px] font-bold uppercase tracking-wide text-slate-400"
                >
                  Opens
                </p>

                <p
                  class="mt-2 text-sm font-black text-slate-900"
                >
                  {{
                    location.is_24_hours
                      ? '24 hours'
                      : formatTime(
                          location.opening_time
                        )
                  }}
                </p>
              </div>

              <div
                class="rounded-2xl bg-slate-50 p-4"
              >
                <p
                  class="text-[11px] font-bold uppercase tracking-wide text-slate-400"
                >
                  Closes
                </p>

                <p
                  class="mt-2 text-sm font-black text-slate-900"
                >
                  {{
                    location.is_24_hours
                      ? '24 hours'
                      : formatTime(
                          location.closing_time
                        )
                  }}
                </p>
              </div>
            </div>

            <div
              class="mt-5 flex items-center justify-between rounded-2xl border border-slate-200 p-4"
            >
              <div>
                <p
                  class="text-xs font-bold uppercase tracking-wide text-slate-400"
                >
                  Coordinates
                </p>

                <p
                  class="mt-1 text-sm font-semibold text-slate-700"
                >
                  {{ location.latitude }},
                  {{ location.longitude }}
                </p>
              </div>

              <button
                class="inline-flex items-center gap-2 rounded-xl bg-slate-950 px-4 py-3 text-sm font-bold text-white transition hover:bg-slate-800"
                @click="
                  openSpaces(
                    location
                  )
                "
              >
                <Settings2
                  :size="17"
                />
                Manage spaces
              </button>
            </div>
          </div>
        </article>

        <div
          v-if="
            locations.length === 0
          "
          class="col-span-full rounded-3xl border border-dashed border-slate-300 bg-white p-14 text-center"
        >
          <Building2
            :size="38"
            class="mx-auto text-slate-300"
          />

          <p
            class="mt-4 font-bold text-slate-800"
          >
            No parking locations
          </p>

          <button
            class="mt-5 rounded-xl bg-emerald-600 px-5 py-3 font-bold text-white"
            @click="
              openCreateLocation
            "
          >
            Create first location
          </button>
        </div>
      </div>
    </section>

    <!-- Location modal -->
    <Teleport to="body">
      <div
        v-if="locationFormOpen"
        class="fixed inset-0 z-[9999] flex items-center justify-center overflow-y-auto bg-slate-950/65 p-4 backdrop-blur-sm"
        @click.self="
          closeLocationForm
        "
      >
        <div
          class="my-auto w-full max-w-3xl overflow-hidden rounded-3xl bg-white shadow-2xl"
        >
          <div
            class="flex items-center justify-between border-b border-slate-200 p-6"
          >
            <div>
              <p
                class="text-xs font-bold uppercase tracking-wider text-emerald-600"
              >
                Parking network
              </p>

              <h2
                class="mt-1 text-2xl font-black text-slate-900"
              >
                {{
                  editingLocationId
                    ? 'Edit parking location'
                    : 'Create parking location'
                }}
              </h2>
            </div>

            <button
              class="rounded-xl p-2 text-slate-400 hover:bg-slate-100"
              @click="
                closeLocationForm
              "
            >
              <X :size="22" />
            </button>
          </div>

          <form
            class="max-h-[78vh] space-y-5 overflow-y-auto p-6"
            @submit.prevent="
              saveLocation
            "
          >
            <div>
              <label
                class="mb-2 block text-sm font-bold text-slate-700"
              >
                Location name
              </label>

              <input
                v-model="
                  locationForm.name
                "
                required
                minlength="2"
                maxlength="150"
                placeholder="SmartPark Victoria Central"
                class="w-full rounded-xl border border-slate-200 px-4 py-3 outline-none focus:border-emerald-500"
              >
            </div>

            <div>
              <label
                class="mb-2 block text-sm font-bold text-slate-700"
              >
                Address
              </label>

              <input
                v-model="
                  locationForm.address
                "
                required
                minlength="5"
                maxlength="255"
                placeholder="123 Victoria Street"
                class="w-full rounded-xl border border-slate-200 px-4 py-3 outline-none focus:border-emerald-500"
              >
            </div>

            <div
              class="grid gap-4 sm:grid-cols-2"
            >
              <div>
                <label
                  class="mb-2 block text-sm font-bold text-slate-700"
                >
                  City
                </label>

                <input
                  v-model="
                    locationForm.city
                  "
                  required
                  placeholder="London"
                  class="w-full rounded-xl border border-slate-200 px-4 py-3 outline-none focus:border-emerald-500"
                >
              </div>

              <div>
                <label
                  class="mb-2 block text-sm font-bold text-slate-700"
                >
                  Postcode
                </label>

                <input
                  v-model="
                    locationForm.postcode
                  "
                  required
                  placeholder="SW1E 5ND"
                  class="w-full rounded-xl border border-slate-200 px-4 py-3 uppercase outline-none focus:border-emerald-500"
                >
              </div>

              <div>
                <label
                  class="mb-2 block text-sm font-bold text-slate-700"
                >
                  Latitude
                </label>

                <input
                  v-model.number="
                    locationForm.latitude
                  "
                  type="number"
                  required
                  min="-90"
                  max="90"
                  step="0.000001"
                  class="w-full rounded-xl border border-slate-200 px-4 py-3 outline-none focus:border-emerald-500"
                >
              </div>

              <div>
                <label
                  class="mb-2 block text-sm font-bold text-slate-700"
                >
                  Longitude
                </label>

                <input
                  v-model.number="
                    locationForm.longitude
                  "
                  type="number"
                  required
                  min="-180"
                  max="180"
                  step="0.000001"
                  class="w-full rounded-xl border border-slate-200 px-4 py-3 outline-none focus:border-emerald-500"
                >
              </div>

              <div>
                <label
                  class="mb-2 block text-sm font-bold text-slate-700"
                >
                  Hourly rate (£)
                </label>

                <input
                  v-model.number="
                    locationForm.hourly_rate
                  "
                  type="number"
                  required
                  min="0"
                  max="1000"
                  step="0.01"
                  class="w-full rounded-xl border border-slate-200 px-4 py-3 outline-none focus:border-emerald-500"
                >
              </div>

              <div
                v-if="
                  !editingLocationId
                "
              >
                <label
                  class="mb-2 block text-sm font-bold text-slate-700"
                >
                  Initial spaces
                </label>

                <input
                  v-model.number="
                    locationForm.initial_spaces
                  "
                  type="number"
                  required
                  min="1"
                  max="1000"
                  class="w-full rounded-xl border border-slate-200 px-4 py-3 outline-none focus:border-emerald-500"
                >
              </div>
            </div>

            <label
              class="flex cursor-pointer items-center justify-between rounded-2xl border border-slate-200 p-4"
            >
              <div>
                <p
                  class="font-bold text-slate-800"
                >
                  Open 24 hours
                </p>

                <p
                  class="mt-1 text-xs text-slate-500"
                >
                  Disable fixed opening and closing times.
                </p>
              </div>

              <input
                v-model="
                  locationForm.is_24_hours
                "
                type="checkbox"
                class="h-5 w-5 accent-emerald-600"
              >
            </label>

            <label
              class="mt-4 flex cursor-pointer items-center justify-between rounded-2xl border border-emerald-200 bg-emerald-50/60 p-4"
            >
              <div class="pr-4">
                <div
                  class="flex items-center gap-2"
                >
                  <Sparkles
                    :size="18"
                    class="text-emerald-600"
                  />

                  <p
                    class="font-bold text-slate-800"
                  >
                    Enable AI dynamic pricing
                  </p>
                </div>

                <p
                  class="mt-1 text-xs leading-5 text-slate-500"
                >
                  Adjust booking prices using
                  reservation time, current occupancy
                  and AI-predicted parking demand.
                </p>
              </div>

              <input
                v-model="
                  locationForm.dynamic_pricing_enabled
                "
                type="checkbox"
                class="h-5 w-5 shrink-0 accent-emerald-600"
              >
            </label>

            <div
              v-if="
                !locationForm.is_24_hours
              "
              class="grid gap-4 sm:grid-cols-2"
            >
              <div>
                <label
                  class="mb-2 flex items-center gap-2 text-sm font-bold text-slate-700"
                >
                  <Clock3
                    :size="15"
                  />
                  Opening time
                </label>

                <input
                  v-model="
                    locationForm.opening_time
                  "
                  type="time"
                  required
                  class="w-full rounded-xl border border-slate-200 px-4 py-3 outline-none focus:border-emerald-500"
                >
              </div>

              <div>
                <label
                  class="mb-2 flex items-center gap-2 text-sm font-bold text-slate-700"
                >
                  <Clock3
                    :size="15"
                  />
                  Closing time
                </label>

                <input
                  v-model="
                    locationForm.closing_time
                  "
                  type="time"
                  required
                  class="w-full rounded-xl border border-slate-200 px-4 py-3 outline-none focus:border-emerald-500"
                >
              </div>
            </div>

            <label
              v-if="
                !editingLocationId
              "
              class="flex cursor-pointer items-center justify-between rounded-2xl border border-slate-200 p-4"
            >
              <div>
                <p
                  class="font-bold text-slate-800"
                >
                  Activate immediately
                </p>

                <p
                  class="mt-1 text-xs text-slate-500"
                >
                  Make this location available to SmartPark users.
                </p>
              </div>

              <input
                v-model="
                  locationForm.is_active
                "
                type="checkbox"
                class="h-5 w-5 accent-emerald-600"
              >
            </label>

            <button
              type="submit"
              :disabled="saving"
              class="flex w-full items-center justify-center gap-2 rounded-xl bg-emerald-600 px-5 py-4 font-black text-white transition hover:bg-emerald-700 disabled:opacity-50"
            >
              <Save :size="18" />

              {{
                saving
                  ? 'Saving...'
                  : editingLocationId
                    ? 'Save location changes'
                    : 'Create parking location'
              }}
            </button>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- Space management -->
    <Teleport to="body">
      <div
        v-if="spacesOpen"
        class="fixed inset-0 z-[9998] flex justify-end bg-slate-950/60 backdrop-blur-sm"
      >
        <div
          class="h-full w-full max-w-4xl overflow-y-auto bg-slate-50 shadow-2xl"
        >
          <div
            class="sticky top-0 z-10 border-b border-slate-200 bg-white p-6"
          >
            <div
              class="flex items-start justify-between gap-4"
            >
              <div>
                <p
                  class="text-xs font-bold uppercase tracking-wider text-emerald-600"
                >
                  Space management
                </p>

                <h2
                  class="mt-1 text-2xl font-black text-slate-900"
                >
                  {{
                    selectedLocation
                      ?.name
                  }}
                </h2>

                <p
                  class="mt-2 text-sm text-slate-500"
                >
                  Manage individual parking spaces and live availability.
                </p>
              </div>

              <button
                class="rounded-xl p-2 text-slate-400 hover:bg-slate-100"
                @click="
                  closeSpaces
                "
              >
                <X :size="23" />
              </button>
            </div>
          </div>

          <div
            class="p-6"
          >
            <div
              class="grid gap-3 sm:grid-cols-3"
            >
              <div
                class="rounded-2xl bg-slate-950 p-5 text-white"
              >
                <p
                  class="text-xs uppercase tracking-wide text-slate-400"
                >
                  Total spaces
                </p>

                <p
                  class="mt-2 text-2xl font-black"
                >
                  {{ spaces.length }}
                </p>
              </div>

              <div
                class="rounded-2xl bg-emerald-50 p-5"
              >
                <p
                  class="text-xs uppercase tracking-wide text-emerald-600"
                >
                  Available
                </p>

                <p
                  class="mt-2 text-2xl font-black text-emerald-800"
                >
                  {{ availableSpaces }}
                </p>
              </div>

              <div
                class="rounded-2xl bg-blue-50 p-5"
              >
                <p
                  class="text-xs uppercase tracking-wide text-blue-600"
                >
                  Active spaces
                </p>

                <p
                  class="mt-2 text-2xl font-black text-blue-800"
                >
                  {{ activeSpaces }}
                </p>
              </div>
            </div>

            <div
              class="mt-6 flex justify-end"
            >
              <button
                class="inline-flex items-center gap-2 rounded-xl bg-emerald-600 px-4 py-3 text-sm font-bold text-white"
                @click="
                  openCreateSpace
                "
              >
                <Plus :size="17" />
                Add parking space
              </button>
            </div>

            <div
              v-if="spacesLoading"
              class="mt-6 rounded-2xl bg-white p-10 text-center"
            >
              Loading spaces...
            </div>

            <div
              v-else
              class="mt-6 grid gap-3 sm:grid-cols-2"
            >
              <article
                v-for="space in spaces"
                :key="space.id"
                class="rounded-2xl border border-slate-200 bg-white p-5"
              >
                <div
                  class="flex items-start justify-between gap-4"
                >
                  <div
                    class="flex gap-3"
                  >
                    <div
                      class="flex h-11 w-11 items-center justify-center rounded-xl bg-slate-950 text-white"
                    >
                      <CarFront
                        :size="20"
                      />
                    </div>

                    <div>
                      <div
                        class="flex flex-wrap items-center gap-2"
                      >
                        <h3
                          class="font-black text-slate-900"
                        >
                          Space
                          {{ space.space_number }}
                        </h3>

                        <span
                          :class="[
                            'rounded-full px-2 py-1 text-[10px] font-black uppercase',
                            space.is_available
                              ? 'bg-emerald-100 text-emerald-700'
                              : 'bg-red-100 text-red-700',
                          ]"
                        >
                          {{
                            space.is_available
                              ? 'Available'
                              : 'Unavailable'
                          }}
                        </span>
                      </div>

                      <p
                        class="mt-1 text-xs capitalize text-slate-500"
                      >
                        {{ space.space_type }}
                      </p>
                    </div>
                  </div>

                  <button
                    class="rounded-xl border border-slate-200 p-2 text-slate-500 hover:bg-slate-50"
                    @click="
                      openEditSpace(
                        space
                      )
                    "
                  >
                    <Pencil
                      :size="16"
                    />
                  </button>
                </div>

                <div
                  class="mt-4 flex flex-wrap gap-2"
                >
                  <span
                    v-if="
                      space.has_ev_charging
                    "
                    class="inline-flex items-center gap-1 rounded-full bg-amber-100 px-2.5 py-1 text-xs font-bold text-amber-700"
                  >
                    <Zap :size="13" />
                    EV
                  </span>

                  <span
                    v-if="
                      space.is_accessible
                    "
                    class="inline-flex items-center gap-1 rounded-full bg-blue-100 px-2.5 py-1 text-xs font-bold text-blue-700"
                  >
                    <Accessibility
                      :size="13"
                    />
                    Accessible
                  </span>

                  <span
                    :class="[
                      'rounded-full px-2.5 py-1 text-xs font-bold',
                      space.is_active
                        ? 'bg-slate-100 text-slate-700'
                        : 'bg-red-100 text-red-700',
                    ]"
                  >
                    {{
                      space.is_active
                        ? 'Active'
                        : 'Inactive'
                    }}
                  </span>
                </div>

                <div
                  class="mt-5 grid grid-cols-2 gap-2"
                >
                  <button
                    class="rounded-xl border border-slate-200 px-3 py-2.5 text-xs font-bold text-slate-700 hover:bg-slate-50"
                    @click="
                      toggleSpaceAvailability(
                        space
                      )
                    "
                  >
                    {{
                      space.is_available
                        ? 'Mark unavailable'
                        : 'Mark available'
                    }}
                  </button>

                  <button
                    class="rounded-xl border border-slate-200 px-3 py-2.5 text-xs font-bold text-slate-700 hover:bg-slate-50"
                    @click="
                      toggleSpaceStatus(
                        space
                      )
                    "
                  >
                    {{
                      space.is_active
                        ? 'Deactivate'
                        : 'Activate'
                    }}
                  </button>
                </div>
              </article>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Space form -->
    <Teleport to="body">
      <div
        v-if="spaceFormOpen"
        class="fixed inset-0 z-[10000] flex items-center justify-center bg-slate-950/70 p-4 backdrop-blur-sm"
        @click.self="
          closeSpaceForm
        "
      >
        <div
          class="w-full max-w-lg overflow-hidden rounded-3xl bg-white shadow-2xl"
        >
          <div
            class="flex items-center justify-between border-b border-slate-200 p-6"
          >
            <div>
              <p
                class="text-xs font-bold uppercase tracking-wider text-emerald-600"
              >
                Parking space
              </p>

              <h2
                class="mt-1 text-xl font-black text-slate-900"
              >
                {{
                  editingSpaceId
                    ? 'Edit space'
                    : 'Add parking space'
                }}
              </h2>
            </div>

            <button
              class="rounded-xl p-2 text-slate-400 hover:bg-slate-100"
              @click="
                closeSpaceForm
              "
            >
              <X :size="21" />
            </button>
          </div>

          <form
            class="space-y-5 p-6"
            @submit.prevent="
              saveSpace
            "
          >
            <div>
              <label
                class="mb-2 block text-sm font-bold text-slate-700"
              >
                Space number
              </label>

              <input
                v-model="
                  spaceForm.space_number
                "
                required
                maxlength="30"
                placeholder="A-01"
                class="w-full rounded-xl border border-slate-200 px-4 py-3 uppercase outline-none focus:border-emerald-500"
              >
            </div>

            <div>
              <label
                class="mb-2 block text-sm font-bold text-slate-700"
              >
                Space type
              </label>

              <select
                v-model="
                  spaceForm.space_type
                "
                class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3"
              >
                <option value="standard">
                  Standard
                </option>

                <option value="compact">
                  Compact
                </option>

                <option value="large">
                  Large
                </option>
              </select>
            </div>

            <div
              class="space-y-3"
            >
              <label
                class="flex cursor-pointer items-center justify-between rounded-2xl border border-slate-200 p-4"
              >
                <span
                  class="flex items-center gap-2 font-semibold text-slate-700"
                >
                  <Zap
                    :size="17"
                    class="text-amber-500"
                  />
                  EV charging
                </span>

                <input
                  v-model="
                    spaceForm.has_ev_charging
                  "
                  type="checkbox"
                  class="h-5 w-5 accent-emerald-600"
                >
              </label>

              <label
                class="flex cursor-pointer items-center justify-between rounded-2xl border border-slate-200 p-4"
              >
                <span
                  class="flex items-center gap-2 font-semibold text-slate-700"
                >
                  <Accessibility
                    :size="17"
                    class="text-blue-500"
                  />
                  Accessible
                </span>

                <input
                  v-model="
                    spaceForm.is_accessible
                  "
                  type="checkbox"
                  class="h-5 w-5 accent-emerald-600"
                >
              </label>

              <label
                class="flex cursor-pointer items-center justify-between rounded-2xl border border-slate-200 p-4"
              >
                <span
                  class="font-semibold text-slate-700"
                >
                  Available
                </span>

                <input
                  v-model="
                    spaceForm.is_available
                  "
                  type="checkbox"
                  class="h-5 w-5 accent-emerald-600"
                >
              </label>

              <label
                class="flex cursor-pointer items-center justify-between rounded-2xl border border-slate-200 p-4"
              >
                <span
                  class="font-semibold text-slate-700"
                >
                  Active
                </span>

                <input
                  v-model="
                    spaceForm.is_active
                  "
                  type="checkbox"
                  class="h-5 w-5 accent-emerald-600"
                >
              </label>
            </div>

            <button
              type="submit"
              :disabled="saving"
              class="flex w-full items-center justify-center gap-2 rounded-xl bg-emerald-600 px-5 py-4 font-black text-white disabled:opacity-50"
            >
              <Save :size="18" />

              {{
                saving
                  ? 'Saving...'
                  : editingSpaceId
                    ? 'Save space changes'
                    : 'Add parking space'
              }}
            </button>
          </form>
        </div>
      </div>
    </Teleport>
  </AppShell>
</template>
