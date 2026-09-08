import { useEffect, useState } from "react";
import { api } from "../api/client.js";

// Covers US-2 (register/certify roles) and US-3 (employment status changes)
// against the seeded Sprint 1 warehouse.
const WAREHOUSE_ID = "wh-001";

export default function EmployeesPage() {
  const [employees, setEmployees] = useState([]);
  const [jobRoles, setJobRoles] = useState([]);
  const [rolesByEmployee, setRolesByEmployee] = useState({});
  const [error, setError] = useState(null);
  const [pendingRole, setPendingRole] = useState({});

  const loadEmployees = () =>
    api
      .listEmployees(WAREHOUSE_ID)
      .then(async (emps) => {
        setEmployees(emps);
        const roleLists = await Promise.all(
          emps.map((e) => api.listEmployeeRoles(e.id).then((r) => [e.id, r]))
        );
        setRolesByEmployee(Object.fromEntries(roleLists));
      })
      .catch((e) => setError(e.message));

  useEffect(() => {
    api.listJobRoles().then(setJobRoles).catch((e) => setError(e.message));
    loadEmployees();
  }, []);

  const jobRoleName = (id) => jobRoles.find((r) => r.id === id)?.name ?? id;

  async function handleTerminate(employeeId) {
    setError(null);
    try {
      await api.updateEmployee(employeeId, { employment_status: "terminated" });
      await loadEmployees();
    } catch (e) {
      setError(e.message);
    }
  }

  async function handleAddRole(employeeId) {
    const jobRoleId = pendingRole[employeeId];
    if (!jobRoleId) return;
    setError(null);
    try {
      await api.addEmployeeRole(employeeId, { job_role_id: jobRoleId, is_primary: false });
      await loadEmployees();
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <div>
      <h2>Employees</h2>
      {error && <p className="error">Error: {error}</p>}
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Type</th>
            <th>Status</th>
            <th>Roles</th>
            <th>Add role</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {employees.map((emp) => (
            <tr key={emp.id}>
              <td>{emp.name}</td>
              <td>{emp.employee_type}</td>
              <td className={`status status-${emp.employment_status}`}>
                {emp.employment_status}
              </td>
              <td>
                {(rolesByEmployee[emp.id] ?? [])
                  .map((r) => jobRoleName(r.job_role_id) + (r.is_primary ? " (primary)" : ""))
                  .join(", ") || "—"}
              </td>
              <td>
                <select
                  value={pendingRole[emp.id] ?? ""}
                  onChange={(e) =>
                    setPendingRole((prev) => ({ ...prev, [emp.id]: e.target.value }))
                  }
                >
                  <option value="">Select role…</option>
                  {jobRoles.map((r) => (
                    <option key={r.id} value={r.id}>
                      {r.name}
                    </option>
                  ))}
                </select>
                <button onClick={() => handleAddRole(emp.id)}>Certify</button>
              </td>
              <td>
                <button
                  disabled={emp.employment_status === "terminated"}
                  onClick={() => handleTerminate(emp.id)}
                >
                  Terminate
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
