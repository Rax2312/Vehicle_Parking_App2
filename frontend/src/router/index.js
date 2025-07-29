import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import AdminDashboard from '../views/AdminDashboard.vue'
import UserDashboard from '../views/UserDashboard.vue'
import NotFound from '../views/NotFound.vue'
import Profile from '../views/Profile.vue'
// Lazy import for RecentHistory
const RecentHistory = () => import('../views/RecentHistory.vue');

const routes = [
    {
        path: '/',
        name: 'Home',
        component: Home
    },
    {
        path: '/login',
        name: 'Login',
        component: Login
    },
    {
        path: '/register',
        name: 'Register',
        component: Register
    },
    {
        path: '/admin',
        name: 'AdminDashboard',
        component: AdminDashboard,
        meta: { requiresAuth: true, role: 'admin' }
    },
    {
        path: '/dashboard',
        name: 'UserDashboard',
        component: UserDashboard,
        meta: { requiresAuth: true, role: 'user' }
    },
    {
        path: '/profile',
        name: 'Profile',
        component: Profile,
        meta: { requiresAuth: true, role: 'user' }
    },
    {
        path: '/recent-history',
        name: 'RecentHistory',
        component: RecentHistory,
        meta: { requiresAuth: true, role: 'user' }
    },
    {
        path: '/:pathMatch(.*)*',
        name: 'NotFound',
        component: NotFound
    }
]

const router = createRouter({
    history: createWebHistory(process.env.BASE_URL),
    routes
})

// Navigation Guard
router.beforeEach((to, from, next) => {
    const loggedIn = !!localStorage.getItem('token');
    const userRole = localStorage.getItem('role');

    if (to.meta.requiresAuth) {
        if (!loggedIn) {
            // If its not logged in, then redirect to login page
            next('/login');
        } else {
            // If logged in, check role
            if (to.meta.role && to.meta.role !== userRole) {
                // If role not authorized,then redirect to a fallback page
                next(userRole === 'admin' ? '/admin' : '/dashboard');
            } else {
                // Authorized
                next();
            }
        }
    } else {
        // No auth req for root
        next();
    }
});


export default router 
