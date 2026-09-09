<script setup>
import {
  computed,
  onMounted,
  ref,
} from 'vue'

import {
  MessageSquareText,
  RefreshCw,
  Search,
  ShieldCheck,
  Star,
  Trash2,
  X,
} from '@lucide/vue'

import AppShell from '../components/AppShell.vue'
import api from '../services/api'

const reviews = ref([])
const loading = ref(true)
const errorMessage = ref('')
const successMessage = ref('')

const searchQuery = ref('')
const ratingFilter = ref('all')
const locationFilter = ref('all')

const selectedReview = ref(null)
const deleteModalOpen = ref(false)
const deleteLoading = ref(false)

const totalReviews = computed(
  () => reviews.value.length
)

const averageRating = computed(() => {
  if (!reviews.value.length) {
    return 0
  }

  const total =
    reviews.value.reduce(
      (sum, review) =>
        sum + Number(review.rating),
      0
    )

  return (
    total /
    reviews.value.length
  ).toFixed(1)
})

const fiveStarReviews = computed(
  () =>
    reviews.value.filter(
      (review) =>
        review.rating === 5
    ).length
)

const reviewedLocations = computed(
  () =>
    new Set(
      reviews.value.map(
        (review) =>
          review.parking_location_id
      )
    ).size
)

const locations = computed(() => {
  return [
    ...new Set(
      reviews.value.map(
        (review) =>
          review.parking_location_name
      )
    ),
  ].sort()
})

const filteredReviews = computed(() => {
  const query =
    searchQuery.value
      .trim()
      .toLowerCase()

  return reviews.value.filter(
    (review) => {
      const matchesSearch =
        !query ||
        review.user_name
          ?.toLowerCase()
          .includes(query) ||
        review.user_email
          ?.toLowerCase()
          .includes(query) ||
        review.parking_location_name
          ?.toLowerCase()
          .includes(query) ||
        review.comment
          ?.toLowerCase()
          .includes(query)

      const matchesRating =
        ratingFilter.value === 'all' ||
        review.rating ===
          Number(ratingFilter.value)

      const matchesLocation =
        locationFilter.value === 'all' ||
        review.parking_location_name ===
          locationFilter.value

      return (
        matchesSearch &&
        matchesRating &&
        matchesLocation
      )
    }
  )
})

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

async function loadReviews() {
  loading.value = true
  errorMessage.value = ''

  try {
    const response =
      await api.get(
        '/api/admin/reviews'
      )

    reviews.value =
      response.data
  } catch (error) {
    errorMessage.value =
      error.response?.data?.detail ||
      'Unable to load reviews.'
  } finally {
    loading.value = false
  }
}

function openDeleteModal(review) {
  selectedReview.value = review
  deleteModalOpen.value = true
  errorMessage.value = ''
  successMessage.value = ''
}

function closeDeleteModal() {
  if (deleteLoading.value) {
    return
  }

  selectedReview.value = null
  deleteModalOpen.value = false
}

async function confirmDelete() {
  if (!selectedReview.value) {
    return
  }

  deleteLoading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    const reviewId =
      selectedReview.value.id

    await api.delete(
      `/api/admin/reviews/${reviewId}`
    )

    reviews.value =
      reviews.value.filter(
        (review) =>
          review.id !== reviewId
      )

    successMessage.value =
      'Review removed successfully.'

    selectedReview.value = null
    deleteModalOpen.value = false
  } catch (error) {
    errorMessage.value =
      error.response?.data?.detail ||
      'Unable to remove review.'
  } finally {
    deleteLoading.value = false
  }
}

onMounted(
  loadReviews
)
</script>

