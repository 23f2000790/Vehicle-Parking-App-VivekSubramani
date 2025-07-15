
<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import Barchart from './Barchart.vue'

const earnings = ref(0)
const actusers = ref(0)
const unausers = ref(0)
const lots = ref(0)
const spots = ref(0)
const lotaddress = ref([])
const lotprices = ref([])
const usernames = ref([])
const userfreq = ref([])
const moneyspent = ref(0)
const activeres = ref(0)
const expiredres = ref(0)
const res_address = ref([])
const res_price = ref([])
const role = ref('')
const username = ref('')
const tooltips = ref([])
const ready = ref(false)

onMounted(async () => {
  const token = localStorage.getItem('token')
  try {
    const res = await axios.get('http://127.0.0.1:5000/api/summary', {
        headers:{
            "Content-Type" : "application/json",
            "Access-Control-Allow-Origin" : "*",
            "Authorization" : `Bearer ${token}`
        }})
    role.value = res.data.role
    if (res.data.role == "admin") {
        username.value = res.data.username
        actusers.value = res.data.actusers
        unausers.value = res.data.unausers
        lots.value = res.data.lots
        spots.value = res.data.spots
        earnings.value = res.data.earning.toFixed(2)
        lotaddress.value = res.data.profitable_lots.map(i => i.label)
        lotprices.value = res.data.profitable_lots.map(i => i.value)
        usernames.value = res.data.frequent_users.map(i => i.label)
        userfreq.value = res.data.frequent_users.map(i => i.value)
    }
    else {
        username.value = res.data.username
        moneyspent.value = res.data.money_spent
        activeres.value = res.data.activeres
        expiredres.value = res.data.expiredres
        res_address.value = res.data.res_data.map(i => i.label)
        res_price.value = res.data.res_data.map(i => i.value)
        tooltips.value = res.data.res_data.map(i => i.date)
    } 
    setTimeout(() => {
      ready.value = true
    }, 100)
  } catch (err) {
    console.error('Error loading summary:', err)
  }
})
</script>


<template>
  <div v-if="!ready" class="loading-screen">
    <div class="spinner-border text-primary" role="status">
    <span class="visually-hidden">Loading...</span>
    </div>
  </div>
  <div v-if="role == 'admin'" class="d-flex flex-row min-vh-100">
    <div class="sidebar text-white p-3">
      <p><strong>Welcome,&ensp;{{ username }}</strong></p>
      <RouterLink class="d-block mb-2 text-white" to="/dashboard">Home</RouterLink>
      <RouterLink class="d-block mb-2 text-white" to="/users">Users</RouterLink>
      <RouterLink class="d-block mb-2 text-white" to="/summary">Summary</RouterLink>
    </div>
    <div class="flex-grow-1 p-3">
      <div style="background-color: #e0f0ff; margin: 5px 10px; border-radius: 8px;">
        <h1 style="text-align: center; padding: 0.2rem;">Summary</h1>
      </div>
        <div class="d-flex flex-column gap-4">
            <div class="summary-row">
                <div class="summary-card">
                    <h3 class="h5">Total Earnings</h3>
                    <p class="h3 text-success fw-bold">₹ {{ earnings }}</p>
                </div>
                <div class="summary-card">
                    <h3 class="h5">Active Users</h3>
                    <p class="h3 text-success fw-bold">{{ actusers }}</p>
                </div>
                <div class="summary-card">
                    <h3 class="h5">Unauthorized Users</h3>
                    <p class="h3 text-danger fw-bold">{{ unausers }}</p>
                </div>
                <div class="summary-card">
                    <h3 class="h5">Lots</h3>
                    <p class="h3 text-danger fw-bold">{{ lots }}</p>
                </div>
                <div class="summary-card">
                    <h3 class="h5">Spots</h3>
                    <p class="h3 text-danger fw-bold">{{ spots }}</p>
                </div>
            </div>
            <div class="summary-card">
                <div>
                    <h4 class="h5 mb-2 text-center">Top 5 Profitable Lots</h4>
                    <Barchart :labels="lotaddress" :data="lotprices" label="Total ₹ Earned"/>
                </div>
                <p></p>
                <div>
                    <h4 class="h5 mb-2 text-center">Top 5 Frequent Customers</h4>
                    <Barchart :labels="usernames" :data="userfreq" label="Bookings" />
                </div>
            </div>
        </div>
    </div>
  </div>

  <div v-else class="d-flex flex-row min-vh-100">
    <div class="sidebar text-white p-3">
      <p><strong>Welcome,&ensp;{{ username }}</strong></p>
      <RouterLink class="d-block mb-2 text-white" to="/dashboard">Home</RouterLink>
      <RouterLink class="d-block mb-2 text-white" to="/summary">Summary</RouterLink>
    </div>
    <div class="flex-grow-1 p-3">
      <div style="background-color: #e0f0ff; margin: 5px 10px; border-radius: 8px;">
        <h1 style="text-align: center; padding: 0.2rem;">Summary</h1>
      </div>
        <div class="d-flex flex-column gap-4">
            <div class="d-flex flex-wrap justify-content-between gap-4">
                <div class="summary-card">
                    <h3 class="h5">Amount Spent</h3>
                    <p class="h3 text-success fw-bold">₹ {{ moneyspent }}</p>
                </div>
                <div class="summary-card">
                    <h3 class="h5">Active Reservations</h3>
                    <p class="h3 text-success fw-bold">{{ activeres }}</p>
                </div>
                <div class="summary-card">
                    <h3 class="h5">Expired Reservations</h3>
                    <p class="h3 text-danger fw-bold">{{ expiredres }}</p>
                </div>
            </div>
            <div class="summary-card">
                <div>
                    <h4 class="h5 mb-2 text-center">Reservation Data</h4>
                    <Barchart :labels="res_address" :data="res_price" :tooltips="tooltips" label="Total ₹ Spent"/>
                </div>
            </div>
        </div>
    </div>
  </div>
</template>


<style scoped>
.sidebar {
  min-width: 220px;
  background-color: #212529;
  padding: 1.5rem 1rem;
  font-size: 1.1rem;
}
.sidebar a {
  text-decoration: none;
}
.summary-card {
  flex: 1 1 250px;
  padding: 1.5rem;
  background-color: #ffffff;
  border: 1px solid #e3e3e3;
  border-radius: 0.75rem;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.08);
}
.summary-row {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 1.5rem;
}
.loading-screen {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>
