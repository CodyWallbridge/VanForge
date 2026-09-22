import { useEffect, useState } from "react";
import { faPen, faPlus, faTrashCan } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { createExpansion, deleteExpansion, getExpansions, updateExpansion } from "../api/expansions";
import { getSettings, setCurrentExpansion } from "../api/settings";
import ConfirmDialog from "../components/ConfirmDialog";
import DataTable from "../components/DataTable";
import type { TableColumn } from "../components/DataTable";
import type { AppSettingsRead } from "../dto/AppSettingsRead";
import type { ExpansionRead } from "../dto/ExpansionRead";
import "./Expansions.css";

interface ExpansionsProps {
    canManageCatalog: boolean;
}

export default function Expansions({ canManageCatalog }: ExpansionsProps) {
    const [expansions, setExpansions] = useState<ExpansionRead[]>([]);
    const [settings, setSettings] = useState<AppSettingsRead | null>(null);
    const [loading, setLoading] = useState(true);
    const [loadError, setLoadError] = useState<string | null>(null);

    const [showForm, setShowForm] = useState(false);
    const [editingExpansion, setEditingExpansion] = useState<ExpansionRead | null>(null);
    const [name, setName] = useState("");
    const [saving, setSaving] = useState(false);
    const [formError, setFormError] = useState<string | null>(null);

    const [settingCurrentId, setSettingCurrentId] = useState<number | null>(null);
    const [currentError, setCurrentError] = useState<string | null>(null);

    const [expansionToDelete, setExpansionToDelete] = useState<ExpansionRead | null>(null);
    const [deleting, setDeleting] = useState(false);
    const [deleteError, setDeleteError] = useState<string | null>(null);

    useEffect(() => {
        let active = true;

        async function loadExpansions() {
            try {
                const expansionResults = await getExpansions();
                let settingsResult: AppSettingsRead | null = null;

                try {
                    settingsResult = await getSettings();
                } catch (error) {
                    if (!(error instanceof Error) || error.message !== "Select an expansion first") {
                        throw error;
                    }
                }

                if (active) {
                    setExpansions(expansionResults);
                    setSettings(settingsResult);
                }
            } catch (error) {
                if (active) {
                    setLoadError(error instanceof Error ? error.message : "Unable to load expansions.");
                }
            } finally {
                if (active) {
                    setLoading(false);
                }
            }
        }

        void loadExpansions();

        return () => {
            active = false;
        };
    }, []);

    function openAddForm() {
        setEditingExpansion(null);
        setName("");
        setFormError(null);
        setShowForm(true);
    }

    function openEditForm(expansion: ExpansionRead) {
        setEditingExpansion(expansion);
        setName(expansion.name);
        setFormError(null);
        setShowForm(true);
    }

    function closeForm() {
        setShowForm(false);
        setEditingExpansion(null);
        setName("");
        setFormError(null);
    }

    async function saveExpansion(event: React.SubmitEvent<HTMLFormElement>) {
        event.preventDefault();
        setFormError(null);

        const trimmedName = name.trim();

        if (!trimmedName) {
            setFormError("Enter an expansion name.");
            return;
        }

        setSaving(true);

        try {
            if (editingExpansion) {
                const updated = await updateExpansion(editingExpansion.id, { name: trimmedName });
                setExpansions((previous) =>
                    previous.map((expansion) => expansion.id === updated.id ? updated : expansion),
                );
                setSettings((previous) =>
                    previous?.current_expansion_id === updated.id
                        ? { ...previous, current_expansion: updated }
                        : previous,
                );
            } else {
                const created = await createExpansion({ name: trimmedName });
                setExpansions((previous) => [...previous, created]);
            }

            closeForm();
        } catch (error) {
            setFormError(error instanceof Error ? error.message : "Unable to save expansion.");
        } finally {
            setSaving(false);
        }
    }

    async function changeCurrent(expansion: ExpansionRead) {
        setCurrentError(null);
        setSettingCurrentId(expansion.id);

        try {
            const updated = await setCurrentExpansion(expansion.id);
            setSettings(updated);
        } catch (error) {
            setCurrentError(error instanceof Error ? error.message : "Unable to change the current expansion.");
        } finally {
            setSettingCurrentId(null);
        }
    }

    async function removeExpansion() {
        if (!expansionToDelete || deleting) {
            return;
        }

        const expansion = expansionToDelete;
        setDeleteError(null);
        setDeleting(true);

        try {
            await deleteExpansion(expansion.id);
            setExpansions((previous) => previous.filter((item) => item.id !== expansion.id));
            setExpansionToDelete(null);
        } catch (error) {
            setDeleteError(error instanceof Error ? error.message : "Unable to delete expansion.");
        } finally {
            setDeleting(false);
        }
    }

    const columns: TableColumn<ExpansionRead>[] = [
        { key: "name", label: "Expansion", value: (expansion) => expansion.name },
        {
            key: "status",
            label: "Status",
            value: (expansion) =>
                expansion.id === settings?.current_expansion_id ? "Current" : "Available",
        },
    ];

    return (
        <div className="expansions-page">
            <h1>Expansions</h1>

            <ConfirmDialog
                open={canManageCatalog && expansionToDelete !== null}
                title="Delete expansion?"
                message={<>Delete <strong>{expansionToDelete?.name}</strong>? This cannot be undone.</>}
                confirmLabel="Delete expansion"
                busy={deleting}
                error={deleteError}
                onConfirm={() => void removeExpansion()}
                onClose={() => setExpansionToDelete(null)}
            />

            {showForm && (
                <form className="expansion-form" onSubmit={saveExpansion}>
                    <h2>{editingExpansion ? "Edit expansion" : "Add expansion"}</h2>
                    <label>
                        Name
                        <input value={name} onChange={(event) => setName(event.target.value)} required />
                    </label>

                    {formError && <p role="alert" className="expansion-form-error">{formError}</p>}

                    <div className="expansion-form-actions">
                        <button type="submit" className="expansion-save-button" disabled={saving}>
                            {saving ? "Saving..." : editingExpansion ? "Save changes" : "Save expansion"}
                        </button>
                        <button type="button" className="expansion-cancel-button" disabled={saving} onClick={closeForm}>
                            Cancel
                        </button>
                    </div>
                </form>
            )}

            {loading && <p role="status">Loading expansions...</p>}
            {loadError && <p role="alert">{loadError}</p>}

            {!loading && !loadError && (
                <>
                    <p className="expansion-current-summary">
                        Current expansion: <strong>{settings?.current_expansion.name ?? "None selected"}</strong>
                    </p>
                    {currentError && <p role="alert" className="expansion-current-error">{currentError}</p>}

                    <DataTable
                        columns={columns}
                        rows={expansions}
                        rowKey={(expansion) => expansion.id}
                        searchLabel="Search expansions"
                        emptyMessage={expansions.length === 0 ? "No expansions added yet." : "No matching expansions."}
                        rowActions={(expansion) => (
                            <div className="expansion-row-actions">
                                {expansion.id === settings?.current_expansion_id ? (
                                    <span className="expansion-current-label">Current</span>
                                ) : (
                                    <button
                                        type="button"
                                        className="expansion-select-button"
                                        disabled={saving || deleting || settingCurrentId !== null}
                                        onClick={() => void changeCurrent(expansion)}
                                    >
                                        {settingCurrentId === expansion.id ? "Selecting..." : "Make current"}
                                    </button>
                                )}
                                {canManageCatalog && (
                                    <>
                                        <button
                                            type="button"
                                            className="expansion-icon-button"
                                            disabled={saving || deleting || settingCurrentId !== null}
                                            onClick={() => openEditForm(expansion)}
                                            aria-label={`Edit ${expansion.name}`}
                                        >
                                            <FontAwesomeIcon icon={faPen} aria-hidden="true" />
                                        </button>
                                        <button
                                            type="button"
                                            className="expansion-icon-button"
                                            disabled={saving || deleting || settingCurrentId !== null || expansion.id === settings?.current_expansion_id}
                                            onClick={() => {
                                                setDeleteError(null);
                                                setExpansionToDelete(expansion);
                                            }}
                                            aria-label={`Delete ${expansion.name}`}
                                            title={expansion.id === settings?.current_expansion_id ? "Select another expansion before deleting this one" : undefined}
                                        >
                                            <FontAwesomeIcon icon={faTrashCan} aria-hidden="true" />
                                        </button>
                                    </>
                                )}
                            </div>
                        )}
                        action={canManageCatalog && !showForm && (
                            <button type="button" className="expansion-add-button" onClick={openAddForm}>
                                <FontAwesomeIcon icon={faPlus} aria-hidden="true" />
                                <span>Add expansion</span>
                            </button>
                        )}
                    />
                </>
            )}
        </div>
    );
}
