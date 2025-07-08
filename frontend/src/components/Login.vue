<script>
import axios from 'axios'
export default{
    data(){
        return {
            formdata: {
                username : "",
                password : ""
            },
            token : "",
            errormsg: ""
        }
    },
    methods: {
        Loginuser(event){
            event.preventDefault()
            const response = axios.post("http://127.0.0.1:5000/api/login", {
                username: this.formdata.username,
                password: this.formdata.password
            }, {
                headers:{
                    "Content-Type" : "application/json",
                    "Access-Control-Allow-Origin" : "*"
                }
            }).then(res => {
                this.token = res.data.access_token
                localStorage.setItem("token", res.data.access_token)
                this.$router.push('/dashboard')
            }).catch(error => {
                this.errormsg = error.response.data.msg
            })
        }
    }
}
</script>


<template>
    <div id = "canvas">
        <div id = "form-body" style="color: black;">
            <h1 id="centre-text">Login Form</h1>
            <p v-if="errormsg" class="text-danger text-center">{{ errormsg }}</p>
            <form @submit="Loginuser">
                <div class="mb-3">
                    <label for="Username" class="form-label">Username</label>
                    <input type="text" class="form-control" id="username" placeholder = "example" v-model="formdata.username">
                </div>
                <div class="mb-3">
                    <label for="pwd" class="form-label">Password</label>
                    <input type="password" class="form-control" id="pwd" placeholder = "password" v-model="formdata.password">
                </div>    
                <div class="text-center">
                    <input type="submit" class="btn btn-success" value="Login">
                </div>
            </form>
            <p></p>
            <p id="centre-text">Are you a new User? <RouterLink to="/register"> <button class="btn btn-primary">Register</button></RouterLink></p> 
        </div>
    </div>

</template>


<style>

</style>


