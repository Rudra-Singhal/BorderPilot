import { BrowserRouter, Route, Routes } from "react-router-dom";
import { AppShell } from "./components/AppShell";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { Login } from "./pages/Login";
import { Dashboard } from "./pages/Dashboard";
import { Receivables } from "./pages/Receivables";
import { Counterparties } from "./pages/Counterparties";
import { CashForecast } from "./pages/CashForecast";
import { Liquidity } from "./pages/Liquidity";
import { FxExposure } from "./pages/FxExposure";
import { Compliance } from "./pages/Compliance";
import { Assistant } from "./pages/Assistant";
import { Activity } from "./pages/Activity";
import { NettingRuns } from "./pages/NettingRuns";
import { NettingRunDetail } from "./pages/NettingRunDetail";
import { PacketView } from "./pages/PacketView";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route element={<ProtectedRoute />}>
          <Route element={<AppShell />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/forecast" element={<CashForecast />} />
            <Route path="/receivables" element={<Receivables />} />
            <Route path="/counterparties" element={<Counterparties />} />
            <Route path="/liquidity" element={<Liquidity />} />
            <Route path="/netting-runs" element={<NettingRuns />} />
            <Route path="/netting-runs/:runId" element={<NettingRunDetail />} />
            <Route path="/netting-runs/:runId/packet" element={<PacketView />} />
            <Route path="/fx" element={<FxExposure />} />
            <Route path="/compliance" element={<Compliance />} />
            <Route path="/assistant" element={<Assistant />} />
            <Route path="/activity" element={<Activity />} />
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
