import axios from 'axios';

// Creating isolated Axios instance 
const API = axios.create({
    baseURL: 'http://localhost:5000/api', 
});

export default {
    async login(credentials) {
        const response = await API.post('/auth/login', credentials);
        const token = response.data.access_token;
        const role = response.data.role;
        localStorage.setItem('token', token);
        localStorage.setItem('role', role);

        // Storing user data in localStorage
        if (response.data.user) {
            localStorage.setItem('userData', JSON.stringify(response.data.user));
        }

        return response; 
    },

    async get(resource, config = {}) {
        const token = localStorage.getItem('token');

        console.log("Token being sent:", token);
        console.log("Token length:", token ? token.length : 0);

        // Merging headers with config parameters
        const headers = { Authorization: `Bearer ${token}` };
        if (!config.headers) config.headers = headers;
        else config.headers = { ...config.headers, ...headers };

        return API.get(resource, config);
    },

    async post(resource, data) {
        const token = localStorage.getItem('token');

        console.log("Token being sent:", token);
        console.log("Token length:", token ? token.length : 0);

        return API.post(resource, data, {
            headers: {
                Authorization: `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
    },

    async put(resource, data) {
        const token = localStorage.getItem('token');
        return API.put(resource, data, {
            headers: { Authorization: `Bearer ${token}` }
        });
    },

    async delete(resource) {
        const token = localStorage.getItem('token');

        console.log("Token being sent:", token);
        console.log("Token length:", token?.length);

        return API.delete(resource, {
            headers: { Authorization: `Bearer ${token}` }
        });
    },

    logout() {
        localStorage.removeItem('token');
        localStorage.removeItem('role');
        localStorage.removeItem('userData');
    }
}; 
