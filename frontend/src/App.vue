<script setup>
import Navbar from './components/Navbar.vue';
import Footer from './components/Footer.vue';
import { ref, onMounted } from 'vue';

const ready = ref(false)
onMounted(() => {
  setTimeout(() => {
    ready.value = true
  }, 100)
})
const loggedin = ref(!!localStorage.getItem('token'))
const handlelogout = () => {
  loggedin.value = false
}
const handlelogin = () => {
  console.log("Login successful")
  loggedin.value = true
}
</script>

<template>
  <div id="app">
    <div v-if="!ready" class="loading-screen">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
    <div v-else><Navbar :loggedin="loggedin" @logout="handlelogout"></Navbar></div>
    <div class="content"><router-view @successful-login="handlelogin"/></div>
    <Footer></Footer>
  </div>
</template>

<style scoped>
html, body {
  height: 100%;
  margin: 0;
}

#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.content {
  flex: 1;
}
.loading-screen {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>
