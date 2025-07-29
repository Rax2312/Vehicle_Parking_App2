<template>
  <div>
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
      <div class="container-fluid">
        <a class="navbar-brand" href="#">Vehicle Parking</a>
        <div class="collapse navbar-collapse">
          <ul class="navbar-nav ms-auto mb-2 mb-lg-0">
            <li class="nav-item">
              <router-link class="nav-link" to="/dashboard">Dashboard</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/profile">Profile</router-link>
            </li>
          </ul>
        </div>
      </div>
    </nav>
    <div class="container py-4">
      <h1 class="mb-4">User Dashboard</h1>
      <div class="d-flex justify-content-end mb-3">
        <router-link class="btn btn-outline-info" to="/recent-history">Recent Parking History</router-link>
      </div>

      <!-- Book Spot Form -->
      <div class="card mb-4">
        <div class="card-body">
          <h2 class="h5 mb-3">Book a Parking Spot</h2>
          <form @submit.prevent="bookSpot">
            <div class="row g-3 align-items-end">
              <div class="col-md-4">
                <label class="form-label">Select Parking Lot</label>
                <select class="form-select" v-model="bookingForm.lot_id" required>
                  <option value="" disabled>Select a lot</option>
                  <option v-for="lot in lots" :key="lot.id" :value="lot.id">
                    {{ lot.name }} ({{ lot.available_spots }}/{{ lot.total_spots }} available)
                  </option>
                </select>
              </div>
              <div class="col-md-3">
                <label class="form-label">Vehicle Number</label>
                <input type="text" class="form-control" v-model="bookingForm.vehicle_number" required>
              </div>
              <div class="col-md-3">
                <label class="form-label">Phone Number</label>
                <input type="text" class="form-control" v-model="bookingForm.phone_number" required>
              </div>
              <div class="col-md-2">
                <label class="form-label">Name</label>
                <input type="text" class="form-control" v-model="bookingForm.customer_name" required>
              </div>
            </div>
            <div class="row mt-3">
              <div class="col">
                <label class="form-label">Remarks (optional)</label>
                <input type="text" class="form-control" v-model="bookingForm.remarks">
              </div>
            </div>
            <div class="mt-3">
              <button class="btn btn-success" type="submit" :disabled="booking || isVehicleBooked">
                {{ booking ? 'Booking...' : 'Book Spot' }}
              </button>
              <span v-if="isVehicleBooked" class="text-danger ms-3">Release current spot for this vehicle to book again.</span>
              <span v-else class="text-success ms-3">You can now book a spot.</span>
            </div>
          </form>
        </div>
      </div>

      <!-- Active Reservations Table -->
      <div v-if="activeReservations && activeReservations.length > 0" class="mb-4">
        <div class="card">
          <div class="card-header bg-info text-dark fw-bold">
            Active Reservations
          </div>
          <div class="card-body p-0">
            <div class="table-responsive">
              <table class="table mb-0">
                <thead class="table-light">
                  <tr>
                    <th>Lot</th>
                    <th>Spot</th>
                    <th>Vehicle</th>
                    <th>Since</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="ar in activeReservations" :key="ar.id">
                    <td>{{ ar.lot_name }}</td>
                    <td>{{ ar.spot_number }}</td>
                    <td>{{ ar.vehicle_number }}</td>
                    <td>{{ formatDateTime(ar.parking_timestamp) }}</td>
                    <td>
                      <button class="btn btn-danger btn-sm" @click="releaseSpot(ar.id)" :disabled="releasing">
                        {{ releasing ? 'Releasing...' : 'Release Spot' }}
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- Parking Lots List -->
      <div>
        <h2 class="h5 mb-3">Available Parking Lots</h2>
        <div v-if="loadingLots" class="alert alert-info">Loading parking lots...</div>
        <div v-else-if="lots.length === 0" class="alert alert-warning">No parking lots available.</div>
        <div class="row g-3">
          <div v-for="lot in lots" :key="lot.id" class="col-md-4">
            <div class="card h-100">
              <div class="card-body d-flex flex-column">
                <h5 class="card-title">{{ lot.name }}</h5>
                <p class="mb-1"><strong>Price per Hour:</strong> ₹{{ lot.price_per_hour }}</p>
                <span class="badge bg-primary fs-6 mb-2">
                  Available: {{ lot.available_spots }}/{{ lot.total_spots }}
                </span>
                <button class="btn btn-outline-info btn-sm mt-auto" @click="openLotModal(lot)">
                  View Lot Details
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- User Analytics Section -->
      <div class="mt-5">
        <h2 class="h5 mb-3">My Analytics</h2>
        <div v-if="loadingAnalytics" class="alert alert-info">Loading analytics...</div>
        <div v-else-if="analyticsError" class="alert alert-danger">{{ analyticsError }}</div>
        <div v-else>
          <div v-if="userSummary">
            <UserAnalytics 
              :summary="userSummary"
              :monthly-data="userMonthlyData"
              :reservation-history="reservationHistory"
            />
          </div>
          <div v-else class="alert alert-warning">
            No analytics data available. Make some reservations to see your analytics.
          </div>
        </div>
      </div>

      <!-- Lot Details Modal -->
      <div v-if="showLotModal" class="modal fade" tabindex="-1" :class="{ show: showLotModal }" style="display: block;">
        <div class="modal-dialog modal-lg">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">Parking Lot Details</h5>
              <button type="button" class="btn-close" @click="closeLotModal"></button>
            </div>
            <div class="modal-body" v-if="selectedLotDetails && selectedLotDetails.spots">
              <p><strong>Name:</strong> {{ selectedLotDetails.name }}</p>
              <p><strong>Price per Hour:</strong> ₹{{ selectedLotDetails.price_per_hour }}</p>
              <p><strong>Total Spots:</strong> {{ selectedLotDetails.total_spots }}</p>
              <div class="d-flex flex-wrap gap-2 justify-content-center">
                <div
                  v-for="spot in paginatedSpots"
                  :key="spot.id"
                  class="spot-box"
                  :class="{
                    'spot-occupied': spot.is_occupied || spot.status === 'O',
                    'spot-available': !spot.is_occupied && spot.status === 'A'
                  }"
                >
                  {{ spot.spot_number }}
                </div>
              </div>
              <div v-if="totalPages > 1" class="pagination-controls d-flex justify-content-center mt-3">
                <button class="btn btn-outline-secondary me-2" @click="currentFloor--" :disabled="currentFloor === 1">←</button>
                <span class="align-self-center">Floor {{ currentFloor }} of {{ totalPages }}</span>
                <button class="btn btn-outline-secondary ms-2" @click="currentFloor++" :disabled="currentFloor === totalPages">→</button>
              </div>

              <div class="text-muted mt-2">Green: Available, Red: Occupied</div>

            </div>
            <div class="modal-body" v-else>
              <div class="text-center text-muted py-4">Loading lot details...</div>
            </div>
            <div class="modal-footer">
              <button class="btn btn-secondary" @click="closeLotModal">Close</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Error Modal -->
      <div v-if="showErrorModal" class="modal fade" tabindex="-1" :class="{ show: showErrorModal }" style="display: block;">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">Error</h5>
              <button type="button" class="btn-close" @click="showErrorModal = false"></button>
            </div>
            <div class="modal-body">
              <div class="alert alert-danger">{{ errorMessage }}</div>
            </div>
            <div class="modal-footer">
              <button class="btn btn-secondary" @click="showErrorModal = false">Close</button>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import ApiService from '../services/ApiService';
