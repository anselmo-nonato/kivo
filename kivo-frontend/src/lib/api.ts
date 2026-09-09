import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Interceptor para injetar o Access Token JWT e o Trusted Device Token
api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("kivo_access_token");
    const trustedDeviceToken = localStorage.getItem("kivo_trusted_device_token");

    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    if (trustedDeviceToken && config.headers) {
      config.headers["X-Trusted-Device-Token"] = trustedDeviceToken;
    }
  }
  return config;
});

let isRefreshing = false;
let failedQueue: Array<{ resolve: (token: string) => void; reject: (err: any) => void }> = [];

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else if (token) {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

// Interceptor de Resposta com Auto-Refresh do Token
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && typeof window !== "undefined" && !originalRequest._retry) {
      const isAuthRoute = window.location.pathname.includes("/login") || window.location.pathname.includes("/register");
      if (isAuthRoute) {
        return Promise.reject(error);
      }

      const refreshToken = localStorage.getItem("kivo_refresh_token");
      if (!refreshToken) {
        localStorage.removeItem("kivo_access_token");
        localStorage.removeItem("kivo_user");
        window.location.href = "/login";
        return Promise.reject(error);
      }

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return api(originalRequest);
          })
          .catch((err) => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const res = await axios.post(`${API_BASE_URL}/auth/refresh?refresh_token=${refreshToken}`);
        const newAccessToken = res.data.access_token;
        const newRefreshToken = res.data.refresh_token;

        localStorage.setItem("kivo_access_token", newAccessToken);
        if (newRefreshToken) localStorage.setItem("kivo_refresh_token", newRefreshToken);
        if (res.data.user) localStorage.setItem("kivo_user", JSON.stringify(res.data.user));

        api.defaults.headers.common.Authorization = `Bearer ${newAccessToken}`;
        processQueue(null, newAccessToken);
        return api(originalRequest);
      } catch (refreshErr) {
        processQueue(refreshErr, null);
        localStorage.removeItem("kivo_access_token");
        localStorage.removeItem("kivo_refresh_token");
        localStorage.removeItem("kivo_user");
        window.location.href = "/login";
        return Promise.reject(refreshErr);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);
