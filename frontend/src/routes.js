import { createWebHistory, createRouter } from "vue-router";
import Homepage from "./components/Homepage.vue";
import Login from "./components/Login.vue";
import Register from "./components/Register.vue";

const routes = [
    { path: "/", component: Homepage },
    { path: "/login", component: Login },
    { path: "/register", component: Register }
]

export const router = createRouter({
    history: createWebHistory(),
    routes: routes
})