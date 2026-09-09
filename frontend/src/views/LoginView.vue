<script setup>
import {
  computed,
  ref,
} from 'vue'

import {
  RouterLink,
  useRoute,
  useRouter,
} from 'vue-router'

import {
  ArrowRight,
  BrainCircuit,
  CarFront,
  CheckCircle2,
  Eye,
  EyeOff,
  LockKeyhole,
  MapPinned,
  ShieldCheck,
  Sparkles,
} from '@lucide/vue'

import { auth } from '../stores/auth'

const router = useRouter()
const route = useRoute()

const email = ref('')
const password = ref('')

const errorMessage = ref('')
const showPassword = ref(false)

const sessionMessage = computed(() => {
  if (
    route.query.reason ===
    'session-expired'
  ) {
    return 'Your session expired. Please sign in again.'
  }

  return ''
})

async function submitLogin() {
  errorMessage.value = ''

  try {
    await auth.login(
      email.value.trim(),
      password.value
    )

    const redirect =
      typeof route.query.redirect === 'string'
        ? route.query.redirect
        : '/dashboard'

    const safeRedirect =
      redirect.startsWith('/')
        ? redirect
        : '/dashboard'

    window.location.replace(
      safeRedirect
    )
  } catch (error) {
    errorMessage.value =
      error.response?.data?.detail ||
      'Unable to sign in. Please check your details and try again.'
  }
}
</script>

