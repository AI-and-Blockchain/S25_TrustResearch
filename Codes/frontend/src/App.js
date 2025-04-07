import React, { useState } from "react";
import axios from "axios";

const App = () => {
    const [files, setFiles] = useState([]);
    const [message, setMessage] = useState("");

    const handleFileChange = (event) => {
        setFiles(event.target.files);
    };

    const handleUpload = async () => {
        if (files.length === 0) {
            return setMessage("Please select files to upload.");
        }

        const formData = new FormData();
        for (let i = 0; i < files.length; i++) {
            formData.append("files", files[i]);
        }

        try {
            const response = await axios.post("http://127.0.0.1:5000/upload", formData);
            setMessage(response.data.message);
        } catch (error) {
            setMessage("Upload failed.");
        }
    };

    return (
        <div>
            <h2>Upload Files</h2>
            <input type="file" onChange={handleFileChange} multiple />
            <button onClick={handleUpload}>Upload</button>
            <p>{message}</p>
        </div>
    );
};

export default App;
