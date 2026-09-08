// Thin HTTP client wrapping backend REST calls, per docs/SOLUTION_ARCHITECTURE.md.
const BASE_URL = "http://127.0.0.1:8000";

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const message = body?.detail?.error || body?.detail || res.statusText;
    throw new Error(typeof message === "string" ? message : JSON.stringify(message));
  }
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  listWarehouses: () => request("/warehouses"),
  listZones: (warehouseId) => request(`/warehouses/${warehouseId}/zones`),
  listJobRoles: () => request("/job-roles"),
  listEmployees: (warehouseId) =>
    request(`/employees?warehouse_id=${encodeURIComponent(warehouseId)}`),
  listEmployeeRoles: (employeeId) => request(`/employees/${employeeId}/roles`),
  addEmployeeRole: (employeeId, payload) =>
    request(`/employees/${employeeId}/roles`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  updateEmployee: (employeeId, payload) =>
    request(`/employees/${employeeId}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    }),
};