<template>
  <main
    class="relative min-h-screen overflow-hidden bg-slate-950"
  >
    <!-- Background effects -->
    <div
      class="pointer-events-none absolute -left-40 -top-40 h-[520px] w-[520px] rounded-full bg-emerald-500/20 blur-[120px]"
    />

    <div
      class="pointer-events-none absolute -bottom-40 right-0 h-[520px] w-[520px] rounded-full bg-cyan-500/15 blur-[130px]"
    />

    <div
      class="relative mx-auto flex min-h-screen max-w-[1600px] items-center justify-center p-4 sm:p-6 lg:p-8"
    >
      <div
        class="grid w-full max-w-7xl overflow-hidden rounded-[2.25rem] border border-white/10 bg-white shadow-2xl shadow-black/30 lg:min-h-[820px] lg:grid-cols-[1.08fr_0.92fr]"
      >
        <!-- Left panel -->
        <section
          class="relative hidden overflow-hidden bg-slate-950 p-10 text-white lg:flex lg:flex-col lg:justify-between xl:p-14"
        >
          <div
            class="absolute inset-0 bg-gradient-to-br from-emerald-500/20 via-transparent to-cyan-500/10"
          />

          <div
            class="absolute -right-28 top-24 h-80 w-80 rounded-full border border-emerald-400/10"
          />

          <div
            class="absolute -right-10 top-44 h-52 w-52 rounded-full border border-cyan-400/10"
          />

          <div class="relative">
            <RouterLink
              to="/"
              class="inline-flex items-center gap-3"
            >
              <div
                class="flex h-12 w-12 items-center justify-center rounded-2xl bg-emerald-500 text-lg font-black text-slate-950 shadow-lg shadow-emerald-500/20"
              >
                P
              </div>

              <div>
                <p
                  class="text-xl font-black tracking-tight"
                >
                  SmartPark AI
                </p>

                <p
                  class="text-xs text-slate-400"
                >
                  Intelligent Urban Parking
                </p>
              </div>
            </RouterLink>

            <div
              class="mt-16 inline-flex items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/10 px-4 py-2 text-xs font-semibold text-emerald-300"
            >
              <Sparkles :size="15" />
              AI-powered parking intelligence
            </div>

            <h1
              class="mt-7 max-w-xl text-5xl font-black leading-[1.05] tracking-tight xl:text-6xl"
            >
              Smarter parking
              <span
                class="bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent"
              >
                starts before
              </span>
              you arrive.
            </h1>

            <p
              class="mt-7 max-w-xl text-base leading-8 text-slate-300"
            >
              Predict parking demand, compare live
              availability and receive intelligent
              recommendations from one connected
              SmartPark platform.
            </p>

            <div
              class="mt-10 grid max-w-xl gap-3 sm:grid-cols-2"
            >
              <div
                class="rounded-2xl border border-white/10 bg-white/5 p-4 backdrop-blur"
              >
                <div
                  class="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-400/10 text-emerald-300"
                >
                  <BrainCircuit :size="20" />
                </div>

                <p
                  class="mt-4 text-sm font-bold"
                >
                  AI Demand Forecasting
                </p>

                <p
                  class="mt-1 text-xs leading-5 text-slate-400"
                >
                  XGBoost-powered parking occupancy
                  prediction.
                </p>
              </div>

              <div
                class="rounded-2xl border border-white/10 bg-white/5 p-4 backdrop-blur"
              >
                <div
                  class="flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-400/10 text-cyan-300"
                >
                  <MapPinned :size="20" />
                </div>

                <p
                  class="mt-4 text-sm font-bold"
                >
                  Smart Recommendations
                </p>

                <p
                  class="mt-1 text-xs leading-5 text-slate-400"
                >
                  Rank parking using demand, price,
                  distance and availability.
                </p>
              </div>

              <div
                class="rounded-2xl border border-white/10 bg-white/5 p-4 backdrop-blur"
              >
                <div
                  class="flex h-10 w-10 items-center justify-center rounded-xl bg-violet-400/10 text-violet-300"
                >
                  <CarFront :size="20" />
                </div>

                <p
                  class="mt-4 text-sm font-bold"
                >
                  Complete Parking Journey
                </p>

                <p
                  class="mt-1 text-xs leading-5 text-slate-400"
                >
                  Reserve, check in, pay and check out.
                </p>
              </div>

              <div
                class="rounded-2xl border border-white/10 bg-white/5 p-4 backdrop-blur"
              >
                <div
                  class="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-400/10 text-amber-300"
                >
                  <ShieldCheck :size="20" />
                </div>

                <p
                  class="mt-4 text-sm font-bold"
                >
                  Secure Account Access
                </p>

                <p
                  class="mt-1 text-xs leading-5 text-slate-400"
                >
                  Protected authentication and
                  personalised parking activity.
                </p>
              </div>
            </div>
          </div>

          <div
            class="relative mt-10 flex items-center justify-between border-t border-white/10 pt-6"
          >
            <div
              class="flex items-center gap-2 text-xs text-slate-400"
            >
              <CheckCircle2
                :size="16"
                class="text-emerald-400"
              />
              Live parking intelligence
            </div>

            <p
              class="text-xs text-slate-500"
            >
              SmartPark AI
            </p>
          </div>
        </section>

        <!-- Login panel -->
        <section
          class="relative flex items-center justify-center bg-gradient-to-b from-white to-slate-50 px-6 py-10 sm:px-10 lg:px-12 xl:px-16"
        >
          <div
            class="w-full max-w-md"
          >
            <!-- Mobile logo -->
            <RouterLink
              to="/"
              class="mb-10 flex items-center gap-3 lg:hidden"
            >
              <div
                class="flex h-11 w-11 items-center justify-center rounded-2xl bg-emerald-500 font-black text-slate-950"
              >
                P
              </div>

              <div>
                <p
                  class="font-black text-slate-900"
                >
                  SmartPark AI
                </p>

                <p
                  class="text-xs text-slate-500"
                >
                  Intelligent Parking
                </p>
              </div>
            </RouterLink>

            <div
              class="inline-flex items-center gap-2 rounded-full bg-emerald-50 px-3 py-1.5 text-xs font-bold text-emerald-700"
            >
              <LockKeyhole :size="14" />
              Secure sign in
            </div>

            <h2
              class="mt-5 text-4xl font-black tracking-tight text-slate-950"
            >
              Welcome back
            </h2>

            <p
              class="mt-3 leading-7 text-slate-500"
            >
              Sign in to access your SmartPark dashboard,
              AI predictions, reservations and wallet.
            </p>

            <div
              v-if="sessionMessage"
              class="mt-6 rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm font-medium text-amber-800"
            >
              {{ sessionMessage }}
            </div>

            <form
              class="mt-8 space-y-5"
              @submit.prevent="submitLogin"
            >
              <div>
                <label
                  for="email"
                  class="mb-2 block text-sm font-bold text-slate-700"
                >
                  Email address
                </label>

                <input
                  id="email"
                  v-model="email"
                  type="email"
                  autocomplete="email"
                  required
                  placeholder="name@example.com"
                  class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-4 text-slate-900 shadow-sm outline-none transition placeholder:text-slate-400 focus:border-emerald-500 focus:ring-4 focus:ring-emerald-100"
                >
              </div>

              <div>
                <div
                  class="mb-2 flex items-center justify-between"
                >
                  <label
                    for="password"
                    class="text-sm font-bold text-slate-700"
                  >
                    Password
                  </label>

                  <span
                    class="text-xs font-medium text-slate-400"
                  >
                    Protected account
                  </span>
                </div>

                <div class="relative">
                  <input
                    id="password"
                    v-model="password"
                    :type="
                      showPassword
                        ? 'text'
                        : 'password'
                    "
                    autocomplete="current-password"
                    required
                    placeholder="Enter your password"
                    class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-4 pr-14 text-slate-900 shadow-sm outline-none transition placeholder:text-slate-400 focus:border-emerald-500 focus:ring-4 focus:ring-emerald-100"
                  >

                  <button
                    type="button"
                    class="absolute inset-y-0 right-3 flex items-center justify-center rounded-xl px-2 text-slate-400 transition hover:bg-slate-100 hover:text-slate-700"
                    @click="
                      showPassword =
                        !showPassword
                    "
                  >
                    <EyeOff
                      v-if="showPassword"
                      :size="20"
                    />

                    <Eye
                      v-else
                      :size="20"
                    />
                  </button>
                </div>
              </div>

              <div
                v-if="errorMessage"
                class="rounded-2xl border border-red-200 bg-red-50 p-4 text-sm font-medium leading-6 text-red-700"
              >
                {{ errorMessage }}
              </div>

              <button
                type="submit"
                :disabled="auth.state.loading"
                class="group flex w-full items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-emerald-600 to-teal-600 px-5 py-4 font-bold text-white shadow-lg shadow-emerald-600/20 transition hover:-translate-y-0.5 hover:shadow-xl disabled:cursor-not-allowed disabled:opacity-60"
              >
                {{
                  auth.state.loading
                    ? 'Signing in...'
                    : 'Sign in to SmartPark'
                }}

                <ArrowRight
                  v-if="
                    !auth.state.loading
                  "
                  :size="19"
                  class="transition-transform group-hover:translate-x-1"
                />
              </button>
            </form>

            <div
              class="my-8 flex items-center gap-4"
            >
              <div
                class="h-px flex-1 bg-slate-200"
              />

              <span
                class="text-xs font-semibold uppercase tracking-wider text-slate-400"
              >
                New user
              </span>

              <div
                class="h-px flex-1 bg-slate-200"
              />
            </div>

            <RouterLink
              to="/register"
              class="flex w-full items-center justify-center rounded-2xl border border-slate-200 bg-white px-5 py-4 font-bold text-slate-700 shadow-sm transition hover:border-emerald-200 hover:bg-emerald-50 hover:text-emerald-700"
            >
              Create a SmartPark account
            </RouterLink>

            <div
              class="mt-8 flex items-center justify-center gap-2 text-xs text-slate-400"
            >
              <ShieldCheck
                :size="15"
                class="text-emerald-500"
              />

              Secure JWT-based authentication
            </div>
          </div>
        </section>
      </div>
    </div>
  </main>
</template>
