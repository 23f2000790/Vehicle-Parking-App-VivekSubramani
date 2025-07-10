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
            userid: null,
            showrestab: false,
            resdata: {id: "", lotid: "", spotid: ",", parkingts: "", leavingts: "", price: "", vehiclename: "", vehiclenp: "", status: ""},
            username: "",
            billdata: {},
            showbillview: false
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
        },
        userres: function(user) {
            this.username = user.username;
            this.resdata = user.reservations;
            this.showrestab = true;
        },
        showbilladmin: function(res) {
            axios.get("http://127.0.0.1:5000/api/bill", {
                params: {id: res.id},
                headers: {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin" : "*",
                "Authorization": `Bearer ${this.token}`   
                }}
            ).then(res => {
                this.billdata = res.data.billdata;
                this.showbillview = true;
            })
        }
    }
}
</script>


<template>
    <div v-if="role == 'admin'">
        <div class="d-flex">
            <div class="sidebar bg-dark text-white p-3">
                <p><strong>Welcome,&ensp;Admin</strong></p>
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
                                <button v-if="user.reservations.length > 0" class="btn btn-primary" @click="userres(user)">Reservations</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
        <div v-if="showconfirmtab" class="modal-backdrop">
            <div class="modal-content-view">
                <h5><strong>Are you sure that you want to change this user's status?</strong></h5><p></p>
                <div class="d-flex justify-content-center">
                    <button class="btn btn-danger" @click="changestatus(); showconfirmtab = false">Confirm</button> &ensp;&ensp;
                    <button class="btn btn-secondary" @click="loaddata(); showconfirmtab = false">Close</button>
                </div>
            </div>
        </div>
        <div v-if="showrestab" class="modal-backdrop">
            <div class="d-flex justify-content-center">
                <div class="modal-content">
                    <div class="table-responsive mt-3">
                        <table class="table table-bordered table-hover align-middle" style="width: auto;">
                            <thead class="table-light">
                                <tr>
                                    <th>LotID</th>
                                    <th>SlotID</th>
                                    <th>Parked</th>
                                    <th>Vacated</th>
                                    <th>Price</th>
                                    <th>Vehicle</th>
                                    <th>Number</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="res in resdata" :key="res.id">
                                    <td>{{ res.lotid }}</td>
                                    <td>{{ res.spotid }}</td>
                                    <td>{{ res.parkingts }}</td>
                                    <td>{{ res.leavingts || '-' }}</td>
                                    <td>{{ res.price || '-' }}</td>
                                    <td>{{ res.vehiclename }}</td>
                                    <td>{{ res.vehiclenp }}</td>
                                    <td class="text-center align-middle">
                                        <div v-if="res.status">
                                            <button class="btn btn-success">Active</button>
                                        </div>
                                        <div v-else>
                                            <button class="btn btn-warning" @click="showbilladmin(res)">
                                                Expired
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    <div class="d-flex justify-content-center">
                        <button class="btn btn-secondary" @click="showrestab = false">Close</button>
                    </div>
                </div>
            </div>
        </div>
        <div v-if="showbillview" class="modal-backdrop">
            <div class="modal-content-view">
                <h5><strong>Reservation - #{{ billdata.resid }}</strong></h5>
                <p><strong>Vehicle: </strong> {{ billdata.vehiclename }}</p>
                <p><strong>Number Plate: </strong> {{ billdata.vehiclenp }}</p>
                <p><strong>Address:</strong> {{ billdata.address }}</p>
                <p><strong>Parked: </strong> {{ billdata.parkingts }}</p>
                <p><strong>Vacated: </strong> {{ billdata.leavingts }}</p>
                <p><strong>Price per Hour:</strong> ₹{{ billdata.priceperhour }}</p>
                <p><strong>Parking duration:</strong> {{ billdata.timetaken }}</p>
                <p><strong>Price:</strong> ₹{{ billdata.price }}</p>
                <button class="btn btn-secondary" @click="showbillview = false">Close</button>
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
  display: inline-block;
  max-width: 95vw;
  padding: 1rem;
  overflow-x: auto;
  white-space: nowrap;
}
.modal-content-view {
  background: white;
  padding: 2rem;
  border-radius: 10px;
  width: 400px;
}
</style>