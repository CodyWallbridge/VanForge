import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getCharacterRecipes } from "../api/characterRecipes";
import { getCharacters } from "../api/characters";
import { optimizePlan } from "../api/planner";
import { getProfessions } from "../api/professions";
import { getRecipes } from "../api/recipes";
import { getSettings } from "../api/settings";
import type { AppSettingsRead } from "../dto/AppSettingsRead";
import type { CharacterRead } from "../dto/CharacterRead";
import type { OptimizationRead } from "../dto/OptimizationRead";
import type { ProfessionRead } from "../dto/ProfessionRead";
import type { RecipeRead } from "../dto/RecipeRead";
import "./MaximizeProfit.css";

function formatGold(amount: number): string {
    return `${amount.toLocaleString()} gold`;
}

export default function MaximizeProfit() {
    const [characters, setCharacters] = useState<CharacterRead[]>([]);
    const [professions, setProfessions] = useState<ProfessionRead[]>([]);
    const [recipes, setRecipes] = useState<RecipeRead[]>([]);
    const [settings, setSettings] = useState<AppSettingsRead | null>(null);
    const [selectedIds, setSelectedIds] = useState<number[]>([]);
    const [eligibleIds, setEligibleIds] = useState<number[]>([]);
    const [loading, setLoading] = useState(true);
    const [loadError, setLoadError] = useState<string | null>(null);
    const [optimizing, setOptimizing] = useState(false);
    const [optimizationError, setOptimizationError] = useState<string | null>(null);
    const [result, setResult] = useState<OptimizationRead | null>(null);

    useEffect(() => {
        let active = true;

        async function loadOptions() {
            try {
                const [characterResults, professionResults, recipeResults, settingsResult] = await Promise.all([
                    getCharacters(),
                    getProfessions(),
                    getRecipes(),
                    getSettings(),
                ]);

                const assignmentLists = await Promise.all(
                    characterResults.map((character) => getCharacterRecipes(character.id)),
                );
                const availableIds: number[] = [];

                for (let index = 0; index < characterResults.length; index += 1) {
                    if (assignmentLists[index].length > 0) {
                        availableIds.push(characterResults[index].id);
                    }
                }

                if (active) {
                    setCharacters(characterResults);
                    setProfessions(professionResults);
                    setRecipes(recipeResults);
                    setSettings(settingsResult);
                    setEligibleIds(availableIds);
                    setSelectedIds(availableIds);
                }
            } catch (error) {
                if (active) {
                    setLoadError(error instanceof Error ? error.message : "Unable to load planning options.");
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

    function changeSelection(characterId: number, selected: boolean) {
        if (!eligibleIds.includes(characterId)) {
            return;
        }

        setSelectedIds((previous) =>
            selected
                ? [...previous, characterId]
                : previous.filter((id) => id !== characterId),
        );
        setResult(null);
        setOptimizationError(null);
    }

    function selectAll() {
        setSelectedIds(eligibleIds);
        setResult(null);
        setOptimizationError(null);
    }

    function clearSelection() {
        setSelectedIds([]);
        setResult(null);
        setOptimizationError(null);
    }

    async function runOptimization() {
        if (selectedIds.length === 0) {
            setOptimizationError("Select at least one character.");
            return;
        }

        setOptimizing(true);
        setOptimizationError(null);
        setResult(null);

        try {
            const optimized = await optimizePlan({ character_ids: selectedIds });
            setResult(optimized);
        } catch (error) {
            setOptimizationError(error instanceof Error ? error.message : "Unable to maximize profit.");
        } finally {
            setOptimizing(false);
        }
    }

    const eligibleCharacters = characters.filter((character) => eligibleIds.includes(character.id));
    const unavailableCharacters = characters.filter((character) => !eligibleIds.includes(character.id));
    const professionNames = new Map(professions.map((profession) => [profession.id, profession.name]));
    const recipeById = new Map(recipes.map((recipe) => [recipe.id, recipe]));

    return (
        <div className="maximize-page">
            <h1>Maximize Profit</h1>

            {loading && <p role="status">Loading planning options...</p>}
            {loadError && <p role="alert">{loadError}</p>}

            {!loading && !loadError && (
                <>
                    <p className="maximize-intro">
                        Select the characters to plan for. Each of their professions uses its own concentration budget.
                    </p>
                    <p className="maximize-expansion">
                        Current expansion: <Link to="/expansions">{settings?.current_expansion.name}</Link>
                    </p>

                    <section className="maximize-selection" aria-labelledby="maximize-selection-title">
                        <div className="maximize-selection-heading">
                            <h2 id="maximize-selection-title">Characters</h2>
                            <div className="maximize-selection-actions">
                                <button type="button" disabled={optimizing || eligibleCharacters.length === 0} onClick={selectAll}>
                                    Select all
                                </button>
                                <button type="button" disabled={optimizing || selectedIds.length === 0} onClick={clearSelection}>
                                    Clear selection
                                </button>
                            </div>
                        </div>

                        {characters.length === 0 && (
                            <p>No characters available. Add a character before maximizing profit.</p>
                        )}

                        {eligibleCharacters.length > 0 && (
                            <section className="maximize-character-section" aria-labelledby="maximize-ready-title">
                                <h3 id="maximize-ready-title">Ready to optimize ({eligibleCharacters.length})</h3>
                                <div className="maximize-character-grid">
                                    {eligibleCharacters.map((character) => (
                                        <label className="maximize-character" key={character.id}>
                                            <input
                                                type="checkbox"
                                                checked={selectedIds.includes(character.id)}
                                                disabled={optimizing}
                                                onChange={(event) => changeSelection(character.id, event.target.checked)}
                                            />
                                            <span>
                                                <strong>{character.name}</strong>
                                                <small>
                                                    {professionNames.get(character.profession1_id) ?? "Unknown profession"}
                                                    {" / "}
                                                    {professionNames.get(character.profession2_id) ?? "Unknown profession"}
                                                    {" - "}{character.concentration} concentration each
                                                </small>
                                            </span>
                                        </label>
                                    ))}
                                </div>
                            </section>
                        )}

                        {unavailableCharacters.length > 0 && (
                            <section className="maximize-character-section" aria-labelledby="maximize-unavailable-title">
                                <h3 id="maximize-unavailable-title">No known recipes ({unavailableCharacters.length})</h3>
                                <p>These characters have no known recipes for the current expansion and active professions.</p>
                                <div className="maximize-character-grid">
                                    {unavailableCharacters.map((character) => (
                                        <div className="maximize-character maximize-character-unavailable" key={character.id}>
                                            <input type="checkbox" disabled aria-label={`${character.name} has no known recipes`} />
                                            <span>
                                                <strong>{character.name}</strong>
                                                <small>
                                                    {professionNames.get(character.profession1_id) ?? "Unknown profession"}
                                                    {" / "}
                                                    {professionNames.get(character.profession2_id) ?? "Unknown profession"}
                                                </small>
                                                <Link to={`/characters/${character.id}`}>Add known recipes</Link>
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            </section>
                        )}

                        <div className="maximize-run">
                            <span>{selectedIds.length} of {eligibleCharacters.length} available selected</span>
                            <button
                                type="button"
                                disabled={optimizing || selectedIds.length === 0}
                                onClick={() => void runOptimization()}
                            >
                                {optimizing ? "Calculating..." : "Maximize profit"}
                            </button>
                        </div>
                        {optimizationError && <p role="alert" className="maximize-error">{optimizationError}</p>}
                    </section>

                    {result && (
                        <section className="maximize-results" aria-labelledby="maximize-results-title">
                            <div className="maximize-results-heading">
                                <h2 id="maximize-results-title">Recommended crafts</h2>
                                <div className="maximize-results-actions">
                                    <strong>Total profit: {formatGold(result.total_profit)}</strong>
                                    {result.crafts.length > 0 && (
                                        <Link
                                            className="maximize-manual-link"
                                            to="/manual"
                                            state={{ crafts: result.crafts, expansionId: result.expansion_id }}
                                        >
                                            Use in Manual Planner
                                        </Link>
                                    )}
                                </div>
                            </div>

                            {result.characters.map((characterResult) => (
                                <section className="maximize-character-result" key={characterResult.character_id}>
                                    <div className="maximize-character-result-heading">
                                        <h3>{characterResult.character_name}</h3>
                                        <strong>{formatGold(characterResult.profit)}</strong>
                                    </div>

                                    {characterResult.professions.map((professionResult) => {
                                        const crafts = result.crafts.filter((item) => {
                                            const recipe = recipeById.get(item.recipe_id);

                                            return item.character_id === characterResult.character_id &&
                                                recipe?.profession_id === professionResult.profession_id;
                                        });

                                        return (
                                            <div className="maximize-profession-result" key={professionResult.profession_id}>
                                                <div className="maximize-profession-heading">
                                                    <h4>{professionNames.get(professionResult.profession_id) ?? "Unknown profession"}</h4>
                                                    <span>
                                                        {professionResult.concentration_used} used,
                                                        {" "}{professionResult.concentration_remaining} remaining
                                                        {" · "}{formatGold(professionResult.profit)}
                                                    </span>
                                                </div>

                                                {crafts.length === 0 ? (
                                                    <p>No profitable crafts available.</p>
                                                ) : (
                                                    <div className="maximize-crafts-scroll">
                                                        <table className="maximize-crafts">
                                                            <thead>
                                                                <tr>
                                                                    <th scope="col">Recipe</th>
                                                                    <th scope="col">Crafts</th>
                                                                    <th scope="col">Profit per craft</th>
                                                                    <th scope="col">Total profit</th>
                                                                </tr>
                                                            </thead>
                                                            <tbody>
                                                                {crafts.map((item) => {
                                                                    const recipe = recipeById.get(item.recipe_id);

                                                                    return (
                                                                        <tr key={item.recipe_id}>
                                                                            <td>{recipe?.name ?? `Recipe #${item.recipe_id}`}</td>
                                                                            <td>{item.crafts}</td>
                                                                            <td>{formatGold(recipe?.profit_per_craft ?? 0)}</td>
                                                                            <td>{formatGold(item.crafts * (recipe?.profit_per_craft ?? 0))}</td>
                                                                        </tr>
                                                                    );
                                                                })}
                                                            </tbody>
                                                        </table>
                                                    </div>
                                                )}
                                            </div>
                                        );
                                    })}
                                </section>
                            ))}
                        </section>
                    )}
                </>
            )}
        </div>
    );
}
