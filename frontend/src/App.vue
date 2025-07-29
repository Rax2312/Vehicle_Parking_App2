<template>
  <div id="app">
    <NavBar />
    <main class="container mt-4">
      <router-view />
    </main>
  </div>
</template>

<script>
import NavBar from './components/NavBar.vue';

export default {
  name: 'App',
  components: {
    NavBar,
  },
};
</script>

<style>
body {
  background-color: #f8f9fa;
}
</style> 
