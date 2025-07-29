<template>
  <div class="app-wrapper gradient-bg">
    <div class="home-container">
      <div class="content-wrapper glass">
        <h1 class="gradient-text">Welcome to Smart Parking</h1>
        <p class="subtitle">Efficient. Convenient. Smart.</p>
        
        <div class="features-grid">
          <div class="feature-card card-hover">
            <i class="bi bi-car-front"></i>
            <h3>Easy Booking</h3>
            <p>Book your parking spot in seconds</p>
          </div>
          <div class="feature-card card-hover">
            <i class="bi bi-clock"></i>
            <h3>Real-time Availability</h3>
            <p>Check spot availability instantly</p>
          </div>
          <div class="feature-card card-hover">
            <i class="bi bi-graph-up"></i>
            <h3>Smart Analytics</h3>
            <p>Track your parking history</p>
          </div>
          <div class="feature-card card-hover">
            <i class="bi bi-bell"></i>
            <h3>Smart Notifications</h3>
            <p>Get messages and reports</p>
          </div>
        </div>

        <div class="cta-buttons">
          <router-link to="/login" class="btn btn-primary btn-glow">Get Started</router-link>
          <router-link to="/register" class="btn btn-outline-light">Sign Up</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Home'
}
</script>

<style scoped>
@import '../assets/animations.css';

.app-wrapper {
  min-height: 100vh;
  width: 100%;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(45deg, #030213, #1a1b4b, #2b2c7c);
  background-size: 200% 200%;
  animation: gradient-xy 15s ease infinite;
  z-index: 0;
}

.home-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  color: white;
}

.content-wrapper {
  max-width: 1200px;
  padding: 3rem;
  text-align: center;
  border-radius: 20px;
}

h1 {
  font-size: 3.5rem;
  margin-bottom: 1rem;
  font-weight: bold;
}

.subtitle {
  font-size: 1.5rem;
  margin-bottom: 3rem;
  opacity: 0.9;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 2rem;
  margin: 3rem 0;
}

.feature-card {
  padding: 2rem;
  border-radius: 15px;
  background: rgba(255, 255, 255, 0.1);
}

.feature-card i {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.feature-card h3 {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
}

.feature-card p {
  opacity: 0.8;
}

.cta-buttons {
  margin-top: 3rem;
}

.cta-buttons .btn {
  margin: 0 1rem;
  padding: 0.75rem 2rem;
  font-size: 1.1rem;
  border-radius: 50px;
}

@media (max-width: 768px) {
  .content-wrapper {
    padding: 2rem;
  }

  h1 {
    font-size: 2.5rem;
  }

  .subtitle {
    font-size: 1.2rem;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }

  .cta-buttons .btn {
    display: block;
    margin: 1rem auto;
    width: 80%;
  }
}
</style>
