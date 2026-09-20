import { useEffect, useState } from "react";
import { faPlus, faTrashCan } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { Link, useLocation } from "react-router-dom";
import { getCharacters } from "../api/characters";
import { calculateMaterials, getPlannerOptions } from "../api/planner";
import { getProfessions } from "../api/professions";
import { getSettings } from "../api/settings";
import DataTable from "../components/DataTable";
import type { TableColumn } from "../components/DataTable";
import type { AppSettingsRead } from "../dto/AppSettingsRead";
import type { CharacterPlanItem } from "../dto/CharacterPlanItem";
import type { CharacterRead } from "../dto/CharacterRead";
import type { PlannerOption } from "../dto/PlannerOption";
import type { ProfessionRead } from "../dto/ProfessionRead";
import "./ManualPlanner.css";

interface ImportedPlan {
    crafts: CharacterPlanItem[];
    expansionId: number;
}

interface MaterialRow {
    name: string;
    amount: number;
}

export default function ManualPlanner() {
    const location = useLocation();
    const importedPlan = location.state as ImportedPlan | null;

    const [characters, setCharacters] = useState<CharacterRead[]>([]);
    const [professions, setProfessions] = useState<ProfessionRead[]>([]);
    const [settings, setSettings] = useState<AppSettingsRead | null>(null);
    const [optionsByCharacter, setOptionsByCharacter] = useState<Record<number, PlannerOption[]>>({});
    const [loading, setLoading] = useState(true);
    const [loadError, setLoadError] = useState<string | null>(null);

    const [plan, setPlan] = useState<CharacterPlanItem[]>(() => importedPlan?.crafts ?? []);
    const [sourceExpansionId, setSourceExpansionId] = useState<number | null>(
        importedPlan?.expansionId ?? null,
    );
    const [selectedCharacterId, setSelectedCharacterId] = useState("");
    const [selectedRecipeId, setSelectedRecipeId] = useState("");
    const [newCrafts, setNewCrafts] = useState("1");
    const [planError, setPlanError] = useState<string | null>(null);

    const [materials, setMaterials] = useState<Record<string, number> | null>(null);
    const [calculating, setCalculating] = useState(false);
    const [calculationError, setCalculationError] = useState<string | null>(null);

    useEffect(() => {
        let active = true;

        async function loadOptions() {
            try {
                const [characterResults, professionResults, settingsResult] = await Promise.all([
                    getCharacters(),
                    getProfessions(),
                    getSettings(),
                ]);
                const optionLists = await Promise.all(
                    characterResults.map((character) => getPlannerOptions(character.id)),
                );
                const options: Record<number, PlannerOption[]> = {};

                for (let index = 0; index < characterResults.length; index += 1) {
                    options[characterResults[index].id] = optionLists[index];
                }

                if (active) {
                    setCharacters(characterResults);
                    setProfessions(professionResults);
                    setSettings(settingsResult);
                    setOptionsByCharacter(options);
                }
            } catch (error) {
                if (active) {
                    setLoadError(error instanceof Error ? error.message : "Unable to load planner options.");
                }
            } finally {
                if (active) {
                    setLoading(false);
                }
            }
        }

        void loadOptions();

        return () => {
            active = false;
        };
    }, []);

    function addCraft(event: React.SubmitEvent<HTMLFormElement>) {
        event.preventDefault();

        if (calculating) {
            return;
        }
        setPlanError(null);

        const characterId = Number(selectedCharacterId);
        const recipeId = Number(selectedRecipeId);
        const count = Number(newCrafts);
        const options = optionsByCharacter[characterId] ?? [];
        const recipeIsAvailable = options.some((option) => option.recipe_id === recipeId);

        if (!selectedCharacterId || !selectedRecipeId || !recipeIsAvailable) {
            setPlanError("Select a character and one of their known recipes.");
            return;
        }

        if (!Number.isSafeInteger(count) || count <= 0) {
            setPlanError("Craft count must be a positive whole number.");
            return;
        }

        setPlan((previous) => {
            const existing = previous.find((item) =>
                item.character_id === characterId && item.recipe_id === recipeId,
            );

            if (existing) {
                return previous.map((item) =>
                    item.character_id === characterId && item.recipe_id === recipeId
                        ? { ...item, crafts: item.crafts + count }
                        : item,
                );
            }

            return [...previous, { character_id: characterId, recipe_id: recipeId, crafts: count }];
        });
        setSelectedRecipeId("");
        setNewCrafts("1");
        setMaterials(null);
        setCalculationError(null);
    }

    function changeCraftCount(item: CharacterPlanItem, value: string) {
        const count = value === "" ? 0 : Number(value);

        setPlan((previous) =>
            previous.map((entry) =>
                entry.character_id === item.character_id && entry.recipe_id === item.recipe_id
                    ? { ...entry, crafts: count }
                    : entry,
            ),
        );
        setMaterials(null);
        setCalculationError(null);
    }

    function removeCraft(item: CharacterPlanItem) {
        setPlan((previous) =>
            previous.filter((entry) =>
                entry.character_id !== item.character_id || entry.recipe_id !== item.recipe_id,
            ),
        );
        setMaterials(null);
        setCalculationError(null);
    }

    function clearPlan() {
        setPlan([]);
        setSourceExpansionId(null);
        setMaterials(null);
        setPlanError(null);
        setCalculationError(null);
    }

    async function calculate() {
        setCalculationError(null);

        if (plan.length === 0) {
            setCalculationError("Add at least one craft before calculating materials.");
            return;
        }

        if (plan.some((item) => !Number.isSafeInteger(item.crafts) || item.crafts <= 0)) {
            setCalculationError("Every craft count must be a positive whole number.");
            return;
        }

        if (sourceExpansionId !== null && sourceExpansionId !== settings?.current_expansion_id) {
            setCalculationError("This plan came from another expansion. Clear it and create a new plan.");
            return;
        }

        setCalculating(true);

        try {
            const totals = await calculateMaterials(plan);
            setMaterials(totals);
        } catch (error) {
            setCalculationError(error instanceof Error ? error.message : "Unable to calculate materials.");
        } finally {
            setCalculating(false);
        }
    }

    const characterNames = new Map(characters.map((character) => [character.id, character.name]));
    const professionNames = new Map(professions.map((profession) => [profession.id, profession.name]));
    const selectedOptions = optionsByCharacter[Number(selectedCharacterId)] ?? [];
    const optionByRecipe = new Map<number, PlannerOption>();

    for (const options of Object.values(optionsByCharacter)) {
        for (const option of options) {
            optionByRecipe.set(option.recipe_id, option);
        }
    }

    const columns: TableColumn<CharacterPlanItem>[] = [
        {
            key: "character",
            label: "Character",
            value: (item) => characterNames.get(item.character_id) ?? `Character #${item.character_id}`,
        },
        {
            key: "recipe",
            label: "Recipe",
            value: (item) => optionByRecipe.get(item.recipe_id)?.recipe_name ?? `Recipe #${item.recipe_id}`,
        },
        {
            key: "profession",
            label: "Profession",
            value: (item) => {
                const professionId = optionByRecipe.get(item.recipe_id)?.profession_id;

                return professionNames.get(professionId ?? -1) ?? "Unknown profession";
            },
        },
        {
            key: "crafts",
            label: "Crafts",
            value: (item) => item.crafts,
            render: (item) => (
                <input
                    className="manual-craft-count"
                    type="number"
                    min="1"
                    step="1"
                    value={item.crafts}
                    disabled={calculating}
                    onChange={(event) => changeCraftCount(item, event.target.value)}
                    aria-label={`Craft count for ${optionByRecipe.get(item.recipe_id)?.recipe_name ?? "recipe"} on ${characterNames.get(item.character_id) ?? "character"}`}
                />
            ),
        },
    ];

    const materialRows: MaterialRow[] = materials
        ? Object.entries(materials)
            .map(([name, amount]) => ({ name, amount }))
            .sort((first, second) => first.name.localeCompare(second.name))
        : [];
    const materialColumns: TableColumn<MaterialRow>[] = [
        { key: "name", label: "Material", value: (row) => row.name },
        { key: "amount", label: "Amount needed", value: (row) => row.amount },
    ];

    return (
        <div className="manual-page">
            <h1>Manual Planner</h1>

            {loading && <p role="status">Loading planner options...</p>}
            {loadError && <p role="alert">{loadError}</p>}

            {!loading && !loadError && (
                <>
                    <p>
                        Enter the crafts you want to make, then calculate the materials to buy.
                        Each profession uses the character's full concentration amount.
                    </p>
                    <p className="manual-expansion">
                        Current expansion: <Link to="/expansions">{settings?.current_expansion.name}</Link>
                    </p>

                    {sourceExpansionId !== null && plan.length > 0 && (
                        <p className="manual-import-note">
                            Plan imported from Maximize Profit.
                            {sourceExpansionId !== settings?.current_expansion_id &&
                                " The current expansion has changed; clear this plan before calculating."}
                        </p>
                    )}

                    <form className="manual-add-form" onSubmit={addCraft}>
                        <h2>Add craft</h2>
                        <div className="manual-add-fields">
                            <label>
                                Character
                                <select
                                    value={selectedCharacterId}
                                    onChange={(event) => {
                                        setSelectedCharacterId(event.target.value);
                                        setSelectedRecipeId("");
                                    }}
                                    required
                                >
                                    <option value="">Select a character</option>
                                    {characters.map((character) => (
                                        <option key={character.id} value={character.id}>{character.name}</option>
                                    ))}
                                </select>
                            </label>
                            <label>
                                Known recipe
                                <select
                                    value={selectedRecipeId}
                                    onChange={(event) => setSelectedRecipeId(event.target.value)}
                                    disabled={!selectedCharacterId || selectedOptions.length === 0}
                                    required
                                >
                                    <option value="">Select a recipe</option>
                                    {selectedOptions.map((option) => (
                                        <option key={option.recipe_id} value={option.recipe_id}>
                                            {option.recipe_name} - {professionNames.get(option.profession_id) ?? "Profession"}
                                            {" ("}{option.concentration_cost} concentration each{")"}
                                        </option>
                                    ))}
                                </select>
                            </label>
                            <label>
                                Crafts
                                <input
                                    type="number"
                                    min="1"
                                    step="1"
                                    value={newCrafts}
                                    onChange={(event) => setNewCrafts(event.target.value)}
                                    required
                                />
                            </label>
                            <button type="submit" className="manual-add-button" disabled={calculating}>
                                <FontAwesomeIcon icon={faPlus} aria-hidden="true" />
                                Add craft
                            </button>
                        </div>
                        {selectedCharacterId && selectedOptions.length === 0 && (
                            <p>No known recipes for this character in the current expansion.</p>
                        )}
                        {planError && <p role="alert" className="manual-error">{planError}</p>}
                    </form>

                    <section className="manual-plan" aria-labelledby="manual-plan-title">
                        <div className="manual-section-heading">
                            <h2 id="manual-plan-title">Craft plan</h2>
                            <button type="button" className="manual-clear-button" disabled={plan.length === 0 || calculating} onClick={clearPlan}>
                                Clear plan
                            </button>
                        </div>
                        <DataTable
                            columns={columns}
                            rows={plan}
                            rowKey={(item) => `${item.character_id}:${item.recipe_id}`}
                            searchLabel="Search crafts"
                            emptyMessage={plan.length === 0 ? "No crafts added yet." : "No matching crafts."}
                            rowActions={(item) => (
                                <button
                                    type="button"
                                    className="manual-remove-button"
                                    disabled={calculating}
                                    onClick={() => removeCraft(item)}
                                    aria-label={`Remove ${optionByRecipe.get(item.recipe_id)?.recipe_name ?? "recipe"} for ${characterNames.get(item.character_id) ?? "character"}`}
                                >
                                    <FontAwesomeIcon icon={faTrashCan} aria-hidden="true" />
                                </button>
                            )}
                        />
                        <div className="manual-calculate">
                            <span>{plan.reduce((total, item) => total + item.crafts, 0)} crafts planned</span>
                            <button type="button" disabled={calculating || plan.length === 0} onClick={() => void calculate()}>
                                {calculating ? "Calculating..." : "Calculate materials"}
                            </button>
                        </div>
                        {calculationError && <p role="alert" className="manual-error">{calculationError}</p>}
                    </section>

                    {materials && (
                        <section className="manual-materials" aria-labelledby="manual-materials-title">
                            <h2 id="manual-materials-title">Materials to buy</h2>
                            <DataTable
                                columns={materialColumns}
                                rows={materialRows}
                                rowKey={(row) => row.name}
                                searchLabel="Search materials"
                                emptyMessage="No materials needed."
                            />
                        </section>
                    )}
                </>
            )}
        </div>
    );
}
