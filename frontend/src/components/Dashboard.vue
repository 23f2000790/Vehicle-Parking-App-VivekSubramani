<script>
import axios from 'axios'
export default {
    data(){
        return {
            token: "",
            username: "",
            role: "",
            lots: [],
            formdata: {cityname: "", address: "", pincode: "", maxspots: "", priceperhour: "", status: ""},
            reservedata: {vehiclename: "", vehiclenp: ""},
            errormsg: "",
            successmsg: "",
            showaddlot: false,
            editmode: false,
            editlotid: null,
            viewlotdetail: false,
            lotid: null,
            reservationdata: [],
            availablelotdata: [],
            selectedlot: null,
            openbookingform: false,
            searchword: "",
            billdata: {},
            showbillview: false,
            spotdata: {},
            showspotdata: false,
            spotuser: ""
        }
    },
    mounted(){
        this.loadtoken();
        this.loaduser();
    },
    methods: {
        loadtoken: function(){
            const token = localStorage.getItem("token");
            if(token){
                this.token = token;
            }
        },
        loaduser: function(){
            this.errormsg = "";
            this.successmsg = "";
            axios.get("http://127.0.0.1:5000/api/dashboard", {
                headers:{
                    "Content-Type" : "application/json",
                    "Access-Control-Allow-Origin" : "*",
                    "Authorization" : `Bearer ${this.token}`
                }
            }).then(res => {
                this.role = res.data.role;
                this.username = res.data.username;
                if (res.data.role =="admin"){
                    this.lots = res.data.data;
                } else {
                    this.reservationdata = res.data.resdata;
                    this.availablelotdata = res.data.lotdata;
                }
                
               
            })
        },
        occupancy: function(lot) {
            let count = 0;
            const status = Object.values(lot.status_dict);
            for (let i = 0; i < status.length; i++){
                if (status[i] === true){
                    count += 1;
                }
            }
            return count;
        },
        openaddlotform() {
            this.showaddlot = true;
            this.errormsg = "";
            this.successmsg = "";
            this.formdata = {cityname: "", address: "", pincode: "", maxspots: "", priceperhour: "", status: ""}
        },
        sendlot: function(){
            this.errormsg = "";
            this.successmsg = "";
            if (typeof this.formdata.status === "boolean") {
                this.formdata.status = this.formdata.status ? "active" : "inactive";
            }
            if (this.editmode) {
                axios.put(`http://127.0.0.1:5000/api/editlot/${this.editlotid}`, this.formdata,{ 
                        headers: {
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Origin" : "*",
                        "Authorization": `Bearer ${this.token}`
                    }}).then(res => {
                        this.successmsg = res.data.msg;
                        this.openaddlotform();
                        this.showaddlot = false;
                        this.loaduser()
                    }).catch(error => {
                        this.errormsg = error.response?.data?.msg
                    })
            } else {
                if (!this.formdata.cityname || !this.formdata.address || !this.formdata.pincode || !this.formdata.maxspots || !this.formdata.status || !this.formdata.priceperhour) {
                    this.errormsg = "Please enter all fields!!"
                    return
                }
                axios.post("http://127.0.0.1:5000/api/addlot", this.formdata, { 
                        headers: {
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Origin" : "*",
                        "Authorization": `Bearer ${this.token}`
                    }}
                ).then(res => {
                    this.successmsg = res.data.msg
                    this.showaddlot = false;
                    this.loaduser();
                }).catch(error => {
                    this.errormsg = error.response?.data?.msg
                })
            }

        },
        deletelot: function(lotid){
            this.successmsg = "";
            this.errormsg = "";
            axios.delete(`http://127.0.0.1:5000/api/deletelot/${lotid}`, { headers: {"Authorization": `Bearer ${this.token}`}}
            ).then(res => {
                this.successmsg = res.data.msg;
                this.loaduser();
            }).catch(error => {
                this.errormsg = error.response?.data?.msg
            })
        },
        editlot: function(lot) {
            this.successmsg = "";
            this.errormsg = "";
            this.editmode = true;
            this.editlotid = lot.lot_id;
            this.formdata = {cityname: lot.city, address: lot.address, pincode: lot.pincode, maxspots: lot.spots, priceperhour: lot.price, status: lot.status};
            this.showaddlot = true;
        },
        viewlot: function(lot) {
            this.lotid = lot.lot_id;
            this.formdata = {cityname: lot.city, address: lot.address, pincode: lot.pincode, maxspots: lot.spots, priceperhour: lot.price, status: lot.status ? "active" : "inactive"};
            this.viewlotdetail = true;
        },
        bookingform: function (lot) {
            this.selectedlot = lot.id;
            this.openbookingform = true;
            this.errormsg = "";
            this.successmsg = "";
        },
        bookspot: function() {
            this.successmsg = "";
            this.errormsg = "";
            if (!this.reservedata.vehiclename || !this.reservedata.vehiclenp) {
                this.errormsg = "Please fill all the fields!!";
                return;
            }
            axios.post("http://127.0.0.1:5000/api/bookspot", {
                lotid: this.selectedlot,
                vehiclename: this.reservedata.vehiclename,
                vehiclenp: this.reservedata.vehiclenp
            }, {
                headers: {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin" : "*",
                    "Authorization": `Bearer ${this.token}`   
                }
            }).then(res => {
                this.loaduser();
                this.openbookingform = false;
                this.reservedata.vehiclename = "";
                this.reservedata.vehiclenp = "";
                this.successmsg = res.data.msg;
            }).catch(error => {
                this.openbookingform = false;
                this.reservedata.vehiclename = "";
                this.reservedata.vehiclenp = "";
                this.errormsg = error.response?.data?.msg;               
            })
        },
        vacatespot: function(spotid, pts, id) {
            this.successmsg = "";
            axios.put("http://127.0.0.1:5000/api/vacatespot", {spotid:spotid, pts:pts, id:id}, {
                headers: {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin" : "*",
                    "Authorization": `Bearer ${this.token}`   
                }}).then(res => {
                    this.successmsg = res.data.msg;
                    this.loaduser();
                })
        },
        search: function() {
            this.availablelotdata = [];
            this.errormsg = "";
            this.successmsg = "";
            axios.get("http://127.0.0.1:5000/api/search", {
                params: {searchword: this.searchword},
                headers: {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin" : "*",
                "Authorization": `Bearer ${this.token}`   
                }}
                ).then(res => {
                    this.availablelotdata = res.data.searchres;
                }).catch(error => {
                    this.errormsg = error.response?.data?.msg;
                })
        },
        showbill: function(res) {
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
        },
        viewspot: function(spotid) {
            this.spotdata = {};
            this.spotuser = "";
            axios.get("http://127.0.0.1:5000/api/viewspot", {
                params: {id: spotid},
                headers: {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin" : "*",
                "Authorization": `Bearer ${this.token}`   
                }}
            ).then(res => {
                this.spotdata = res.data.spotdata;
                this.spotuser = res.data.username;
                this.showspotdata = true;
            })
        },
        downloadCSV: function() {
            axios.get('http://127.0.0.1:5000/exportcsv',{
                    headers: {
                        Authorization: `Bearer ${this.token}`
                    }
            })
                .then(response => {
                    const id = response.data.id;

                    // wait 2 seconds (or use polling for better UX)
                    setTimeout(() => {
                        window.location.href = `http://127.0.0.1:5000/api/csv_result/${id}`; 

                    }, 2000);
                })
                .catch(err => {
                    console.error("Error exporting CSV:", err);
                    alert("Failed to generate CSV.");
                });
        }
    }
}
</script>

