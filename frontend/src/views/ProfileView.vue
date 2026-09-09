<script setup>
import {
  computed,
  onMounted,
  ref,
} from 'vue'

import {
  CarFront,
  CheckCircle2,
  Mail,
  Pencil,
  Plus,
  Save,
  ShieldCheck,
  Star,
  Trash2,
  UserRound,
  X,
} from '@lucide/vue'

import AppShell from '../components/AppShell.vue'
import api from '../services/api'
import { auth } from '../stores/auth'

const vehicles = ref([])
const loading = ref(true)
const saving = ref(false)
const deletingId = ref(null)

const errorMessage = ref('')
const successMessage = ref('')

const formOpen = ref(false)
const editingVehicleId = ref(null)

const vehicleForm = ref({
  registration_number: '',
  make: '',
  model: '',
  colour: '',
  vehicle_type: 'car',
  is_default: false,
})

const user = computed(
  () => auth.state.user
)

const initials = computed(() => {
  const name =
    user.value?.full_name ||
    'SmartPark User'

  return name
    .split(/\s+/)
    .slice(0, 2)
    .map(
      (part) => part[0]
    )
    .join('')
    .toUpperCase()
})

const defaultVehicle = computed(
  () =>
    vehicles.value.find(
      (vehicle) =>
        vehicle.is_default
    ) || null
)

function resetVehicleForm() {
  vehicleForm.value = {
    registration_number: '',
    make: '',
    model: '',
    colour: '',
    vehicle_type: 'car',
    is_default: false,
  }

  editingVehicleId.value = null
}

function openAddVehicle() {
  resetVehicleForm()
  errorMessage.value = ''
  successMessage.value = ''
  formOpen.value = true
}

function openEditVehicle(vehicle) {
  errorMessage.value = ''
  successMessage.value = ''

  editingVehicleId.value =
    vehicle.id

  vehicleForm.value = {
    registration_number:
      vehicle.registration_number,
    make: vehicle.make,
    model: vehicle.model,
    colour: vehicle.colour,
    vehicle_type:
      vehicle.vehicle_type,
    is_default:
      vehicle.is_default,
  }

  formOpen.value = true
}

function closeVehicleForm() {
  formOpen.value = false
  resetVehicleForm()
}

async function loadVehicles() {
  loading.value = true
  errorMessage.value = ''

  try {
    const response =
      await api.get(
        '/api/vehicles'
      )

    vehicles.value =
      response.data
  } catch (error) {
    errorMessage.value =
      error.response?.data?.detail ||
      'Unable to load vehicles.'
  } finally {
    loading.value = false
  }
}

async function saveVehicle() {
  errorMessage.value = ''
  successMessage.value = ''
  saving.value = true

  const payload = {
    registration_number:
      vehicleForm.value
        .registration_number
        .trim()
        .toUpperCase(),

    make:
      vehicleForm.value
        .make
        .trim(),

    model:
      vehicleForm.value
        .model
        .trim(),

    colour:
      vehicleForm.value
        .colour
        .trim(),

    vehicle_type:
      vehicleForm.value
        .vehicle_type,

    is_default:
      Boolean(
        vehicleForm.value
          .is_default
      ),
  }

  try {
    if (
      editingVehicleId.value
    ) {
      await api.patch(
        `/api/vehicles/${editingVehicleId.value}`,
        payload
      )

      successMessage.value =
        'Vehicle updated successfully.'
    } else {
      await api.post(
        '/api/vehicles',
        payload
      )

      successMessage.value =
        'Vehicle added successfully.'
    }

    closeVehicleForm()
    await loadVehicles()
  } catch (error) {
    errorMessage.value =
      error.response?.data?.detail ||
      'Unable to save vehicle.'
  } finally {
    saving.value = false
  }
}

async function makeDefault(vehicle) {
  errorMessage.value = ''
  successMessage.value = ''

  try {
    await api.patch(
      `/api/vehicles/${vehicle.id}`,
      {
        is_default: true,
      }
    )

    successMessage.value =
      `${vehicle.registration_number} is now your default vehicle.`

    await loadVehicles()
  } catch (error) {
    errorMessage.value =
      error.response?.data?.detail ||
      'Unable to update the default vehicle.'
  }
}

async function deleteVehicle(vehicle) {
  const confirmed =
    window.confirm(
      `Delete vehicle ${vehicle.registration_number}?`
    )

  if (!confirmed) {
    return
  }

  deletingId.value =
    vehicle.id

  errorMessage.value = ''
  successMessage.value = ''

  try {
    await api.delete(
      `/api/vehicles/${vehicle.id}`
    )

    successMessage.value =
      `${vehicle.registration_number} was removed.`

    await loadVehicles()
  } catch (error) {
    errorMessage.value =
      error.response?.data?.detail ||
      'Unable to delete vehicle. It may be linked to an existing reservation.'
  } finally {
    deletingId.value = null
  }
}

