<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <div class="card">
          <div class="card-header">Login</div>
          <div class="card-body">
            <form @submit.prevent="login" autocomplete="new-password" data-form-type="other">
              <!-- Multiple hidden fields to prevent autofill -->
              <div style="display:none">
                <input type="text" name="prevent_autofill" />
                <input type="password" name="password_fake" />
                <input type="email" name="email_fake" />
              </div>
              
              <div v-if="error" class="alert alert-danger">{{ error }}</div>
              <div class="mb-3">
                <label for="username" class="form-label">Username or Email</label>
                <input 
                  type="text" 
                  id="username" 
                  name="username_random"
                  v-model="username" 
                  class="form-control" 
                  required 
                  autocomplete="off"
                  data-form-type="other"
                  readonly
                  onfocus="this.removeAttribute('readonly');"
                />
              </div>
              <div class="mb-3">
                <label for="password" class="form-label">Password</label>
                <input 
                  type="password" 
                  id="password" 
                  name="password_random"
                  v-model="password" 
                  class="form-control" 
                  required 
                  autocomplete="off"
                  data-form-type="other"
                  readonly
                  onfocus="this.removeAttribute('readonly');"
                />
              </div>
              <button type="submit" class="btn btn-primary" :disabled="loggingIn">
                {{ loggingIn ? 'Logging in...' : 'Login' }}
              </button>
            </form>
            <p class="mt-3">
              Don't have an account? <router-link to="/register">Register here</router-link>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ApiService from '../services/ApiService';
export default {
  data() {
    return {
      username: '',
      password: '',
      error: null,
      loggingIn: false,
    };
  },
  methods: {
    async login() {
      this.error = null;
      this.loggingIn = true;
      
      try {
        const response = await ApiService.login({
          username: this.username, 
          password: this.password,
        });
        
        if (response.data.success) {
          // Redirection based on role
          if (response.data.role === 'admin') {
            this.$router.push('/admin');
          } else {
            this.$router.push('/dashboard');
          }
        } else {
          this.error = response.data.message || 'Login failed.';
        }

      } catch (error) {
        this.error = error.response?.data?.message || 'An error occurred during login.';
      } finally {
        this.loggingIn = false;
      }
    },
  },
};
</script> 