<template>
    <div v-if="token">

        <div v-if=" role == 'user' " class="d-flex">
            <div class="sidebar bg-secondary text-white p-3">
            <p><strong>Welcome, {{ this.username }}</strong></p>
            <RouterLink class="d-block mb-2 text-white" @click="loaduser()" to="/dashboard">Home</RouterLink>
            <RouterLink class="d-block mb-2 text-white" to="/">Summary</RouterLink>
            <button @click="downloadCSV()">Download CSV</button>
            </div>
            <div class="flex-grow-1 p-3">
                <div style="background-color: #e0f0ff; margin: 10px; padding: 20px; border-radius: 8px;">
                    <h1 style="text-align: center; padding: 0.2rem;">Available parking lots</h1>
                    <form @submit.prevent="search">
                        <div class="d-flex justify-content-center">
                            <div class="input-group" style="width: 50%;">
                                <input type="search" class="form-control form-control-lg" id="search" placeholder = "Type here..." v-model="searchword" style="border-radius: 8px 0 0 8px;">
                                <button type="submit" class="btn btn-primary" style="border-radius: 0 8px 8px 0;">Search</button>
                            </div>
                        </div>
                    </form>
                </div>
                <table class="table table-bordered table-hover mt-3">
                    <thead class="table-light">
                        <tr>
                            <th>ID</th>
                            <th>Address</th>
                            <th>pincode</th>
                            <th>available spots</th>
                            <th>price</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="lot in availablelotdata" :key="lot.id">
                        <td>{{ lot.id }}</td>
                        <td>{{ lot.address }}</td>
                        <td>{{ lot.pincode }}</td>
                        <td>{{ lot.maxspots }}</td>
                        <td>₹{{ lot.price }}</td>
                        <td><button class="btn btn-primary" @click="bookingform(lot)">Book</button></td>
                        </tr>
                    </tbody>
                </table>
                <div class="text-center">
                    <p v-if="successmsg" class="text-success text-center">{{ successmsg }}</p>
                    <p v-if="errormsg" class="text-danger text-center">{{ errormsg }}</p>
                </div>
                <div v-if="openbookingform" class="modal-backdrop">
                    <div class="modal-content">
                        <h1 class="text-center">Book Spot</h1>
                        <p v-if="errormsg" class="text-danger text-center">{{ errormsg }}</p>
                        <form @submit.prevent="bookspot">
                            <div class="mb-3">
                                <label for="vehiclename" class="form-label">Vehicle Name</label>
                                <input type="text" class="form-control" id="vehiclename" placeholder = "vehiclename" v-model="reservedata.vehiclename">
                            </div>
                            <div class="mb-3">
                                <label for="vehiclenp" class="form-label">Vehicle Number Plate</label>
                                <input type="text" class="form-control" id="vehiclenp" placeholder = "vehiclenp" v-model="reservedata.vehiclenp">
                            </div>    
                            <div class="d-flex justify-content-center gap-3">
                                <button type="submit" class="btn btn-success">Add</button>
                                <button type="button" class="btn btn-danger" @click="openbookingform = false">Cancel</button>
                            </div>
                        </form>
                    </div>
                </div>
                <div v-if="reservationdata.length > 0" class="flex-grow-1 p-3">
                    <div style="background-color: #e0f0ff; margin: 5px 10px 5px 10px; border-radius: 8px;">
                        <h1 style="text-align: center; padding: 0.2rem;">Booking Data</h1>
                    </div>
                    <table class="table table-bordered table-hover mt-3">
                        <thead class="table-light">
                            <tr>
                                <th>Spot ID</th>
                                <th>Address</th>
                                <th>Vehicle Name</th>
                                <th>Number Plate</th>
                                <th>Booking Time</th>
                                <th>Leaving Time</th>
                                <th>Price</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="res in reservationdata" :key="res.id">
                                <td>{{ res.spotid }}</td>
                                <td>{{ res.address }}</td>
                                <td>{{ res.vehiclename }}</td>
                                <td>{{ res.vehiclenp }}</td>
                                <td>{{ res.parkingts }}</td>
                                <td>{{ res.leavingts ? res.leavingts : '-' }}</td>
                                <td>{{ res.price || '-' }}</td>
                                <td>
                                <div v-if="res.leavingts" class="d-flex justify-content-center gap-2">
                                    <button class="btn btn-warning" @click="showbill(res)">
                                        Bill
                                    </button>
                                </div>
                                <div class="text-center">
                                 <button class="btn btn-warning" v-if="!res.leavingts" @click="vacatespot(res.spotid, res.parkingts, res.id)">
                                    Vacate
                                 </button>                                   
                                </div>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                <div v-if="showbillview" class="modal-backdrop">
                    <div class="modal-content">
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

        </div>


        <div v-else class="d-flex">
            <div class="sidebar bg-dark text-white p-3">
                <p><strong>Welcome,&ensp;Admin</strong></p>
                <RouterLink class="d-block mb-2 text-white" to="/dashboard">Home</RouterLink>
                <RouterLink class="d-block mb-2 text-white" to="/users">Users</RouterLink>
                <RouterLink class="d-block mb-2 text-white" to="/">Summary</RouterLink>
            </div>
            <div class="flex-grow-1 p-3">
                <div style="background-color: #e0f0ff; margin: 5px 10px 5px 10px; border-radius: 8px;">
                    <h1 style="text-align: center; padding: 0.2rem;">Parking Lots</h1>
                </div>
                <div class="d-flex flex-wrap gap-4 p-3 justify-content-center">
                    <div v-for="lot in lots" :key="lot.lot_id" :class="['p-3', 'border', 'rounded', 'shadow', lot.status == 1 ? 'lot-active' : 'lot-inactive']" style="width: 250px;">
                    <div class="d-flex justify-content-center">
                        <a href="#" style="color: blue;" @click.prevent="viewlot(lot)">Parking {{ lot.lot_id }}</a>
                    </div>
                    <p class="text-center">{{ lot.city }} | {{ lot.pincode }} | {{ lot.price }}₹</p>
                    <div class="text-center mb-1">
                        <button class="btn btn-warning" @click="editlot(lot)">Edit</button> |
                        <button class="btn btn-danger" @click="deletelot(lot.lot_id)">Delete</button>
                    </div>
                    <p class="text-success text-center fw-bold">
                        (Occupied: {{ occupancy(lot) }}/{{ lot.spots }})
                    </p>

                    <div class="d-flex flex-wrap justify-content-center gap-2">
                        <div v-for="(status, spotid) in lot.status_dict" :key="spotid">
                            <div v-if="status == true" @click="viewspot(spotid)">    
                                <button class="spot occupied">{{ spotid }}</button>
                            </div>
                            <div v-else class="spot available">
                                {{ spotid }}
                            </div>
                        </div>
                        <!-- <div v-for="(status, spotId) in lot.status_dict" :key="spotId" :class="status ? 'spot occupied' : 'spot available'">
                        {{ spotId }}
                        </div> -->
                    </div>
                    </div>
                </div>
                <div class="text-center">
                    <button class="btn btn-success" @click="openaddlotform">+ Add Lot</button>
                    <p v-if="successmsg" class="text-success text-center">{{ successmsg }}</p>
                    <p v-if="errormsg" class="text-danger text-center">{{ errormsg }}</p>
                </div>
                <div v-if="showaddlot" class="modal-backdrop">
                    <div class="modal-content">
                        <h1 class="text-center">Add new Lot</h1>
                        <p v-if="errormsg" class="text-danger text-center">{{ errormsg }}</p>
                        <form @submit.prevent="sendlot">
                            <div class="mb-3">
                                <label for="City" class="form-label">City</label>
                                <input type="text" class="form-control" id="City" placeholder = "example" v-model="formdata.cityname">
                            </div>
                            <div class="mb-3">
                                <label for="Address" class="form-label">Address</label>
                                <input type="text" class="form-control" id="Address" placeholder = "Address" v-model="formdata.address">
                            </div>    
                            <div class="mb-3">
                                <label for="Pincode" class="form-label">Pincode</label>
                                <input type="text" class="form-control" id="Pincode" placeholder = "Pincode" v-model="formdata.pincode">
                            </div>    
                            <div class="mb-3">
                                <label for="maxspots" class="form-label">Max Spots</label>
                                <input type="text" class="form-control" id="maxspots" placeholder = "maxspots" v-model="formdata.maxspots">
                            </div>    
                            <div class="mb-3">
                                <label for="pph" class="form-label">Price/Hour</label>
                                <input type="text" class="form-control" id="pph" placeholder = "pph" v-model="formdata.priceperhour">
                            </div>   
                            <div class="mb-3">
                                <label for="Status" class="form-label">Status</label>
                                <select id="status" class="form-select" v-model="formdata.status">
                                    <option value="active">Active</option>
                                    <option value="inactive">Inactive</option>
                                </select>
                            </div>   
                            <div class="d-flex justify-content-center gap-3">
                                <div v-if="editmode">
                                    <button type="submit" class="btn btn-success">Edit</button>
                                </div>
                                <div v-else>
                                    <button type="submit" class="btn btn-success">Add</button>
                                </div>
                                <button type="button" class="btn btn-danger" @click="showaddlot = false; editmode = false">Cancel</button>
                            </div>
                        </form>
                    </div>
                </div>
                <div v-if="viewlotdetail" class="modal-backdrop">
                    <div class="modal-content">
                        <h5><strong>Lot Id - {{ lotid }}</strong></h5>
                        <p><strong>City:</strong> {{ formdata.cityname }}</p>
                        <p><strong>Address:</strong> {{ formdata.address }}</p>
                        <p><strong>Pincode:</strong> {{ formdata.pincode }}</p>
                        <p><strong>Max Spots:</strong> {{ formdata.maxspots }}</p>
                        <p><strong>Price per Hour:</strong> ₹{{ formdata.priceperhour }}</p>
                        <p><strong>Status:</strong> {{ formdata.status }}</p>
                        <button class="btn btn-secondary" @click="viewlotdetail = false">Close</button>
                    </div>
                </div>
                <div v-if="showspotdata" class="modal-backdrop">
                    <div class="modal-content">
                        <h5><strong>Spot Id - {{ spotdata.spotid }}</strong></h5>
                        <p><strong>Occupied by:</strong> {{ spotuser }}</p>
                        <p><strong>Vehicle:</strong> {{ spotdata.vehiclename }}</p>
                        <p><strong>Vehicle Number:</strong> {{ spotdata.vehiclenp }}</p>
                        <p><strong>Parked At:</strong> {{ spotdata.parkingts }}</p>
                        <button class="btn btn-secondary" @click="showspotdata = false">Close</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <div v-else>
        Please Login
    </div>
</template>


<style scoped>
.spot {
  width: 30px;
  height: 30px;
  line-height: 30px;
  text-align: center;
  font-weight: bold;
  border-radius: 8px;
  border: 1px solid #000;
}
.available {
  background-color: #d4f8d4;
  color: #0b0;
}
.occupied {
  background-color: #f8caca;
  color: #c00;
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
.lot-active {
  background-color: #d4f8d4;
}

.lot-inactive {
  background-color: #f8caca;
}
.sidebar {
  min-width: 200px;
  height: 100vh;
}
</style>