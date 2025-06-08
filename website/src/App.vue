<script setup>
import Counter from "./components/Counter.vue";
// import HelloWorld from "./components/HelloWorld.vue";
// import TheWelcome from "./components/TheWelcome.vue";
import Navbar from "./components/Navbar.vue";
import ProfileView from "./views/ProfileView.vue";
</script>

<template>
  <main id="app-body">
    <Navbar id="navbar" />
    <div id="app-zone">
      <!-- <div id="top-zone">
        <ProfileView />
      </div> -->
      <RouterView/>
    </div>
  </main>
</template>

<style scoped>
#app-body {
  display: flex;
  height: 100%;
  width: 100%;
}

#top-zone {
  display: flex;
  align-items: end;
}

#app-zone {
  flex: 1;
  flex-direction: column;
}

#navbar {
  display: flex;
  flex-direction: column;
  width: 280px; /* Увеличенная ширина для удобства */
  height: 100vh;
  background-color: #241f3a; /* Характерный тёмно-синий цвет HashiCorp */
  color: #e6e6e6; /* Светлый текст */
  padding: 20px;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
}

header {
  line-height: 1.5;
}

.logo {
  display: block;
  margin: 0 auto 2rem;
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  .logo {
    margin: 0 2rem 0 0;
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }
}
</style>