import UserAnalytics from '../components/UserAnalytics.vue';

export default {
  components: {
    UserAnalytics
  },
  name: 'UserDashboard',
  data() {
    return {
      lots: [],
      loadingLots: false,
      selectedLot: null,
      selectedLotDetails: {
        spots: [],
        name: '',
        price_per_hour: 0,
        total_spots: 0
      },
      showLotModal: false,
      userData: null,
      bookingForm: {
        lot_id: '',
        vehicle_number: '',
        phone_number: '',
        customer_name: '',
        remarks: ''
      },
      booking: false,
      activeReservations: [],
      releasing: false,
      reservationHistory: [],
      loadingHistory: false,
      showErrorModal: false,
      spotsPerFloor: 100,
      currentFloor: 1,
      errorMessage: '',
      loadingAnalytics: false,
      analyticsError: '',
      userSummary: {
        total_cost: 0,
        total_reservations: 0,
        active_reservations: 0,
        completed_reservations: 0,
        total_hours: 0
      },
      userMonthlyData: []
    };
  },
  computed: {
    isVehicleBooked() {
      if (!this.bookingForm.vehicle_number) return false;
      return this.activeReservations.some(ar => ar.vehicle_number === this.bookingForm.vehicle_number);
    },
    paginatedSpots() {
      const start = (this.currentFloor - 1) * this.spotsPerFloor;
      const end = start + this.spotsPerFloor;
      return this.selectedLotDetails.spots.slice(start, end);
    },
    totalPages() {
      return Math.ceil(this.selectedLotDetails.spots.length / this.spotsPerFloor);
    }
  },
  mounted() {
    // Get user data from localStorage
    const userDataStr = localStorage.getItem('userData');
    if (userDataStr) {
      this.userData = JSON.parse(userDataStr);
      // Auto-fill booking form with user data
      this.bookingForm.phone_number = this.userData.phone_number || '';
      this.bookingForm.customer_name = `${this.userData.first_name} ${this.userData.last_name}`;
    }
    this.fetchLots();
    this.fetchActiveReservations();
    this.fetchReservationHistory();
    this.fetchUserAnalytics();
  },
  methods: {
    async fetchLots() {
      this.loadingLots = true;
      try {
        const res = await ApiService.get('/user/parking-lots');
        this.lots = res.data.lots;
      } catch (err) {
        this.showError('Failed to load parking lots.');
      } finally {
        this.loadingLots = false;
      }
    },
    async fetchActiveReservations() {
      try {
        const res = await ApiService.get('/user/reservations/active');
        if (res.data.success) {
          this.activeReservations = res.data.active_reservations || [];
        } else {
          this.activeReservations = [];
        }
      } catch (err) {
        this.activeReservations = [];
      }
    },
    async fetchReservationHistory() {
      this.loadingHistory = true;
      try {
        const res = await ApiService.get('/user/reservations');
        this.reservationHistory = res.data.reservations;
      } catch (err) {
        this.showError('Failed to load reservation history.');
      } finally {
        this.loadingHistory = false;
      }
    },
    async fetchUserAnalytics() {
      this.loadingAnalytics = true;
      try {
        const res = await ApiService.get('/user/analytics');
        this.userSummary = res.data.summary || {
          total_cost: 0,
          total_reservations: 0,
          active_reservations: 0,
          completed_reservations: 0,
          total_hours: 0
        };
        this.userMonthlyData = res.data.monthly_data || {};
      } catch (err) {
        this.analyticsError = err.response?.data?.error || 'Failed to load analytics.';
        this.userSummary = {
          total_cost: 0,
          total_reservations: 0,
          active_reservations: 0,
          completed_reservations: 0,
          total_hours: 0
        };
        this.userMonthlyData = {};
      } finally {
        this.loadingAnalytics = false;
      }
    },
    async bookSpot() {
      if (!this.bookingForm.lot_id) return this.showError('Please select a parking lot.');
      if (this.isVehicleBooked) return this.showError('Release current spot for this vehicle to book again.');
      this.booking = true;
      try {
        const res = await ApiService.post(`/user/parking-lots/${this.bookingForm.lot_id}/reserve`, {
          vehicle_number: this.bookingForm.vehicle_number,
          phone_number: this.bookingForm.phone_number,
          customer_name: this.bookingForm.customer_name,
          remarks: this.bookingForm.remarks
        });
        this.showError('Spot booked successfully!', false);
        this.fetchLots();
        this.fetchActiveReservations();
        this.fetchReservationHistory();
        this.fetchUserAnalytics();
        // Only reset lot_id and vehicle_number, keep phone_number and customer_name
        this.bookingForm.lot_id = '';
        this.bookingForm.vehicle_number = '';
        this.bookingForm.remarks = '';
      } catch (err) {
        const msg = err.response?.data?.error || 'Failed to book spot.';
        this.showError(msg);
      } finally {
        this.booking = false;
      }
    },
    async releaseSpot(reservationId) {
      if (!confirm('Are you sure you want to release this spot?')) return;
      this.releasing = true;
      try {
        await ApiService.post(`/user/reservations/${reservationId}/release`, {});
        this.showError('Spot released successfully!', false);
        this.fetchLots();
        this.fetchActiveReservations();
        this.fetchUserAnalytics();
      } catch (err) {
        const msg = err.response?.data?.error || 'Failed to release spot.';
        this.showError(msg);
      } finally {
        this.releasing = false;
      }
    },
    async openLotModal(lot) {
      this.selectedLot = lot;
      this.showLotModal = true;
      this.selectedLotDetails = {
        spots: [],
        name: '',
        price_per_hour: 0,
        total_spots: 0
      };
      try {
        const res = await ApiService.get(`/user/parking-lots/${lot.id}`);
        this.selectedLotDetails = res.data.lot;
      } catch (err) {
        this.selectedLotDetails = null;
        this.showError('Failed to load lot details.');
      }
    },
    closeLotModal() {
      this.showLotModal = false;
      this.selectedLot = null;
      this.selectedLotDetails = {
        spots: [],
        name: '',
        price_per_hour: 0,
        total_spots: 0
      };
    },
    showError(msg, isError = true) {
      this.errorMessage = msg;
      this.showErrorModal = isError;
      if (!isError) {
        setTimeout(() => { this.showErrorModal = false; }, 1500);
      }
    },
    formatDateTime(dt) {
      if (!dt) return '-';
      const d = new Date(dt);
      return d.toLocaleString('en-IN', {
        timeZone: 'Asia/Kolkata',
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
      });
    }
  }
};
</script>

<style scoped>
.spot-box {
  width: 36px;
  height: 36px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  margin: 2px;
  font-weight: bold;
  font-size: 1rem;
  cursor: default;
  border: 2px solid;
  background-color: rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.spot-available {
  border-color: #28a745;
  color: #28a745;
  box-shadow: 0 0 10px rgba(40, 167, 69, 0.3);
}

.spot-available:hover {
  box-shadow: 0 0 15px rgba(40, 167, 69, 0.5);
  transform: scale(1.05);
}

.spot-occupied {
  border-color: #dc3545;
  color: #dc3545;
  box-shadow: 0 0 10px rgba(220, 53, 69, 0.3);
}

.spot-occupied:hover {
  box-shadow: 0 0 15px rgba(220, 53, 69, 0.5);
  transform: scale(1.05);
}
</style> 
