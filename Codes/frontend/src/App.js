import React, { useState } from "react";
import axios from "axios";
import "./App.css";

const App = () => {
    const [files, setFiles] = useState([]);
    const [message, setMessage] = useState("");
    const [cidList, setCidList] = useState([]); // ⬅️ New state for showing uploaded CIDs
    const [reviewNotes, setReviewNotes] = useState("");

    const handleFileChange = (event) => {
        setFiles(event.target.files);
        setMessage("");
        setCidList([]);
    };

    const handleUpload = async () => {
        if (files.length === 0) {
            return setMessage("⚠️ Please select files to upload.");
        }

        const formData = new FormData();
        for (let i = 0; i < files.length; i++) {
            formData.append("files", files[i]);
        }

        try {
            const response = await axios.post("http://127.0.0.1:5000/upload", formData);
            setMessage(response.data.message);

            // Parse and store CID list
            if (response.data.details) {
                const formatted = response.data.details.map(line => {
                    const [name, cid] = line.split(": ");
                    return { name, cid };
                });
                setCidList(formatted);
            }
        } catch (error) {
            setMessage("❌ Upload failed.");
            setCidList([]);
        }
    };

    const handleSubmitReview = async () => {
        if (!reviewNotes.trim()) {
            return setMessage("⚠️ Please enter some review notes.");
        }

        const formData = new FormData();
        const blob = new Blob([reviewNotes], { type: "text/plain" });
        const file = new File([blob], "review_notes.txt");
        formData.append("uploaded_files", file);

        try {
            const response = await axios.post("http://127.0.0.1:8081/receive-file", formData);

            if (response.status === 200) {
                const msg = response.data?.message || "✅ Review notes sent successfully.";
                setMessage(msg);
            } else {
                setMessage("⚠️ Review notes may not have been received.");
            }
        } catch (error) {
            console.error("❌ Error sending review notes:", error);
            if (error.response) {
                setMessage(`❌ Server responded with ${error.response.status}: ${error.response.data?.error || "Unknown error"}`);
            } else if (error.request) {
                setMessage("❌ No response received. Is the server running?");
            } else {
                setMessage(`❌ Request error: ${error.message}`);
            }
        }
    };

    return (
        <div className="App">
            <h2>📤 Author Upload</h2>
            <input type="file" onChange={handleFileChange} multiple />
            <button onClick={handleUpload}>Upload</button>

            {cidList.length > 0 && (
                <div style={{ marginTop: "20px", background: "#f4f4f4", padding: "10px", borderRadius: "5px" }}>
                    <h3>📄 Uploaded Files and IPFS CIDs:</h3>
                    <ul>
                        {cidList.map((item, index) => (
                            <li key={index}>
                                <strong>{item.name}</strong>: <code>{item.cid}</code>
                            </li>
                        ))}
                    </ul>
                </div>
            )}

            <hr />

            <h2>🧪 Reviewer Claim Validation</h2>
            <textarea
                value={reviewNotes}
                onChange={(e) => setReviewNotes(e.target.value)}
                rows={6}
                cols={50}
                placeholder="Write your review notes here..."
            />
            <br />
            <button onClick={handleSubmitReview}>Submit Review Notes</button>

            <p style={{ fontWeight: "bold", marginTop: "10px" }}>{message}</p>
        </div>
    );
};

export default App;
