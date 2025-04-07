import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import Reviewer from "./Reviewer";

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
    <React.StrictMode>
        <div>
            <h1>Decentralized File Storage</h1>
            <App />
            <Reviewer />
        </div>
    </React.StrictMode>
);
