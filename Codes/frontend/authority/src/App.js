import React, { useEffect, useState } from "react";

function App() {
  const [accounts, setAccounts] = useState([]);
  const [selectedReviewer, setSelectedReviewer] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    fetch("http://127.0.0.1:8081/list-accounts")
      .then(res => res.json())
      .then(data => setAccounts(data))
      .catch(err => setMessage("Failed to fetch accounts."));
  }, []);

  const handleAssign = async () => {
    const formData = new FormData();
    formData.append("reviewer_address", selectedReviewer);

    try {
      const res = await fetch("http://127.0.0.1:8081/assign-reviewer", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      setMessage(data.message || data.error);
    } catch (error) {
      setMessage("Assignment failed.");
    }
  };

  return (
    <div style={{ padding: 30 }}>
      <h2>Journal Authority Portal</h2>
      <label>Select Reviewer Address:</label>
      <select
        value={selectedReviewer}
        onChange={e => setSelectedReviewer(e.target.value)}
        style={{ marginLeft: 10 }}
      >
        <option value="">-- Choose --</option>
        {accounts.map(addr => (
          <option key={addr} value={addr}>
            {addr}
          </option>
        ))}
      </select>
      <br /><br />
      <button onClick={handleAssign}>Assign Reviewer</button>
      <p style={{ color: "green" }}>{message}</p>
    </div>
  );
}

export default App;
