<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-light">
    <div class="container-fluid">
      <router-link class="navbar-brand" to="/">Vehicle Parking</router-link>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav me-auto mb-2 mb-lg-0">
          <li class="nav-item">
            <router-link class="nav-link" to="/">Home</router-link>
          </li>
          <li v-if="isLoggedIn && userRole === 'admin'" class="nav-item">
            <router-link class="nav-link" to="/admin">Admin Dashboard</router-link>
          </li>
          <li v-if="isLoggedIn && userRole === 'user'" class="nav-item">
            <router-link class="nav-link" to="/dashboard">My Dashboard</router-link>
          </li>
        </ul>
        <ul class="navbar-nav ms-auto">
          <li v-if="!isLoggedIn" class="nav-item">
            <router-link class="nav-link" to="/login">Login</router-link>
          </li>
          <li v-if="!isLoggedIn" class="nav-item">
            <router-link class="nav-link" to="/register">Register</router-link>
          </li>
          <li v-if="isLoggedIn" class="nav-item">
            <a class="nav-link" href="#" @click.prevent="logout">Logout</a>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script>
export default {
  data() {
    return {
      isLoggedIn: false,
      userRole: null,
    };
  },
  created() {
    this.updateLoginState();
  },
  watch: {
    '$route'() {
      // Watch for route changes to update login state
      this.updateLoginState();
    }
  },
  methods: {
    updateLoginState() {
      const token = localStorage.getItem('token');
      this.isLoggedIn = !!token;
      this.userRole = localStorage.getItem('role');
    },
    logout() {
      localStorage.removeItem('token');
      localStorage.removeItem('role');
      this.updateLoginState();
      this.$router.push('/login');
    },
  },
};
</script> 
