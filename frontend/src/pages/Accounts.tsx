import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { faTrashCan } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { deleteAccount, getAccounts, updateAccountRole } from "../api/accounts";
import ConfirmDialog from "../components/ConfirmDialog";
import DataTable from "../components/DataTable";
import type { TableColumn } from "../components/DataTable";
import type { AuthenticatedUser } from "../dto/AuthenticatedUser";
import "./Accounts.css";

interface RoleSelectorProps {
    value: "user" | "admin";
    disabled: boolean;
    onChange: (role: "user" | "admin") => void;
}

interface AccountsProps {
    currentAccountId: number;
    onCurrentAccountChange: (account: AuthenticatedUser) => void;
}

function RoleSelector({ value, disabled, onChange }: RoleSelectorProps) {
    const [open, setOpen] = useState(false);
    const [menuPosition, setMenuPosition] = useState({ top: 0, left: 0, width: 0 });
    const triggerRef = useRef<HTMLButtonElement>(null);

    useEffect(() => {
        if (!open) {
            return;
        }

        function closeMenu() {
            setOpen(false);
        }

        window.addEventListener("resize", closeMenu);
        window.addEventListener("scroll", closeMenu, true);

        return () => {
            window.removeEventListener("resize", closeMenu);
            window.removeEventListener("scroll", closeMenu, true);
        };
    }, [open]);

    function selectRole(role: "user" | "admin") {
        onChange(role);
        setOpen(false);
    }

    function toggleMenu() {
        if (!open && triggerRef.current) {
            const bounds = triggerRef.current.getBoundingClientRect();
            const menuHeight = 82;
            const opensBelow = bounds.bottom + menuHeight + 4 <= window.innerHeight;
            setMenuPosition({
                top: opensBelow ? bounds.bottom + 4 : bounds.top - menuHeight - 4,
                left: bounds.left,
                width: bounds.width,
            });
        }

        setOpen((current) => !current);
    }

    return (
        <div className="role-selector" onBlur={(event) => {
            if (!event.currentTarget.contains(event.relatedTarget)) {
                setOpen(false);
            }
        }}>
            <button ref={triggerRef} type="button" className="role-selector-trigger" aria-haspopup="listbox" aria-expanded={open} disabled={disabled} onClick={toggleMenu}>
                <span>{value === "admin" ? "Admin" : "User"}</span>
                <span className="role-selector-arrow" aria-hidden="true" />
            </button>
            {open && createPortal(
                <div className="role-selector-menu" role="listbox" aria-label="Account role" style={menuPosition}>
                    <button type="button" role="option" aria-selected={value === "user"} onMouseDown={(event) => event.preventDefault()} onClick={() => selectRole("user")}>User</button>
                    <button type="button" role="option" aria-selected={value === "admin"} onMouseDown={(event) => event.preventDefault()} onClick={() => selectRole("admin")}>Admin</button>
                </div>,
                document.body,
            )}
        </div>
    );
}

export default function Accounts({ currentAccountId, onCurrentAccountChange }: AccountsProps) {
    const [accounts, setAccounts] = useState<AuthenticatedUser[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [accountToDelete, setAccountToDelete] = useState<AuthenticatedUser | null>(null);
    const [busyId, setBusyId] = useState<number | null>(null);

    useEffect(() => {
        getAccounts().then(setAccounts).catch((loadError: unknown) => {
            setError(loadError instanceof Error ? loadError.message : "Unable to load accounts.");
        }).finally(() => setLoading(false));
    }, []);

    async function changeRole(account: AuthenticatedUser, role: "user" | "admin") {
        setBusyId(account.id);
        setError(null);

        try {
            const updated = await updateAccountRole(account.id, role);
            setAccounts((previous) => previous.map((item) => item.id === updated.id ? updated : item));

            if (updated.id === currentAccountId) {
                onCurrentAccountChange(updated);
            }
        } catch (updateError) {
            setError(updateError instanceof Error ? updateError.message : "Unable to update the role.");
        } finally {
            setBusyId(null);
        }
    }

    async function removeAccount() {
        if (!accountToDelete) {
            return;
        }

        setBusyId(accountToDelete.id);
        setError(null);

        try {
            await deleteAccount(accountToDelete.id);
            setAccounts((previous) => previous.filter((account) => account.id !== accountToDelete.id));
            setAccountToDelete(null);
        } catch (deleteError) {
            setError(deleteError instanceof Error ? deleteError.message : "Unable to delete the account.");
        } finally {
            setBusyId(null);
        }
    }

    const columns: TableColumn<AuthenticatedUser>[] = [
        { key: "id", label: "ID", value: (account) => account.id },
        { key: "email", label: "Email", value: (account) => account.email ?? "No email" },
        { key: "role", label: "Role", value: (account) => account.role },
    ];

    return (
        <div className="accounts-page">
            <h1>Accounts</h1>
            <p>Manage VanForge roles and local account data.</p>
            <ConfirmDialog
                open={accountToDelete !== null}
                title="Delete account?"
                message={<>Delete <strong>{accountToDelete?.email}</strong> and all of its VanForge data?</>}
                confirmLabel="Delete account"
                busy={busyId !== null}
                error={error}
                onConfirm={() => void removeAccount()}
                onClose={() => setAccountToDelete(null)}
            />
            {loading && <p role="status">Loading accounts...</p>}
            {error && !accountToDelete && <p role="alert">{error}</p>}
            {!loading && (
                <DataTable
                    columns={columns}
                    rows={accounts}
                    rowKey={(account) => account.id}
                    searchLabel="Search accounts"
                    emptyMessage="No accounts found."
                    rowActions={(account) => (
                        <div className="account-actions">
                            <RoleSelector value={account.role} disabled={busyId !== null} onChange={(role) => void changeRole(account, role)} />
                            <button type="button" className="account-delete-button" disabled={busyId !== null} onClick={() => setAccountToDelete(account)} aria-label={`Delete ${account.email ?? "account"}`}>
                                <FontAwesomeIcon icon={faTrashCan} aria-hidden="true" />
                            </button>
                        </div>
                    )}
                />
            )}
        </div>
    );
}
