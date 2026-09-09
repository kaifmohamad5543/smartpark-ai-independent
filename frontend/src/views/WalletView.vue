<script setup>
import {
  computed,
  onMounted,
  ref,
} from 'vue'

import {
  ArrowDownLeft,
  ArrowUpRight,
  Banknote,
  CheckCircle2,
  Clock3,
  CreditCard,
  History,
  Plus,
  RefreshCw,
  ShieldCheck,
  Sparkles,
  WalletCards,
} from '@lucide/vue'

import AppShell from '../components/AppShell.vue'
import api from '../services/api'

const wallet = ref(null)
const transactions = ref([])

const loading = ref(true)
const toppingUp = ref(false)

const errorMessage = ref('')
const successMessage = ref('')

const topUpAmount = ref(20)

const presets = [
  10,
  20,
  50,
  100,
]

const balance = computed(() =>
  Number(
    wallet.value?.balance ?? 0
  )
)

const totalCredits = computed(() =>
  transactions.value
    .filter(
      (item) =>
        item.direction === 'credit'
    )
    .reduce(
      (total, item) =>
        total +
        Number(item.amount),
      0
    )
)

const totalDebits = computed(() =>
  transactions.value
    .filter(
      (item) =>
        item.direction === 'debit'
    )
    .reduce(
      (total, item) =>
        total +
        Number(item.amount),
      0
    )
)

const recentTransactions = computed(
  () =>
    transactions.value.slice(0, 12)
)

