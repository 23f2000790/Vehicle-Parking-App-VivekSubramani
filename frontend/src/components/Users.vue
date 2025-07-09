<script>
import axios from 'axios';
export default {
    data() {
        return {
            token: "",
            role: "",
            data: [],
            msg: "",
            showconfirmtab: false,
            userid: null
        }
    },
    mounted() {
        this.loadtoken();
        this.loaddata();
    },
    methods: {
        loadtoken: function(){
            const token = localStorage.getItem("token");
            if(token){
                this.token = token;
            }
        },
        loaddata: function() {
            axios.get("http://127.0.0.1:5000/api/users", {
                headers:{
                    "Content-Type" : "application/json",
                    "Access-Control-Allow-Origin" : "*",
                    "Authorization" : `Bearer ${this.token}`
                }
            }).then(res =>{
                this.role = res.data.role;
                this.data = res.data.data;
                this.userid = null;
            })
        },
        changestatus: function() {
            this.msg = "",
            axios.put("http://127.0.0.1:5000/api/edituser", {userid: this.userid}, {
                headers:{
                    "Content-Type" : "application/json",
                    "Access-Control-Allow-Origin" : "*",
                    "Authorization" : `Bearer ${this.token}`
                }
            }).then(res =>{
                this.loaddata();
                this.msg = res.data.msg;
            })
        },
        askagain: function(user) {
            this.showconfirmtab = true;
            this.userid = user.id;
        }
    }
}
</script>


<template>
    <div v-if="role == 'admin'">
        <div class="d-flex">
            <div class="sidebar bg-dark text-white p-3">
                <RouterLink class="d-block mb-2 text-white" to="/dashboard">Home</RouterLink>
                <RouterLink class="d-block mb-2 text-white" to="/users">Users</RouterLink>
                <RouterLink class="d-block mb-2 text-white" to="/">Summary</RouterLink>
            </div>
            <div class="flex-grow-1 p-3">
                <div style="background-color: #e0f0ff; margin: 5px 10px 5px 10px; border-radius: 8px;">
                    <h1 style="text-align: center; padding: 0.2rem;">Users</h1>
                    <p v-if="msg" class="text-success text-center">{{ errormsg }}</p>
                </div>
                <table class="table table-bordered table-hover mt-3">
                    <thead class="table-light">
                        <tr>
                            <th>ID</th>
                            <th>Email</th>
                            <th>Username</th>
                            <th>Phone No</th>
                            <th style="width: 240px;">Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="user in data" :key="user.id">
                            <td>{{ user.id }}</td>
                            <td>{{ user.email }}</td>
                            <td>{{ user.username }}</td>
                            <td>{{ user.phone_no }}</td>
                            <td class="d-flex justify-content-center">
                                <button :class="user.status ? 'Active rounded-3' : 'Unauthorized rounded-3'" @click="askagain(user)">
                                    {{ user.status ? "Active" : "Unauthorized" }}
                                </button> &ensp;
                                <button v-if="user.status == true" class="btn btn-primary" @click="userhistory(user)">History</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
        <div v-if="showconfirmtab" class="modal-backdrop">
            <div class="modal-content">
                <h5><strong>Are you sure that you want to remove this user?</strong></h5><p></p>
                <div class="d-flex justify-content-center">
                    <button class="btn btn-danger" @click="changestatus(); showconfirmtab = false">Confirm</button> &ensp;&ensp;
                    <button class="btn btn-secondary" @click="loaddata(); showconfirmtab = false">Close</button>
                </div>
            </div>
        </div>
    </div>
</template>


<style scoped>
.sidebar {
  min-width: 200px;
  height: 100vh;
}
.Active {
    background-color: green;
    color: white;
}
.Unauthorized {
    background-color: red;
    color: white;
}
td, th {
  vertical-align: middle;
  text-align: center;
}
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 10;
}

.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 10px;
  width: 400px;
}
</style>