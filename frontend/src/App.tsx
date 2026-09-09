import { useEffect, useState } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import Sidebar from "./Sidebar";
import "./App.css";
import Characters from "./pages/Characters";

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
                    <Route path="/maximize"
                        element={
                            <>
                                <h1>Maximize Profit</h1>
                                <p>
                                    Select characters and generate profitable
                                    crafting recommendations.
                                </p>
                            </>
                        }
                    />
                    <Route
                        path="/manual"
                        element={
                            <>
                                <h1>Manual Planner</h1>
                                <p>
                                    Enter craft quantities and calculate the
                                    materials you need.
                                </p>
                            </>
                        }
                    />
                    <Route path="/characters" element={<Characters />} />
                    <Route
                        path="/recipes"
                        element={
                            <>
                                <h1>Recipes</h1>
                                <p>
                                    Manage recipes, ingredients, and profit
                                    per craft.
                                </p>
                            </>
                        }
                    />
                    <Route
                        path="/expansions"
                        element={
                            <>
                                <h1>Expansions</h1>
                                <p>
                                    Manage expansions and select the current
                                    expansion for planning.
                                </p>
                            </>
                        }
                    />
                    <Route
                        path="*"
                        element={<Navigate to="/maximize" replace />}
                    />
                </Routes>
            </main>
        </div>
    );
}