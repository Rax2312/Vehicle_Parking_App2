<template>
  <div class="parking-analytics">
    <div v-if="hasData">
      <div class="row">
        <!-- Summary Charts Name Card -->
        <div class="col-md-3 mb-4">
          <div class="card bg-primary text-white">
            <div class="card-body">
              <h5 class="card-title">Total Revenue</h5>
              <h3 class="card-text">₹{{ summary.total_revenue || 0 }}</h3>
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
              <h5 class="card-title">Active Reservations</h5>
              <h3 class="card-text">{{ summary.active_reservations || 0 }}</h3>
            </div>
          </div>
        </div>
        <div class="col-md-3 mb-4">
          <div class="card bg-warning text-white">
            <div class="card-body">
              <h5 class="card-title">Occupied Spots</h5>
              <h3 class="card-text">{{ summary.occupied_spots || 0 }}</h3>
            </div>
          </div>
        </div>
      </div>

      <div class="row">
        <!-- Revenue Chart -->
        <div class="col-md-6 mb-4">
          <div class="card">
            <div class="card-header">
              <h5 class="card-title mb-0">Revenue Trend</h5>
            </div>
            <div class="card-body">
              <canvas ref="revenueChart" width="400" height="200"></canvas>
            </div>
          </div>
        </div>

        <!-- Parking Activity Chart -->
        <div class="col-md-6 mb-4">
          <div class="card">
            <div class="card-header">
              <h5 class="card-title mb-0">Parking Activity</h5>
            </div>
            <div class="card-body">
              <canvas ref="activityChart" width="400" height="200"></canvas>
            </div>
          </div>
        </div>
      </div>

      <div class="row">
        <!-- Monthly Breakdown -->
        <div class="col-md-8 mb-4">
          <div class="card">
            <div class="card-header">
              <h5 class="card-title mb-0">Monthly Statistics</h5>
            </div>
            <div class="card-body">
              <canvas ref="monthlyChart" width="400" height="200"></canvas>
            </div>
          </div>
        </div>

        <!-- Lot Performance -->
        <div class="col-md-4 mb-4">
          <div class="card">
            <div class="card-header">
              <h5 class="card-title mb-0">Lot Performance</h5>
            </div>
            <div class="card-body">
              <canvas ref="lotChart" width="400" height="200"></canvas>
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
  name: 'ParkingAnalytics',
  props: {
    summary: {
      type: Object,
      default: () => ({
        total_revenue: 0,
        total_reservations: 0,
        active_reservations: 0,
        completed_reservations: 0,
        occupied_spots: 0
      })
    },
    monthlyData: {
      type: Object,
      default: () => ({})
    },
    lotData: {
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
    lotData: {
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
      console.log('Analytics hasData check:', {
        summary: this.summary,
        monthlyData: this.monthlyData,
        lotData: this.lotData,
        summaryKeys: this.summary ? Object.keys(this.summary) : [],
        monthlyKeys: this.monthlyData ? Object.keys(this.monthlyData) : [],
        lotDataLength: this.lotData ? this.lotData.length : 0
      })
      
      // Check if theres any meaningful data
      const hasSummary = this.summary && Object.values(this.summary).some(val => val > 0)
      const hasMonthly = this.monthlyData && Object.keys(this.monthlyData).length > 0
      const hasLotData = this.lotData && this.lotData.length > 0
      
      console.log('Data checks:', { hasSummary, hasMonthly, hasLotData })
      
      return hasSummary || hasMonthly || hasLotData
    }
  },
  methods: {
    createCharts() {
      if (this.chartInitialized) return
      
      console.log('Creating charts with data:', {
        summary: this.summary,
        monthlyData: this.monthlyData,
        lotData: this.lotData
      })
      
      this.destroyCharts()
      
      try {
        this.createRevenueChart()
        this.createActivityChart()
        this.createMonthlyChart()
        this.createLotChart()
        this.chartInitialized = true
        console.log('Charts created successfully')
      } catch (error) {
        console.error('Error creating charts:', error)
        console.error('Chart error details:', error.message, error.stack)
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
    createRevenueChart() {
      const ctx = this.$refs.revenueChart
      if (!ctx) return

      this.charts.revenue = new Chart(ctx, {
        type: 'line',
        data: {
          labels: this.getMonthlyLabels(),
          datasets: [{
            label: 'Revenue (₹)',
            data: this.getRevenueData(),
            borderColor: 'rgb(75, 192, 192)',
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
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
    },
    createActivityChart() {
      const ctx = this.$refs.activityChart
      if (!ctx) return

      this.charts.activity = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: ['Active', 'Completed'],
          datasets: [{
            data: [
              this.summary.active_reservations || 0,
              this.summary.completed_reservations || 0
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
    },
    createMonthlyChart() {
      const ctx = this.$refs.monthlyChart
      if (!ctx) return

      this.charts.monthly = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: this.getMonthlyLabels(),
          datasets: [{
            label: 'Reservations',
            data: this.getMonthlyReservations(),
            backgroundColor: 'rgba(255, 99, 132, 0.8)'
          }, {
            label: 'Revenue (₹)',
            data: this.getMonthlyRevenue(),
            backgroundColor: 'rgba(54, 162, 235, 0.8)',
            yAxisID: 'y1'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              type: 'linear',
              display: true,
              position: 'left',
              label: 'Reservations'
            },
            y1: {
              type: 'linear',
              display: true,
              position: 'right',
              label: 'Revenue (₹)',
              grid: {
                drawOnChartArea: false,
              },
            }
          }
        }
      })
    },
    createLotChart() {
      const ctx = this.$refs.lotChart
      if (!ctx) return

      this.charts.lot = new Chart(ctx, {
        type: 'pie',
        data: {
          labels: this.getLotLabels(),
          datasets: [{
            data: this.getLotData(),
            backgroundColor: [
              'rgba(255, 99, 132, 0.8)',
              'rgba(54, 162, 235, 0.8)',
              'rgba(255, 205, 86, 0.8)',
              'rgba(75, 192, 192, 0.8)'
            ]
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false
        }
      })
    },
    getMonthlyLabels() {
      return Object.keys(this.monthlyData).sort()
    },
    getRevenueData() {
      return Object.values(this.monthlyData).map(month => month.cost || 0)
    },
    getMonthlyReservations() {
      return Object.values(this.monthlyData).map(month => month.count || 0)
    },
    getMonthlyRevenue() {
      return Object.values(this.monthlyData).map(month => month.cost || 0)
    },
    getLotLabels() {
      return this.lotData.map(lot => lot.name)
    },
    getLotData() {
      return this.lotData.map(lot => lot.occupied)
    },
    updateCharts() {
      if (!this.chartInitialized) return
      
      this.$nextTick(() => {
        try {
          if (this.charts.revenue && this.charts.revenue.data) {
            this.charts.revenue.data.labels = this.getMonthlyLabels()
            this.charts.revenue.data.datasets[0].data = this.getRevenueData()
            this.charts.revenue.update('none')
          }
          if (this.charts.activity && this.charts.activity.data) {
            this.charts.activity.data.datasets[0].data = [
              this.summary?.active_reservations || 0,
              this.summary?.completed_reservations || 0
            ]
            this.charts.activity.update('none')
          }
          if (this.charts.monthly && this.charts.monthly.data) {
            this.charts.monthly.data.labels = this.getMonthlyLabels()
            this.charts.monthly.data.datasets[0].data = this.getMonthlyReservations()
            this.charts.monthly.data.datasets[1].data = this.getMonthlyRevenue()
            this.charts.monthly.update('none')
          }
          if (this.charts.lot && this.charts.lot.data) {
            this.charts.lot.data.labels = this.getLotLabels()
            this.charts.lot.data.datasets[0].data = this.getLotData()
            this.charts.lot.update('none')
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