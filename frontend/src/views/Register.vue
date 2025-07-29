<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-8">
        <div class="card border-2">
          <div class="card-header">Register</div>
          <div class="card-body">
            <form @submit.prevent="register" autocomplete="off">
              <div v-if="error" class="alert alert-danger">{{ error }}</div>
              <div v-if="successMessage" class="alert alert-success">{{ successMessage }}</div>
              
              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label for="first_name" class="form-label">First Name *</label>
                    <input 
                      type="text" 
                      id="first_name" 
                      v-model="first_name" 
                      class="form-control" 
                      :class="{ 'is-valid': validation.first_name.valid, 'is-invalid': validation.first_name.valid === false }"
                      required 
                      @blur="validateField('first_name')"
                    />
                    <div v-if="validation.first_name.valid === false" class="invalid-feedback">
                      {{ validation.first_name.message }}
                    </div>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3">
                    <label for="last_name" class="form-label">Last Name *</label>
                    <input 
                      type="text" 
                      id="last_name" 
                      v-model="last_name" 
                      class="form-control" 
                      :class="{ 'is-valid': validation.last_name.valid, 'is-invalid': validation.last_name.valid === false }"
                      required 
                      @blur="validateField('last_name')"
                    />
                    <div v-if="validation.last_name.valid === false" class="invalid-feedback">
                      {{ validation.last_name.message }}
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label for="username" class="form-label">Username *</label>
                    <div class="input-group">
                      <input 
                        type="text" 
                        id="username" 
                        v-model="username" 
                        class="form-control"
                        autocomplete="new-username" 
                        :class="{
                          'is-valid': usernameAvailable === true && validation.username.valid,
                          'is-invalid': usernameAvailable === false || validation.username.valid === false
                        }"
                        required 
                        @input="checkUsernameAvailability"
                        @blur="validateField('username')"
                      />
                      <span v-if="checkingUsername" class="input-group-text">
                        <div class="spinner-border spinner-border-sm" role="status">
                          <span class="visually-hidden">Checking...</span>
                        </div>
                      </span>
                      <span v-else-if="usernameAvailable === true && validation.username.valid" class="input-group-text text-success">
                        ✓ Available
                      </span>
                      <span v-else-if="usernameAvailable === false" class="input-group-text text-danger">
                        ✗ Taken
                      </span>
                    </div>
                    <div v-if="usernameAvailable === false" class="invalid-feedback d-block">
                      This username is already taken. Please choose another one.
                    </div>
                    <div v-if="validation.username.valid === false" class="invalid-feedback d-block">
                      {{ validation.username.message }}
                    </div>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3">
                    <label for="email" class="form-label">Email *</label>
                    <input 
                      type="email" 
                      id="email" 
                      v-model="email" 
                      class="form-control"
                      autocomplete="new-email" 
                      :class="{ 'is-valid': validation.email.valid, 'is-invalid': validation.email.valid === false }"
                      required 
                      @blur="validateField('email')"
                    />
                    <div v-if="validation.email.valid === false" class="invalid-feedback">
                      {{ validation.email.message }}
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label for="phone_number" class="form-label">Phone Number *</label>
                    <input 
                      type="tel" 
                      id="phone_number" 
                      v-model="phone_number" 
                      class="form-control" 
                      :class="{ 'is-valid': validation.phone_number.valid, 'is-invalid': validation.phone_number.valid === false }"
                      required 
                      @blur="validateField('phone_number')"
                    />
                    <div v-if="validation.phone_number.valid === false" class="invalid-feedback">
                      {{ validation.phone_number.message }}
                    </div>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3">
                    <label for="age" class="form-label">Age</label>
                    <input 
                      type="number" 
                      id="age" 
                      v-model="age" 
                      class="form-control" 
                      :class="{ 'is-valid': validation.age.valid, 'is-invalid': validation.age.valid === false }"
                      min="1" 
                      max="120" 
                      @blur="validateField('age')"
                    />
                    <div v-if="validation.age.valid === false" class="invalid-feedback">
                      {{ validation.age.message }}
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="mb-3">
                <label for="address" class="form-label">Address</label>
                <textarea 
                  id="address" 
                  v-model="address" 
                  class="form-control" 
                  :class="{ 'is-valid': validation.address.valid, 'is-invalid': validation.address.valid === false }"
                  rows="3"
                  @blur="validateField('address')"
                ></textarea>
                <div v-if="validation.address.valid === false" class="invalid-feedback">
                  {{ validation.address.message }}
                </div>
              </div>
              
              <div class="mb-3">
                <label for="password" class="form-label">Password *</label>
                <input 
                  type="password" 
                  id="password" 
                  v-model="password" 
                  class="form-control"
                  autocomplete="new-password" 
                  :class="{ 'is-valid': validation.password.valid, 'is-invalid': validation.password.valid === false }"
                  required 
                  @blur="validateField('password')"
                />
                <div v-if="validation.password.valid === false" class="invalid-feedback">
                  {{ validation.password.message }}
                </div>
                <div v-if="password" class="form-text">
                  <small class="text-muted">
                    Password strength: 
                    <span :class="passwordStrengthClass">{{ passwordStrengthText }}</span>
                  </small>
                </div>
              </div>
              
              <button type="submit" class="btn btn-primary" :disabled="registering || usernameAvailable === false || !isFormValid">
                {{ registering ? 'Registering...' : 'Register' }}
              </button>
            </form>
            <p class="mt-3">
              Already have an account? <router-link to="/login">Login here</router-link>
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
      first_name: '',
      last_name: '',
      username: '',
      email: '',
      phone_number: '',
      age: '',
      address: '',
      password: '',
      error: null,
      successMessage: '',
      registering: false,
      usernameAvailable: null,
      checkingUsername: false,
      usernameCheckTimeout: null,
      validation: {
        first_name: { valid: null, message: '' },
        last_name: { valid: null, message: '' },
        username: { valid: null, message: '' },
        email: { valid: null, message: '' },
        phone_number: { valid: null, message: '' },
        age: { valid: null, message: '' },
        address: { valid: null, message: '' },
        password: { valid: null, message: '' }
      }
    };
  },
  computed: {
    passwordStrengthText() {
      if (!this.password) return '';
      const strength = this.getPasswordStrength(this.password);
      switch (strength) {
        case 'weak': return 'Weak';
        case 'medium': return 'Medium';
        case 'strong': return 'Strong';
        default: return 'Very Weak';
      }
    },
    passwordStrengthClass() {
      if (!this.password) return '';
      const strength = this.getPasswordStrength(this.password);
      switch (strength) {
        case 'weak': return 'text-warning';
        case 'medium': return 'text-info';
        case 'strong': return 'text-success';
        default: return 'text-danger';
      }
    },
    isFormValid() {
      return Object.values(this.validation).every(field => field.valid === true) && 
             this.usernameAvailable !== false;
    }
  },
  methods: {
    validateField(fieldName) {
      const value = this[fieldName];
      
      switch (fieldName) {
        case 'first_name':
          if (!value.trim()) {
            this.validation.first_name = { valid: false, message: 'First name is required' };
          } else if (value.trim().length < 2) {
            this.validation.first_name = { valid: false, message: 'First name must be at least 2 characters' };
          } else if (!/^[a-zA-Z\s]+$/.test(value.trim())) {
            this.validation.first_name = { valid: false, message: 'First name can only contain letters and spaces' };
          } else {
            this.validation.first_name = { valid: true, message: '' };
          }
          break;
          
        case 'last_name':
          if (!value.trim()) {
            this.validation.last_name = { valid: false, message: 'Last name is required' };
          } else if (value.trim().length < 2) {
            this.validation.last_name = { valid: false, message: 'Last name must be at least 2 characters' };
          } else if (!/^[a-zA-Z\s]+$/.test(value.trim())) {
            this.validation.last_name = { valid: false, message: 'Last name can only contain letters and spaces' };
          } else {
            this.validation.last_name = { valid: true, message: '' };
          }
          break;
          
        case 'username':
          if (!value.trim()) {
            this.validation.username = { valid: false, message: 'Username is required' };
          } else if (value.trim().length < 3) {
            this.validation.username = { valid: false, message: 'Username must be at least 3 characters' };
          } else if (!/^[a-zA-Z0-9_]+$/.test(value.trim())) {
            this.validation.username = { valid: false, message: 'Username can only contain letters, numbers, and underscores' };
          } else {
            this.validation.username = { valid: true, message: '' };
          }
          break;
          
        case 'email':
          if (!value.trim()) {
            this.validation.email = { valid: false, message: 'Email is required' };
          } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value.trim())) {
            this.validation.email = { valid: false, message: 'Please enter a valid email address' };
          } else {
            this.validation.email = { valid: true, message: '' };
          }
          break;
          
        case 'phone_number':
          if (!value.trim()) {
            this.validation.phone_number = { valid: false, message: 'Phone number is required' };
          } else if (!/^[0-9]{10}$/.test(value.trim().replace(/\D/g, ''))) {
            this.validation.phone_number = { valid: false, message: 'Please enter a valid 10-digit phone number' };
          } else {
            this.validation.phone_number = { valid: true, message: '' };
          }
          break;
          
        case 'age':
          if (value !== '' && value !== null && value !== undefined) {
            const ageNum = Number(value);
            if (isNaN(ageNum) || ageNum < 1 || ageNum > 120) {
            this.validation.age = { valid: false, message: 'Age must be between 1 and 120' };
            } else {
            this.validation.age = { valid: true, message: '' };
            }
          } else {
          this.validation.age = { valid: null, message: '' }; // not validated yet
          }
          break;

          
        case 'address':
          if (value && value.trim() && value.trim().length < 10) {
            this.validation.address = { valid: false, message: 'Address must be at least 10 characters if provided' };
          } else {
            this.validation.address = { valid: true, message: '' };
          }
          break;
          
        case 'password':
          if (!value) {
            this.validation.password = { valid: false, message: 'Password is required' };
          } else if (value.length < 8) {
            this.validation.password = { valid: false, message: 'Password must be at least 8 characters' };
          } else {
            this.validation.password = { valid: true, message: '' };
          }
          break;
      }
    },
    
    //length and characters check for pwd
    getPasswordStrength(password) {
      let score = 0;
      
      if (password.length >= 8) score++;
      if (password.length >= 12) score++;
      
      if (/[a-z]/.test(password)) score++;
      if (/[A-Z]/.test(password)) score++;
      if (/[0-9]/.test(password)) score++;
      if (/[^A-Za-z0-9]/.test(password)) score++;
      
      if (score <= 2) return 'weak';
      if (score <= 4) return 'medium';
      return 'strong';
    },
    
    async checkUsernameAvailability() {
      // clear previous timeout
      if (this.usernameCheckTimeout) {
        clearTimeout(this.usernameCheckTimeout);
      }
      
      // initial condition - username is too short - no checking
      if (this.username.length < 3) {
        this.usernameAvailable = null;
        return;
      }
      
      // timeout for debouncing (500ms delay)
      this.usernameCheckTimeout = setTimeout(async () => {
        this.checkingUsername = true;
        try {
          const response = await ApiService.post('/auth/check-username', {
            username: this.username
          });
          this.usernameAvailable = response.data.available;
        } catch (error) {
          // If endpoint doesn't exist, assume available
          this.usernameAvailable = true;
        } finally {
          this.checkingUsername = false;
        }
      }, 500);
    },
    
    validateForm() {
      ['first_name', 'last_name', 'username', 'email', 'phone_number', 'age', 'address', 'password'].forEach(field => {
        this.validateField(field);
      });
      return this.isFormValid;
    },
    
    async register() {
      if (!this.validateForm()) {
        this.error = 'Please fix the validation errors before submitting.';
        return;
      }
      
      this.error = null;
      this.successMessage = '';
      this.registering = true;
      
      try {
        const response = await ApiService.post('/auth/register', {
          first_name: this.first_name,
          last_name: this.last_name,
          username: this.username,
          email: this.email,
          phone_number: this.phone_number,
          age: this.age || null,
          address: this.address,
          password: this.password,
        });
        
        if (response.data.success) {
          this.successMessage = 'Registration successful! Redirecting to login...';
          setTimeout(() => {
            this.$router.push('/login');
          }, 2000);
        } else {
          this.error = response.data.message || 'Registration failed.';
        }
      } catch (error) {
        this.error = error.response?.data?.message || 'An error occurred during registration.';
      } finally {
        this.registering = false;
      }
    },
  },
};
</script> 
