import { useEffect, useState } from "react";
import { getCharacters } from "../api/characters";
import type { CharacterRead } from "../dto/CharacterRead";

export default function Characters() {
    const [characters, setCharacters] = useState<CharacterRead[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        let active = true;

        async function loadCharacters() {
            try {
                const results = await getCharacters();

                if (active) {
                    setCharacters(results);
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

    return (
        <>
            <h1>Characters</h1>

            {loading && <p role="status">Loading characters…</p>}

            {error && <p role="alert">{error}</p>}

            {!loading && !error && (
                characters.length === 0 ? (
                    <p>No characters added yet.</p>
                ) : (
                    <table>
                        <thead>
                            <tr>
                                <th scope="col">Name</th>
                                <th scope="col">Concentration</th>
                            </tr>
                        </thead>
                        <tbody>
                            {characters.map((character) => (
                                <tr key={character.id}>
                                    <td>{character.name}</td>
                                    <td>{character.concentration}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )
            )}
        </>
    );
}