<template>
  <div class="profile-view">
    <h1>Профиль пользователя</h1>
    <div v-if="user.isLoggedIn">
      <p><strong>Имя:</strong> {{ user.name }}</p>
      <p><strong>Email:</strong> {{ user.email }}</p>
      <button @click="logout">Выйти</button>
    </div>
    <div v-else>
      <p>Вы не вошли в систему.</p>
    </div>
  </div>
</template>

<script setup>
import { useUserStore } from "@/stores/user";

const user = useUserStore();

function logout() {
  user.logout();
}
</script>

<style scoped>
.profile-view {
  padding: 20px;
}
button {
  margin-top: 10px;
}
</style>
