const config = {
  apiUrl: import.meta.env.VITE_API_URL || "http://localhost:5174",
  apiBaseUrl: "/api",
};

export const getApiUrl = (endpoint) => {
  const baseUrl = config.apiUrl;
  return `${baseUrl}/api${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`;
};

export default config;
