import React, { useState } from "react";
import axios from "axios";
import "./App.css";

const App = () => {
    const [files, setFiles] = useState([]);
    const [message, setMessage] = useState("");
    const [cidList, setCidList] = useState([]);
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

    return (
        <div className="App">
            <h2>📤 Author Upload</h2>
            <input type="file" onChange={handleFileChange} multiple />
            <button onClick={handleUpload}>Upload</button>

            {cidList.length > 0 && (
                <div className="cid-box">
                    <h3>📄 Uploaded Files and IPFS CIDs:</h3>
                    <ul>
                        {cidList.map((item, index) => (
                            <li key={index}><strong>{item.name}</strong>: <code>{item.cid}</code></li>
                        ))}
                    </ul>
                </div>
            )}

            <hr />
        </div>
    );
};

export default App;