function money(value) {
  return Number(
    value || 0
  ).toLocaleString(
    'en-GB',
    {
      style: 'currency',
      currency: 'GBP',
    }
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

function prettyType(value) {
  if (!value) {
    return 'Transaction'
  }

  return value
    .replaceAll('_', ' ')
    .replace(
      /\b\w/g,
      (letter) =>
        letter.toUpperCase()
    )
}

async function loadWallet() {
  loading.value = true
  errorMessage.value = ''

  try {
    const [
      walletResponse,
      transactionResponse,
    ] = await Promise.all([
      api.get('/api/wallet'),
      api.get(
        '/api/wallet/transactions'
      ),
    ])

    wallet.value =
      walletResponse.data

    transactions.value =
      transactionResponse.data
  } catch (error) {
    errorMessage.value =
      error.response?.data?.detail ||
      'Unable to load wallet information.'
  } finally {
    loading.value = false
  }
}

async function topUp() {
  errorMessage.value = ''
  successMessage.value = ''

  const amount =
    Number(topUpAmount.value)

  if (
    !Number.isFinite(amount) ||
    amount <= 0
  ) {
    errorMessage.value =
      'Enter a valid top-up amount.'
    return
  }

  if (amount > 1000) {
    errorMessage.value =
      'Maximum top-up amount is £1,000.'
    return
  }

  toppingUp.value = true

  try {
    const response =
      await api.post(
        '/api/wallet/top-up',
        {
          amount:
            amount.toFixed(2),
        }
      )

    wallet.value =
      response.data.wallet

    transactions.value = [
      response.data.transaction,
      ...transactions.value.filter(
        (item) =>
          item.id !==
          response.data
            .transaction.id
      ),
    ]

    successMessage.value =
      `${money(amount)} added to your SmartPark wallet.`

    topUpAmount.value = 20
  } catch (error) {
    errorMessage.value =
      error.response?.data?.detail ||
      'Unable to top up wallet.'
  } finally {
    toppingUp.value = false
  }
}

onMounted(loadWallet)
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
          class="absolute -right-16 -top-24 h-72 w-72 rounded-full bg-emerald-500/20 blur-3xl"
        />

        <div
          class="absolute bottom-0 left-1/3 h-44 w-44 rounded-full bg-cyan-400/10 blur-3xl"
        />

        <div
          class="relative grid gap-8 lg:grid-cols-[1fr_auto] lg:items-center"
        >
          <div>
            <div
              class="inline-flex items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1.5 text-xs font-semibold text-emerald-300"
            >
              <ShieldCheck
                :size="15"
              />
              Secure digital wallet
            </div>

            <h1
              class="mt-5 text-3xl font-black tracking-tight sm:text-4xl"
            >
              SmartPark Wallet
            </h1>

            <p
              class="mt-3 max-w-xl text-sm leading-7 text-slate-300"
            >
              Add funds, track parking
              payments and manage your
              SmartPark transaction
              history in one place.
            </p>
          </div>

          <div
            class="min-w-[260px] rounded-3xl border border-white/10 bg-white/5 p-6 backdrop-blur"
          >
            <div
              class="flex items-center justify-between"
            >
              <p
                class="text-sm text-slate-400"
              >
                Available balance
              </p>

              <WalletCards
                :size="22"
                class="text-emerald-400"
              />
            </div>

            <p
              class="mt-3 text-4xl font-black tracking-tight"
            >
              {{ money(balance) }}
            </p>

            <p
              class="mt-2 text-xs text-slate-400"
            >
              Ready for wallet-enabled
              parking checkout
            </p>
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
        class="mt-7 grid gap-6 xl:grid-cols-[0.8fr_1.2fr]"
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
              <Plus :size="22" />
            </div>

            <div>
              <h2
                class="font-bold text-slate-900"
              >
                Add wallet funds
              </h2>

              <p
                class="text-xs text-slate-500"
              >
                Prototype digital top-up
              </p>
            </div>
          </div>

          <div
            class="mt-6 grid grid-cols-4 gap-2"
          >
            <button
              v-for="amount in presets"
              :key="amount"
              type="button"
              class="rounded-xl border px-3 py-3 text-sm font-bold transition"
              :class="
                Number(topUpAmount) ===
                amount
                  ? 'border-emerald-500 bg-emerald-50 text-emerald-700'
                  : 'border-slate-200 text-slate-600 hover:bg-slate-50'
              "
              @click="
                topUpAmount = amount
              "
            >
              £{{ amount }}
            </button>
          </div>

          <div class="mt-5">
            <label
              class="mb-2 block text-sm font-semibold text-slate-700"
            >
              Custom amount
            </label>

            <div class="relative">
              <span
                class="absolute left-4 top-1/2 -translate-y-1/2 font-bold text-slate-500"
              >
                £
              </span>

              <input
                v-model.number="
                  topUpAmount
                "
                type="number"
                min="0.01"
                max="1000"
                step="0.01"
                class="w-full rounded-xl border border-slate-200 py-3.5 pl-9 pr-4 text-lg font-bold outline-none transition focus:border-emerald-500 focus:ring-4 focus:ring-emerald-100"
              >
            </div>

            <p
              class="mt-2 text-xs text-slate-400"
            >
              Maximum top-up:
              £1,000.00
            </p>
          </div>

          <button
            class="mt-6 flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 px-5 py-4 font-bold text-white shadow-lg shadow-emerald-600/20 transition hover:-translate-y-0.5 disabled:opacity-50"
            :disabled="toppingUp"
            @click="topUp"
          >
            <CreditCard
              :size="19"
            />

            {{
              toppingUp
                ? 'Adding funds...'
                : `Add ${money(topUpAmount)}`
            }}
          </button>

          <div
            class="mt-6 rounded-2xl bg-slate-50 p-4"
          >
            <div
              class="flex items-center gap-2"
            >
              <Sparkles
                :size="17"
                class="text-emerald-600"
              />

              <p
                class="text-sm font-bold text-slate-800"
              >
                Wallet checkout
              </p>
            </div>

            <p
              class="mt-2 text-xs leading-5 text-slate-500"
            >
              Wallet funds can be selected
              as the payment method when
              completing an active parking
              session.
            </p>
          </div>
        </section>

        <section
          class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm"
        >
          <div
            class="flex items-center justify-between gap-4"
          >
            <div
              class="flex items-center gap-3"
            >
              <div
                class="flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-100 text-slate-700"
              >
                <Banknote
                  :size="22"
                />
              </div>

              <div>
                <h2
                  class="font-bold text-slate-900"
                >
                  Wallet overview
                </h2>

                <p
                  class="text-xs text-slate-500"
                >
                  Current financial activity
                </p>
              </div>
            </div>

            <button
              class="rounded-xl border border-slate-200 p-3 text-slate-600 transition hover:bg-slate-50"
              @click="loadWallet"
            >
              <RefreshCw
                :size="18"
                :class="
                  loading
                    ? 'animate-spin'
                    : ''
                "
              />
            </button>
          </div>

          <div
            class="mt-6 grid gap-3 sm:grid-cols-3"
          >
            <div
              class="rounded-2xl bg-slate-950 p-5 text-white"
            >
              <p
                class="text-xs text-slate-400"
              >
                Balance
              </p>

              <p
                class="mt-2 text-2xl font-black"
              >
                {{ money(balance) }}
              </p>
            </div>

            <div
              class="rounded-2xl bg-emerald-50 p-5"
            >
              <div
                class="flex items-center gap-2 text-emerald-700"
              >
                <ArrowDownLeft
                  :size="17"
                />

                <p class="text-xs font-semibold">
                  Credits
                </p>
              </div>

              <p
                class="mt-2 text-2xl font-black text-emerald-700"
              >
                {{
                  money(
                    totalCredits
                  )
                }}
              </p>
            </div>

            <div
              class="rounded-2xl bg-amber-50 p-5"
            >
              <div
                class="flex items-center gap-2 text-amber-700"
              >
                <ArrowUpRight
                  :size="17"
                />

                <p class="text-xs font-semibold">
                  Debits
                </p>
              </div>

              <p
                class="mt-2 text-2xl font-black text-amber-700"
              >
                {{
                  money(
                    totalDebits
                  )
                }}
              </p>
            </div>
          </div>

          <div
            class="mt-6 flex items-center gap-3"
          >
            <History
              :size="19"
              class="text-slate-500"
            />

            <div>
              <h3
                class="font-bold text-slate-900"
              >
                Recent transactions
              </h3>

              <p
                class="text-xs text-slate-500"
              >
                Wallet credits, payments
                and refunds
              </p>
            </div>
          </div>

          <div
            v-if="loading"
            class="mt-5 rounded-2xl bg-slate-50 p-8 text-center text-sm text-slate-500"
          >
            Loading transactions...
          </div>

          <div
            v-else-if="
              recentTransactions.length ===
              0
            "
            class="mt-5 rounded-2xl bg-slate-50 p-8 text-center text-sm text-slate-500"
          >
            No wallet transactions yet.
          </div>

          <div
            v-else
            class="mt-5 space-y-3"
          >
            <article
              v-for="transaction in recentTransactions"
              :key="transaction.id"
              class="flex flex-col gap-4 rounded-2xl border border-slate-100 p-4 transition hover:border-slate-200 hover:bg-slate-50 sm:flex-row sm:items-center sm:justify-between"
            >
              <div
                class="flex min-w-0 items-center gap-3"
              >
                <div
                  class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl"
                  :class="
                    transaction.direction ===
                    'credit'
                      ? 'bg-emerald-50 text-emerald-600'
                      : 'bg-amber-50 text-amber-600'
                  "
                >
                  <ArrowDownLeft
                    v-if="
                      transaction.direction ===
                      'credit'
                    "
                    :size="20"
                  />

                  <ArrowUpRight
                    v-else
                    :size="20"
                  />
                </div>

                <div class="min-w-0">
                  <p
                    class="font-bold text-slate-800"
                  >
                    {{
                      prettyType(
                        transaction.transaction_type
                      )
                    }}
                  </p>

                  <p
                    class="mt-1 truncate text-xs text-slate-500"
                  >
                    {{
                      transaction.description ||
                      transaction.transaction_reference
                    }}
                  </p>

                  <p
                    class="mt-1 flex items-center gap-1 text-[11px] text-slate-400"
                  >
                    <Clock3
                      :size="12"
                    />

                    {{
                      formatDate(
                        transaction.created_at
                      )
                    }}
                  </p>
                </div>
              </div>

              <div
                class="text-left sm:text-right"
              >
                <p
                  class="text-lg font-black"
                  :class="
                    transaction.direction ===
                    'credit'
                      ? 'text-emerald-600'
                      : 'text-slate-900'
                  "
                >
                  {{
                    transaction.direction ===
                    'credit'
                      ? '+'
                      : '-'
                  }}{{
                    money(
                      transaction.amount
                    )
                  }}
                </p>

                <p
                  class="mt-1 text-xs text-slate-400"
                >
                  Balance
                  {{
                    money(
                      transaction.balance_after
                    )
                  }}
                </p>
              </div>
            </article>
          </div>
        </section>
      </div>
    </section>
  </AppShell>
</template>