onMounted(loadVehicles)
</script>

<template>
  <AppShell>
    <section
      class="mx-auto max-w-7xl"
    >
      <div
        class="relative overflow-hidden rounded-[2rem] bg-slate-950 p-7 text-white shadow-2xl sm:p-9"
      >
        <div
          class="absolute -right-24 -top-24 h-72 w-72 rounded-full bg-emerald-500/20 blur-3xl"
        />

        <div
          class="relative grid gap-8 lg:grid-cols-[1fr_auto] lg:items-center"
        >
          <div>
            <div
              class="inline-flex items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1.5 text-xs font-semibold text-emerald-300"
            >
              <UserRound
                :size="15"
              />
              Account & vehicle management
            </div>

            <h1
              class="mt-5 text-3xl font-black tracking-tight sm:text-4xl"
            >
              My SmartPark Profile
            </h1>

            <p
              class="mt-3 max-w-2xl text-sm leading-7 text-slate-300"
            >
              Manage your account details
              and the vehicles used for
              SmartPark reservations.
            </p>
          </div>

          <div
            class="flex items-center gap-4 rounded-3xl border border-white/10 bg-white/5 p-5 backdrop-blur"
          >
            <div
              class="flex h-16 w-16 items-center justify-center rounded-2xl bg-emerald-500 text-xl font-black text-slate-950"
            >
              {{ initials }}
            </div>

            <div>
              <p
                class="font-bold"
              >
                {{
                  user?.full_name
                }}
              </p>

              <p
                class="mt-1 text-xs text-slate-400"
              >
                {{
                  user?.email
                }}
              </p>

              <span
                class="mt-2 inline-flex rounded-full bg-white/10 px-3 py-1 text-[11px] font-bold uppercase tracking-wide text-emerald-300"
              >
                {{
                  user?.role ||
                  'user'
                }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div
        v-if="successMessage"
        class="mt-6 flex items-start gap-3 rounded-2xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-700"
      >
        <CheckCircle2
          :size="19"
          class="mt-0.5 shrink-0"
        />

        {{ successMessage }}
      </div>

      <div
        v-if="errorMessage"
        class="mt-6 rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-700"
      >
        {{ errorMessage }}
      </div>

      <div
        class="mt-7 grid gap-6 xl:grid-cols-[0.75fr_1.25fr]"
      >
        <section
          class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm"
        >
          <div
            class="flex items-center gap-3"
          >
            <div
              class="flex h-12 w-12 items-center justify-center rounded-2xl bg-emerald-50 text-emerald-600"
            >
              <UserRound
                :size="22"
              />
            </div>

            <div>
              <h2
                class="font-bold text-slate-900"
              >
                Account details
              </h2>

              <p
                class="text-xs text-slate-500"
              >
                Your SmartPark identity
              </p>
            </div>
          </div>

          <div
            class="mt-6 space-y-4"
          >
            <div
              class="rounded-2xl bg-slate-50 p-4"
            >
              <p
                class="text-xs font-semibold uppercase tracking-wide text-slate-400"
              >
                Full name
              </p>

              <p
                class="mt-2 font-bold text-slate-900"
              >
                {{
                  user?.full_name
                }}
              </p>
            </div>

            <div
              class="rounded-2xl bg-slate-50 p-4"
            >
              <div
                class="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-slate-400"
              >
                <Mail :size="14" />
                Email
              </div>

              <p
                class="mt-2 font-bold text-slate-900"
              >
                {{
                  user?.email
                }}
              </p>
            </div>

            <div
              class="rounded-2xl bg-slate-50 p-4"
            >
              <div
                class="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-slate-400"
              >
                <ShieldCheck
                  :size="14"
                />
                Account status
              </div>

              <div
                class="mt-2 flex items-center justify-between"
              >
                <span
                  class="font-bold text-slate-900"
                >
                  {{
                    user?.role
                      ?.replace(
                        /\b\w/g,
                        (letter) =>
                          letter.toUpperCase()
                      )
                  }}
                </span>

                <span
                  class="rounded-full bg-emerald-100 px-3 py-1 text-xs font-bold text-emerald-700"
                >
                  {{
                    user?.is_active
                      ? 'Active'
                      : 'Inactive'
                  }}
                </span>
              </div>
            </div>
          </div>

          <div
            v-if="defaultVehicle"
            class="mt-5 rounded-2xl bg-slate-950 p-5 text-white"
          >
            <div
              class="flex items-center gap-2 text-emerald-400"
            >
              <Star
                :size="17"
              />

              <p
                class="text-xs font-bold uppercase tracking-wide"
              >
                Default vehicle
              </p>
            </div>

            <p
              class="mt-3 text-xl font-black"
            >
              {{
                defaultVehicle
                  .registration_number
              }}
            </p>

            <p
              class="mt-1 text-sm text-slate-400"
            >
              {{
                defaultVehicle.make
              }}
              {{
                defaultVehicle.model
              }}
            </p>
          </div>
        </section>

        <section
          class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm"
        >
          <div
            class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between"
          >
            <div
              class="flex items-center gap-3"
            >
              <div
                class="flex h-12 w-12 items-center justify-center rounded-2xl bg-cyan-50 text-cyan-600"
              >
                <CarFront
                  :size="22"
                />
              </div>

              <div>
                <h2
                  class="font-bold text-slate-900"
                >
                  My vehicles
                </h2>

                <p
                  class="text-xs text-slate-500"
                >
                  {{
                    vehicles.length
                  }}
                  registered
                  {{
                    vehicles.length === 1
                      ? 'vehicle'
                      : 'vehicles'
                  }}
                </p>
              </div>
            </div>

            <button
              class="inline-flex items-center justify-center gap-2 rounded-xl bg-emerald-600 px-4 py-3 text-sm font-bold text-white shadow-lg shadow-emerald-600/15 transition hover:bg-emerald-700"
              @click="openAddVehicle"
            >
              <Plus :size="18" />
              Add vehicle
            </button>
          </div>

          <div
            v-if="loading"
            class="mt-6 rounded-2xl bg-slate-50 p-10 text-center text-sm text-slate-500"
          >
            Loading vehicles...
          </div>

          <div
            v-else-if="
              vehicles.length === 0
            "
            class="mt-6 rounded-2xl border border-dashed border-slate-300 p-10 text-center"
          >
            <CarFront
              :size="38"
              class="mx-auto text-slate-300"
            />

            <h3
              class="mt-4 font-bold text-slate-800"
            >
              No vehicles registered
            </h3>

            <p
              class="mt-2 text-sm text-slate-500"
            >
              Add a vehicle before making
              a parking reservation.
            </p>

            <button
              class="mt-5 rounded-xl bg-emerald-600 px-5 py-3 text-sm font-semibold text-white"
              @click="openAddVehicle"
            >
              Add your first vehicle
            </button>
          </div>

          <div
            v-else
            class="mt-6 space-y-4"
          >
            <article
              v-for="vehicle in vehicles"
              :key="vehicle.id"
              class="rounded-2xl border border-slate-200 p-5 transition hover:border-emerald-200 hover:shadow-md"
            >
              <div
                class="flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between"
              >
                <div
                  class="flex gap-4"
                >
                  <div
                    class="flex h-13 w-13 shrink-0 items-center justify-center rounded-2xl bg-slate-950 p-3 text-white"
                  >
                    <CarFront
                      :size="24"
                    />
                  </div>

                  <div>
                    <div
                      class="flex flex-wrap items-center gap-2"
                    >
                      <h3
                        class="text-lg font-black text-slate-900"
                      >
                        {{
                          vehicle.registration_number
                        }}
                      </h3>

                      <span
                        v-if="
                          vehicle.is_default
                        "
                        class="inline-flex items-center gap-1 rounded-full bg-emerald-100 px-2.5 py-1 text-[11px] font-bold text-emerald-700"
                      >
                        <Star
                          :size="12"
                        />
                        Default
                      </span>
                    </div>

                    <p
                      class="mt-1 font-semibold text-slate-700"
                    >
                      {{
                        vehicle.make
                      }}
                      {{
                        vehicle.model
                      }}
                    </p>

                    <div
                      class="mt-3 flex flex-wrap gap-2"
                    >
                      <span
                        class="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600"
                      >
                        {{
                          vehicle.colour
                        }}
                      </span>

                      <span
                        class="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium capitalize text-slate-600"
                      >
                        {{
                          vehicle.vehicle_type
                        }}
                      </span>
                    </div>
                  </div>
                </div>

                <div
                  class="flex flex-wrap gap-2"
                >
                  <button
                    v-if="
                      !vehicle.is_default
                    "
                    class="inline-flex items-center gap-1.5 rounded-xl border border-emerald-200 px-3 py-2 text-xs font-semibold text-emerald-700 transition hover:bg-emerald-50"
                    @click="
                      makeDefault(
                        vehicle
                      )
                    "
                  >
                    <Star
                      :size="15"
                    />
                    Make default
                  </button>

                  <button
                    class="inline-flex items-center gap-1.5 rounded-xl border border-slate-200 px-3 py-2 text-xs font-semibold text-slate-600 transition hover:bg-slate-50"
                    @click="
                      openEditVehicle(
                        vehicle
                      )
                    "
                  >
                    <Pencil
                      :size="15"
                    />
                    Edit
                  </button>

                  <button
                    class="inline-flex items-center gap-1.5 rounded-xl border border-red-200 px-3 py-2 text-xs font-semibold text-red-600 transition hover:bg-red-50 disabled:opacity-50"
                    :disabled="
                      deletingId ===
                      vehicle.id
                    "
                    @click="
                      deleteVehicle(
                        vehicle
                      )
                    "
                  >
                    <Trash2
                      :size="15"
                    />

                    {{
                      deletingId ===
                      vehicle.id
                        ? 'Deleting...'
                        : 'Delete'
                    }}
                  </button>
                </div>
              </div>
            </article>
          </div>
        </section>
      </div>
    </section>

    <Teleport to="body">
      <div
        v-if="formOpen"
        class="fixed inset-0 z-[9999] flex items-center justify-center overflow-y-auto bg-slate-950/60 p-4 backdrop-blur-sm"
      @click.self="
        closeVehicleForm
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
              Vehicle management
            </p>

            <h2
              class="mt-1 text-xl font-black text-slate-900"
            >
              {{
                editingVehicleId
                  ? 'Edit vehicle'
                  : 'Add vehicle'
              }}
            </h2>
          </div>

          <button
            class="rounded-xl p-2 text-slate-400 transition hover:bg-slate-100 hover:text-slate-700"
            @click="
              closeVehicleForm
            "
          >
            <X :size="21" />
          </button>
        </div>

        <form
          class="space-y-5 p-6"
          @submit.prevent="
            saveVehicle
          "
        >
          <div>
            <label
              class="mb-2 block text-sm font-semibold text-slate-700"
            >
              Registration number
            </label>

            <input
              v-model="
                vehicleForm.registration_number
              "
              required
              minlength="2"
              maxlength="20"
              placeholder="AB12 CDE"
              class="w-full rounded-xl border border-slate-200 px-4 py-3.5 uppercase outline-none transition focus:border-emerald-500 focus:ring-4 focus:ring-emerald-100"
            >
          </div>

          <div
            class="grid gap-4 sm:grid-cols-2"
          >
            <div>
              <label
                class="mb-2 block text-sm font-semibold text-slate-700"
              >
                Make
              </label>

              <input
                v-model="
                  vehicleForm.make
                "
                required
                maxlength="60"
                placeholder="Toyota"
                class="w-full rounded-xl border border-slate-200 px-4 py-3.5 outline-none focus:border-emerald-500"
              >
            </div>

            <div>
              <label
                class="mb-2 block text-sm font-semibold text-slate-700"
              >
                Model
              </label>

              <input
                v-model="
                  vehicleForm.model
                "
                required
                maxlength="60"
                placeholder="Corolla"
                class="w-full rounded-xl border border-slate-200 px-4 py-3.5 outline-none focus:border-emerald-500"
              >
            </div>

            <div>
              <label
                class="mb-2 block text-sm font-semibold text-slate-700"
              >
                Colour
              </label>

              <input
                v-model="
                  vehicleForm.colour
                "
                required
                maxlength="40"
                placeholder="Black"
                class="w-full rounded-xl border border-slate-200 px-4 py-3.5 outline-none focus:border-emerald-500"
              >
            </div>

            <div>
              <label
                class="mb-2 block text-sm font-semibold text-slate-700"
              >
                Vehicle type
              </label>

              <select
                v-model="
                  vehicleForm.vehicle_type
                "
                class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3.5 outline-none focus:border-emerald-500"
              >
                <option value="car">
                  Car
                </option>

                <option value="electric">
                  Electric
                </option>

                <option value="van">
                  Van
                </option>

                <option value="motorcycle">
                  Motorcycle
                </option>

                <option value="other">
                  Other
                </option>
              </select>
            </div>
          </div>

          <label
            class="flex cursor-pointer items-center justify-between rounded-2xl border border-slate-200 p-4"
          >
            <div>
              <p
                class="text-sm font-bold text-slate-800"
              >
                Default vehicle
              </p>

              <p
                class="mt-1 text-xs text-slate-500"
              >
                Automatically select this
                vehicle for new bookings.
              </p>
            </div>

            <input
              v-model="
                vehicleForm.is_default
              "
              type="checkbox"
              class="h-5 w-5 accent-emerald-600"
            >
          </label>

          <div
            v-if="errorMessage"
            class="rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700"
          >
            {{ errorMessage }}
          </div>

          <button
            type="submit"
            :disabled="saving"
            class="flex w-full items-center justify-center gap-2 rounded-xl bg-emerald-600 px-5 py-4 font-bold text-white shadow-lg shadow-emerald-600/15 transition hover:bg-emerald-700 disabled:opacity-50"
          >
            <Save :size="18" />

            {{
              saving
                ? 'Saving...'
                : editingVehicleId
                  ? 'Save changes'
                  : 'Add vehicle'
            }}
          </button>
        </form>
      </div>
      </div>
    </Teleport>
  </AppShell>
</template>
