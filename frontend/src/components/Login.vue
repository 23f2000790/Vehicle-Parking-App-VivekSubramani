<script>
import axios from 'axios'
export default{
    data(){
        return {
            formdata: {
                username : "",
                password : ""
            },
            token : ""
        }
    },
    methods: {
        Loginuser(event){
            event.preventDefault()
            const response = axios.post("http://127.0.0.1:5000/api/login", JSON.stringify(this.formdata), {
                headers:{
                    "Content-Type" : "application/json",
                    "Access-Control-Allow-Origin" : "*",
                    "Authorization" : `Bearer ${localStorage.getItem("token")}`
                }
            })
            response.then(res => {
                if (res.status == 200){
                    this.token = res.data.access_token
                    localStorage.setItem("token", res.data.access_token)
                }
                else {
                    console.log(res.response.data.msg)
                }
            })
        }
    }
}
</script>


<template>
    <div id = "canvas">
        <div id = "form-body" style="color: black;">
            <h1 id="centre-text">Login Form</h1>
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
                    <input type="submit" class="btn btn-primary" value="Login">
                </div>
            </form>
            <p id="centre-text">Are you a new User? <a href="">Register now.</a></p> 
        </div>
    </div>

</template>


<style>

</style>