<template>
  <AppShell>
    <main
      class="mx-auto w-full max-w-7xl px-4 py-8 sm:px-6 lg:px-8"
    >
      <section
        class="overflow-hidden rounded-3xl bg-slate-950 px-6 py-8 text-white shadow-xl sm:px-8"
      >
        <div
          class="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between"
        >
          <div>
            <div
              class="mb-4 inline-flex items-center gap-2 rounded-full bg-emerald-400/10 px-3 py-1 text-xs font-bold uppercase tracking-[0.18em] text-emerald-300 ring-1 ring-inset ring-emerald-400/20"
            >
              <ShieldCheck :size="15" />
              Review Moderation
            </div>

            <h1
              class="text-3xl font-black tracking-tight sm:text-4xl"
            >
              Reviews Management
            </h1>

            <p
              class="mt-3 max-w-2xl text-sm leading-6 text-slate-300 sm:text-base"
            >
              Monitor customer ratings and feedback across
              SmartPark parking locations.
            </p>
          </div>

          <button
            type="button"
            class="inline-flex items-center justify-center gap-2 rounded-xl bg-white px-4 py-3 text-sm font-bold text-slate-950 transition hover:bg-emerald-50 disabled:opacity-60"
            :disabled="loading"
            @click="loadReviews"
          >
            <RefreshCw
              :size="17"
              :class="
                loading
                  ? 'animate-spin'
                  : ''
              "
            />

            Refresh reviews
          </button>
        </div>
      </section>

      <div
        v-if="successMessage"
        class="mt-6 rounded-2xl border border-emerald-200 bg-emerald-50 p-4 text-sm font-semibold text-emerald-800"
      >
        {{ successMessage }}
      </div>

      <div
        v-if="errorMessage"
        class="mt-6 rounded-2xl border border-rose-200 bg-rose-50 p-4 text-sm font-semibold text-rose-700"
      >
        {{ errorMessage }}
      </div>

      <section
        class="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4"
      >
        <article
          class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
        >
          <p class="text-sm font-semibold text-slate-500">
            Total Reviews
          </p>

          <p class="mt-2 text-3xl font-black text-slate-950">
            {{ totalReviews }}
          </p>

          <MessageSquareText
            class="mt-3 text-slate-400"
            :size="20"
          />
        </article>

        <article
          class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
        >
          <p class="text-sm font-semibold text-slate-500">
            Average Rating
          </p>

          <p class="mt-2 text-3xl font-black text-amber-600">
            {{ averageRating }}
          </p>

          <p class="mt-3 text-xs text-slate-500">
            Out of 5.0
          </p>
        </article>

        <article
          class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
        >
          <p class="text-sm font-semibold text-slate-500">
            Five-Star Reviews
          </p>

          <p class="mt-2 text-3xl font-black text-emerald-700">
            {{ fiveStarReviews }}
          </p>

          <Star
            class="mt-3 text-amber-500"
            :size="20"
          />
        </article>

        <article
          class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
        >
          <p class="text-sm font-semibold text-slate-500">
            Reviewed Locations
          </p>

          <p class="mt-2 text-3xl font-black text-violet-700">
            {{ reviewedLocations }}
          </p>

          <p class="mt-3 text-xs text-slate-500">
            Locations with feedback
          </p>
        </article>
      </section>

      <section
        class="mt-6 overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm"
      >
        <div
          class="border-b border-slate-200 p-5 sm:p-6"
        >
          <div
            class="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between"
          >
            <div>
              <h2
                class="text-xl font-black text-slate-950"
              >
                Customer Reviews
              </h2>

              <p
                class="mt-1 text-sm text-slate-500"
              >
                {{ filteredReviews.length }}
                review{{ filteredReviews.length === 1 ? '' : 's' }}
                shown
              </p>
            </div>

            <div
              class="grid gap-3 sm:grid-cols-3"
            >
              <label class="relative">
                <Search
                  class="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
                  :size="17"
                />

                <input
                  v-model="searchQuery"
                  type="search"
                  placeholder="Search reviews..."
                  class="w-full rounded-xl border border-slate-200 py-2.5 pl-10 pr-3 text-sm font-medium outline-none focus:border-emerald-500"
                />
              </label>

              <select
                v-model="ratingFilter"
                class="rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm font-semibold text-slate-700 outline-none"
              >
                <option value="all">
                  All ratings
                </option>

                <option value="5">
                  5 stars
                </option>

                <option value="4">
                  4 stars
                </option>

                <option value="3">
                  3 stars
                </option>

                <option value="2">
                  2 stars
                </option>

                <option value="1">
                  1 star
                </option>
              </select>

              <select
                v-model="locationFilter"
                class="rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm font-semibold text-slate-700 outline-none"
              >
                <option value="all">
                  All locations
                </option>

                <option
                  v-for="location in locations"
                  :key="location"
                  :value="location"
                >
                  {{ location }}
                </option>
              </select>
            </div>
          </div>
        </div>

        <div
          v-if="loading"
          class="flex min-h-72 items-center justify-center"
        >
          <RefreshCw
            class="animate-spin text-emerald-600"
            :size="28"
          />
        </div>

        <div
          v-else-if="filteredReviews.length === 0"
          class="flex min-h-72 items-center justify-center p-8 text-center"
        >
          <div>
            <MessageSquareText
              class="mx-auto text-slate-300"
              :size="40"
            />

            <p
              class="mt-3 font-bold text-slate-700"
            >
              No matching reviews
            </p>
          </div>
        </div>

        <div
          v-else
          class="divide-y divide-slate-100"
        >
          <article
            v-for="review in filteredReviews"
            :key="review.id"
            class="p-6"
          >
            <div
              class="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between"
            >
              <div class="min-w-0 flex-1">
                <div
                  class="flex flex-wrap items-center gap-3"
                >
                  <p
                    class="font-black text-slate-900"
                  >
                    {{ review.user_name }}
                  </p>

                  <span
                    class="text-sm text-slate-500"
                  >
                    {{ review.user_email }}
                  </span>
                </div>

                <p
                  class="mt-2 text-sm font-semibold text-emerald-700"
                >
                  {{ review.parking_location_name }}
                </p>

                <div
                  class="mt-4 flex items-center gap-1"
                >
                  <Star
                    v-for="number in 5"
                    :key="number"
                    :size="18"
                    :class="
                      number <= review.rating
                        ? 'fill-amber-400 text-amber-400'
                        : 'text-slate-300'
                    "
                  />

                  <span
                    class="ml-2 text-sm font-bold text-slate-700"
                  >
                    {{ review.rating }}/5
                  </span>
                </div>

                <p
                  class="mt-4 max-w-3xl text-sm leading-6 text-slate-600"
                >
                  {{
                    review.comment ||
                    'No written comment provided.'
                  }}
                </p>

                <p
                  class="mt-4 text-xs text-slate-400"
                >
                  Submitted
                  {{ formatDate(review.created_at) }}
                </p>
              </div>

              <button
                type="button"
                class="inline-flex shrink-0 items-center justify-center gap-2 rounded-xl bg-rose-50 px-4 py-2.5 text-sm font-bold text-rose-700 transition hover:bg-rose-100"
                @click="openDeleteModal(review)"
              >
                <Trash2 :size="16" />
                Remove
              </button>
            </div>
          </article>
        </div>
      </section>
    </main>

    <Teleport to="body">
      <div
        v-if="deleteModalOpen"
        class="fixed inset-0 z-[100] flex items-center justify-center bg-slate-950/60 p-4 backdrop-blur-sm"
        @click.self="closeDeleteModal"
      >
        <div
          class="w-full max-w-md overflow-hidden rounded-3xl bg-white shadow-2xl"
        >
          <div
            class="flex items-start justify-between border-b border-slate-200 p-6"
          >
            <div>
              <div
                class="mb-3 flex h-11 w-11 items-center justify-center rounded-xl bg-rose-50 text-rose-700"
              >
                <Trash2 :size="20" />
              </div>

              <h3
                class="text-xl font-black text-slate-950"
              >
                Remove review
              </h3>
            </div>

            <button
              type="button"
              class="rounded-lg p-2 text-slate-400 hover:bg-slate-100"
              @click="closeDeleteModal"
            >
              <X :size="20" />
            </button>
          </div>

          <div
            v-if="selectedReview"
            class="p-6"
          >
            <p
              class="text-sm leading-6 text-slate-600"
            >
              This moderation action permanently removes
              the selected customer review.
            </p>

            <div
              class="mt-5 rounded-2xl bg-slate-50 p-4"
            >
              <p
                class="font-bold text-slate-900"
              >
                {{ selectedReview.user_name }}
              </p>

              <p
                class="mt-1 text-sm text-slate-500"
              >
                {{ selectedReview.parking_location_name }}
              </p>

              <p
                class="mt-3 text-sm text-slate-600"
              >
                {{ selectedReview.comment }}
              </p>
            </div>
          </div>

          <div
            class="flex gap-3 border-t border-slate-200 p-6"
          >
            <button
              type="button"
              class="flex-1 rounded-xl border border-slate-200 px-4 py-3 text-sm font-bold text-slate-700 hover:bg-slate-50"
              :disabled="deleteLoading"
              @click="closeDeleteModal"
            >
              Cancel
            </button>

            <button
              type="button"
              class="flex flex-1 items-center justify-center gap-2 rounded-xl bg-rose-600 px-4 py-3 text-sm font-bold text-white hover:bg-rose-700 disabled:opacity-60"
              :disabled="deleteLoading"
              @click="confirmDelete"
            >
              <RefreshCw
                v-if="deleteLoading"
                class="animate-spin"
                :size="16"
              />

              <Trash2
                v-else
                :size="16"
              />

              {{
                deleteLoading
                  ? 'Removing...'
                  : 'Confirm removal'
              }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </AppShell>
</template>
