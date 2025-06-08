import GraphView from "@/views/GraphView.vue";
import { createMemoryHistory, createRouter } from "vue-router";

const routes = [
    { path: '/', component: GraphView}
]

export const router = createRouter({
    history: createMemoryHistory(),
    routes,
})