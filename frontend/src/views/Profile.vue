<template>
  <div class="container py-4">
    <h2>User Profile</h2>
    <div v-if="loading" class="alert alert-info">Loading...</div>
    <div v-else>
      <form @submit.prevent="updateDetails">
        <div class="mb-3">
          <label class="form-label">Username</label>
          <input class="form-control" type="text" :value="profile.username" disabled />
        </div>
        <div class="mb-3">
          <label class="form-label">Email</label>
          <input class="form-control" v-model="profile.email" type="email" required />
        </div>
        <div class="mb-3">
          <label class="form-label">First Name</label>
          <input class="form-control" v-model="profile.first_name" type="text" required />
        </div>
        <div class="mb-3">
          <label class="form-label">Last Name</label>
          <input class="form-control" v-model="profile.last_name" type="text" required />
        </div>
        <div class="mb-3">
          <label class="form-label">Phone Number</label>
          <input class="form-control" v-model="profile.phone_number" type="text" required />
        </div>
        <div class="mb-3">
          <label class="form-label">Age</label>
          <input class="form-control" v-model="profile.age" type="number" min="0" />
        </div>
        <div class="mb-3">
          <label class="form-label">Address</label>
          <input class="form-control" v-model="profile.address" type="text" />
        </div>
        <button class="btn btn-primary" type="submit">Update Details</button>
        <span v-if="detailsMsg" class="ms-3 text-success">{{ detailsMsg }}</span>
      </form>
      <hr />
      <h4>Change Password</h4>
      <form @submit.prevent="updatePassword">
        <div class="mb-3">
          <label class="form-label">Current Password</label>
          <input class="form-control" v-model="passwordForm.current_password" type="password" required />
        </div>
        <div class="mb-3">
          <label class="form-label">New Password</label>
          <input class="form-control" v-model="passwordForm.new_password" type="password" required />
        </div>
        <button class="btn btn-warning" type="submit">Update Password</button>
        <span v-if="passwordMsg" :class="{'text-success': passwordSuccess, 'text-danger': !passwordSuccess}" class="ms-3">{{ passwordMsg }}</span>
      </form>
    </div>
  </div>
</template>

<script>
import ApiService from '../services/ApiService'
export default {
  name: 'Profile',
  data() {
    return {
      profile: {},
      loading: true,
      detailsMsg: '',
      passwordForm: {
        current_password: '',
        new_password: ''
      },
      passwordMsg: '',
      passwordSuccess: false
    }
  },
  methods: {
    async fetchProfile() {
      this.loading = true
      try {
        const res = await ApiService.get('/user/profile')
        this.profile = res.data
      } catch (err) {
        this.detailsMsg = 'Failed to load profile.'
      } finally {
        this.loading = false
      }
    },
    async updateDetails() {
      try {
        await ApiService.put('/user/profile', this.profile)
        this.detailsMsg = 'Profile updated successfully!'
      } catch (err) {
        this.detailsMsg = err.response?.data?.message || 'Failed to update profile.'
      }
    },
    async updatePassword() {
      this.passwordMsg = ''
      this.passwordSuccess = false
      try {
        const res = await ApiService.put('/user/profile/password', this.passwordForm)
        this.passwordMsg = res.data.message
        this.passwordSuccess = true
        this.passwordForm.current_password = ''
        this.passwordForm.new_password = ''
      } catch (err) {
        this.passwordMsg = err.response?.data?.message || 'Failed to update password.'
        this.passwordSuccess = false
      }
    }
  },
  mounted() {
    this.fetchProfile()
  }
}
</script>

<style scoped>
.container {
  max-width: 600px;
}
</style> 