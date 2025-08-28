import React, { useEffect, useState } from "react";

function App() {
  const [message, setMessage] = useState("");
  const [query, setQuery] = useState("")
  const [results, setResults] = useState([])

  useEffect(() => {
    fetch("http://127.0.0.1:8000/")
      .then((res) => res.json())
      .then((data) => setMessage(data.message))
      .catch((err) => console.error("Error:", err));
  }, []);

  const sendQuery = () => {
    fetch("http://127.0.0.1:8000/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: query })
    })
      .then((res) => res.json())
      .then((data) => setResults(data))
      .catch((err) => console.error("Error:", err));
  };

  return (
    <div style={{ textAlign: "center", marginTop: "50px" }}>
      <h1>FastAPI + React</h1>
      <p>Message from backend: {message}</p>
      <div style={{ marginTop: "30px" }}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)} // update query as user types
          style={{ width: "400px", padding: "8px" }}
          placeholder="Type SQL query here"
        />
        <button
          onClick={sendQuery}                        // call sendQuery when clicked
          style={{ marginLeft: "10px", padding: "8px" }}
        >
          Run Query
        </button>
      </div>

      {results.length > 0 && (
        <table style={{ margin: "30px auto", borderCollapse: "collapse" }}>
          <thead>
            <tr>
              {Object.keys(results[0]).map((key) => (
                <th key={key} style={{ border: "1px solid black", padding: "8px" }}>
                  {key}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {results.map((row, idx) => (
              <tr key={idx}>
                {Object.values(row).map((val, i) => (
                  <td key={i} style={{ border: "1px solid black", padding: "8px" }}>
                    {val}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default App;
