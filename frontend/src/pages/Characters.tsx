import { useEffect, useRef, useState } from "react";
import { createCharacter, deleteCharacter, getCharacters, updateCharacter } from "../api/characters";
import { getProfessions } from "../api/professions";
import DataTable from "../components/DataTable";
import type { TableColumn } from "../components/DataTable";
import type { CharacterRead } from "../dto/CharacterRead";
import type { ProfessionRead } from "../dto/ProfessionRead";
import "./Characters.css";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faPen, faPlus, faTrashCan } from "@fortawesome/free-solid-svg-icons";

export default function Characters() {
    const [characters, setCharacters] = useState<CharacterRead[]>([]);
    const [professions, setProfessions] = useState<ProfessionRead[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const [showForm, setShowForm] = useState(false);
    const [name, setName] = useState("");
    const [firstProfession, setFirstProfession] = useState("");
    const [secondProfession, setSecondProfession] = useState("");
    const [concentration, setConcentration] = useState("1000");
    const [saving, setSaving] = useState(false);
    const [editingCharacter, setEditingCharacter] = useState<CharacterRead | null>(null);
    const [formError, setFormError] = useState<string | null>(null);

    const [characterToDelete, setCharacterToDelete] = useState<CharacterRead | null>(null);
    const deleteDialogRef = useRef<HTMLDialogElement>(null);

    const [deletingId, setDeletingId] = useState<number | null>(null);
    const [deleteError, setDeleteError] = useState<string | null>(null);

    useEffect(() => {
        let active = true;

        async function loadCharacters() {
            try {
                const [characterResults, professionResults] = await Promise.all([
                    getCharacters(),
                    getProfessions(),
                ]);

                if (active) {
                    setCharacters(characterResults);
                    setProfessions(professionResults);
                }
            } catch (error) {
                if (active) {
                    const message =
                        error instanceof Error
                            ? error.message
                            : "Unable to load characters.";

                    setError(message);
                }
            } finally {
                if (active) {
                    setLoading(false);
                }
            }
        }

        void loadCharacters();

        return () => {
            active = false;
        };
    }, []);

    useEffect(() => {
        const dialog = deleteDialogRef.current;

        if (!dialog) {
            return;
        }

        if (characterToDelete && !dialog.open) {
            dialog.showModal();
        } else if (!characterToDelete && dialog.open) {
            dialog.close();
        }
    }, [characterToDelete]);

    function editCharacter(character: CharacterRead) {
        setEditingCharacter(character);
        setName(character.name);
        setFirstProfession(String(character.profession1_id));
        setSecondProfession(String(character.profession2_id));
        setConcentration(String(character.concentration));
        setFormError(null);
        setShowForm(true);
    }

    function closeForm() {
        setShowForm(false);
        setEditingCharacter(null);
        setFormError(null);
        setName("");
        setFirstProfession("");
        setSecondProfession("");
        setConcentration("1000");
    }

    async function saveCharacter(event: React.SubmitEvent<HTMLFormElement>) {
        event.preventDefault();
        setFormError(null);

        if (!name.trim()) {
            setFormError("Enter a character name.");
            return;
        }

        if (!firstProfession || !secondProfession) {
            setFormError("Select both professions.");
            return;
        }

        if (firstProfession === secondProfession) {
            setFormError("Choose two different professions.");
            return;
        }

        const concentrationValue = Number(concentration);

        if (
            !Number.isInteger(concentrationValue) ||
            concentrationValue < 0 ||
            concentrationValue > 1000
        ) {
            setFormError("Concentration must be a whole number from 0 to 1000.");
            return;
        }

        setSaving(true);

        try {
            const characterData = {
                name: name.trim(),
                profession1_id: Number(firstProfession),
                profession2_id: Number(secondProfession),
                concentration: concentrationValue,
            };

            if (editingCharacter) {
                const updated = await updateCharacter(editingCharacter.id, characterData);
                setCharacters((previous) =>
                    previous.map((character) =>
                        character.id === updated.id ? updated : character,
                    ),
                );
            } else {
                const created = await createCharacter(characterData);
                setCharacters((previous) => [...previous, created]);
            }

            closeForm();
        } catch (error) {
            const message =
                error instanceof Error
                    ? error.message
                    : editingCharacter
                        ? "Unable to update character."
                        : "Unable to add character.";

            setFormError(message);
        } finally {
            setSaving(false);
        }
    }

    async function removeCharacter() {
        if (!characterToDelete || deletingId !== null) {
            return;
        }

        const character = characterToDelete;
        setDeleteError(null);
        setDeletingId(character.id);

        try {
            await deleteCharacter(character.id);
            setCharacters((previous) =>
                previous.filter((item) => item.id !== character.id),
            );
            setCharacterToDelete(null);
        } catch (error) {
            const message =
                error instanceof Error
                    ? error.message
                    : "Unable to delete character.";

            setDeleteError(message);
        } finally {
            setDeletingId(null);
        }
    }

    const professionNames = new Map(
        professions.map((profession) => [profession.id, profession.name]),
    );

    const columns: TableColumn<CharacterRead>[] = [
        { key: "name", label: "Name", value: (character) => character.name },
        {
            key: "firstProfession",
            label: "First profession",
            value: (character) =>
                professionNames.get(character.profession1_id) ?? "Unknown profession",
        },
        {
            key: "secondProfession",
            label: "Second profession",
            value: (character) =>
                professionNames.get(character.profession2_id) ?? "Unknown profession",
        },
        {
            key: "concentration",
            label: "Concentration",
            value: (character) => character.concentration,
        },
    ];

    return (
        <>
            <h1>Characters</h1>

            <dialog
                ref={deleteDialogRef}
                className="character-delete-dialog"
                aria-labelledby="character-delete-title"
                onClose={() => setCharacterToDelete(null)}
                onCancel={(event) => {
                    if (deletingId !== null) {
                        event.preventDefault();
                    }
                }}
            >
                <h2 id="character-delete-title">Delete character?</h2>
                <p>
                    Delete <strong>{characterToDelete?.name}</strong>? Their known
                    recipes will also be removed.
                </p>

                {deleteError && <p role="alert" className="character-delete-error">{deleteError}</p>}

                <div className="character-delete-dialog-actions">
                    <button
                        type="button"
                        className="character-delete-cancel"
                        disabled={deletingId !== null}
                        onClick={() => setCharacterToDelete(null)}
                    >
                        Cancel
                    </button>
                    <button
                        type="button"
                        className="character-delete-confirm"
                        disabled={deletingId !== null}
                        onClick={() => void removeCharacter()}
                    >
                        {deletingId !== null ? "Deleting..." : "Delete character"}
                    </button>
                </div>
            </dialog>

            {showForm && (
                <form className="character-form" onSubmit={saveCharacter}>
                    <h2>{editingCharacter ? "Edit character" : "Add character"}</h2>

                    <div className="character-form-fields">
                        <label>
                            Name
                            <input
                                value={name}
                                onChange={(event) => setName(event.target.value)}
                                required
                            />
                        </label>

                        <label>
                            First profession
                            <select
                                value={firstProfession}
                                onChange={(event) =>
                                    setFirstProfession(event.target.value)
                                }
                                required
                            >
                                <option value="">Select a profession</option>
                                {professions.map((profession) => (
                                    <option key={profession.id} value={profession.id}>
                                        {profession.name}
                                    </option>
                                ))}
                            </select>
                        </label>

                        <label>
                            Second profession
                            <select
                                value={secondProfession}
                                onChange={(event) =>
                                    setSecondProfession(event.target.value)
                                }
                                required
                            >
                                <option value="">Select a profession</option>
                                {professions.map((profession) => (
                                    <option key={profession.id} value={profession.id}>
                                        {profession.name}
                                    </option>
                                ))}
                            </select>
                        </label>

                        <label>
                            Concentration
                            <input
                                type="number"
                                min="0"
                                max="1000"
                                step="1"
                                value={concentration}
                                onChange={(event) =>
                                    setConcentration(event.target.value)
                                }
                                required
                            />
                        </label>
                    </div>

                    {formError && <p role="alert">{formError}</p>}

                    <div className="character-form-actions">
                        <button type="submit" disabled={saving}>
                            {saving
                                ? "Saving..."
                                : editingCharacter
                                    ? "Save changes"
                                    : "Save character"}
                        </button>
                        <button
                            type="button"
                            className="character-cancel-button"
                            disabled={saving}
                            onClick={closeForm}
                        >
                            Cancel
                        </button>
                    </div>
                </form>
            )}

            {loading && <p role="status">Loading characters…</p>}
            {error && <p role="alert">{error}</p>}

            {!loading && !error && (
                <DataTable
                    columns={columns}
                    rows={characters}
                    rowKey={(character) => character.id}
                    rowActions={(character) => (
                        <div className="character-row-actions">
                            <button
                                type="button"
                                className="character-edit-button"
                                disabled={saving || deletingId !== null}
                                onClick={() => editCharacter(character)}
                                aria-label={`Edit ${character.name}`}
                            >
                                <FontAwesomeIcon icon={faPen} aria-hidden="true" />
                            </button>
                            <button
                                type="button"
                                className="character-delete-button"
                                disabled={saving || deletingId !== null}
                                onClick={() => {
                                    setDeleteError(null);
                                    setCharacterToDelete(character);
                                }}
                                aria-label={`Delete ${character.name}`}
                            >
                                <FontAwesomeIcon icon={faTrashCan} aria-hidden="true" />
                            </button>
                        </div>
                    )}
                    searchLabel="Search characters"
                    emptyMessage={
                        characters.length === 0
                            ? "No characters added yet."
                            : "No matching characters."
                    }
                    action={
                        !showForm && (
                            <button
                                type="button"
                                className="character-add-button"
                                onClick={() => {
                                    setFormError(null);
                                    setEditingCharacter(null);
                                    setShowForm(true);
                                }}
                            >
                                <FontAwesomeIcon icon={faPlus} aria-hidden="true" />
                                <span>Add character</span>
                            </button>
                        )
                    }
                />
            )}
        </>
    );
}