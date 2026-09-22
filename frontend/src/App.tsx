import { useEffect, useState } from "react";
import { Navigate, Route, Routes, useNavigate } from "react-router-dom";
import Sidebar from "./Sidebar";
import "./App.css";
import Characters from "./pages/Characters";
import CharacterDetails from "./pages/CharacterDetails";
import Recipes from "./pages/Recipes";
import Expansions from "./pages/Expansions";
import MaximizeProfit from "./pages/MaximizeProfit";
import ManualPlanner from "./pages/ManualPlanner";
import NotFound from "./pages/NotFound";
import Auth from "./pages/Auth";
import Accounts from "./pages/Accounts";
import { authClient } from "./auth";
import { NeonAuthUIProvider } from "@neondatabase/auth/react/ui";
import { getAuthenticatedUser } from "./api/authentication";
import type { AuthenticatedUser } from "./dto/AuthenticatedUser";

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

interface ProtectedApplicationProps {
    darkMode: boolean;
    onDarkModeChange: (enabled: boolean) => void;
}

function ProtectedApplication({
    darkMode,
    onDarkModeChange,
}: ProtectedApplicationProps) {
    const session = authClient.useSession();

    const [account, setAccount] = useState<AuthenticatedUser | null>(null);
    const [accountError, setAccountError] = useState<string | null>(null);

    useEffect(() => {
        if (!session.data) {
            return;
        }

        getAuthenticatedUser()
            .then((authenticatedAccount) => {
                setAccount(authenticatedAccount);
                setAccountError(null);
            })
            .catch((error: unknown) => {
                const message = error instanceof Error
                    ? error.message
                    : "Unable to load your VanForge account.";

                setAccountError(message);
            });
    }, [session.data]);

    if (session.isPending) {
        return <main className="app-loading">Loading VanForge...</main>;
    }

    if (!session.data) {
        return <Navigate to="/auth/sign-in" replace />;
    }

    if (accountError) {
        return <main className="app-loading">{accountError}</main>;
    }

    if (!account) {
        return <main className="app-loading">Loading your VanForge account...</main>;
    }

    return (
        <div className="app-layout">
            <Sidebar
                darkMode={darkMode}
                onDarkModeChange={onDarkModeChange}
                isAdmin={account.role === "admin"}
            />

            <main className="main-content">
                <Routes>
                    <Route path="/" element={<Navigate to="/maximize" replace />} />
                    <Route path="/maximize" element={<MaximizeProfit />} />
                    <Route path="/manual" element={<ManualPlanner />} />
                    <Route path="/characters" element={<Characters />} />
                    <Route path="/characters/:characterId" element={<CharacterDetails />} />
                    <Route path="/recipes" element={<Recipes canManageCatalog={account.role === "admin"} />} />
                    <Route path="/expansions" element={<Expansions canManageCatalog={account.role === "admin"} />} />
                    <Route path="/accounts" element={account.role === "admin" ? <Accounts currentAccountId={account.id} onCurrentAccountChange={setAccount} /> : <Navigate to="/maximize" replace />} />
                    <Route path="*" element={<NotFound />} />
                </Routes>
            </main>
        </div>
    );
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

    const navigate = useNavigate();

    function replaceRoute(path: string) {
        navigate(path, { replace: true });
    }

    return (
        <NeonAuthUIProvider
            authClient={authClient}
            redirectTo={`${import.meta.env.BASE_URL}maximize`}
            emailVerification={{ otp: true }}
            localization={{
                SIGN_UP_EMAIL: "Account created. Check your email for a verification code.",
            }}
            social={{ providers: ["google", "github"] }}
            navigate={navigate}
            replace={replaceRoute}
        >
            <Routes>
                <Route path="/auth/:authPath" element={<Auth />} />
                <Route
                    path="*"
                    element={
                        <ProtectedApplication
                            darkMode={darkMode}
                            onDarkModeChange={changeDarkMode}
                        />
                    }
                />
            </Routes>
        </NeonAuthUIProvider>
    );
}
