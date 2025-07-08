<script>
import axios from 'axios';
export default{
    data(){
        return {
            formdata: {
                email: "",
                username : "",
                password : "",
                confirmpassword: "",
                phone_no: ""
            },
            successmsg: "",
            errormsg: ""
        }
    },
    methods: {
        registeruser(event) {
            event.preventDefault()
            this.successmsg = ""
            this.errormsg = ""
            if (this.formdata.password != this.formdata.confirmpassword){
                this.errormsg = "Passwords do not match!!"
                return
            }
            const response = axios.post("http://127.0.0.1:5000/api/register", {
                email: this.formdata.email,
                username: this.formdata.username,
                password: this.formdata.password,
                phone_no: this.formdata.phone_no,
            }, {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin" : "*"
            })
            response.then(res => {
                if (res.status == 201) {
                    this.successmsg = res.data.msg
                    this.$router.push('/login')
                }
                else {
                    this.errormsg = err.response?.data?.msg
                }
            })
        }
    }
}
</script>


<template>
    <div id = "bg">
        <div id = "canvas">
            <div id = "form-body-register">
                <h1 id="centre-text">Registration Form</h1>
                <p v-if="successmsg" class="text-success text-center">{{ successmsg }}</p>
                <p v-if="errormsg" class="text-danger text-center">{{ errormsg }}</p>
                <form @submit="registeruser">
                    <div class="mb-3">
                        <label for="fullname" class="form-label">Email</label>
                        <input type="email" class="form-control" id="fullname" v-model="formdata.email">
                    </div>    
                    <div class="mb-3">
                        <label for="username" class="form-label">Username</label>
                        <input type="text" class="form-control" id="username" placeholder = "example123" v-model="formdata.username" >
                    </div>
                    <div class="mb-3">
                        <label for="pwd" class="form-label">Password</label>
                        <input type="password" class="form-control" id="pwd"  v-model="formdata.password">
                    </div>    
                    <div class="mb-3">
                        <label for="cpwd" class="form-label">Confirm Password</label>
                        <input type="password" class="form-control" id="cpwd"  v-model="formdata.confirmpassword">
                    </div>    
                    <div class="mb-3">
                        <label for="phone_no" class="form-label">Phone No.</label>
                        <input type="text" class="form-control" id="qualification"  v-model="formdata.phone_no">
                    </div>    
                    <div class="text-center">
                        <input type="submit" class="btn btn-primary" value="Register">
                    </div>
                </form>
                <p id="centre-text">Already Registered? <button @click="this.$router.push('/login')">Login</button></p> 
            </div>
        </div>
    </div>
</template>