import { Link } from "react-router-dom";
import "./NotFound.css";

export default function NotFound() {
    return (
        <section className="not-found-page" aria-labelledby="not-found-title">
            <div className="not-found-card">
                <img className="not-found-icon" src={`${import.meta.env.BASE_URL}vanforge.jpg`} alt="VanForge icon" />
                <span className="not-found-code">404</span>
                <h1 id="not-found-title">Page not found</h1>
                <p>That page does not exist. Head back to your crafting plans.</p>
                <Link className="not-found-link" to="/maximize">
                    Go to Maximize Profit
                </Link>
            </div>
        </section>
    );
}
