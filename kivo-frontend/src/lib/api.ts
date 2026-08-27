import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Interceptor para injetar o Access Token JWT
api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("kivo_access_token");
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Interceptor de Resposta para Refresh Token ou Redirecionamento
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401 && typeof window !== "undefined") {
      const isAuthRoute = window.location.pathname.includes("/login") || window.location.pathname.includes("/register");
      if (!isAuthRoute) {
        localStorage.removeItem("kivo_access_token");
        localStorage.removeItem("kivo_user");
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);
