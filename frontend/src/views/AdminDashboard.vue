<template>
  <div class="admin-dashboard container py-4">
    <div class="row mb-4 gy-2 align-items-center">
      <div class="col-12 col-md-6">
        <h1 class="mb-2 mb-md-0">Admin Dashboard</h1>
      </div>
      <div class="col-12 col-md-6 text-md-end">
        <div class="btn-group w-100 w-md-auto">
          <button class="btn btn-outline-info w-100 w-md-auto mb-2 mb-md-0 me-0 me-md-2" @click="openRecordsModal">
            View All Records
          </button>
          <button class="btn btn-outline-primary w-100 w-md-auto" @click="fetchUsers">
            View Users
          </button>
        </div>
      </div>
    </div>

    <!-- Create Parking Lot Button -->
    <div class="mb-4 text-center text-md-start">
      <button 
        class="btn btn-success btn-lg w-100 w-md-auto" 
        @click="toggleCreateForm"
        :class="{ 'btn-outline-success': showCreateForm }"
      >
        <i class="bi bi-plus-circle me-2"></i>
        {{ showCreateForm ? 'Hide Create Form' : 'Create Parking Lot' }}
      </button>
    </div>

    <!-- Search Functionality -->
    <div class="mb-4">
      <div class="row align-items-center g-2">
        <div class="col-12 col-md-4 mb-2 mb-md-0">
          <div class="dropdown w-100">
            <button 
              class="btn btn-outline-secondary dropdown-toggle w-100" 
              type="button" 
              data-bs-toggle="dropdown" 
              aria-expanded="false"
            >
              {{ searchType || 'Search' }}
            </button>
            <ul class="dropdown-menu w-100">
              <li><a class="dropdown-item" href="#" @click.prevent="setSearchType('Parking Lots')">Parking Lots</a></li>
              <li><a class="dropdown-item" href="#" @click.prevent="setSearchType('Parking Spots (Available/Occupied)')">Parking Spots (Available/Occupied)</a></li>
              <li><a class="dropdown-item" href="#" @click.prevent="setSearchType('Users')">Users</a></li>
            </ul>
          </div>
        </div>
        <div class="col-12 col-md-8">
          <div class="input-group flex-nowrap">
            <span class="input-group-text">
              <i class="bi bi-search"></i>
            </span>
            <input 
              type="text" 
              class="form-control" 
              placeholder="Search..." 
              v-model="searchQuery"
              @input="performSearch"
              @keyup.enter="performSearch"
            >
            <button class="btn btn-primary" type="button" @click="performSearch">
              <i class="bi bi-search me-1"></i>Search
            </button>
            <button v-if="searchQuery" class="btn btn-outline-secondary" type="button" @click="clearSearch">
              <i class="bi bi-x"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Search Results -->
    <div v-if="searchType && searchQuery" class="mb-4">
      <div class="card">
        <div class="card-header d-flex flex-column flex-md-row justify-content-between align-items-center">
          <h5 class="mb-2 mb-md-0">Search Results ({{ searchResults.length }})</h5>
          <button class="btn btn-sm btn-outline-secondary w-100 w-md-auto" @click="clearSearch">Clear</button>
        </div>
        <div class="card-body">
          <!-- No Results Message -->
          <div v-if="searchResults.length === 0" class="text-center text-muted py-4">
            <i class="bi bi-search fs-1 mb-3"></i>
            <p class="mb-0">No results found for "{{ searchQuery }}"</p>
            <small>Try different keywords or search criteria</small>
          </div>

          <!-- Parking Lots Search Results -->
          <div v-else-if="searchType === 'Parking Lots'" class="row g-3">
            <div v-for="lot in searchResults" :key="lot.id" class="col-12 col-md-6">
              <div class="card h-100">
                <div class="card-body">
                  <h6 class="card-title">{{ lot.name }}</h6>
                  <p class="card-text small mb-1"><strong>Address:</strong> {{ lot.address }}</p>
                  <p class="card-text small mb-1"><strong>Pin Code:</strong> {{ lot.pin_code }}</p>
                  <p class="card-text small mb-2"><strong>Price:</strong> ₹{{ lot.price_per_hour }}/hour</p>
                  <div class="d-flex flex-column flex-sm-row justify-content-between align-items-start align-items-sm-center gap-2">
                    <span class="badge bg-primary">{{ lot.occupied }}/{{ lot.total_spots }} occupied</span>
                    <div class="btn-group btn-group-sm">
                      <button class="btn btn-outline-info btn-sm" @click="openViewLot(lot)">View</button>
                      <button class="btn btn-outline-primary btn-sm" @click="editLot(lot)">Edit</button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Parking Spots Search Results -->
          <div v-else-if="searchType === 'Parking Spots (Available/Occupied)'" class="table-responsive">
            <table class="table table-sm table-bordered">
              <thead class="table-light">
                <tr>
                  <th>Spot #</th>
                  <th>Lot</th>
                  <th>Address</th>
                  <th>Status</th>
                  <th>Floor</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="spot in searchResults" :key="spot.id">
                  <td>{{ spot.spot_number }}</td>
                  <td>{{ spot.lot_name }}</td>
                  <td>{{ spot.lot_address }}</td>
                  <td>
                    <span :class="spot.status === 'A' ? 'badge bg-success' : 'badge bg-warning'">
                      {{ spot.status === 'A' ? 'Available' : 'Occupied' }}
                    </span>
                  </td>
                  <td>{{ spot.floor }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Users Search Results -->
          <div v-else-if="searchType === 'Users'" class="table-responsive">
            <table class="table table-sm table-bordered">
              <thead class="table-light">
                <tr>
                  <th>Name</th>
                  <th>Username</th>
                  <th>Email</th>
                  <th>Phone</th>
                  <th>Role</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="user in searchResults" :key="user.id">
                  <td>{{ user.first_name }} {{ user.last_name }}</td>
                  <td>{{ user.username }}</td>
                  <td>{{ user.email }}</td>
                  <td>{{ user.phone_number }}</td>
                  <td>
                    <span :class="user.role === 'admin' ? 'badge bg-danger' : 'badge bg-secondary'">
                      {{ user.role }}
                    </span>
                  </td>
                  <td>
                    <span :class="user.flagged ? 'badge bg-warning' : 'badge bg-success'">
                      {{ user.flagged ? 'Flagged' : 'Normal' }}
                    </span>
                  </td>
                  <td>
                    <button class="btn btn-outline-info btn-sm" @click="openUserModal(user.id)">
                      View Details
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Create/Edit Parking Lot Form (Collapsible) -->
    <div v-if="showCreateForm" class="card mb-4">
      <div class="card-body">
        <h2 class="h5 mb-3">{{ editingLot ? 'Edit Parking Lot' : 'Create New Parking Lot' }}</h2>
        <form @submit.prevent="editingLot ? updateParkingLot() : createParkingLot()">
          <div class="row">
            <div class="col-md-6">
              <div class="mb-3">
                <label class="form-label">Location Name</label>
                <input type="text" class="form-control" v-model="lotForm.prime_location_name" required>
              </div>
            </div>
            <div class="col-md-6">
              <div class="mb-3">
                <label class="form-label">Price per Hour (₹)</label>
                <input type="number" class="form-control" v-model="lotForm.price" required step="1" min="1">
              </div>
            </div>
          </div>
          <div class="row">
            <div class="col-md-6">
              <div class="mb-3">
                <label class="form-label">Address</label>
                <textarea class="form-control" v-model="lotForm.address" required rows="3"></textarea>
              </div>
            </div>
            <div class="col-md-6">
              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Pin Code</label>
                    <input type="text" class="form-control" v-model="lotForm.pin_code" required>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Number of Spots</label>
                    <input type="number" class="form-control" v-model="lotForm.number_of_spots" required min="1">
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="d-flex gap-2">
            <button type="submit" class="btn btn-success">
              {{ editingLot ? 'Update Parking Lot' : 'Create Parking Lot' }}
            </button>
            <button v-if="editingLot" type="button" class="btn btn-secondary" @click="cancelEdit">Cancel</button>
            <button type="button" class="btn btn-outline-secondary" @click="toggleCreateForm">Close Form</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Parking Lots List -->
    <div>
      <h2 class="h5 mb-3">Parking Lots</h2>
      <div v-if="loading" class="alert alert-info">Loading parking lots...</div>
      <div v-else-if="error" class="alert alert-danger">{{ error }}</div>
      <div class="row g-3">
        <div v-for="lot in parkingLots" :key="lot.id" class="col-md-4">
          <div class="card h-100">
            <div class="card-body d-flex flex-column">
              <h5 class="card-title">{{ lot.name }}</h5>
              <div class="mb-2">
                <span class="badge bg-primary fs-6">
                  Occupied: {{ lot.occupied }}/{{ lot.total_spots }}
                </span>
              </div>
              <div class="mt-auto d-flex gap-2">
                <button class="btn btn-outline-info btn-sm" @click="openViewLot(lot)">View</button>
                <button class="btn btn-outline-primary btn-sm" @click="editLot(lot)">Edit</button>
                <button class="btn btn-outline-danger btn-sm" @click="confirmDeleteLot(lot)">Delete</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Users List -->
    <div v-if="users.length > 0" class="mt-5">
      <h2 class="h5 mb-3">Users</h2>
      <div class="table-responsive">
        <table class="table table-bordered table-hover">
          <thead class="table-light">
            <tr>
              <th>#</th>
              <th>Name</th>
              <th>Username</th>
              <th>Email</th>
              <th>Phone</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(user, idx) in users" :key="user.id">
              <td>{{ idx + 1 }}</td>
              <td>{{ user.first_name }} {{ user.last_name }}</td>
              <td>{{ user.username }}</td>
              <td>{{ user.email }}</td>
              <td>{{ user.phone_number }}</td>
              <td>
                <button class="btn btn-outline-info btn-sm" @click="openUserModal(user.id)">
                  View Details
                </button>
                <button v-if="user.role !== 'admin' && !user.flagged" class="btn btn-warning btn-sm ms-2" @click="flagUser(user.id)">
                  Flag User
                </button>
                <button v-if="user.role !== 'admin' && user.flagged" class="btn btn-success btn-sm ms-2" @click="unflagUser(user.id)">
                  Unflag User
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Analytics Section -->
    <div class="mt-5">
      <h2 class="h5 mb-3">Analytics Dashboard</h2>
      <button class="btn btn-outline-success mb-3" @click="exportUsersCSV">Export Users CSV</button>
      <div v-if="loadingAnalytics" class="alert alert-info">Loading analytics...</div>
      <div v-else-if="analyticsError" class="alert alert-danger">{{ analyticsError }}</div>
      <div v-else>
        <div v-if="analyticsSummary">
          <ParkingAnalytics 
            :summary="analyticsSummary"
            :monthly-data="analyticsMonthlyData"
            :lot-data="analyticsLotData"
          />
        </div>
        <div v-else class="alert alert-warning">
          No analytics data available. Create some parking lots and reservations to see analytics.
        </div>
      </div>
    </div>

    <!-- View Lot Modal -->
    <div class="modal fade" tabindex="-1" :class="{ show: showViewModal }" style="display: block;" v-if="showViewModal">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Parking Lot Details</h5>
            <button type="button" class="btn-close" @click="closeViewLot"></button>
          </div>
          <div class="modal-body">
            <div v-if="!viewLotDetails" class="text-center text-muted py-4">
              Loading...
            </div>
            <div v-else>
              <p><strong>Location Name:</strong> {{ viewLotDetails.name }}</p>
              <p><strong>Price per Hour:</strong> ₹{{ viewLotDetails.price_per_hour }}</p>
              <p><strong>Address:</strong> {{ viewLotDetails.address }}</p>
              <p><strong>Pin Code:</strong> {{ viewLotDetails.pin_code }}</p>
              <p><strong>Number of Spots:</strong> {{ viewLotDetails.total_spots }}</p>
              <p>
                <strong>Floors:</strong>
                {{ totalFloors(viewLotDetails.total_spots) }}
                <span v-for="floor in totalFloors(viewLotDetails.total_spots)" :key="floor">
                  <br>
                  Floor {{ floor }}: 
                  {{ floorStart(floor) }} - {{ floorEnd(floor, viewLotDetails.total_spots) }}
                </span>
              </p>
              <div class="d-flex align-items-center mb-3">
                <span
                  class="badge fs-6 status-badge"
                  :class="{'bg-success': viewLotDetails.occupied === 0, 'bg-warning': viewLotDetails.occupied > 0}"
                  @mouseover="hoverStatus = true"
                  @mouseleave="hoverStatus = false"
                  @click="openStatusModal(viewLotDetails)"
                  style="cursor:pointer; transition:0.2s; background-color: #007bff; color: white;"
                  :style="hoverStatus ? 'transform:scale(1.1);border:2px solid #007bff;' : ''"
                >
                  Status: {{ viewLotDetails.occupied }}/{{ viewLotDetails.total_spots }} occupied
                </span>
              </div>
            </div>
          </div>
          <div class="modal-footer" v-if="viewLotDetails">
            <button
              class="btn btn-danger"
              :disabled="viewLotDetails.occupied > 0"
              @click="deleteLot(viewLotDetails.id)"
            >
              Delete
            </button>
            <button class="btn btn-secondary" @click="closeViewLot">Close</button>
          </div>
        </div>
      </div>
    </div>
    

    <!-- Status Modal (Grid of Spots) -->
    <div v-if="showStatusModal" class="modal-backdrop">
      <div class="modal-content">
        <div class="lot-header">
          <h2>{{ statusLot.name }} ({{ statusLot.address }})</h2>
          <p>
            Available: {{ statusLot.available_spots }} |
            Occupied: {{ statusLot.occupied_spots }}
          </p>
        </div>
        <div v-if="totalPages > 1" class="pagination-controls">
          <button @click="currentFloor--" :disabled="currentFloor === 1">←</button>
          <span>Floor {{ currentFloor }} of {{ totalPages }}</span>
          <button @click="currentFloor++" :disabled="currentFloor === totalPages">→</button>
        </div>

        <div class="spot-grid" v-if="statusLot.spots && statusLot.spots.length > 0">
          <div
            v-for="spot in paginatedSpots"
            :key="spot.id"
            :class="['spot-box', spot.status === 'A' ? 'available' : 'occupied']"
            @click="spot.status === 'O' ? openSpotDetails(spot.id) : null"
            :style="spot.status === 'O' ? 'cursor: pointer;' : ''"
            :title="spot.status === 'O' ? 'Click to view user details' : 'Available spot'"
          >
            {{ spot.spot_number }}
          </div>
        </div>
        <div v-else class="text-muted">No spots available</div>
        <button @click="closeStatusModal">Close</button>
      </div>
    </div>

    <!-- Occupied Spot Details Modal -->
    <div class="modal fade" tabindex="-1" :class="{ show: showSpotModal }" style="display: block;" v-if="showSpotModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Occupied Parking Spot Details</h5>
            <button type="button" class="btn-close" @click="closeSpotModal"></button>
          </div>
          <div class="modal-body" v-if="spotDetails">
            <p><strong>Spot ID:</strong> {{ spotDetails.spot_number }}</p>
            <p><strong>Customer ID:</strong> {{ spotDetails.reservation?.customer_id }}</p>
            <p><strong>Customer Name:</strong> {{ spotDetails.reservation?.customer_name }}</p>
            <p><strong>Vehicle Number:</strong> {{ spotDetails.reservation?.vehicle_number }}</p>
            <p><strong>Phone Number:</strong> {{ spotDetails.reservation?.phone_number }}</p>
            <p><strong>Date of Parking:</strong> {{ formatDate(spotDetails.reservation?.parking_timestamp) }}</p>
            <p><strong>Time of Parking:</strong> {{ formatTime(spotDetails.reservation?.parking_timestamp) }}</p>
            <p><strong>Estimated Parking Cost:</strong> ₹{{ spotDetails.reservation?.parking_cost || 'N/A' }}</p>
            <p><strong>Remarks:</strong> {{ spotDetails.reservation?.remarks || 'N/A' }}</p>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="closeSpotModal">Close</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Alert Modal -->
    <div class="modal fade" tabindex="-1" :class="{ show: showDeleteModal }" style="display: block;" v-if="showDeleteModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Delete Parking Lot</h5>
            <button type="button" class="btn-close" @click="closeDeleteModal"></button>
          </div>
          <div class="modal-body">
            <p v-if="deleteLotObj && deleteLotObj.occupied > 0" class="text-danger">
              Cannot delete this parking lot because some spots are occupied!
            </p>
            <p v-else>
              Are you sure you want to delete this parking lot?
            </p>
          </div>
          <div class="modal-footer">
            <button class="btn btn-danger" :disabled="deleteLotObj && deleteLotObj.occupied > 0" @click="deleteLot(deleteLotObj.id)">Delete</button>
            <button class="btn btn-secondary" @click="closeDeleteModal">Cancel</button>
          </div>
        </div>
      </div>
    </div>

    <!-- All Parking Records Modal -->
    <div class="modal fade" tabindex="-1" :class="{ show: showRecordsModal }" style="display: block;" v-if="showRecordsModal">
      <div class="modal-dialog modal-xl">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">All Parking Records</h5>
            <button type="button" class="btn-close" @click="closeRecordsModal"></button>
          </div>
          <div class="modal-body">
            <div v-if="loadingRecords" class="text-center text-muted py-4">
              Loading records...
            </div>
            <div v-else-if="!parkingRecords || parkingRecords.length === 0" class="text-center text-muted py-4">
              No parking records found.
            </div>
            <div v-else class="table-responsive">
              <table class="table table-bordered table-hover">
                <thead class="table-light">
                  <tr>
                    <th>#</th>
                    <th>User</th>
                    <th>Lot</th>
                    <th>Spot</th>
                    <th>Vehicle</th>
                    <th>Start</th>
                    <th>End</th>
                    <th>Duration (hrs)</th>
                    <th>Cost (₹)</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(record, idx) in parkingRecords" :key="record.id">
                    <td>{{ idx + 1 }}</td>
                    <td>{{ record.user_name }}</td>
                    <td>{{ record.lot_name }}</td>
                    <td>{{ record.spot_number }}</td>
                    <td>{{ record.vehicle_number }}</td>
                    <td>{{ formatDateTime(record.parking_timestamp) }}</td>
                    <td>{{ record.leaving_timestamp ? formatDateTime(record.leaving_timestamp) : '-' }}</td>
                    <td>{{ record.duration_hours ?? '-' }}</td>
                    <td>{{ record.cost ?? '-' }}</td>
                    <td>
                      <span :class="record.status === 'Active' ? 'badge bg-success' : 'badge bg-secondary'">
                        {{ record.status }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="closeRecordsModal">Close</button>
          </div>
        </div>
      </div>
    </div>

    <!-- User Details Modal -->
    <div class="modal fade" tabindex="-1" :class="{ show: showUserModal }" style="display: block;" v-if="showUserModal">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">User Details</h5>
            <button type="button" class="btn-close" @click="closeUserModal"></button>
          </div>
          <div class="modal-body">
            <div v-if="selectedUserDetails && selectedUserDetails.id">
              <div class="row">
                <div class="col-md-6">
                  <h6>Personal Information</h6>
                  <p><strong>Name:</strong> {{ selectedUserDetails.first_name || '-' }} {{ selectedUserDetails.last_name || '-' }}</p>
                  <p><strong>Username:</strong> {{ selectedUserDetails.username || '-' }}</p>
                  <p><strong>Email:</strong> {{ selectedUserDetails.email || '-' }}</p>
                  <p><strong>Phone:</strong> {{ selectedUserDetails.phone_number || '-' }}</p>
                  <p><strong>Address:</strong> {{ selectedUserDetails.address || '-' }}</p>
                  <p><strong>Age:</strong> {{ selectedUserDetails.age || '-' }}</p>
                  <p><strong>Member Since:</strong> {{ selectedUserDetails.created_at ? formatDateTime(selectedUserDetails.created_at) : '-' }}</p>
                  <p><strong>Role:</strong> {{ selectedUserDetails.role || '-' }}</p>
                  <p><strong>Status:</strong>
                    <span v-if="selectedUserDetails.flagged" class="badge bg-danger">Flagged</span>
                    <span v-else class="badge bg-success">Normal</span>
                  </p>
                </div>
              </div>
              <hr>
              <h6>Reservation History</h6>
              <div v-if="selectedUserDetails.reservations && selectedUserDetails.reservations.length > 0" class="table-responsive">
                <table class="table table-sm table-bordered">
                  <thead class="table-light">
                    <tr>
                      <th>Lot</th>
                      <th>Spot</th>
                      <th>Vehicle</th>
                      <th>Start</th>
                      <th>End</th>
                      <th>Cost</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="res in selectedUserDetails.reservations" :key="res.id">
                      <td>{{ res.lot_name }}</td>
                      <td>{{ res.spot_number }}</td>
                      <td>{{ res.vehicle_number }}</td>
                      <td>{{ formatDateTime(res.parking_timestamp) }}</td>
                      <td>{{ res.leaving_timestamp ? formatDateTime(res.leaving_timestamp) : '-' }}</td>
                      <td>{{ res.cost ?? '-' }}</td>
                      <td>
                        <span :class="res.status === 'Active' ? 'badge bg-success' : 'badge bg-secondary'">
                          {{ res.status }}
                        </span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <div v-else class="text-muted">None</div>
            </div>
            <div v-else class="text-danger">
              No user details available to display.
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="closeUserModal">Close</button>
            <button v-if="selectedUserDetails && selectedUserDetails.flagged && selectedUserDetails.role !== 'admin'" class="btn btn-success ms-2" @click="unflagUser(selectedUserDetails.id)">Unflag User</button>
          </div>
        </div>
      </div>
    </div>
    </div>
  </template> 

<script>
import ApiService from '../services/ApiService'
import ParkingAnalytics from '../components/ParkingAnalytics.vue'

export default {
  components: {
    ParkingAnalytics
  },
  name: 'AdminDashboard',
  data() {
    return {
      parkingLots: [],
      loading: false,
      error: '',
      showCreateForm: false,
      editingLot: null,
      lotForm: {
        prime_location_name: '',
        price: '',
        address: '',
        pin_code: '',
        number_of_spots: ''
      },
      users: [],
      showUserModal: false,
      selectedUser: null,
      userReservations: [],
      loadingUserReservations: false,
      showRecordsModal: false,
      parkingRecords: [],
      loadingRecords: false,
      showViewModal: false,
      viewLotDetails: null,
      showStatusModal: false,
      statusLot: {
        spots: [],
        available_spots: 0,
        occupied_spots: 0,
        name: '',
        address: ''
      },
      showSpotModal: false,
      spotDetails: null,
      deleteLotObj: null,
      showDeleteModal: false,
      spotsPerFloor: 100,
      currentFloor: 1,
      hoverStatus: false,
      loadingAnalytics: false,
      analyticsError: '',
      analyticsSummary: {},
      analyticsMonthlyData: {},
      analyticsLotData: {},
      selectedUserDetails: null, 
      // Search functionality
      searchType: '',
      searchQuery: '',
      searchResults: [],
      searchTimeout: null,
    };
  },
  computed: {
    spotsForCurrentFloor() {
      if (!this.statusLot || !this.statusLot.spots) return [];
      const start = (this.currentFloor - 1) * this.spotsPerFloor + 1;
      const end = this.currentFloor * this.spotsPerFloor;
      return this.statusLot.spots.filter(
        s => s.spot_number >= start && s.spot_number <= end
      );
    },
    paginatedSpots() {
      const start = (this.currentFloor - 1) * this.spotsPerFloor;
      const end = start + this.spotsPerFloor;
      return this.statusLot.spots.slice(start, end);
    },
    totalPages() {
      return Math.ceil(this.statusLot.spots.length / this.spotsPerFloor);
    },
    userDetailsLogger() {
      if (this.selectedUserDetails) {
        console.log('User details in modal:', this.selectedUserDetails);
      }
      return null;
    }
  },
  watch: {
    selectedUserDetails(newVal) {
      console.log('selectedUserDetails changed:', newVal);
    }
  },
  methods: {
    async fetchParkingLots() {
      this.loading = true;
      this.error = '';
      try {
        console.log('Fetching parking lots...');
        const response = await ApiService.get('/admin/parking-lots');
        console.log('Parking lots response:', response);
        this.parkingLots = response.data;
      } catch (err) {
        console.error('Error fetching parking lots:', err);
        console.error('Error response:', err.response);
        console.error('Error status:', err.response?.status);
        console.error('Error data:', err.response?.data);
        this.error = err.response?.data?.error || 'Error loading parking lots';
      } finally {
        this.loading = false;
      }
    },
    async createParkingLot() {
      this.error = ''
      try {
        await ApiService.post('/admin/parking-lots', this.lotForm)
        this.resetForm()
        this.fetchParkingLots()
      } catch (err) {
        this.error = 'Error creating parking lot'
      }
    },
    editLot(lot) {
      console.log('Edit button clicked for lot:', lot);
      this.editingLot = lot.id;
      // Mapping backend fields to form fields for timely update
      this.lotForm = {
        prime_location_name: lot.name || lot.prime_location_name || '',
        price: lot.price_per_hour || lot.price || '',
        address: lot.address || '',
        pin_code: lot.pin_code || '',
        number_of_spots: lot.total_spots || lot.number_of_spots || ''
      };
      this.showCreateForm = true;
      console.log('editingLot:', this.editingLot, 'lotForm:', this.lotForm, 'showCreateForm:', this.showCreateForm);
    },
    async updateParkingLot() {
      this.error = ''
      try {
        await ApiService.put(`/admin/parking-lots/${this.editingLot}`, this.lotForm)
        this.resetForm()
        this.fetchParkingLots()
      } catch (err) {
        this.error = 'Error updating parking lot'
      }
    },
    cancelEdit() {
      this.resetForm()
    },
    resetForm() {
      this.lotForm = {
        prime_location_name: '',
        price: '',
        address: '',
        pin_code: '',
        number_of_spots: ''
      }
      this.editingLot = null
    },
    openViewLot(lot) {
      this.viewLotDetails = null
      this.showViewModal = true
      ApiService.get(`/admin/parking-lots/${lot.id}/details`)
        .then(res => {
          this.viewLotDetails = res.data
        })
        .catch((err) => {
          console.error('Error loading lot details:', err);
          this.error = 'Error loading lot details'
          this.showViewModal = false
        })
    },
    closeViewLot() {
      this.showViewModal = false
      this.viewLotDetails = null
    },
    async openStatusModal(lot) {
      this.statusLot = {
        spots: [],
        available_spots: 0,
        occupied_spots: 0,
        name: '',
        address: ''
      };
      this.showStatusModal = true;
      this.showViewModal = false; 
      
      try {
        const response = await ApiService.get(`/admin/parking-lots/${lot.id}/details`);
        this.statusLot = response.data;
      } catch (err) {
        console.error('Failed to fetch lot details:', err);
        this.showStatusModal = false;
      }
    },
    closeStatusModal() {
      this.showStatusModal = false;
      // reset statusLot if req
      // this.statusLot = { spots: [], available_spots: 0, occupied_spots: 0, name: '', address: '' };
    },
    openSpotDetails(spotId) {
      this.spotDetails = null
      this.showSpotModal = true
      ApiService.get(`/admin/parking-spots/${spotId}/details`)
        .then(res => {
          this.spotDetails = res.data
        })
        .catch(() => {
          this.error = 'Error loading spot details'
          this.showSpotModal = false
        })
    },
    closeSpotModal() {
      this.showSpotModal = false
      this.spotDetails = null
    },
    totalFloors(numSpots) {
      return Math.ceil(numSpots / this.spotsPerFloor);
    },
    floorStart(floor) {
      return (floor - 1) * this.spotsPerFloor + 1;
    },
    floorEnd(floor, numSpots) {
      return Math.min(floor * this.spotsPerFloor, numSpots);
    },
    confirmDeleteLot(lot) {
      this.deleteLotObj = lot
      this.showDeleteModal = true
    },
    closeDeleteModal() {
      this.showDeleteModal = false
      this.deleteLotObj = null
    },
    async deleteLot(lotId) {
      if (this.deleteLotObj && this.deleteLotObj.occupied > 0) {
        this.closeDeleteModal()
        return
      }
      try {
        await ApiService.delete(`/admin/parking-lots/${lotId}`)
        this.fetchParkingLots()
      } catch (err) {
        this.error = 'Error deleting parking lot'
      }
      this.closeDeleteModal()
      this.closeViewLot()
    },
    formatDate(dt) {
      if (!dt) return ''
      return new Date(dt).toLocaleDateString()
    },
    formatTime(dt) {
      if (!dt) return ''
      return new Date(dt).toLocaleTimeString()
    },
    formatDateTime(dt) {
      if (!dt) return '-'
      return new Date(dt).toLocaleString()
    },
    async openRecordsModal() {
      this.showRecordsModal = true
      this.loadingRecords = true
      try {
        const res = await ApiService.get('/admin/parking-records')
        this.parkingRecords = res.data.records
      } catch (err) {
        this.error = 'Error loading parking records'
      } finally {
        this.loadingRecords = false
      }
    },
    closeRecordsModal() {
      this.showRecordsModal = false
      this.parkingRecords = []
    },
    async openUserModal(userId) {
      this.showUserModal = true;
      this.selectedUserDetails = null;
      try {
        const res = await ApiService.get(`/admin/users/${userId}/details`);
        if (!res.data.reservations) res.data.reservations = [];
        this.selectedUserDetails = res.data || {};
      } catch (err) {
        this.error = 'Error loading user details';
        this.showUserModal = false;
      }
    },
    closeUserModal() {
      this.showUserModal = false
      this.selectedUserDetails = null
    },
    async fetchUsers() {
      try {
        const res = await ApiService.get('/admin/users')
        this.users = res.data
      } catch (err) {
        this.error = 'Error loading users'
      }
    },
    toggleCreateForm() {
      this.showCreateForm = !this.showCreateForm
      if (!this.showCreateForm) {
        this.resetForm() 
      }
    },
    async fetchAnalytics() {
      this.loadingAnalytics = true;
      this.analyticsError = '';
      try {
        console.log('Fetching analytics...');
        const [summaryRes, monthlyRes, lotRes] = await Promise.all([
          ApiService.get('/admin/analytics/summary'),
          ApiService.get('/admin/analytics/monthly'),
          ApiService.get('/admin/analytics/lot')
        ]);
        console.log('Analytics responses:', { summaryRes, monthlyRes, lotRes });
        console.log('Summary data:', summaryRes.data);
        console.log('Monthly data:', monthlyRes.data);
        console.log('Lot data:', lotRes.data);
        
        this.analyticsSummary = summaryRes.data || {
          total_revenue: 0,
          total_reservations: 0,
          active_reservations: 0,
          completed_reservations: 0,
          occupied_spots: 0
        };
        this.analyticsMonthlyData = monthlyRes.data || {};
        this.analyticsLotData = lotRes.data || [];
        
        console.log('Final analytics data:', {
          summary: this.analyticsSummary,
          monthly: this.analyticsMonthlyData,
          lot: this.analyticsLotData
        });
      } catch (err) {
        console.error('Analytics error:', err);
        console.error('Analytics error response:', err.response);
        console.error('Analytics error status:', err.response?.status);
        console.error('Analytics error data:', err.response?.data);
        this.analyticsError = 'Error loading analytics data';
        // default values to prevent null errors
        this.analyticsSummary = {
          total_revenue: 0,
          total_reservations: 0,
          active_reservations: 0,
          completed_reservations: 0,
          occupied_spots: 0
        };
        this.analyticsMonthlyData = {};
        this.analyticsLotData = [];
      } finally {
        this.loadingAnalytics = false;
      }
    },
    async flagUser(userId) {
      try {
        await ApiService.post(`/admin/users/${userId}/flag`);
        // Update the flagged status in the users array when flagged
        const user = this.users.find(u => u.id === userId);
        if (user) user.flagged = true;
        this.error = 'User flagged successfully!';
      } catch (err) {
        this.error = 'Error flagging user: ' + (err.response?.data?.error || err.message);
      }
    },
    async unflagUser(userId) {
      try {
        await ApiService.post(`/admin/users/${userId}/unflag`);
        // Update the flagged status in the users array when unflagged
        const user = this.users.find(u => u.id === userId);
        if (user) user.flagged = false;
        this.error = 'User unflagged successfully!';
      } catch (err) {
        this.error = 'Error unflagging user: ' + (err.response?.data?.error || err.message);
      }
    },
    async exportUsersCSV() {
      try {
        // export task
        const res = await ApiService.post('/admin/export-users-csv');
        const taskId = res.data.task_id;
        
        // loading message
        this.error = 'Exporting users to CSV... Please wait.';
        
        // Poll for task completion
        let attempts = 0;
        const maxAttempts = 30; // 30 seconds timeout
        
        while (attempts < maxAttempts) {
          try {
            // Poll status endpoint
            const statusRes = await ApiService.get(`/admin/export-users-csv/${taskId}/status?t=${Date.now()}`);
            if (statusRes.data.state === 'SUCCESS') {
              // Downloading file
              const fileRes = await ApiService.get(`/admin/export-users-csv/${taskId}/download`, {
                responseType: 'blob'
              });
              const url = window.URL.createObjectURL(new Blob([fileRes.data]));
              const link = document.createElement('a');
              link.href = url;
              link.setAttribute('download', `users_export_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.csv`);
              document.body.appendChild(link);
              link.click();
              link.remove();
              window.URL.revokeObjectURL(url);
              this.error = 'CSV export completed successfully!';
              return;
            } else if (statusRes.data.state === 'FAILURE') {
              this.error = `Export failed: ${statusRes.data.error}`;
              return;
            } else {
              await new Promise(resolve => setTimeout(resolve, 1000));
              attempts++;
            }
          } catch (pollErr) {
            if (pollErr.response && (pollErr.response.status === 202 || pollErr.response.status === 404)) {
              await new Promise(resolve => setTimeout(resolve, 1000));
              attempts++;
              continue;
            }
            this.error = `Export failed: ${pollErr.response?.data?.error || pollErr.message}`;
            return;
          }
        }
        this.error = 'Export timed out. Please try again.';
      } catch (err) {
        this.error = `Failed to start export: ${err.response?.data?.error || err.message}`;
      }
    },
    // Search functionality 
    setSearchType(type) {
      this.searchType = type;
      this.searchQuery = '';
      this.searchResults = [];
    },
    async performSearch() {
      if (!this.searchType || !this.searchQuery.trim()) {
        this.searchResults = [];
        return;
      }

      console.log('Performing search:', {
        type: this.searchType,
        query: this.searchQuery,
        trimmed: this.searchQuery.trim()
      });

      // Clear previous timeout
      if (this.searchTimeout) {
        clearTimeout(this.searchTimeout);
      }

      // Debounce search
      this.searchTimeout = setTimeout(async () => {
        try {
          let endpoint = '';
          let params = { q: this.searchQuery.trim() };

          switch (this.searchType) {
            case 'Parking Lots':
              endpoint = '/admin/search/parking-lots';
              break;
            case 'Parking Spots (Available/Occupied)':
              endpoint = '/admin/search/parking-spots';
              // does query contains status keywords
              const query = this.searchQuery.trim().toLowerCase();
              if (query.includes('available') || query.includes('free') || query.includes('open')) {
                params.status = 'available';
                // Remove status keywords from search query
                params.q = this.searchQuery.trim().replace(/available|free|open/gi, '').trim();
              } else if (query.includes('occupied') || query.includes('taken') || query.includes('used')) {
                params.status = 'occupied';
                params.q = this.searchQuery.trim().replace(/occupied|taken|used/gi, '').trim();
              }
              break;
            case 'Users':
              endpoint = '/admin/search/users';
              break;
            default:
              console.log('Unknown search type:', this.searchType);
              return;
          }

          console.log('Making API call:', { endpoint, params });
          const response = await ApiService.get(endpoint, { params });
          console.log('Search response:', response);
          this.searchResults = response.data || [];
          console.log('Search results:', this.searchResults);
        } catch (err) {
          console.error('Search error:', err);
          console.error('Error response:', err.response);
          this.error = 'Error performing search: ' + (err.response?.data?.error || err.message);
          this.searchResults = [];
        }
      }, 300); // 300ms debounce
    },
    clearSearch() {
      this.searchQuery = '';
      this.searchResults = [];
      this.searchType = '';
    },
    async debugData() {
      try {
        const [parkingLots, users, parkingRecords] = await Promise.all([
          ApiService.get('/admin/parking-lots'),
          ApiService.get('/admin/users'),
          ApiService.get('/admin/parking-records')
        ]);
        console.log('Debug Data - Parking Lots:', parkingLots.data);
        console.log('Debug Data - Users:', users.data);
        console.log('Debug Data - Parking Records:', parkingRecords.data);
        
        // Test search functionality
        if (parkingLots.data && parkingLots.data.length > 0) {
          const testLot = parkingLots.data[0];
          console.log('Testing search for lot:', testLot.name);
          const searchResult = await ApiService.get('/admin/search/parking-lots', { 
            params: { q: testLot.name } 
          });
          console.log('Search result for lot:', searchResult.data);
        }
        
        if (users.data && users.data.length > 0) {
          const testUser = users.data[0];
          console.log('Testing search for user:', testUser.username);
          const searchResult = await ApiService.get('/admin/search/users', { 
            params: { q: testUser.username } 
          });
          console.log('Search result for user:', searchResult.data);
        }
        
        this.error = 'Debug data fetched and logged to console. Check browser console for details.';
      } catch (err) {
        console.error('Debug error:', err);
        this.error = 'Error fetching debug data: ' + (err.response?.data?.error || err.message);
      }
    }
  },
  mounted() {
    this.fetchParkingLots()
    this.fetchAnalytics()
  }
}
</script>

<style scoped>
.status-badge {
  background-color: #007bff !important;
  color: white !important;
  padding: 8px 12px;
  border-radius: 6px;
  font-weight: 500;
}

.status-badge.bg-success {
  background-color: #28a745 !important;
}

.status-badge.bg-warning {
  background-color: #ffc107 !important;
  color: #212529 !important;
}

.lot-header {
  text-align: center;
  margin-bottom: 20px;
}

.pagination-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 5px;
  gap: 12px; 
}


.spot-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(45px, 1fr));
  gap: 12px;
  justify-content: center;
  max-width: 750px;
  margin: 16px auto;
}

