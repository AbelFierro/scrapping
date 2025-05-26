import React from "react";
import ReactDOM from "react-dom/client";
import Tasador from "./pages/tasador"; // asegurate que la ruta esté bien
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <Tasador />
  </React.StrictMode>
);
