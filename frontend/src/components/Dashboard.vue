<script>
export default {
    data(){
        return {
            token: "",
            role: ""
        }
    },
    mounted(){
        this.loadtoken()
    },
    methods: {
        loadtoken: function(){
            const token = localStorage.getItem("token");
            if(token){
                this.token = token;
            }
        }
    }
}
</script>

<template>
    <div v-if="token">
        <div>
            user
        </div>
        <div>
            admin
        </div>
    </div>
    <div v-else>
        Please Login
    </div>
</template>