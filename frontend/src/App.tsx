import { useEffect, useState } from "react";
import api from "./services/api";

function App() {
  const [status, setStatus] = useState<any>(null);

  useEffect(() => {
    api.get("/api/status")
      .then((response) => setStatus(response.data))
      .catch((error) => console.error(error));
  }, []);

  return (
    <div style={{ padding: 40, fontFamily: "Arial" }}>
      <h1>🚀 AI Software Company</h1>

      {status ? (
        <>
          <h2>{status.application}</h2>

          <p>Version: {status.version}</p>

          <p>Backend: {status.backend}</p>

          <p>Frontend: {status.frontend}</p>

          <p>Ollama: {status.ollama}</p>

          <p>Database: {status.database}</p>

          <p>System: {status.system}</p>
        </>
      ) : (
        <h2>Loading...</h2>
      )}
    </div>
  );
}

export default App;