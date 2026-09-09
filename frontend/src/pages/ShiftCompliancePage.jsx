import { useEffect, useState } from "react";
import { api } from "../api/client.js";

// Sprint 2 (BL-2): shift templates + attached regulations, with an
// activate action standing in for the legal sign-off gate.
const WAREHOUSE_ID = "wh-001";

export default function ShiftCompliancePage() {
  const [shifts, setShifts] = useState([]);
  const [regulations, setRegulations] = useState([]);
  const [minutesByShift, setMinutesByShift] = useState({});
  const [regsByShift, setRegsByShift] = useState({});
  const [error, setError] = useState(null);
  const [pendingReg, setPendingReg] = useState({});

  const load = () =>
    api
      .listShiftTemplates(WAREHOUSE_ID)
      .then(async (data) => {
        setShifts(data);
        const minutesEntries = await Promise.all(
          data.map((s) => api.getAvailableMinutes(s.id).then((m) => [s.id, m]))
        );
        setMinutesByShift(Object.fromEntries(minutesEntries));
        const regEntries = await Promise.all(
          data.map((s) => api.listShiftRegulations(s.id).then((r) => [s.id, r]))
        );
        setRegsByShift(Object.fromEntries(regEntries));
      })
      .catch((e) => setError(e.message));

  useEffect(() => {
    api.listLaborRegulations().then(setRegulations).catch((e) => setError(e.message));
    load();
  }, []);

  const regulationName = (id) => regulations.find((r) => r.id === id)?.name ?? id;

  async function handleActivateShift(shiftId) {
    setError(null);
    try {
      await api.activateShiftTemplate(shiftId, "Labor Planning PM (demo)");
      await load();
    } catch (e) {
      setError(e.message);
    }
  }

  async function handleActivateRegulation(regulationId) {
    setError(null);
    try {
      await api.activateLaborRegulation(regulationId, "Legal & Compliance (demo)");
      await api.listLaborRegulations().then(setRegulations);
    } catch (e) {
      setError(e.message);
    }
  }

  async function handleAttach(shiftId) {
    const regulationId = pendingReg[shiftId];
    if (!regulationId) return;
    setError(null);
    try {
      await api.attachRegulation(shiftId, regulationId);
      await load();
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <div>
      <h2>Shift Templates &amp; Compliance</h2>
      {error && <p className="error">Error: {error}</p>}

      <table>
        <thead>
          <tr>
            <th>Shift</th>
            <th>Time</th>
            <th>Active?</th>
            <th>Regulations</th>
            <th>Attach</th>
            <th>Available minutes</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {shifts.map((s) => (
            <tr key={s.id}>
              <td>{s.name}</td>
              <td>
                {s.start_time}–{s.end_time}
              </td>
              <td className={s.is_active ? "status-active" : "status-terminated"}>
                {s.is_active ? "active" : "pending sign-off"}
              </td>
              <td>
                {(regsByShift[s.id] ?? []).map((r) => regulationName(r.regulation_id)).join(", ") ||
                  "—"}
              </td>
              <td>
                <select
                  value={pendingReg[s.id] ?? ""}
                  onChange={(e) =>
                    setPendingReg((prev) => ({ ...prev, [s.id]: e.target.value }))
                  }
                >
                  <option value="">Select regulation…</option>
                  {regulations.map((r) => (
                    <option key={r.id} value={r.id} disabled={!r.is_active}>
                      {r.name} {r.is_active ? "" : "(inactive)"}
                    </option>
                  ))}
                </select>
                <button onClick={() => handleAttach(s.id)}>Attach</button>
              </td>
              <td>
                {minutesByShift[s.id]
                  ? `${minutesByShift[s.id].available_shift_minutes} (of ${minutesByShift[s.id].gross_minutes})`
                  : "—"}
              </td>
              <td>
                <button disabled={s.is_active} onClick={() => handleActivateShift(s.id)}>
                  Activate
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <h3>Labor Regulations</h3>
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Max hrs/day</th>
            <th>Max hrs/week</th>
            <th>Break (mins)</th>
            <th>Active?</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {regulations.map((r) => (
            <tr key={r.id}>
              <td>{r.name}</td>
              <td>{r.max_hours_per_day}</td>
              <td>{r.max_hours_per_week}</td>
              <td>{r.break_interval_mins ?? "—"}</td>
              <td className={r.is_active ? "status-active" : "status-terminated"}>
                {r.is_active ? "active" : "pending sign-off"}
              </td>
              <td>
                <button disabled={r.is_active} onClick={() => handleActivateRegulation(r.id)}>
                  Activate
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
