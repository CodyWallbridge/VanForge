import { useState } from "react";
import { Link, NavLink, useLocation } from "react-router-dom";

interface SidebarProps {
    darkMode: boolean;
    onDarkModeChange: (enabled: boolean) => void;
}

const navigationGroups = [
    {
        id: "planning",
        label: "Planning",
        items: [
            { to: "/maximize", label: "Maximize Profit" },
            { to: "/manual", label: "Manual Planner" },
        ],
    },
    {
        id: "management",
        label: "Management",
        items: [
            { to: "/characters", label: "Characters" },
            { to: "/recipes", label: "Recipes" },
        ],
    },
    {
        id: "settings",
        label: "Settings",
        items: [
            { to: "/expansions", label: "Expansions" },
        ],
    },
];

export default function Sidebar({
    darkMode,
    onDarkModeChange,
}: SidebarProps) {
    const location = useLocation();
    const [openGroups, setOpenGroups] = useState<Record<string, boolean>>(() => {
        const initialState: Record<string, boolean> = {};

        for (const group of navigationGroups) {
            const containsCurrentPage = group.items.some(
                (item) => item.to === location.pathname,
            );

            initialState[group.id] =
                group.id === "planning" || containsCurrentPage;
        }

        return initialState;
    });

    function toggleGroup(groupId: string) {
        setOpenGroups((previous) => ({
            ...previous,
            [groupId]: !previous[groupId],
        }));
    }

    return (
        <aside className="sidebar">
            <Link className="sidebar-brand" to="/maximize" aria-label="VanForge home">
                <img className="brand-icon" src="/vanforge.jpg" alt="" />
                <span className="brand-copy">
                    <span className="brand-name"><span>Van</span><span>Forge</span></span>
                    <span className="brand-description">Crafting Planner</span>
                </span>
            </Link>

            <nav aria-label="Main navigation">
                {navigationGroups.map((group) => (
                    <div key={group.id}>
                        <button
                            type="button"
                            className="sidebar-group"
                            aria-expanded={openGroups[group.id]}
                            aria-controls={`${group.id}-navigation`}
                            onClick={() => toggleGroup(group.id)}
                        >
                            <span>{group.label}</span>
                            <span aria-hidden="true">
                                {openGroups[group.id] ? "−" : "+"}
                            </span>
                        </button>

                        <ul
                            id={`${group.id}-navigation`}
                            className="sidebar-links"
                            hidden={!openGroups[group.id]}
                        >
                            {group.items.map((item) => (
                                <li key={item.to}>
                                    <NavLink
                                        to={item.to}
                                        className={({ isActive }) =>
                                            isActive
                                                ? "sidebar-link sidebar-link-active"
                                                : "sidebar-link"
                                        }
                                    >
                                        {item.label}
                                    </NavLink>
                                </li>
                            ))}
                        </ul>
                    </div>
                ))}
            </nav>

            <div className="sidebar-footer">
                <label className="theme-toggle">
                    <span>Dark mode</span>
                    <input
                        type="checkbox"
                        role="switch"
                        checked={darkMode}
                        onChange={(event) =>
                            onDarkModeChange(event.target.checked)
                        }
                    />
                </label>
            </div>
        </aside>
    );
}