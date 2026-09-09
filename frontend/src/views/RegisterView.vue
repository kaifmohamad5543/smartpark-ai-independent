<script setup>
import { ref } from 'vue'
import {
  RouterLink,
  useRouter,
} from 'vue-router'

import { auth } from '../stores/auth'

const router = useRouter()

const fullName = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const errorMessage = ref('')
const showPassword = ref(false)

async function submitRegistration() {
  errorMessage.value = ''

  if (
    password.value !==
    confirmPassword.value
  ) {
    errorMessage.value =
      'Passwords do not match.'
    return
  }

  if (password.value.length < 8) {
    errorMessage.value =
      'Password must contain at least 8 characters.'
    return
  }

  try {
    await auth.register(
      fullName.value.trim(),
      email.value.trim(),
      password.value
    )

    await router.replace(
      '/dashboard'
    )
  } catch (error) {
    errorMessage.value =
      error.response?.data?.detail ||
      'Unable to create your account.'
  }
}
</script>

<template>
  <main
    class="min-h-screen bg-slate-950 px-4 py-10 sm:px-6"
  >
    <div
      class="mx-auto grid min-h-[calc(100vh-5rem)] max-w-6xl overflow-hidden rounded-3xl bg-white shadow-2xl lg:grid-cols-2"
    >
      <section
        class="hidden bg-gradient-to-br from-cyan-700 via-teal-600 to-emerald-600 p-12 text-white lg:flex lg:flex-col lg:justify-between"
      >
        <div>
          <div
            class="inline-flex items-center gap-3 rounded-full bg-white/15 px-4 py-2 text-sm font-semibold backdrop-blur"
          >
            <span
              class="flex h-8 w-8 items-center justify-center rounded-full bg-white text-emerald-700"
            >
              P
            </span>
            SmartPark AI
          </div>

          <h1
            class="mt-16 max-w-lg text-5xl font-bold leading-tight"
          >
            Your intelligent parking journey starts here.
          </h1>

          <p
            class="mt-6 max-w-md text-lg leading-8 text-emerald-50"
          >
            Create one account for AI predictions,
            reservations, digital wallet payments,
            notifications and parking history.
          </p>
        </div>

        <p
          class="max-w-md text-sm leading-6 text-emerald-50"
        >
          Built around real-time parking operations
          and machine-learning assisted decision support.
        </p>
      </section>

      <section
        class="flex items-center justify-center p-6 sm:p-12"
      >
        <div class="w-full max-w-md">
          <RouterLink
            to="/"
            class="text-sm font-semibold text-emerald-600 hover:text-emerald-700"
          >
            ← Back to SmartPark
          </RouterLink>

          <div class="mt-8">
            <p
              class="text-sm font-semibold uppercase tracking-[0.2em] text-emerald-600"
            >
              Get started
            </p>

            <h2
              class="mt-3 text-3xl font-bold tracking-tight text-slate-900"
            >
              Create your SmartPark account
            </h2>
          </div>

          <form
            class="mt-8 space-y-4"
            @submit.prevent="
              submitRegistration
            "
          >
            <div>
              <label
                for="full-name"
                class="mb-2 block text-sm font-semibold text-slate-700"
              >
                Full name
              </label>

              <input
                id="full-name"
                v-model="fullName"
                type="text"
                autocomplete="name"
                minlength="2"
                maxlength="120"
                required
                placeholder="Your full name"
                class="w-full rounded-xl border border-slate-200 px-4 py-3 outline-none transition focus:border-emerald-500 focus:ring-4 focus:ring-emerald-100"
              >
            </div>

            <div>
              <label
                for="register-email"
                class="mb-2 block text-sm font-semibold text-slate-700"
              >
                Email address
              </label>

              <input
                id="register-email"
                v-model="email"
                type="email"
                autocomplete="email"
                required
                placeholder="you@example.com"
                class="w-full rounded-xl border border-slate-200 px-4 py-3 outline-none transition focus:border-emerald-500 focus:ring-4 focus:ring-emerald-100"
              >
            </div>

            <div>
              <label
                for="register-password"
                class="mb-2 block text-sm font-semibold text-slate-700"
              >
                Password
              </label>

              <div class="relative">
                <input
                  id="register-password"
                  v-model="password"
                  :type="
                    showPassword
                      ? 'text'
                      : 'password'
                  "
                  minlength="8"
                  maxlength="128"
                  autocomplete="new-password"
                  required
                  placeholder="Minimum 8 characters"
                  class="w-full rounded-xl border border-slate-200 px-4 py-3 pr-20 outline-none transition focus:border-emerald-500 focus:ring-4 focus:ring-emerald-100"
                >

                <button
                  type="button"
                  class="absolute inset-y-0 right-3 text-sm font-semibold text-slate-500 hover:text-slate-800"
                  @click="
                    showPassword =
                      !showPassword
                  "
                >
                  {{
                    showPassword
                      ? 'Hide'
                      : 'Show'
                  }}
                </button>
              </div>
            </div>

            <div>
              <label
                for="confirm-password"
                class="mb-2 block text-sm font-semibold text-slate-700"
              >
                Confirm password
              </label>

              <input
                id="confirm-password"
                v-model="confirmPassword"
                :type="
                  showPassword
                    ? 'text'
                    : 'password'
                "
                autocomplete="new-password"
                required
                placeholder="Repeat your password"
                class="w-full rounded-xl border border-slate-200 px-4 py-3 outline-none transition focus:border-emerald-500 focus:ring-4 focus:ring-emerald-100"
              >
            </div>

            <div
              v-if="errorMessage"
              class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
            >
              {{ errorMessage }}
            </div>

            <button
              type="submit"
              :disabled="auth.state.loading"
              class="mt-2 flex w-full items-center justify-center rounded-xl bg-emerald-600 px-5 py-3.5 font-semibold text-white shadow-lg shadow-emerald-600/20 transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {{
                auth.state.loading
                  ? 'Creating account...'
                  : 'Create account'
              }}
            </button>
          </form>

          <p
            class="mt-7 text-center text-sm text-slate-500"
          >
            Already have an account?

            <RouterLink
              to="/login"
              class="font-semibold text-emerald-600 hover:text-emerald-700"
            >
              Sign in
            </RouterLink>
          </p>
        </div>
      </section>
    </div>
  </main>
</template>
