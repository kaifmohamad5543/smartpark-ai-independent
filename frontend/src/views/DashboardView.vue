<script setup>
import {
  BrainCircuit,
  CarFront,
  MapPinned,
  Sparkles,
  WalletCards,
} from '@lucide/vue'

import AppShell from '../components/AppShell.vue'
import { auth } from '../stores/auth'

const cards = [
  {
    title: 'Available Parking',
    value: 'Live',
    detail: 'View nearby parking availability',
    icon: MapPinned,
  },
  {
    title: 'AI Prediction',
    value: 'Ready',
    detail: 'Predict future parking occupancy',
    icon: BrainCircuit,
  },
  {
    title: 'Reservations',
    value: 'Manage',
    detail: 'Book, check in and check out',
    icon: CarFront,
  },
  {
    title: 'Digital Wallet',
    value: 'Secure',
    detail: 'Manage parking payments',
    icon: WalletCards,
  },
]
</script>

<template>
  <AppShell>
    <section
      class="mx-auto max-w-7xl"
    >
      <div
        class="overflow-hidden rounded-3xl bg-slate-950 p-6 text-white shadow-xl sm:p-8 lg:p-10"
      >
        <div
          class="grid gap-8 lg:grid-cols-[1fr_auto] lg:items-center"
        >
          <div>
            <div
              class="inline-flex items-center gap-2 rounded-full bg-emerald-500/15 px-3 py-1.5 text-xs font-semibold text-emerald-300"
            >
              <Sparkles :size="15" />
              AI-powered parking intelligence
            </div>

            <h1
              class="mt-5 max-w-3xl text-3xl font-bold tracking-tight sm:text-4xl"
            >
              Welcome to your SmartPark
              dashboard,
              {{
                auth.state.user?.full_name
              }}.
            </h1>

            <p
              class="mt-4 max-w-2xl leading-7 text-slate-300"
            >
              Find suitable parking,
              analyse predicted occupancy
              and manage your complete
              parking journey from one
              intelligent platform.
            </p>
          </div>

          <div
            class="flex h-28 w-28 items-center justify-center rounded-3xl bg-emerald-500 text-4xl font-black text-slate-950 shadow-lg shadow-emerald-500/20"
          >
            AI
          </div>
        </div>
      </div>

      <div
        class="mt-8 grid gap-5 sm:grid-cols-2 xl:grid-cols-4"
      >
        <article
          v-for="card in cards"
          :key="card.title"
          class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:shadow-lg"
        >
          <div
            class="flex h-11 w-11 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600"
          >
            <component
              :is="card.icon"
              :size="22"
            />
          </div>

          <p
            class="mt-5 text-sm font-medium text-slate-500"
          >
            {{ card.title }}
          </p>

          <p
            class="mt-1 text-2xl font-bold text-slate-900"
          >
            {{ card.value }}
          </p>

          <p
            class="mt-2 text-sm leading-6 text-slate-500"
          >
            {{ card.detail }}
          </p>
        </article>
      </div>

      <div
        class="mt-8 grid gap-6 lg:grid-cols-3"
      >
        <section
          class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm lg:col-span-2"
        >
          <p
            class="text-sm font-semibold text-emerald-600"
          >
            Smart parking
          </p>

          <h2
            class="mt-2 text-xl font-bold text-slate-900"
          >
            Start your parking journey
          </h2>

          <p
            class="mt-2 max-w-xl text-sm leading-6 text-slate-500"
          >
            Search parking locations and
            compare current availability,
            predicted demand, distance,
            pricing and ratings.
          </p>

          <RouterLink
            to="/parking"
            class="mt-6 inline-flex rounded-xl bg-emerald-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-emerald-700"
          >
            Find parking
          </RouterLink>
        </section>

        <section
          class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
        >
          <p
            class="text-sm font-semibold text-slate-500"
          >
            Account status
          </p>

          <div class="mt-5 space-y-4">
            <div
              class="flex items-center justify-between"
            >
              <span
                class="text-sm text-slate-500"
              >
                Role
              </span>

              <span
                class="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold uppercase text-slate-700"
              >
                {{
                  auth.state.user?.role
                }}
              </span>
            </div>

            <div
              class="flex items-center justify-between"
            >
              <span
                class="text-sm text-slate-500"
              >
                Account
              </span>

              <span
                class="rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700"
              >
                {{
                  auth.state.user
                    ?.is_active
                    ? 'Active'
                    : 'Inactive'
                }}
              </span>
            </div>
          </div>
        </section>
      </div>
    </section>
  </AppShell>
</template>
