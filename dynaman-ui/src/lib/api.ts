import axios from 'axios';

const api = axios.create({
  baseURL: '', // Use relative path for ALB routing
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add a request interceptor to inject the token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add a response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Clear token and redirect to login if unauthorized
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export interface UserGroup {
  _id: string;
  name: string;
  description?: string;
}

export interface User {
  _id: string;
  email: string;
  role: string;
  is_active: boolean;
  group_ids?: string[];
}

export const groupApi = {
  list: async () => {
    const response = await api.get<UserGroup[]>('/api/v1/groups');
    return response.data;
  },
  create: async (data: { name: string; description?: string }) => {
    const response = await api.post<UserGroup>('/api/v1/groups', data);
    return response.data;
  },
  get: async (id: string) => {
    const response = await api.get<UserGroup>(`/api/v1/groups/${id}`);
    return response.data;
  },
  update: async (id: string, data: { name?: string; description?: string }) => {
    const response = await api.put<UserGroup>(`/api/v1/groups/${id}`, data);
    return response.data;
  },
  delete: async (id: string) => {
    await api.delete(`/api/v1/groups/${id}`);
  },
};

export const userApi = {
  list: async () => {
    const response = await api.get<User[]>('/api/v1/auth/users');
    return response.data;
  },
  update: async (id: string, data: Partial<User>) => {
    const response = await api.put<User>(`/api/v1/auth/users/${id}`, data);
    return response.data;
  }
};

export interface FormLayout {
  _id: string;
  schema_name: string;
  name: string;
  definition: any[]; // JSON structure
  target_group_ids: string[];
  is_default: boolean;
}

export const layoutApi = {
  resolve: async (schemaName: string) => {
    try {
      const response = await api.get<FormLayout | null>(`/api/v1/layouts/resolve/${schemaName}`);
      return response.data;
    } catch (error) {
      console.error("Failed to resolve layout", error);
      return null;
    }
  },
  create: async (data: Omit<FormLayout, '_id'>) => {
    const response = await api.post<FormLayout>('/api/v1/layouts/', data);
    return response.data;
  },
  listBySchema: async (schemaName: string) => {
    const response = await api.get<FormLayout[]>(`/api/v1/layouts/by-schema/${schemaName}`);
    return response.data;
  },
  update: async (id: string, data: Partial<FormLayout>) => {
    const response = await api.put<FormLayout>(`/api/v1/layouts/${id}`, data);
    return response.data;
  },
  delete: async (id: string) => {
    await api.delete(`/api/v1/layouts/${id}`);
  }
};

export default api;
