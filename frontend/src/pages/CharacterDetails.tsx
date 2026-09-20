import { useEffect, useState } from "react";
import { faPen, faPlus, faTrashCan } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { Link, useParams } from "react-router-dom";
import { assignCharacterRecipe, getCharacterRecipes, removeCharacterRecipe, updateCharacterRecipe } from "../api/characterRecipes";
import { getCharacter } from "../api/characters";
import { getProfessions } from "../api/professions";
import { getRecipes } from "../api/recipes";
import { getSettings } from "../api/settings";
import ConfirmDialog from "../components/ConfirmDialog";
import DataTable from "../components/DataTable";
import type { TableColumn } from "../components/DataTable";
import type { CharacterRead } from "../dto/CharacterRead";
import type { CharacterRecipeRead } from "../dto/CharacterRecipeRead";
import type { ProfessionRead } from "../dto/ProfessionRead";
import type { RecipeRead } from "../dto/RecipeRead";
import type { AppSettingsRead } from "../dto/AppSettingsRead";
import "./CharacterDetails.css";

interface KnownRecipeRow {
    recipe: RecipeRead;
    assignment: CharacterRecipeRead;
}

export default function CharacterDetails() {
    const { characterId } = useParams();
    const id = Number(characterId);

    const [character, setCharacter] = useState<CharacterRead | null>(null);
    const [professions, setProfessions] = useState<ProfessionRead[]>([]);
    const [recipes, setRecipes] = useState<RecipeRead[]>([]);
    const [assignments, setAssignments] = useState<CharacterRecipeRead[]>([]);
    const [settings, setSettings] = useState<AppSettingsRead | null>(null);
    const [loading, setLoading] = useState(true);
    const [loadError, setLoadError] = useState<string | null>(null);

    const [formProfessionId, setFormProfessionId] = useState<number | null>(null);
    const [editingRecipeId, setEditingRecipeId] = useState<number | null>(null);
    const [selectedRecipeId, setSelectedRecipeId] = useState("");
    const [concentrationCost, setConcentrationCost] = useState("");
    const [saving, setSaving] = useState(false);
    const [formError, setFormError] = useState<string | null>(null);

    const [assignmentToRemove, setAssignmentToRemove] = useState<KnownRecipeRow | null>(null);
    const [removing, setRemoving] = useState(false);
    const [removeError, setRemoveError] = useState<string | null>(null);

    useEffect(() => {
        let active = true;

        if (!Number.isSafeInteger(id) || id <= 0) {
            setLoadError("Invalid character ID.");
            setLoading(false);
            return;
        }

        async function loadDetails() {
            try {
                const [characterResult, professionResults, recipeResults, assignmentResults, settingsResult] = await Promise.all([
                    getCharacter(id),
                    getProfessions(),
                    getRecipes(),
                    getCharacterRecipes(id),
                    getSettings(),
                ]);

                if (active) {
                    setCharacter(characterResult);
                    setProfessions(professionResults);
                    setRecipes(recipeResults);
                    setAssignments(assignmentResults);
                    setSettings(settingsResult);
                }
            } catch (error) {
                if (active) {
                    setLoadError(error instanceof Error ? error.message : "Unable to load character details.");
                }
            } finally {
                if (active) {
                    setLoading(false);
                }
            }
        }

        void loadDetails();

        return () => {
            active = false;
        };
    }, [id]);

    function closeForm() {
        setFormProfessionId(null);
        setEditingRecipeId(null);
        setSelectedRecipeId("");
        setConcentrationCost("");
        setFormError(null);
    }

    function openAddForm(professionId: number) {
        setFormProfessionId(professionId);
        setEditingRecipeId(null);
        setSelectedRecipeId("");
        setConcentrationCost("");
        setFormError(null);
    }

    function openEditForm(row: KnownRecipeRow) {
        setFormProfessionId(row.recipe.profession_id);
        setEditingRecipeId(row.recipe.id);
        setSelectedRecipeId(String(row.recipe.id));
        setConcentrationCost(String(row.assignment.concentration_cost));
        setFormError(null);
    }

    async function saveAssignment(event: React.SubmitEvent<HTMLFormElement>) {
        event.preventDefault();
        setFormError(null);

        if (!character || !selectedRecipeId) {
            setFormError("Select a recipe.");
            return;
        }

        const cost = Number(concentrationCost);

        if (!Number.isSafeInteger(cost) || cost <= 0) {
            setFormError("Concentration cost must be a positive whole number.");
            return;
        }

        setSaving(true);

        try {
            if (editingRecipeId !== null) {
                const updated = await updateCharacterRecipe(character.id, editingRecipeId, cost);
                setAssignments((previous) =>
                    previous.map((assignment) =>
                        assignment.recipe_id === updated.recipe_id ? updated : assignment,
                    ),
                );
            } else {
                const created = await assignCharacterRecipe(character.id, {
                    recipe_id: Number(selectedRecipeId),
                    concentration_cost: cost,
                });
                setAssignments((previous) => [...previous, created]);
            }

            closeForm();
        } catch (error) {
            setFormError(error instanceof Error ? error.message : "Unable to save known recipe.");
        } finally {
            setSaving(false);
        }
    }

    async function removeAssignment() {
        if (!character || !assignmentToRemove || removing) {
            return;
        }

        const recipeId = assignmentToRemove.recipe.id;
        setRemoveError(null);
        setRemoving(true);

        try {
            await removeCharacterRecipe(character.id, recipeId);
            setAssignments((previous) =>
                previous.filter((assignment) => assignment.recipe_id !== recipeId),
            );
            setAssignmentToRemove(null);
        } catch (error) {
            setRemoveError(error instanceof Error ? error.message : "Unable to remove known recipe.");
        } finally {
            setRemoving(false);
        }
    }

    const recipeById = new Map(recipes.map((recipe) => [recipe.id, recipe]));
    const professionById = new Map(professions.map((profession) => [profession.id, profession.name]));
    const activeProfessions = character
        ? [character.profession1_id, character.profession2_id]
        : [];

    const availableRecipes = formProfessionId === null || !settings
        ? []
        : recipes.filter((recipe) =>
            recipe.profession_id === formProfessionId &&
            recipe.expansion_id === settings.current_expansion_id &&
            (recipe.id === editingRecipeId ||
                !assignments.some((assignment) => assignment.recipe_id === recipe.id)),
        );

    const columns: TableColumn<KnownRecipeRow>[] = [
        { key: "name", label: "Recipe", value: (row) => row.recipe.name },
        {
            key: "cost",
            label: "Concentration cost",
            value: (row) => row.assignment.concentration_cost,
        },
        {
            key: "profit",
            label: "Profit (gold)",
            value: (row) => row.recipe.profit_per_craft,
        },
    ];

    return (
        <div className="character-details-page">
            <Link className="character-details-back" to="/characters">Back to characters</Link>

            {loading && <p role="status">Loading character details...</p>}
            {loadError && <p role="alert">{loadError}</p>}

            {!loading && character && settings && (
                <>
                    <h1>{character.name}</h1>
                    <p className="character-details-summary">
                        Current expansion: {settings.current_expansion.name}. Available concentration:
                        {" "}{character.concentration} for each profession.
                    </p>
                    <p className="character-details-note">
                        Showing known recipes for the current expansion and active professions.
                    </p>

                    <ConfirmDialog
                        open={assignmentToRemove !== null}
                        title="Remove known recipe?"
                        message={<>Remove <strong>{assignmentToRemove?.recipe.name}</strong> from {character.name}? The recipe itself will remain available.</>}
                        confirmLabel="Remove recipe"
                        busy={removing}
                        error={removeError}
                        onConfirm={() => void removeAssignment()}
                        onClose={() => setAssignmentToRemove(null)}
                    />

                    {formProfessionId !== null && (
                        <form className="known-recipe-form" onSubmit={saveAssignment}>
                            <h2>
                                {editingRecipeId !== null ? "Edit concentration cost" : "Add known recipe"}
                                {" - "}{professionById.get(formProfessionId) ?? "Profession"}
                            </h2>
                            <div className="known-recipe-form-fields">
                                <label>
                                    Recipe
                                    <select
                                        value={selectedRecipeId}
                                        onChange={(event) => setSelectedRecipeId(event.target.value)}
                                        disabled={editingRecipeId !== null || saving}
                                        required
                                    >
                                        <option value="">Select a recipe</option>
                                        {availableRecipes.map((recipe) => (
                                            <option key={recipe.id} value={recipe.id}>{recipe.name}</option>
                                        ))}
                                    </select>
                                </label>
                                <label>
                                    Concentration cost
                                    <input
                                        type="number"
                                        min="1"
                                        step="1"
                                        value={concentrationCost}
                                        onChange={(event) => setConcentrationCost(event.target.value)}
                                        required
                                    />
                                </label>
                            </div>
                            {editingRecipeId === null && availableRecipes.length === 0 && (
                                <p className="known-recipe-empty">
                                    No unassigned {professionById.get(formProfessionId) ?? "profession"} recipes are
                                    available for {settings.current_expansion.name}. Create one on the{" "}
                                    <Link to="/recipes">Recipes page</Link> first.
                                </p>
                            )}
                            {formError && <p role="alert" className="known-recipe-error">{formError}</p>}
                            <div className="known-recipe-form-actions">
                                <button type="submit" className="known-recipe-save" disabled={saving || availableRecipes.length === 0}>
                                    {saving ? "Saving..." : editingRecipeId !== null ? "Save cost" : "Add recipe"}
                                </button>
                                <button type="button" className="known-recipe-cancel" disabled={saving} onClick={closeForm}>
                                    Cancel
                                </button>
                            </div>
                        </form>
                    )}

                    {activeProfessions.map((professionId) => {
                        const professionName = professionById.get(professionId) ?? "Unknown profession";
                        const rows: KnownRecipeRow[] = [];

                        for (const assignment of assignments) {
                            const recipe = recipeById.get(assignment.recipe_id);

                            if (recipe && recipe.profession_id === professionId) {
                                rows.push({ recipe, assignment });
                            }
                        }

                        return (
                            <section className="character-profession" key={professionId}>
                                <h2>{professionName}</h2>
                                <DataTable
                                    columns={columns}
                                    rows={rows}
                                    rowKey={(row) => row.recipe.id}
                                    searchLabel={`Search ${professionName} recipes`}
                                    emptyMessage={rows.length === 0 ? "No known recipes for this profession." : "No matching recipes."}
                                    action={formProfessionId === null && (
                                        <button type="button" className="known-recipe-add" onClick={() => openAddForm(professionId)}>
                                            <FontAwesomeIcon icon={faPlus} aria-hidden="true" />
                                            <span>Add known recipe</span>
                                        </button>
                                    )}
                                    rowActions={(row) => (
                                        <div className="known-recipe-row-actions">
                                            <button type="button" disabled={saving || removing} onClick={() => openEditForm(row)} aria-label={`Edit concentration cost for ${row.recipe.name}`}>
                                                <FontAwesomeIcon icon={faPen} aria-hidden="true" />
                                            </button>
                                            <button type="button" disabled={saving || removing} onClick={() => {
                                                setRemoveError(null);
                                                setAssignmentToRemove(row);
                                            }} aria-label={`Remove ${row.recipe.name} from known recipes`}>
                                                <FontAwesomeIcon icon={faTrashCan} aria-hidden="true" />
                                            </button>
                                        </div>
                                    )}
                                />
                            </section>
                        );
                    })}
                </>
            )}
        </div>
    );
}
