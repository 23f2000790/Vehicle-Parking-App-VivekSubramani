<script>
export default {
  props: ['loggedIn'],
  methods: {
    logoutUser() {
      this.token = null;
      localStorage.clear();
      this.$router.push('/');
    }
  }
}
</script>


<template>
  <nav class="navbar">
    <div class="container-fluid">
      <RouterLink class="navbar-brand" to="/">Vehicle Parking App</RouterLink>
      <button @click="logoutUser" class="btn btn-danger">Logout</button>
    </div>
  </nav>
</template>

<style>
    .navbar {
        background-color: #1F2937;
    }
    .navbar-brand {
        color: white;
    }
</style>


