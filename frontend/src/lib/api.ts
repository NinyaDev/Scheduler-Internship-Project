const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type FetchOptions = RequestInit & { params?: Record<string, string> };

async function apiFetch<T>(path: string, options: FetchOptions = {}): Promise<T> {
  const { params, ...init } = options;
  let url = `${API_URL}${path}`;
  if (params) {
    const search = new URLSearchParams(params);
    url += `?${search.toString()}`;
  }
  const res = await fetch(url, {
    credentials: "include",
    headers: { "Content-Type": "application/json", ...init.headers },
    ...init,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `API error ${res.status}`);
  }
  if (res.status === 204) return {} as T;
  return res.json();
}

// Auth
export const api = {
  auth: {
    login: (email: string, password: string) =>
      apiFetch("/api/auth/login", { method: "POST", body: JSON.stringify({ email, password }) }),
    register: (data: Record<string, unknown>) =>
      apiFetch("/api/auth/register", { method: "POST", body: JSON.stringify(data) }),
    me: () => apiFetch("/api/auth/me"),
    refresh: () => apiFetch("/api/auth/refresh", { method: "POST" }),
    logout: () => apiFetch("/api/auth/logout", { method: "POST" }),
  },

  users: {
    list: () => apiFetch("/api/users/"),
    get: (id: number) => apiFetch(`/api/users/${id}`),
    update: (id: number, data: Record<string, unknown>) =>
      apiFetch(`/api/users/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
    delete: (id: number) => apiFetch(`/api/users/${id}`, { method: "DELETE" }),
  },

  locations: {
    list: () => apiFetch("/api/locations/"),
    create: (data: Record<string, unknown>) =>
      apiFetch("/api/locations/", { method: "POST", body: JSON.stringify(data) }),
    update: (id: number, data: Record<string, unknown>) =>
      apiFetch(`/api/locations/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
    delete: (id: number) => apiFetch(`/api/locations/${id}`, { method: "DELETE" }),
  },

  availability: {
    getMine: () => apiFetch("/api/availability/me"),
    submitMine: (data: Record<string, unknown>) =>
      apiFetch("/api/availability/me", { method: "PUT", body: JSON.stringify(data) }),
    getAll: () => apiFetch("/api/availability/all"),
    uploadCsv: (file: File) => {
      const formData = new FormData();
      formData.append("file", file);
      return fetch(`${API_URL}/api/availability/upload-csv`, {
        method: "POST",
        credentials: "include",
        body: formData,
      }).then((r) => {
        if (!r.ok) throw new Error("CSV upload failed");
        return r.json();
      });
    },
  },

  schedules: {
    generate: (data: { week_start_date: string; notes?: string }) =>
      apiFetch("/api/schedules/generate", { method: "POST", body: JSON.stringify(data) }),
    getCurrent: () => apiFetch("/api/schedules/current"),
    list: (status?: string) =>
      apiFetch("/api/schedules/", { params: status ? { status } : undefined }),
    get: (id: number) => apiFetch(`/api/schedules/${id}`),
    publish: (id: number) => apiFetch(`/api/schedules/${id}/publish`, { method: "PATCH" }),
    archive: (id: number) => apiFetch(`/api/schedules/${id}/archive`, { method: "PATCH" }),
    delete: (id: number) => apiFetch(`/api/schedules/${id}`, { method: "DELETE" }),
  },

  shifts: {
    getMine: () => apiFetch("/api/shifts/my"),
    create: (data: Record<string, unknown>) =>
      apiFetch("/api/shifts/", { method: "POST", body: JSON.stringify(data) }),
    update: (id: number, data: Record<string, unknown>) =>
      apiFetch(`/api/shifts/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
    delete: (id: number) => apiFetch(`/api/shifts/${id}`, { method: "DELETE" }),
  },

  holidays: {
    list: () => apiFetch("/api/holidays/"),
    create: (data: Record<string, unknown>) =>
      apiFetch("/api/holidays/", { method: "POST", body: JSON.stringify(data) }),
    update: (id: number, data: Record<string, unknown>) =>
      apiFetch(`/api/holidays/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
    delete: (id: number) => apiFetch(`/api/holidays/${id}`, { method: "DELETE" }),
  },

  export: {
    icsUrl: (scheduleId: number) => `${API_URL}/api/export/ics/${scheduleId}`,
    csvUrl: (scheduleId: number) => `${API_URL}/api/export/csv/${scheduleId}`,
  },
};
