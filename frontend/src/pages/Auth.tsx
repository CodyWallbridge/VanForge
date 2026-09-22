import { AuthView, authViewPaths, type AuthViewPath } from "@neondatabase/auth/react/ui";
import { Navigate, useParams } from "react-router-dom";
import "./Auth.css";

export default function Auth() {
    const { authPath } = useParams();

    const validPaths = Object.values(authViewPaths) as string[];

    if (!authPath || !validPaths.includes(authPath)) {
        return <Navigate to="/auth/sign-in" replace />;
    }

    return (
        <main className="auth-page">
            <AuthView
                path={authPath as AuthViewPath}
                classNames={{
                    form: {
                        otpInputContainer: "auth-code-input",
                    },
                }}
            />
        </main>
    );
}
