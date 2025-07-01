const config = {
  apiUrl: import.meta.env.VITE_API_URL || "http://localhost:5001",
  apiBaseUrl: "/api",
};

export const getApiUrl = (endpoint) => {
  const baseUrl = config.apiBaseUrl;
  return `${baseUrl}${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`;
};

export default config;
