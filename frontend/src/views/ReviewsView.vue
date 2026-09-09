<script setup>
import {
  computed,
  onMounted,
  ref,
  watch,
} from 'vue'

import {
  CheckCircle2,
  ChevronDown,
  MessageSquareText,
  RefreshCw,
  Send,
  Sparkles,
  Star,
} from '@lucide/vue'

import AppShell from '../components/AppShell.vue'
import api from '../services/api'
import { auth } from '../stores/auth'

const locations = ref([])
const selectedLocationId = ref('')

const reviews = ref([])
const summary = ref(null)

const loadingLocations = ref(true)
const loadingReviews = ref(false)
const submitting = ref(false)

const errorMessage = ref('')
const successMessage = ref('')

const rating = ref(0)
const hoverRating = ref(0)
const comment = ref('')

const selectedLocation = computed(
  () =>
    locations.value.find(
      (location) =>
        location.id ===
        selectedLocationId.value
    ) || null
)

const currentUserReview = computed(
  () =>
    reviews.value.find(
      (review) =>
        review.user_id ===
        auth.state.user?.id
    ) || null
)

const canReview = computed(
  () =>
    Boolean(
      selectedLocationId.value &&
      !currentUserReview.value
    )
)

const ratingDistribution = computed(
  () => {
    const distribution = {
      5: 0,
      4: 0,
      3: 0,
      2: 0,
      1: 0,
    }

    for (
      const review of reviews.value
    ) {
      if (
        distribution[
          review.rating
        ] !== undefined
      ) {
        distribution[
          review.rating
        ] += 1
      }
    }

    return distribution
  }
)

function displayRating() {
  return (
    hoverRating.value ||
    rating.value
  )
}

function starFilled(index) {
  return (
    index <= displayRating()
  )
}

function reviewPercentage(stars) {
  if (!reviews.value.length) {
    return 0
  }

  return (
    ratingDistribution.value[
      stars
    ] /
    reviews.value.length
  ) * 100
}

function formatDate(value) {
  if (!value) {
    return '—'
  }

  return new Intl.DateTimeFormat(
    'en-GB',
    {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }
  ).format(
    new Date(value)
  )
}

