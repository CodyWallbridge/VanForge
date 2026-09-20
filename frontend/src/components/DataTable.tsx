import { useId, useState } from "react";
import type { ReactNode } from "react";
import "./DataTable.css";

export interface TableColumn<T> {
    key: string;
    label: string;
    value: (row: T) => string | number;
    render?: (row: T) => ReactNode;
}

interface DataTableProps<T> {
    columns: TableColumn<T>[];
    rows: T[];
    rowKey: (row: T) => string | number;
    searchLabel: string;
    action?: ReactNode;
    rowActions?: (row: T) => ReactNode;
    emptyMessage?: string;
}

export default function DataTable<T>({
    columns,
    rows,
    rowKey,
    searchLabel,
    action,
    rowActions,
    emptyMessage = "No matching results.",
}: DataTableProps<T>) {
    const searchId = useId();
    const [search, setSearch] = useState("");
    const [sortKey, setSortKey] = useState<string | null>(null);
    const [sortDirection, setSortDirection] = useState<"asc" | "desc">("asc");

    const searchText = search.trim().toLocaleLowerCase();
    const visibleRows = rows.filter((row) =>
        columns.some((column) =>
            String(column.value(row)).toLocaleLowerCase().includes(searchText),
        ),
    );

    const sortColumn = columns.find((column) => column.key === sortKey);

    if (sortColumn) {
        visibleRows.sort((first, second) => {
            const firstValue = sortColumn.value(first);
            const secondValue = sortColumn.value(second);
            let comparison: number;

            if (typeof firstValue === "number" && typeof secondValue === "number") {
                comparison = firstValue - secondValue;
            } else {
                comparison = String(firstValue).localeCompare(
                    String(secondValue),
                    undefined,
                    { sensitivity: "base", numeric: true },
                );
            }

            return sortDirection === "asc" ? comparison : -comparison;
        });
    }

    function changeSort(columnKey: string) {
        if (sortKey === columnKey) {
            setSortDirection(sortDirection === "asc" ? "desc" : "asc");
            return;
        }

        setSortKey(columnKey);
        setSortDirection("asc");
    }

    return (
        <div className="data-table">
            <div className="data-table-toolbar">
                <div className="data-table-search">
                    <label htmlFor={searchId}>{searchLabel}</label>
                    <input
                        id={searchId}
                        type="search"
                        value={search}
                        onChange={(event) => setSearch(event.target.value)}
                        placeholder="Search all columns"
                    />
                </div>

                <div className="data-table-controls">
                    <button
                        type="button"
                        disabled={sortKey === null}
                        onClick={() => {
                            setSortKey(null);
                            setSortDirection("asc");
                        }}
                    >
                        Clear sort
                    </button>
                    {action}
                </div>
            </div>

            <div className="data-table-scroll">
                <table>
                    <thead>
                        <tr>
                            {columns.map((column) => (
                                <th
                                    key={column.key}
                                    scope="col"
                                    aria-sort={
                                        sortKey === column.key
                                            ? sortDirection === "asc"
                                                ? "ascending"
                                                : "descending"
                                            : "none"
                                    }
                                >
                                    <button
                                        type="button"
                                        onClick={() => changeSort(column.key)}
                                    >
                                        {column.label}
                                        <span
                                            className={
                                                sortKey === column.key
                                                    ? "data-table-sort-icon data-table-sort-icon-active"
                                                    : "data-table-sort-icon"
                                            }
                                            aria-hidden="true"
                                        >
                                            {sortKey === column.key
                                                ? sortDirection === "asc" ? "\u2191" : "\u2193"
                                                : "\u2195"}
                                        </span>
                                    </button>
                                </th>
                            ))}
                            {rowActions &&
                                <th scope="col" className="data-table-actions-heading">
                                    Actions
                                </th>}
                        </tr>
                    </thead>
                    <tbody>
                        {visibleRows.map((row) => (
                            <tr key={rowKey(row)}>
                                {columns.map((column) => (
                                    <td key={column.key}>
                                        {column.render ? column.render(row) : column.value(row)}
                                    </td>
                                ))}
                                {rowActions &&
                                    <td className="data-table-row-actions">
                                        {rowActions(row)}
                                    </td>}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {visibleRows.length === 0 && (
                <p className="data-table-empty">{emptyMessage}</p>
            )}
        </div>
    );
}
