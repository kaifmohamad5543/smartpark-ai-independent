<script setup>
import {
  computed,
  onMounted,
  ref,
} from 'vue'

import {
  ArrowDownLeft,
  Banknote,
  CheckCircle2,
  CreditCard,
  RefreshCw,
  RotateCcw,
  Search,
  ShieldCheck,
  WalletCards,
  X,
} from '@lucide/vue'

import AppShell from '../components/AppShell.vue'
import api from '../services/api'

const payments = ref([])
const loading = ref(true)
const errorMessage = ref('')
const successMessage = ref('')

const searchQuery = ref('')
const statusFilter = ref('all')
const methodFilter = ref('all')

const selectedPayment = ref(null)
const refundModalOpen = ref(false)
const refundLoading = ref(false)

const totalPayments = computed(
  () => payments.value.length
)

const parkingCharges = computed(
  () =>
    payments.value.filter(
      (payment) =>
        payment.transaction_type ===
        'parking_charge'
    )
)

const refundTransactions = computed(
  () =>
    payments.value.filter(
      (payment) =>
        payment.transaction_type ===
        'refund'
    )
)

const refundablePayments = computed(
  () =>
    payments.value.filter(
      (payment) =>
        payment.is_refundable
    )
)

const totalCharged = computed(
  () =>
    parkingCharges.value.reduce(
      (total, payment) =>
        total + Number(payment.amount || 0),
      0
    )
)

const totalRefunded = computed(
  () =>
    refundTransactions.value.reduce(
      (total, payment) =>
        total + Number(payment.amount || 0),
      0
    )
)

const netPayments = computed(
  () =>
    totalCharged.value -
    totalRefunded.value
)

const filteredPayments = computed(() => {
  const query =
    searchQuery.value
      .trim()
      .toLowerCase()

  return payments.value.filter(
    (payment) => {
      const matchesSearch =
        !query ||
        payment.payment_reference
          ?.toLowerCase()
          .includes(query) ||
        payment.user_name
          ?.toLowerCase()
          .includes(query) ||
        payment.user_email
          ?.toLowerCase()
          .includes(query)

      const matchesStatus =
        statusFilter.value === 'all' ||
        payment.status ===
          statusFilter.value

      const matchesMethod =
        methodFilter.value === 'all' ||
        payment.payment_method ===
          methodFilter.value

      return (
        matchesSearch &&
        matchesStatus &&
        matchesMethod
      )
    }
  )
})

function money(value) {
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

function transactionLabel(value) {
  if (value === 'parking_charge') {
    return 'Parking charge'
  }

  if (value === 'refund') {
    return 'Refund'
  }

  return (
    value
      ?.replaceAll('_', ' ')
      ?.replace(
        /\b\w/g,
        (letter) =>
          letter.toUpperCase()
      ) ||
    'Unknown'
  )
}

function statusClasses(status) {
  if (status === 'paid') {
    return (
      'bg-emerald-50 ' +
      'text-emerald-700 ' +
      'ring-emerald-600/20'
    )
  }

  if (status === 'refunded') {
    return (
      'bg-amber-50 ' +
      'text-amber-700 ' +
      'ring-amber-600/20'
    )
  }

  return (
    'bg-slate-100 ' +
    'text-slate-700 ' +
    'ring-slate-600/20'
  )
}

async function loadPayments() {
  loading.value = true
  errorMessage.value = ''

  try {
    const response =
      await api.get(
        '/api/admin/payments'
      )

    payments.value =
      response.data
  } catch (error) {
    errorMessage.value =
      error.response?.data?.detail ||
      'Unable to load admin payments.'
  } finally {
    loading.value = false
  }
}

function openRefundModal(payment) {
  selectedPayment.value = payment
  refundModalOpen.value = true
  errorMessage.value = ''
  successMessage.value = ''
}

function closeRefundModal() {
  if (refundLoading.value) {
    return
  }

  refundModalOpen.value = false
  selectedPayment.value = null
}

async function confirmRefund() {
  if (
    !selectedPayment.value ||
    !selectedPayment.value.is_refundable
  ) {
    return
  }

  refundLoading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    const reference =
      selectedPayment.value
        .payment_reference

    await api.post(
      `/api/admin/payments/${selectedPayment.value.id}/refund`
    )

    refundModalOpen.value = false
    selectedPayment.value = null

    successMessage.value =
      `Payment ${reference} was refunded successfully.`

    await loadPayments()
  } catch (error) {
    errorMessage.value =
      error.response?.data?.detail ||
      'Unable to refund this payment.'
  } finally {
    refundLoading.value = false
  }
}