.spot-box {
  padding: 12px;
  font-size: 1rem;
  border-radius: 6px;
  color: #fff;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid;
  background-color: rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}


.available {
  border-color: #28a745;
  color: #28a745;
  box-shadow: 0 0 10px rgba(40, 167, 69, 0.3);
}

.available:hover {
  box-shadow: 0 0 15px rgba(40, 167, 69, 0.5);
  transform: scale(1.05);
}

.occupied {
  border-color: #dc3545;
  color: #dc3545;
  box-shadow: 0 0 10px rgba(220, 53, 69, 0.3);
}

.occupied:hover {
  box-shadow: 0 0 15px rgba(220, 53, 69, 0.5);
  transform: scale(1.05);
}

.modal-backdrop {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: #fff;
  padding: 32px;
  border-radius: 8px;
  min-width: 400px;
  max-width: 90vw;
  max-height: 80vh;
  overflow-y: auto;
}

@media (max-width: 767.98px) {
  .admin-dashboard .btn-group {
    flex-direction: column;
    width: 100%;
  }
  .admin-dashboard .btn-group .btn {
    width: 100%;
    margin-bottom: 8px;
  }
  .admin-dashboard .input-group {
    flex-direction: column;
    gap: 8px;
  }
  .admin-dashboard .input-group .form-control {
    width: 100%;
  }
  .admin-dashboard .input-group .btn,
  .admin-dashboard .input-group .input-group-text {
    width: 100%;
  }
  .admin-dashboard .row.g-3 > [class^='col-'] {
    margin-bottom: 16px;
  }
  .admin-dashboard .table-responsive {
    overflow-x: auto;
  }
}
</style>