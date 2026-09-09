import { useState } from "react";
import WarehousePage from "./pages/WarehousePage.jsx";
import EmployeesPage from "./pages/EmployeesPage.jsx";
import ShiftCompliancePage from "./pages/ShiftCompliancePage.jsx";
import "./index.css";

const TABS = {
  warehouse: { label: "Warehouse & Zones", component: WarehousePage },
  employees: { label: "Employees", component: EmployeesPage },
  shifts: { label: "Shifts & Compliance", component: ShiftCompliancePage },
};

export default function App() {
  const [tab, setTab] = useState("warehouse");
  const ActivePage = TABS[tab].component;

  return (
    <div className="app">
      <header>
        <h1>Warehouse Labor Planning Tool</h1>
        <p className="subtitle">Sprint 1–2 demo — Facility &amp; Org Master Data, Shift &amp; Compliance</p>
      </header>
      <nav>
        {Object.entries(TABS).map(([key, { label }]) => (
          <button
            key={key}
            className={key === tab ? "active" : ""}
            onClick={() => setTab(key)}
          >
            {label}
          </button>
        ))}
      </nav>
      <main>
        <ActivePage />
      </main>
    </div>
  );
}
