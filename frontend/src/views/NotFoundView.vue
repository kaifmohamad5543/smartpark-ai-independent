<script setup>
import {
  ArrowLeft,
  Home,
  MapPinned,
} from '@lucide/vue'

import {
  RouterLink,
  useRouter,
} from 'vue-router'

const router = useRouter()

function goBack() {
  if (
    window.history.length > 1
  ) {
    router.back()
    return
  }

  router.push('/')
}
</script>

<template>
  <main
    class="flex min-h-screen items-center justify-center bg-slate-950 px-6 py-12"
  >
    <section
      class="w-full max-w-2xl text-center"
    >
      <div
        class="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-emerald-400 text-slate-950 shadow-lg shadow-emerald-500/20"
      >
        <MapPinned :size="30" />
      </div>

      <p
        class="mt-8 text-sm font-black uppercase tracking-[0.3em] text-emerald-400"
      >
        Error 404
      </p>

      <h1
        class="mt-4 text-5xl font-black tracking-tight text-white sm:text-6xl"
      >
        Parking space not found
      </h1>

      <p
        class="mx-auto mt-5 max-w-xl text-base leading-7 text-slate-400"
      >
        The SmartPark page you requested does not exist,
        may have moved, or the address may be incorrect.
      </p>

      <div
        class="mt-8 flex flex-col justify-center gap-3 sm:flex-row"
      >
        <RouterLink
          to="/"
          class="inline-flex items-center justify-center gap-2 rounded-xl bg-emerald-500 px-5 py-3 text-sm font-black text-slate-950 transition hover:bg-emerald-400"
        >
          <Home :size="17" />
          Return home
        </RouterLink>

        <button
          type="button"
          class="inline-flex items-center justify-center gap-2 rounded-xl border border-white/10 bg-white/5 px-5 py-3 text-sm font-bold text-white transition hover:bg-white/10"
          @click="goBack"
        >
          <ArrowLeft :size="17" />
          Go back
        </button>
      </div>

      <div
        class="mt-12 rounded-2xl border border-white/10 bg-white/[0.03] p-5 text-left"
      >
        <p
          class="text-sm font-bold text-white"
        >
          SmartPark AI
        </p>

        <p
          class="mt-2 text-sm leading-6 text-slate-500"
        >
          AI-powered parking demand prediction,
          reservation and intelligent parking recommendation.
        </p>
      </div>
    </section>
  </main>
</template>
