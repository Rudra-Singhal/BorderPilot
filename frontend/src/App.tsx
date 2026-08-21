import { BrowserRouter, Route, Routes } from "react-router-dom";
import { AppShell } from "./components/AppShell";
import { Dashboard } from "./pages/Dashboard";
import { Receivables } from "./pages/Receivables";
import { NettingRuns } from "./pages/NettingRuns";
import { NettingRunDetail } from "./pages/NettingRunDetail";
import { PacketView } from "./pages/PacketView";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppShell />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/receivables" element={<Receivables />} />
          <Route path="/netting-runs" element={<NettingRuns />} />
          <Route path="/netting-runs/:runId" element={<NettingRunDetail />} />
          <Route path="/netting-runs/:runId/packet" element={<PacketView />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
