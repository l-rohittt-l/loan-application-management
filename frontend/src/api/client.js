// One Axios instance for the whole app.
//
// - The backend address comes from .env (VITE_API_BASE_URL), never from code.
// - The login token is added to every request automatically.
// - If the backend answers 401 (token missing, expired, or bad), the token is
//   dropped and the app is told to go back to the login page.

import axios from "axios";

const baseURL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: `${baseURL}/api/v1`,
  timeout: 15000,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("token");
      window.dispatchEvent(new Event("auth:logout"));
    }
    return Promise.reject(error);
  }
);

// Turn a FastAPI error into one readable sentence for an error banner.
// FastAPI sends either {detail: "text"} or {detail: [{loc, msg}, ...]} for validation.
export function errorMessage(error) {
  const detail = error?.response?.data?.detail;
  if (!detail) {
    if (error?.code === "ERR_NETWORK") return "Cannot reach the server. Is the backend running?";
    return error?.message || "Something went wrong.";
  }
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((e) => {
        const field = Array.isArray(e.loc) ? e.loc[e.loc.length - 1] : "";
        return field ? `${field}: ${e.msg}` : e.msg;
      })
      .join(" · ");
  }
  return JSON.stringify(detail);
}
