import { useEffect, useRef, useState } from "react";
import { faPen, faPlus, faTrashCan } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { getExpansions } from "../api/expansions";
import { getProfessions } from "../api/professions";
import { createRecipe, deleteRecipe, getRecipes, updateRecipe } from "../api/recipes";
import ConfirmDialog from "../components/ConfirmDialog";
import DataTable from "../components/DataTable";
import type { TableColumn } from "../components/DataTable";
import type { RecipeIngredientInput } from "../dto/RecipeCreate";
import type { ExpansionRead } from "../dto/ExpansionRead";
import type { ProfessionRead } from "../dto/ProfessionRead";
import type { RecipeRead } from "../dto/RecipeRead";
import "./Recipes.css";

interface IngredientField {
    key: number;
    name: string;
    amount: string;
}

export default function Recipes() {
    const [recipes, setRecipes] = useState<RecipeRead[]>([]);
    const [professions, setProfessions] = useState<ProfessionRead[]>([]);
    const [expansions, setExpansions] = useState<ExpansionRead[]>([]);
    const [loading, setLoading] = useState(true);
    const [loadError, setLoadError] = useState<string | null>(null);

    const [showForm, setShowForm] = useState(false);
    const [editingRecipe, setEditingRecipe] = useState<RecipeRead | null>(null);
    const [name, setName] = useState("");
    const [professionId, setProfessionId] = useState("");
    const [expansionId, setExpansionId] = useState("");
    const [profit, setProfit] = useState("0");
    const [ingredients, setIngredients] = useState<IngredientField[]>([]);
    const nextIngredientKey = useRef(0);
    const [saving, setSaving] = useState(false);
    const [formError, setFormError] = useState<string | null>(null);

    const [recipeToDelete, setRecipeToDelete] = useState<RecipeRead | null>(null);
    const [deletingId, setDeletingId] = useState<number | null>(null);
    const [deleteError, setDeleteError] = useState<string | null>(null);

    useEffect(() => {
        let active = true;

        async function loadRecipes() {
            try {
                const [recipeResults, professionResults, expansionResults] = await Promise.all([
                    getRecipes(),
                    getProfessions(),
                    getExpansions(),
                ]);

                if (active) {
                    setRecipes(recipeResults);
                    setProfessions(professionResults);
                    setExpansions(expansionResults);
                }
            } catch (error) {
                if (active) {
                    setLoadError(error instanceof Error ? error.message : "Unable to load recipes.");
                }
            } finally {
                if (active) {
                    setLoading(false);
                }
            }
        }

        void loadRecipes();

        return () => {
            active = false;
        };
    }, []);

    function newIngredientField(name = "", amount = "1"): IngredientField {
        nextIngredientKey.current += 1;

        return {
            key: nextIngredientKey.current,
            name,
            amount,
        };
    }

    function openAddForm() {
        setEditingRecipe(null);
        setName("");
        setProfessionId("");
        setExpansionId("");
        setProfit("0");
        setIngredients([newIngredientField()]);
        setFormError(null);
        setShowForm(true);
    }

    function openEditForm(recipe: RecipeRead) {
        setEditingRecipe(recipe);
        setName(recipe.name);
        setProfessionId(String(recipe.profession_id));
        setExpansionId(String(recipe.expansion_id));
        setProfit(String(recipe.profit_per_craft));
        setIngredients(
            recipe.ingredients.map((link) =>
                newIngredientField(link.ingredient.name, String(link.amount_required)),
            ),
        );
        setFormError(null);
        setShowForm(true);
    }

    function closeForm() {
        setShowForm(false);
        setEditingRecipe(null);
        setFormError(null);
    }

    function changeIngredient(key: number, field: "name" | "amount", value: string) {
        setIngredients((previous) =>
            previous.map((ingredient) =>
                ingredient.key === key ? { ...ingredient, [field]: value } : ingredient,
            ),
        );
    }

    function removeIngredient(key: number) {
        setIngredients((previous) => previous.filter((ingredient) => ingredient.key !== key));
    }

    async function saveRecipe(event: React.SubmitEvent<HTMLFormElement>) {
        event.preventDefault();
        setFormError(null);

        if (!name.trim()) {
            setFormError("Enter a recipe name.");
            return;
        }

        if (!professionId || !expansionId) {
            setFormError("Select a profession and expansion.");
            return;
        }

        const profitValue = Number(profit);

        if (!Number.isSafeInteger(profitValue)) {
            setFormError("Profit must be a whole number of gold.");
            return;
        }

        const ingredientInputs: RecipeIngredientInput[] = [];
        const ingredientNames = new Set<string>();

        for (const ingredient of ingredients) {
            const ingredientName = ingredient.name.trim();
            const amount = Number(ingredient.amount);

            if (!ingredientName) {
                setFormError("Enter a name for every ingredient, or remove empty rows.");
                return;
            }

            if (!Number.isSafeInteger(amount) || amount <= 0) {
                setFormError("Each ingredient amount must be a positive whole number.");
                return;
            }

            const nameKey = ingredientName.toLocaleLowerCase();

            if (ingredientNames.has(nameKey)) {
                setFormError("Each ingredient can appear only once in a recipe.");
                return;
            }

            ingredientNames.add(nameKey);
            ingredientInputs.push({ name: ingredientName, amount_required: amount });
        }

        const recipeData = {
            name: name.trim(),
            profession_id: Number(professionId),
            expansion_id: Number(expansionId),
            profit_per_craft: profitValue,
            ingredients: ingredientInputs,
        };

        setSaving(true);

        try {
            if (editingRecipe) {
                const updated = await updateRecipe(editingRecipe.id, recipeData);
                setRecipes((previous) =>
                    previous.map((recipe) => recipe.id === updated.id ? updated : recipe),
                );
            } else {
                const created = await createRecipe(recipeData);
                setRecipes((previous) => [...previous, created]);
            }

            closeForm();
        } catch (error) {
            setFormError(error instanceof Error ? error.message : "Unable to save recipe.");
        } finally {
            setSaving(false);
        }
    }

    async function removeRecipe() {
        if (!recipeToDelete || deletingId !== null) {
            return;
        }

        const recipe = recipeToDelete;
        setDeleteError(null);
        setDeletingId(recipe.id);

        try {
            await deleteRecipe(recipe.id);
            setRecipes((previous) => previous.filter((item) => item.id !== recipe.id));
            setRecipeToDelete(null);
        } catch (error) {
            setDeleteError(error instanceof Error ? error.message : "Unable to delete recipe.");
        } finally {
            setDeletingId(null);
        }
    }

    const professionNames = new Map(professions.map((profession) => [profession.id, profession.name]));
    const expansionNames = new Map(expansions.map((expansion) => [expansion.id, expansion.name]));

    const columns: TableColumn<RecipeRead>[] = [
        { key: "name", label: "Name", value: (recipe) => recipe.name },
        {
            key: "profession",
            label: "Profession",
            value: (recipe) => professionNames.get(recipe.profession_id) ?? "Unknown profession",
        },
        {
            key: "expansion",
            label: "Expansion",
            value: (recipe) => expansionNames.get(recipe.expansion_id) ?? "Unknown expansion",
        },
        { key: "profit", label: "Profit (gold)", value: (recipe) => recipe.profit_per_craft },
        {
            key: "ingredients",
            label: "Ingredients",
            value: (recipe) => recipe.ingredients
                .map((link) => `${link.amount_required} ${link.ingredient.name}`)
                .join(", "),
        },
    ];

    return (
        <div className="recipes-page">
            <h1>Recipes</h1>

            <ConfirmDialog
                open={recipeToDelete !== null}
                title="Delete recipe?"
                message={<>Delete <strong>{recipeToDelete?.name}</strong>? Its ingredient links and character assignments will also be removed.</>}
                confirmLabel="Delete recipe"
                busy={deletingId !== null}
                error={deleteError}
                onConfirm={() => void removeRecipe()}
                onClose={() => setRecipeToDelete(null)}
            />

            {showForm && (
                <form className="recipe-form" onSubmit={saveRecipe}>
                    <h2>{editingRecipe ? "Edit recipe" : "Add recipe"}</h2>

                    <div className="recipe-form-fields">
                        <label>
                            Name
                            <input value={name} onChange={(event) => setName(event.target.value)} required />
                        </label>
                        <label>
                            Profession
                            <select value={professionId} onChange={(event) => setProfessionId(event.target.value)} required>
                                <option value="">Select a profession</option>
                                {professions.map((profession) => (
                                    <option key={profession.id} value={profession.id}>{profession.name}</option>
                                ))}
                            </select>
                        </label>
                        <label>
                            Expansion
                            <select value={expansionId} onChange={(event) => setExpansionId(event.target.value)} required>
                                <option value="">Select an expansion</option>
                                {expansions.map((expansion) => (
                                    <option key={expansion.id} value={expansion.id}>{expansion.name}</option>
                                ))}
                            </select>
                        </label>
                        <label>
                            Profit per craft (gold)
                            <input type="number" step="1" value={profit} onChange={(event) => setProfit(event.target.value)} required />
                        </label>
                    </div>

                    <div className="recipe-ingredients-heading">
                        <h3>Ingredients</h3>
                        <button type="button" disabled={saving} onClick={() => setIngredients((previous) => [...previous, newIngredientField()])}>
                            <FontAwesomeIcon icon={faPlus} aria-hidden="true" /> Add ingredient
                        </button>
                    </div>
                    <div className="recipe-ingredients">
                        {ingredients.map((ingredient) => (
                            <div className="recipe-ingredient-row" key={ingredient.key}>
                                <label>
                                    Ingredient name
                                    <input value={ingredient.name} onChange={(event) => changeIngredient(ingredient.key, "name", event.target.value)} required />
                                </label>
                                <label>
                                    Amount
                                    <input type="number" min="1" step="1" value={ingredient.amount} onChange={(event) => changeIngredient(ingredient.key, "amount", event.target.value)} required />
                                </label>
                                <button type="button" className="recipe-remove-ingredient" disabled={saving} onClick={() => removeIngredient(ingredient.key)} aria-label={`Remove ${ingredient.name || "ingredient"}`}>
                                    <FontAwesomeIcon icon={faTrashCan} aria-hidden="true" />
                                </button>
                            </div>
                        ))}
                        {ingredients.length === 0 && <p>No ingredients added.</p>}
                    </div>

                    {formError && <p role="alert" className="recipe-form-error">{formError}</p>}

                    <div className="recipe-form-actions">
                        <button type="submit" className="recipe-save-button" disabled={saving}>
                            {saving ? "Saving..." : editingRecipe ? "Save changes" : "Save recipe"}
                        </button>
                        <button type="button" className="recipe-cancel-button" disabled={saving} onClick={closeForm}>
                            Cancel
                        </button>
                    </div>
                </form>
            )}

            {loading && <p role="status">Loading recipes...</p>}
            {loadError && <p role="alert">{loadError}</p>}

            {!loading && !loadError && (
                <DataTable
                    columns={columns}
                    rows={recipes}
                    rowKey={(recipe) => recipe.id}
                    searchLabel="Search recipes"
                    emptyMessage={recipes.length === 0 ? "No recipes added yet." : "No matching recipes."}
                    rowActions={(recipe) => (
                        <div className="recipe-row-actions">
                            <button type="button" disabled={saving || deletingId !== null} onClick={() => openEditForm(recipe)} aria-label={`Edit ${recipe.name}`}>
                                <FontAwesomeIcon icon={faPen} aria-hidden="true" />
                            </button>
                            <button type="button" disabled={saving || deletingId !== null} onClick={() => {
                                setDeleteError(null);
                                setRecipeToDelete(recipe);
                            }} aria-label={`Delete ${recipe.name}`}>
                                <FontAwesomeIcon icon={faTrashCan} aria-hidden="true" />
                            </button>
                        </div>
                    )}
                    action={!showForm && (
                        <button type="button" className="recipe-add-button" onClick={openAddForm}>
                            <FontAwesomeIcon icon={faPlus} aria-hidden="true" />
                            <span>Add recipe</span>
                        </button>
                    )}
                />
            )}
        </div>
    );
}