function reviewerLabel(review) {
  if (
    review.user_id ===
    auth.state.user?.id
  ) {
    return 'Your review'
  }

  return `SmartPark user ${String(
    review.user_id
  ).slice(0, 6)}`
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

async function loadLocations() {
  loadingLocations.value = true
  errorMessage.value = ''

  try {
    const response =
      await api.get(
        '/api/parking/locations'
      )

    locations.value =
      response.data.filter(
        (location) =>
          location.is_active
      )

    if (
      !selectedLocationId.value &&
      locations.value.length
    ) {
      selectedLocationId.value =
        locations.value[0].id
    }
  } catch (error) {
    errorMessage.value =
      apiError(
        error,
        'Unable to load parking locations.'
      )
  } finally {
    loadingLocations.value = false
  }
}

async function loadReviews() {
  if (
    !selectedLocationId.value
  ) {
    reviews.value = []
    summary.value = null
    return
  }

  loadingReviews.value = true
  errorMessage.value = ''

  try {
    const [
      reviewsResponse,
      summaryResponse,
    ] = await Promise.all([
      api.get(
        `/api/reviews/location/${selectedLocationId.value}`
      ),

      api.get(
        `/api/reviews/location/${selectedLocationId.value}/summary`
      ),
    ])

    reviews.value =
      reviewsResponse.data

    summary.value =
      summaryResponse.data
  } catch (error) {
    errorMessage.value =
      apiError(
        error,
        'Unable to load reviews.'
      )
  } finally {
    loadingReviews.value = false
  }
}

function resetReviewForm() {
  rating.value = 0
  hoverRating.value = 0
  comment.value = ''
}

async function submitReview() {
  errorMessage.value = ''
  successMessage.value = ''

  if (!rating.value) {
    errorMessage.value =
      'Please select a rating from 1 to 5 stars.'
    return
  }

  if (
    !selectedLocationId.value
  ) {
    errorMessage.value =
      'Please select a parking location.'
    return
  }

  submitting.value = true

  try {
    await api.post(
      '/api/reviews',
      {
        parking_location_id:
          selectedLocationId.value,

        rating:
          rating.value,

        comment:
          comment.value.trim()
            ? comment.value.trim()
            : null,
      }
    )

    successMessage.value =
      'Thank you. Your parking review was submitted successfully.'

    resetReviewForm()

    await loadReviews()
  } catch (error) {
    errorMessage.value =
      apiError(
        error,
        'Unable to submit your review.'
      )
  } finally {
    submitting.value = false
  }
}

async function refreshReviews() {
  successMessage.value = ''
  await loadReviews()
}

watch(
  selectedLocationId,
  async () => {
    resetReviewForm()
    successMessage.value = ''
    await loadReviews()
  }
)

onMounted(
  loadLocations
)
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
          class="absolute -right-24 -top-24 h-80 w-80 rounded-full bg-amber-400/10 blur-3xl"
        />

        <div
          class="absolute bottom-0 left-1/3 h-64 w-64 rounded-full bg-emerald-500/10 blur-3xl"
        />

        <div
          class="relative flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between"
        >
          <div>
            <div
              class="inline-flex items-center gap-2 rounded-full border border-amber-300/20 bg-amber-300/10 px-3 py-1.5 text-xs font-bold text-amber-300"
            >
              <Sparkles :size="15" />
              Community parking feedback
            </div>

            <h1
              class="mt-5 text-3xl font-black tracking-tight sm:text-4xl"
            >
              Reviews & Ratings
            </h1>

            <p
              class="mt-3 max-w-3xl text-sm leading-7 text-slate-300"
            >
              Explore real SmartPark user
              feedback and share one review
              for each parking location.
            </p>
          </div>

          <div
            class="w-full max-w-md"
          >
            <label
              class="mb-2 block text-xs font-bold uppercase tracking-wider text-slate-400"
            >
              Parking location
            </label>

            <div
              class="relative"
            >
              <select
                v-model="
                  selectedLocationId
                "
                :disabled="
                  loadingLocations
                "
                class="w-full appearance-none rounded-2xl border border-white/10 bg-white/10 px-4 py-4 pr-11 font-bold text-white outline-none backdrop-blur focus:border-emerald-400"
              >
                <option
                  v-for="
                    location in locations
                  "
                  :key="location.id"
                  :value="location.id"
                  class="text-slate-900"
                >
                  {{ location.name }}
                </option>
              </select>

              <ChevronDown
                :size="18"
                class="pointer-events-none absolute right-4 top-1/2 -translate-y-1/2 text-slate-400"
              />
            </div>
          </div>
        </div>
      </div>

      <div
        v-if="successMessage"
        class="mt-6 flex items-start gap-3 rounded-2xl border border-emerald-200 bg-emerald-50 p-4 text-sm font-medium text-emerald-700"
      >
        <CheckCircle2
          :size="19"
          class="mt-0.5 shrink-0"
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
        v-if="
          loadingLocations ||
          loadingReviews
        "
        class="mt-7 rounded-3xl border border-slate-200 bg-white p-12 text-center shadow-sm"
      >
        <RefreshCw
          :size="28"
          class="mx-auto animate-spin text-emerald-600"
        />

        <p
          class="mt-4 font-bold text-slate-800"
        >
          Loading parking reviews...
        </p>
      </div>

      <template v-else>
        <div
          class="mt-7 grid gap-6 lg:grid-cols-[0.8fr_1.2fr]"
        >
          <!-- Rating summary -->
          <section
            class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm"
          >
            <div>
              <p
                class="text-xs font-bold uppercase tracking-wider text-amber-600"
              >
                Rating summary
              </p>

              <h2
                class="mt-1 text-xl font-black text-slate-900"
              >
                {{
                  selectedLocation
                    ?.name
                }}
              </h2>
            </div>

            <div
              class="mt-7 flex items-end gap-4"
            >
              <p
                class="text-6xl font-black tracking-tight text-slate-950"
              >
                {{
                  Number(
                    summary
                      ?.average_rating ||
                    0
                  ).toFixed(1)
                }}
              </p>

              <div
                class="pb-1"
              >
                <div
                  class="flex gap-1"
                >
                  <Star
                    v-for="
                      index in 5
                    "
                    :key="index"
                    :size="20"
                    :fill="
                      index <=
                      Math.round(
                        summary
                          ?.average_rating ||
                        0
                      )
                        ? 'currentColor'
                        : 'none'
                    "
                    :class="
                      index <=
                      Math.round(
                        summary
                          ?.average_rating ||
                        0
                      )
                        ? 'text-amber-400'
                        : 'text-slate-300'
                    "
                  />
                </div>

                <p
                  class="mt-2 text-sm text-slate-500"
                >
                  {{
                    summary
                      ?.review_count ||
                    0
                  }}
                  {{
                    summary?.review_count ===
                    1
                      ? 'review'
                      : 'reviews'
                  }}
                </p>
              </div>
            </div>

            <div
              class="mt-8 space-y-3"
            >
              <div
                v-for="
                  stars in [
                    5,
                    4,
                    3,
                    2,
                    1,
                  ]
                "
                :key="stars"
                class="grid grid-cols-[42px_1fr_30px] items-center gap-3"
              >
                <div
                  class="flex items-center gap-1 text-sm font-bold text-slate-700"
                >
                  {{ stars }}
                  <Star
                    :size="13"
                    fill="currentColor"
                    class="text-amber-400"
                  />
                </div>

                <div
                  class="h-2.5 overflow-hidden rounded-full bg-slate-100"
                >
                  <div
                    class="h-full rounded-full bg-amber-400 transition-all"
                    :style="{
                      width:
                        `${reviewPercentage(
                          stars
                        )}%`,
                    }"
                  />
                </div>

                <span
                  class="text-right text-xs font-semibold text-slate-500"
                >
                  {{
                    ratingDistribution[
                      stars
                    ]
                  }}
                </span>
              </div>
            </div>

            <div
              v-if="selectedLocation"
              class="mt-7 rounded-2xl bg-slate-50 p-4"
            >
              <p
                class="text-xs font-bold uppercase tracking-wide text-slate-400"
              >
                Parking information
              </p>

              <p
                class="mt-2 font-bold text-slate-800"
              >
                {{
                  selectedLocation.address
                }}
              </p>

              <p
                class="mt-1 text-sm text-slate-500"
              >
                {{
                  selectedLocation.city
                }}
                {{
                  selectedLocation.postcode
                }}
              </p>

              <p
                class="mt-3 text-sm font-semibold text-emerald-700"
              >
                £{{
                  Number(
                    selectedLocation
                      .hourly_rate
                  ).toFixed(2)
                }}
                per hour
              </p>
            </div>
          </section>

          <!-- Review form -->
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
                  Your experience
                </p>

                <h2
                  class="mt-1 text-xl font-black text-slate-900"
                >
                  Rate this parking location
                </h2>
              </div>

              <MessageSquareText
                :size="23"
                class="text-slate-400"
              />
            </div>

            <div
              v-if="
                currentUserReview
              "
              class="mt-6 rounded-2xl border border-emerald-200 bg-emerald-50 p-5"
            >
              <div
                class="flex items-center gap-2 text-emerald-700"
              >
                <CheckCircle2
                  :size="19"
                />

                <p
                  class="font-black"
                >
                  You already reviewed this location
                </p>
              </div>

              <div
                class="mt-4 flex gap-1"
              >
                <Star
                  v-for="
                    index in 5
                  "
                  :key="index"
                  :size="21"
                  :fill="
                    index <=
                    currentUserReview.rating
                      ? 'currentColor'
                      : 'none'
                  "
                  :class="
                    index <=
                    currentUserReview.rating
                      ? 'text-amber-400'
                      : 'text-slate-300'
                  "
                />
              </div>

              <p
                v-if="
                  currentUserReview.comment
                "
                class="mt-4 text-sm leading-6 text-slate-700"
              >
                {{
                  currentUserReview.comment
                }}
              </p>

              <p
                class="mt-3 text-xs text-slate-500"
              >
                {{
                  formatDate(
                    currentUserReview
                      .created_at
                  )
                }}
              </p>

              <p
                class="mt-4 text-xs font-medium text-emerald-700"
              >
                SmartPark allows one
                review per user for each
                parking location.
              </p>
            </div>

            <form
              v-else-if="canReview"
              class="mt-7 space-y-6"
              @submit.prevent="
                submitReview
              "
            >
              <div>
                <label
                  class="block text-sm font-bold text-slate-700"
                >
                  Your rating
                </label>

                <div
                  class="mt-3 flex flex-wrap items-center gap-2"
                  @mouseleave="
                    hoverRating = 0
                  "
                >
                  <button
                    v-for="
                      index in 5
                    "
                    :key="index"
                    type="button"
                    class="rounded-xl p-1 transition hover:scale-110"
                    @mouseenter="
                      hoverRating =
                        index
                    "
                    @focus="
                      hoverRating =
                        index
                    "
                    @blur="
                      hoverRating = 0
                    "
                    @click="
                      rating = index
                    "
                  >
                    <Star
                      :size="36"
                      :fill="
                        starFilled(
                          index
                        )
                          ? 'currentColor'
                          : 'none'
                      "
                      :class="
                        starFilled(
                          index
                        )
                          ? 'text-amber-400'
                          : 'text-slate-300'
                      "
                    />
                  </button>

                  <span
                    v-if="
                      displayRating()
                    "
                    class="ml-2 rounded-full bg-amber-50 px-3 py-1.5 text-sm font-bold text-amber-700"
                  >
                    {{
                      displayRating()
                    }}
                    / 5
                  </span>
                </div>
              </div>

              <div>
                <div
                  class="mb-2 flex items-center justify-between"
                >
                  <label
                    class="text-sm font-bold text-slate-700"
                  >
                    Comment
                  </label>

                  <span
                    class="text-xs text-slate-400"
                  >
                    {{
                      comment.length
                    }}
                    / 1000
                  </span>
                </div>

                <textarea
                  v-model="comment"
                  maxlength="1000"
                  rows="6"
                  placeholder="Share your experience with availability, access, location or overall parking quality..."
                  class="w-full resize-none rounded-2xl border border-slate-200 px-4 py-4 text-slate-800 outline-none transition placeholder:text-slate-400 focus:border-emerald-500 focus:ring-4 focus:ring-emerald-100"
                />
              </div>

              <button
                type="submit"
                :disabled="
                  submitting ||
                  !rating
                "
                class="flex w-full items-center justify-center gap-2 rounded-2xl bg-emerald-600 px-5 py-4 font-black text-white shadow-lg shadow-emerald-600/15 transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-50"
              >
                <Send
                  :size="18"
                />

                {{
                  submitting
                    ? 'Submitting review...'
                    : 'Submit parking review'
                }}
              </button>
            </form>
          </section>
        </div>

        <!-- Reviews list -->
        <section
          class="mt-7 overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm"
        >
          <div
            class="flex flex-col gap-4 border-b border-slate-200 p-6 sm:flex-row sm:items-center sm:justify-between"
          >
            <div>
              <p
                class="text-xs font-bold uppercase tracking-wider text-violet-600"
              >
                Community feedback
              </p>

              <h2
                class="mt-1 text-xl font-black text-slate-900"
              >
                Recent Reviews
              </h2>
            </div>

            <button
              class="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 px-4 py-3 text-sm font-bold text-slate-700 transition hover:bg-slate-50"
              @click="
                refreshReviews
              "
            >
              <RefreshCw
                :size="16"
              />
              Refresh
            </button>
          </div>

          <div
            v-if="
              reviews.length
            "
            class="divide-y divide-slate-100"
          >
            <article
              v-for="
                review in reviews
              "
              :key="review.id"
              class="p-6"
            >
              <div
                class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between"
              >
                <div>
                  <p
                    class="font-black text-slate-900"
                  >
                    {{
                      reviewerLabel(
                        review
                      )
                    }}
                  </p>

                  <p
                    class="mt-1 text-xs text-slate-400"
                  >
                    {{
                      formatDate(
                        review.created_at
                      )
                    }}
                  </p>
                </div>

                <div
                  class="flex gap-1"
                >
                  <Star
                    v-for="
                      index in 5
                    "
                    :key="index"
                    :size="18"
                    :fill="
                      index <=
                      review.rating
                        ? 'currentColor'
                        : 'none'
                    "
                    :class="
                      index <=
                      review.rating
                        ? 'text-amber-400'
                        : 'text-slate-300'
                    "
                  />
                </div>
              </div>

              <p
                v-if="
                  review.comment
                "
                class="mt-4 max-w-4xl text-sm leading-7 text-slate-600"
              >
                {{ review.comment }}
              </p>

              <p
                v-else
                class="mt-4 text-sm italic text-slate-400"
              >
                No written comment provided.
              </p>
            </article>
          </div>

          <div
            v-else
            class="p-14 text-center"
          >
            <MessageSquareText
              :size="38"
              class="mx-auto text-slate-300"
            />

            <h3
              class="mt-4 font-black text-slate-800"
            >
              No reviews yet
            </h3>

            <p
              class="mt-2 text-sm text-slate-500"
            >
              Be the first SmartPark user
              to review this parking
              location.
            </p>
          </div>
        </section>
      </template>
    </section>
  </AppShell>
</template>
