import { useCallback, useEffect, useState } from "react";
import Sidebar from "./components/Sidebar";
import ChatPanel from "./components/ChatPanel";
import SourcePanel from "./components/SourcePanel";
import { getHealth } from "./api";

export default function App() {
  const [health, setHealth] = useState(null);
  const [sources, setSources] = useState([]);

  const refreshHealth = useCallback(() => {
    getHealth()
      .then(setHealth)
      .catch(() => setHealth({ status: "down" }));
  }, []);

  useEffect(() => {
    refreshHealth();
    const interval = setInterval(refreshHealth, 10000);
    return () => clearInterval(interval);
  }, [refreshHealth]);

  return (
    <div className="app-shell">
      <Sidebar health={health} onIngested={refreshHealth} />
      <ChatPanel onNewSources={setSources} />
      <SourcePanel sources={sources} />
    </div>
  );
}