onMounted(
  loadPayments
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
              Admin Finance Control
            </div>

            <h1
              class="text-3xl font-black tracking-tight sm:text-4xl"
            >
              Payments & Refunds
            </h1>

            <p
              class="mt-3 max-w-2xl text-sm leading-6 text-slate-300 sm:text-base"
            >
              Review parking payments, monitor transaction status,
              and process eligible wallet refunds securely.
            </p>
          </div>

          <button
            type="button"
            class="inline-flex items-center justify-center gap-2 rounded-xl bg-white px-4 py-3 text-sm font-bold text-slate-950 transition hover:bg-emerald-50 disabled:cursor-not-allowed disabled:opacity-60"
            :disabled="loading"
            @click="loadPayments"
          >
            <RefreshCw
              :size="17"
              :class="
                loading
                  ? 'animate-spin'
                  : ''
              "
            />
            Refresh payments
          </button>
        </div>
      </section>

      <div
        v-if="successMessage"
        class="mt-6 flex items-start gap-3 rounded-2xl border border-emerald-200 bg-emerald-50 p-4 text-sm font-medium text-emerald-800"
      >
        <CheckCircle2
          class="mt-0.5 shrink-0"
          :size="19"
        />
        {{ successMessage }}
      </div>

      <div
        v-if="errorMessage"
        class="mt-6 rounded-2xl border border-rose-200 bg-rose-50 p-4 text-sm font-medium text-rose-700"
      >
        {{ errorMessage }}
      </div>

      <section
        class="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4"
      >
        <article
          class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
        >
          <div
            class="flex items-start justify-between"
          >
            <div>
              <p
                class="text-sm font-semibold text-slate-500"
              >
                Payment Records
              </p>

              <p
                class="mt-2 text-3xl font-black text-slate-950"
              >
                {{ totalPayments }}
              </p>
            </div>

            <div
              class="rounded-xl bg-slate-100 p-3 text-slate-700"
            >
              <CreditCard :size="21" />
            </div>
          </div>

          <p
            class="mt-4 text-xs text-slate-500"
          >
            All recorded payment transactions
          </p>
        </article>

        <article
          class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
        >
          <div
            class="flex items-start justify-between"
          >
            <div>
              <p
                class="text-sm font-semibold text-slate-500"
              >
                Parking Charges
              </p>

              <p
                class="mt-2 text-3xl font-black text-slate-950"
              >
                {{ money(totalCharged) }}
              </p>
            </div>

            <div
              class="rounded-xl bg-emerald-50 p-3 text-emerald-700"
            >
              <Banknote :size="21" />
            </div>
          </div>

          <p
            class="mt-4 text-xs text-slate-500"
          >
            Gross value of parking charges
          </p>
        </article>

        <article
          class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
        >
          <div
            class="flex items-start justify-between"
          >
            <div>
              <p
                class="text-sm font-semibold text-slate-500"
              >
                Refunds Issued
              </p>

              <p
                class="mt-2 text-3xl font-black text-slate-950"
              >
                {{ money(totalRefunded) }}
              </p>
            </div>

            <div
              class="rounded-xl bg-amber-50 p-3 text-amber-700"
            >
              <ArrowDownLeft :size="21" />
            </div>
          </div>

          <p
            class="mt-4 text-xs text-slate-500"
          >
            Net retained:
            <span
              class="font-bold text-slate-700"
            >
              {{ money(netPayments) }}
            </span>
          </p>
        </article>

        <article
          class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
        >
          <div
            class="flex items-start justify-between"
          >
            <div>
              <p
                class="text-sm font-semibold text-slate-500"
              >
                Refundable
              </p>

              <p
                class="mt-2 text-3xl font-black text-slate-950"
              >
                {{ refundablePayments.length }}
              </p>
            </div>

            <div
              class="rounded-xl bg-violet-50 p-3 text-violet-700"
            >
              <RotateCcw :size="21" />
            </div>
          </div>

          <p
            class="mt-4 text-xs text-slate-500"
          >
            Eligible wallet parking charges
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
                Transaction History
              </h2>

              <p
                class="mt-1 text-sm text-slate-500"
              >
                {{ filteredPayments.length }}
                transaction{{ filteredPayments.length === 1 ? '' : 's' }}
                shown
              </p>
            </div>

            <div
              class="grid gap-3 sm:grid-cols-3"
            >
              <label
                class="relative"
              >
                <Search
                  class="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
                  :size="17"
                />

                <input
                  v-model="searchQuery"
                  type="search"
                  placeholder="Search payments..."
                  class="w-full rounded-xl border border-slate-200 bg-white py-2.5 pl-10 pr-3 text-sm font-medium text-slate-800 outline-none transition focus:border-emerald-500 focus:ring-4 focus:ring-emerald-500/10"
                />
              </label>

              <select
                v-model="statusFilter"
                class="rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm font-semibold text-slate-700 outline-none focus:border-emerald-500"
              >
                <option value="all">
                  All statuses
                </option>
                <option value="paid">
                  Paid
                </option>
                <option value="refunded">
                  Refunded
                </option>
              </select>

              <select
                v-model="methodFilter"
                class="rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm font-semibold text-slate-700 outline-none focus:border-emerald-500"
              >
                <option value="all">
                  All methods
                </option>
                <option value="wallet">
                  Wallet
                </option>
                <option value="card">
                  Card
                </option>
              </select>
            </div>
          </div>
        </div>

        <div
          v-if="loading"
          class="flex min-h-72 items-center justify-center"
        >
          <div
            class="text-center"
          >
            <RefreshCw
              class="mx-auto animate-spin text-emerald-600"
              :size="28"
            />
            <p
              class="mt-3 text-sm font-semibold text-slate-500"
            >
              Loading payments...
            </p>
          </div>
        </div>

        <div
          v-else-if="filteredPayments.length === 0"
          class="flex min-h-72 items-center justify-center p-8 text-center"
        >
          <div>
            <CreditCard
              class="mx-auto text-slate-300"
              :size="36"
            />
            <p
              class="mt-3 font-bold text-slate-700"
            >
              No matching payments
            </p>
            <p
              class="mt-1 text-sm text-slate-500"
            >
              Try changing your search or filters.
            </p>
          </div>
        </div>

        <div
          v-else
          class="overflow-x-auto"
        >
          <table
            class="min-w-full divide-y divide-slate-200"
          >
            <thead
              class="bg-slate-50"
            >
              <tr
                class="text-left text-xs font-bold uppercase tracking-wider text-slate-500"
              >
                <th class="px-6 py-4">
                  Payment
                </th>
                <th class="px-6 py-4">
                  Customer
                </th>
                <th class="px-6 py-4">
                  Type
                </th>
                <th class="px-6 py-4">
                  Method
                </th>
                <th class="px-6 py-4">
                  Amount
                </th>
                <th class="px-6 py-4">
                  Status
                </th>
                <th class="px-6 py-4">
                  Date
                </th>
                <th class="px-6 py-4 text-right">
                  Action
                </th>
              </tr>
            </thead>

            <tbody
              class="divide-y divide-slate-100"
            >
              <tr
                v-for="payment in filteredPayments"
                :key="payment.id"
                class="transition hover:bg-slate-50/80"
              >
                <td
                  class="whitespace-nowrap px-6 py-4"
                >
                  <p
                    class="font-bold text-slate-900"
                  >
                    {{ payment.payment_reference }}
                  </p>

                  <p
                    class="mt-1 max-w-48 truncate text-xs text-slate-400"
                  >
                    {{ payment.id }}
                  </p>
                </td>

                <td
                  class="px-6 py-4"
                >
                  <p
                    class="font-semibold text-slate-800"
                  >
                    {{ payment.user_name }}
                  </p>

                  <p
                    class="mt-1 text-xs text-slate-500"
                  >
                    {{ payment.user_email }}
                  </p>
                </td>

                <td
                  class="whitespace-nowrap px-6 py-4 text-sm font-semibold text-slate-700"
                >
                  {{ transactionLabel(payment.transaction_type) }}
                </td>

                <td
                  class="whitespace-nowrap px-6 py-4"
                >
                  <div
                    class="inline-flex items-center gap-2 text-sm font-semibold text-slate-700"
                  >
                    <WalletCards
                      v-if="payment.payment_method === 'wallet'"
                      :size="16"
                    />
                    <CreditCard
                      v-else
                      :size="16"
                    />

                    {{
                      payment.payment_method
                        ?.charAt(0)
                        .toUpperCase() +
                      payment.payment_method
                        ?.slice(1)
                    }}
                  </div>
                </td>

                <td
                  class="whitespace-nowrap px-6 py-4 text-sm font-black text-slate-900"
                >
                  {{ money(payment.amount) }}
                </td>

                <td
                  class="whitespace-nowrap px-6 py-4"
                >
                  <span
                    class="inline-flex rounded-full px-2.5 py-1 text-xs font-bold capitalize ring-1 ring-inset"
                    :class="statusClasses(payment.status)"
                  >
                    {{ payment.status }}
                  </span>
                </td>

                <td
                  class="whitespace-nowrap px-6 py-4 text-sm text-slate-500"
                >
                  {{ formatDate(payment.created_at) }}
                </td>

                <td
                  class="whitespace-nowrap px-6 py-4 text-right"
                >
                  <button
                    v-if="payment.is_refundable"
                    type="button"
                    class="inline-flex items-center gap-2 rounded-lg bg-rose-50 px-3 py-2 text-xs font-bold text-rose-700 transition hover:bg-rose-100"
                    @click="openRefundModal(payment)"
                  >
                    <RotateCcw :size="14" />
                    Refund
                  </button>

                  <span
                    v-else
                    class="text-xs font-semibold text-slate-400"
                  >
                    Not eligible
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </main>

    <Teleport to="body">
      <div
        v-if="refundModalOpen"
        class="fixed inset-0 z-[100] flex items-center justify-center bg-slate-950/60 p-4 backdrop-blur-sm"
        @click.self="closeRefundModal"
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
                <RotateCcw :size="21" />
              </div>

              <h3
                class="text-xl font-black text-slate-950"
              >
                Confirm wallet refund
              </h3>

              <p
                class="mt-2 text-sm leading-6 text-slate-500"
              >
                This action will credit the customer's wallet and mark
                the original payment as refunded.
              </p>
            </div>

            <button
              type="button"
              class="rounded-lg p-2 text-slate-400 hover:bg-slate-100 hover:text-slate-700"
              @click="closeRefundModal"
            >
              <X :size="20" />
            </button>
          </div>

          <div
            v-if="selectedPayment"
            class="space-y-4 p-6"
          >
            <div
              class="rounded-2xl bg-slate-50 p-4"
            >
              <div
                class="flex justify-between gap-4"
              >
                <span
                  class="text-sm text-slate-500"
                >
                  Reference
                </span>
                <span
                  class="text-sm font-bold text-slate-900"
                >
                  {{ selectedPayment.payment_reference }}
                </span>
              </div>

              <div
                class="mt-3 flex justify-between gap-4"
              >
                <span
                  class="text-sm text-slate-500"
                >
                  Customer
                </span>
                <span
                  class="text-right text-sm font-bold text-slate-900"
                >
                  {{ selectedPayment.user_name }}
                </span>
              </div>

              <div
                class="mt-3 flex justify-between gap-4"
              >
                <span
                  class="text-sm text-slate-500"
                >
                  Refund amount
                </span>
                <span
                  class="text-lg font-black text-rose-700"
                >
                  {{ money(selectedPayment.amount) }}
                </span>
              </div>
            </div>

            <p
              class="text-xs leading-5 text-slate-500"
            >
              SmartPark records a separate refund transaction while
              preserving the original payment for audit history.
            </p>
          </div>

          <div
            class="flex gap-3 border-t border-slate-200 p-6"
          >
            <button
              type="button"
              class="flex-1 rounded-xl border border-slate-200 px-4 py-3 text-sm font-bold text-slate-700 transition hover:bg-slate-50"
              :disabled="refundLoading"
              @click="closeRefundModal"
            >
              Cancel
            </button>

            <button
              type="button"
              class="flex flex-1 items-center justify-center gap-2 rounded-xl bg-rose-600 px-4 py-3 text-sm font-bold text-white transition hover:bg-rose-700 disabled:cursor-not-allowed disabled:opacity-60"
              :disabled="refundLoading"
              @click="confirmRefund"
            >
              <RefreshCw
                v-if="refundLoading"
                class="animate-spin"
                :size="16"
              />

              <RotateCcw
                v-else
                :size="16"
              />

              {{
                refundLoading
                  ? 'Processing...'
                  : 'Confirm refund'
              }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </AppShell>
</template>
