import { createWebHistory, createRouter } from "vue-router";
import Homepage from "./components/Homepage.vue";
import Login from "./components/Login.vue";
import Register from "./components/Register.vue";
import Dashboard from "./components/Dashboard.vue";
import Users from "./components/Users.vue";

const routes = [
    { path: "/", component: Homepage },
    { path: "/login", component: Login },
    { path: "/register", component: Register },
    { path: "/dashboard", component: Dashboard },
    { path: "/users", component: Users }
]

export const router = createRouter({
    history: createWebHistory(),
    routes: routes
})