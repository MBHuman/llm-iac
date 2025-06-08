import { defineStore } from "pinia";

export const useUserStore = defineStore('user', {
    state: () => ({
        name: '',
        email: '',
        isLoggedIn: false
    }),
    actions: {
        logout() {
            this.name = '',
            this.email = '',
            this.isLoggedIn = false
        }
    }
})