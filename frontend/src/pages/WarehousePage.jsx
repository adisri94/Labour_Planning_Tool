import { useEffect, useState } from "react";
import { api } from "../api/client.js";

// Covers US-1 (view zones and capacity within a warehouse).
export default function WarehousePage() {
  const [warehouses, setWarehouses] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [zones, setZones] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    api
      .listWarehouses()
      .then((data) => {
        setWarehouses(data);
        if (data.length > 0) setSelectedId(data[0].id);
      })
      .catch((e) => setError(e.message));
  }, []);

  useEffect(() => {
    if (!selectedId) return;
    api.listZones(selectedId).then(setZones).catch((e) => setError(e.message));
  }, [selectedId]);

  if (error) return <p className="error">Error: {error}</p>;

  return (
    <div>
      <h2>Warehouses &amp; Zones</h2>
      <label>
        Warehouse:{" "}
        <select value={selectedId ?? ""} onChange={(e) => setSelectedId(e.target.value)}>
          {warehouses.map((w) => (
            <option key={w.id} value={w.id}>
              {w.name} ({w.location})
            </option>
          ))}
        </select>
      </label>

      <table>
        <thead>
          <tr>
            <th>Zone</th>
            <th>Type</th>
            <th>Capacity</th>
          </tr>
        </thead>
        <tbody>
          {zones.map((z) => (
            <tr key={z.id}>
              <td>{z.name}</td>
              <td>{z.zone_type}</td>
              <td>{z.capacity ?? "—"}</td>
            </tr>
          ))}
          {zones.length === 0 && (
            <tr>
              <td colSpan={3}>No zones for this warehouse.</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
