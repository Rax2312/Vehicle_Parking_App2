<template>
  <div class="container py-4">
    <h2 class="mb-4">Recent Parking History</h2>
    <div class="d-flex align-items-center mb-3">
      <select class="form-select w-auto me-2" v-model="searchType">
        <option value="">Search by...</option>
        <option value="date">Date</option>
        <option value="lot">Parking Lot Name</option>
        <option value="vehicle">Vehicle Number</option>
      </select>
      <div v-if="searchType === 'date'">
        <input type="date" class="form-control w-auto" v-model="searchDate" />
      </div>
      <div v-else-if="searchType === 'lot' || searchType === 'vehicle'">
        <input type="text" class="form-control w-auto" v-model="searchQuery" :placeholder="searchType === 'lot' ? 'Enter parking lot name' : 'Enter vehicle number'" />
      </div>
      <button class="btn btn-primary ms-2" @click="applySearch">Search</button>
      <button class="btn btn-secondary ms-2" @click="resetSearch">Reset</button>
    </div>
    <div v-if="loading" class="alert alert-info">Loading history...</div>
    <div v-else-if="filteredHistory.length === 0" class="alert alert-warning">No parking history found.</div>
    <div v-else class="table-responsive">
      <table class="table table-bordered table-hover">
        <thead class="table-light">
          <tr>
            <th>#</th>
            <th>Date</th>
            <th>Parking Lot</th>
            <th>Vehicle Number</th>
            <th>Time Parked (hrs)</th>
            <th>Revenue Spent (₹)</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(res, idx) in filteredHistory" :key="res.id">
            <td>{{ idx + 1 }}</td>
            <td>{{ formatDate(res.parking_timestamp) }}</td>
            <td>{{ res.lot_name }}</td>
            <td>{{ res.vehicle_number }}</td>
            <td>{{ res.duration_hours ?? '-' }}</td>
            <td>{{ res.cost ?? '-' }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <button class="btn btn-outline-secondary mt-3" @click="$router.push('/dashboard')">Back to Dashboard</button>
  </div>
</template>

<script>
import ApiService from '../services/ApiService';

export default {
  name: 'RecentHistory',
  data() {
    return {
      history: [],
      loading: false,
      searchType: '',
      searchQuery: '',
      searchDate: '',
      filteredHistory: []
    };
  },
  mounted() {
    this.fetchHistory();
  },
  methods: {
    async fetchHistory() {
      this.loading = true;
      try {
        const res = await ApiService.get('/user/reservations');
        this.history = res.data.reservations || [];
        this.filteredHistory = this.history;
      } catch (err) {
        this.history = [];
        this.filteredHistory = [];
      } finally {
        this.loading = false;
      }
    },
    applySearch() {
      if (!this.searchType) {
        this.filteredHistory = this.history;
        return;
      }
      if (this.searchType === 'date' && this.searchDate) {
        this.filteredHistory = this.history.filter(res => {
          const dateStr = this.formatDate(res.parking_timestamp);
          return dateStr === this.formatDate(this.searchDate);
        });
      } else if (this.searchType === 'lot' && this.searchQuery) {
        const q = this.searchQuery.trim().toLowerCase();
        this.filteredHistory = this.history.filter(res =>
          res.lot_name && res.lot_name.toLowerCase().includes(q)
        );
      } else if (this.searchType === 'vehicle' && this.searchQuery) {
        const q = this.searchQuery.trim().toLowerCase();
        this.filteredHistory = this.history.filter(res =>
          res.vehicle_number && res.vehicle_number.toLowerCase().includes(q)
        );
      } else {
        this.filteredHistory = this.history;
      }
    },
    resetSearch() {
      this.searchType = '';
      this.searchQuery = '';
      this.searchDate = '';
      this.filteredHistory = this.history;
    },
    formatDate(dt) {
      if (!dt) return '-';
      const d = new Date(dt);
      return d.toLocaleDateString('en-IN', {
        timeZone: 'Asia/Kolkata',
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      });
    }
  }
};
</script>

<style scoped>
.table th, .table td {
  vertical-align: middle;
}
</style> 