<script>
</script>

<template>
  <div class="container-fluid vh-100 d-flex p-0">
    <div class="img"></div>
    <div class="bttn d-flex flex-column justify-content-center align-items-center">
      <h2 class="mb-4">Vehicle Parking App</h2>
      <button @click="this.$router.push('/login')" class="btn btn-success mb-3 w-75">Login</button>
      <button @click="this.$router.push('/register')" class="btn btn-primary w-75">Register</button>
    </div>
  </div>
</template>


<style scoped>
.img {
  width: 70%;
  background-image: url('../assets/michael-fousert-a7WIJiOZDO0-unsplash.jpg');
  background-size: cover;
  background-position: center;
}

.bttn {
  width: 30%;
  background-color: #F3F4F6;
  text-align: center;
}
</style>
