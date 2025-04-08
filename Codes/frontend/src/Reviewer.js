import React, { useState } from "react";
import axios from "axios";

const Reviewer = () => {
    const [file, setFile] = useState(null);
    const [message, setMessage] = useState("");
    const [output, setOutput] = useState("");
    const [isLoading, setIsLoading] = useState(false);

    const handleFileChange = (event) => {
        setFile(event.target.files[0]);
        setMessage("");
        setOutput("");
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
                setOutput("");
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

    return (
        <div style={{ padding: "20px", maxWidth: "800px", margin: "auto", fontFamily: "Arial" }}>
            <h2>📄 Reviewer Claim Validation</h2>
            <input type="file" onChange={handleFileChange} />
            <br />
            <button onClick={handleValidate} disabled={isLoading} style={{ marginTop: "10px", marginRight: "10px" }}>
                {isLoading ? "Validating..." : "Run Validation"}
            </button>
            <button onClick={handleDownload} disabled={isLoading} style={{ marginTop: "10px" }}>
                Download Files
            </button>

            <p style={{ marginTop: "10px", fontWeight: "bold" }}>{message}</p>

            {output && (
                <div style={{ background: "#eef", padding: "10px", borderRadius: "6px", marginTop: "20px" }}>
                    <h3>🧪 Validation Output:</h3>
                    <pre style={{ whiteSpace: "pre-wrap" }}>{output}</pre>
                </div>
            )}
        </div>
    );
};

export default Reviewer;
