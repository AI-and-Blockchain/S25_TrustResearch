import React, { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");
  const [output, setOutput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [reviewFile, setReviewFile] = useState(null);  // <-- NEW

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
    setMessage("");
    setOutput("");
  };

  const handleReviewFileChange = (event) => {
    setReviewFile(event.target.files[0]);
    setMessage("");
  };

  const handleValidate = async () => {
    if (!file) {
      setMessage("⚠️ Please upload the uploaded_files.txt.");
      return;
    }

    setIsLoading(true);
    setMessage("⏳ Running validation...");
    setOutput("");

    const formData = new FormData();
    formData.append("uploaded_files", file);

    try {
      const response = await axios.post("http://127.0.0.1:5000/review-validate", formData);

      if (response.data.output) {
        setMessage("✅ Validation completed.");
        setOutput(response.data.output);
      } else {
        setMessage("✅ Validation completed but no output received.");
      }
    } catch (error) {
      setMessage("❌ Validation failed.");
      const err = error.response?.data;
      const allOutput = `${err?.stdout || ""}\n${err?.stderr || ""}`;
      setOutput(allOutput || "Unknown error occurred.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownload = async () => {
    if (!file) {
      setMessage("⚠️ Please upload the uploaded_files.txt first.");
      return;
    }

    const formData = new FormData();
    formData.append("uploaded_files", file);

    try {
      const response = await axios.post("http://127.0.0.1:5000/review-download", formData, {
        responseType: "blob",
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", "downloaded_files.zip");
      document.body.appendChild(link);
      link.click();
      link.remove();
      setMessage("✅ Files downloaded successfully.");
    } catch (error) {
      setMessage("❌ File download failed.");
    }
  };

  const handleSendToJournal = async () => {
    if (!reviewFile) {
      return setMessage("⚠️ Please upload a .txt review file to send.");
    }

    const formData = new FormData();
    formData.append("uploaded_files", reviewFile);

    try {
      const response = await axios.post("http://127.0.0.1:8081/receive-file", formData);

      if (response.status === 200) {
        const msg = response.data?.message || "✅ Review file sent successfully.";
        setMessage(msg);
      } else {
        setMessage("⚠️ Review file may not have been received.");
      }
    } catch (error) {
      console.error("❌ Error sending review file:", error);
      setMessage("❌ Failed to send review file to journal authority.");
    }
  };

  return (
    <div className="reviewer-container">
      <h2>📄 Reviewer Claim Validation</h2>
      <input type="file" onChange={handleFileChange} />
      <div className="button-group">
        <button onClick={handleValidate} disabled={isLoading}>
          {isLoading ? "Validating..." : "Run Validation"}
        </button>
        <button onClick={handleDownload} disabled={isLoading}>
          Download Files
        </button>
      </div>

      <hr style={{ margin: "20px 0" }} />

      <h3>✉️ Send Review Notes to Journal Authority</h3>
      <input type="file" accept=".txt" onChange={handleReviewFileChange} />
      <button style={{ marginTop: "10px" }} onClick={handleSendToJournal}>
        Send Review File
      </button>

      <p className="message">{message}</p>

      {output && (
        <div className="output-box">
          <h3>🧪 Validation Output:</h3>
          <pre>{output}</pre>
        </div>
      )}
    </div>
  );
}

export default App;
