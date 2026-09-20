import { useEffect, useState } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import Sidebar from "./Sidebar";
import "./App.css";
import Characters from "./pages/Characters";
import CharacterDetails from "./pages/CharacterDetails";
import Recipes from "./pages/Recipes";
import Expansions from "./pages/Expansions";
import MaximizeProfit from "./pages/MaximizeProfit";
import ManualPlanner from "./pages/ManualPlanner";

function getInitialDarkMode(): boolean {
    try {
        const savedTheme = localStorage.getItem("vanforge-theme");

        if (savedTheme === "dark") {
            return true;
        }

        if (savedTheme === "light") {
            return false;
        }
    } catch {
        // Fall back to the system preference when storage is unavailable.
    }

    return window.matchMedia("(prefers-color-scheme: dark)").matches;
}

export default function App() {
    const [darkMode, setDarkMode] = useState(getInitialDarkMode);

    useEffect(() => {
        document.documentElement.dataset.theme = darkMode ? "dark" : "light";
    }, [darkMode]);

    function changeDarkMode(enabled: boolean) {
        setDarkMode(enabled);

        try {
            localStorage.setItem("vanforge-theme", enabled ? "dark" : "light");
        } catch {
            // The toggle still works when the browser cannot save preferences.
        }
    }

    return (
        <div className="app-layout">
            <Sidebar
                darkMode={darkMode}
                onDarkModeChange={changeDarkMode}
            />

            <main className="main-content">
                <Routes>
                    <Route path="/maximize" element={<MaximizeProfit />} />
                    <Route path="/manual" element={<ManualPlanner />} />
                    <Route path="/characters" element={<Characters />} />
                    <Route path="/characters/:characterId" element={<CharacterDetails />} />
                    <Route path="/recipes" element={<Recipes />} />
                    <Route path="/expansions" element={<Expansions />} />
                    <Route
                        path="*"
                        element={<Navigate to="/maximize" replace />}
                    />
                </Routes>
            </main>
        </div>
    );
}
