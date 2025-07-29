<template>
  <div class="user-analytics">
    <div v-if="hasData">
      <!-- Summary CHart Card Name -->
      <div class="row">
        <div class="col-md-3 mb-4">
          <div class="card bg-primary text-white">
            <div class="card-body">
              <h5 class="card-title">Total Spent</h5>
              <h3 class="card-text">₹{{ summary.total_cost || 0 }}</h3>
            </div>
          </div>
        </div>
        <div class="col-md-3 mb-4">
          <div class="card bg-success text-white">
            <div class="card-body">
              <h5 class="card-title">Total Reservations</h5>
              <h3 class="card-text">{{ summary.total_reservations || 0 }}</h3>
            </div>
          </div>
        </div>
        <div class="col-md-3 mb-4">
          <div class="card bg-info text-white">
            <div class="card-body">
              <h5 class="card-title">Total Hours</h5>
              <h3 class="card-text">{{ summary.total_hours || 0 }}h</h3>
            </div>
          </div>
        </div>
        <div class="col-md-3 mb-4">
          <div class="card bg-warning text-white">
            <div class="card-body">
              <h5 class="card-title">Active Reservations</h5>
              <h3 class="card-text">{{ summary.active_reservations || 0 }}</h3>
            </div>
          </div>
        </div>
      </div>

      <div class="row">
        <!-- Monthly Spending Chart -->
        <div class="col-md-6 mb-4">
          <div class="card">
            <div class="card-header">
              <h5 class="card-title mb-0">Monthly Spending</h5>
            </div>
            <div class="card-body">
              <canvas ref="spendingChart" width="400" height="200"></canvas>
            </div>
          </div>
        </div>

        <!-- Reservation Status Chart -->
        <div class="col-md-6 mb-4">
          <div class="card">
            <div class="card-header">
              <h5 class="card-title mb-0">Reservation Status</h5>
            </div>
            <div class="card-body">
              <canvas ref="statusChart" width="400" height="200"></canvas>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div v-else>
      <p class="text-center text-muted">No analytics data available.</p>
    </div>
  </div>
</template>

<script>
import { Chart, registerables } from 'chart.js'
Chart.register(...registerables)

export default {
  name: 'UserAnalytics',
  props: {
    summary: {
      type: Object,
      default: () => ({
        total_cost: 0,
        total_reservations: 0,
        active_reservations: 0,
        completed_reservations: 0,
        total_hours: 0
      })
    },
    monthlyData: {
      type: Object,
      default: () => ({})
    },
    reservationHistory: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      charts: {},
      chartInitialized: false
    }
  },
  mounted() {
    this.$nextTick(() => {
      this.createCharts()
    })
  },
  watch: {
    summary: {
      handler() {
        this.$nextTick(() => {
          this.updateCharts()
        })
      },
      deep: true
    },
    monthlyData: {
      handler() {
        this.$nextTick(() => {
          this.updateCharts()
        })
      },
      deep: true
    },
    reservationHistory: {
      handler() {
        this.$nextTick(() => {
          this.updateCharts()
        })
      },
      deep: true
    }
  },
  computed: {
    hasData() {
      return this.summary && Object.keys(this.monthlyData || {}).length > 0
    }
  },
  methods: {
    createCharts() {
      if (this.chartInitialized) return
      
      this.destroyCharts()
      
      try {
        this.createSpendingChart()
        this.createStatusChart()
        this.chartInitialized = true
      } catch (error) {
        console.error('Error creating charts:', error)
      }
    },
    destroyCharts() {
      Object.values(this.charts).forEach(chart => {
        if (chart && typeof chart.destroy === 'function') {
          try {
            chart.destroy()
          } catch (error) {
            console.error('Error destroying chart:', error)
          }
        }
      })
      this.charts = {}
    },
    createSpendingChart() {
      const ctx = this.$refs.spendingChart
      if (!ctx) return

      try {
        this.charts.spending = new Chart(ctx, {
          type: 'line',
          data: {
            labels: this.getMonthlyLabels(),
            datasets: [{
              label: 'Spending (₹)',
              data: this.getMonthlySpending(),
              borderColor: 'rgb(255, 99, 132)',
              backgroundColor: 'rgba(255, 99, 132, 0.2)',
              tension: 0.1
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              y: {
                beginAtZero: true
              }
            }
          }
        })
      } catch (error) {
        console.error('Error creating spending chart:', error)
      }
    },
    createStatusChart() {
      const ctx = this.$refs.statusChart
      if (!ctx) return

      try {
        this.charts.status = new Chart(ctx, {
          type: 'doughnut',
          data: {
            labels: ['Active', 'Completed'],
            datasets: [{
              data: [
                this.summary?.active_reservations || 0,
                this.summary?.completed_reservations || 0
              ],
              backgroundColor: [
                'rgba(255, 99, 132, 0.8)',
                'rgba(54, 162, 235, 0.8)'
              ]
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false
          }
        })
      } catch (error) {
        console.error('Error creating status chart:', error)
      }
    },
    getMonthlyLabels() {
      if (!this.monthlyData || typeof this.monthlyData !== 'object') return []
      return Object.keys(this.monthlyData).sort()
    },
    getMonthlySpending() {
      if (!this.monthlyData || typeof this.monthlyData !== 'object') return []
      return Object.values(this.monthlyData).map(month => month?.cost || 0)
    },
    updateCharts() {
      if (!this.chartInitialized) return
      
      this.$nextTick(() => {
        try {
          if (this.charts.spending && this.charts.spending.data) {
            this.charts.spending.data.labels = this.getMonthlyLabels()
            this.charts.spending.data.datasets[0].data = this.getMonthlySpending()
            this.charts.spending.update('none')
          }
          if (this.charts.status && this.charts.status.data) {
            this.charts.status.data.datasets[0].data = [
              this.summary?.active_reservations || 0,
              this.summary?.completed_reservations || 0
            ]
            this.charts.status.update('none')
          }
        } catch (error) {
          console.error('Error updating charts:', error)
        }
      })
    }
  },
  beforeUnmount() {
    this.destroyCharts()
  }
}
</script> 