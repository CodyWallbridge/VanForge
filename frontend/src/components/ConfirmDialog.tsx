import { useEffect, useRef } from "react";
import type { ReactNode } from "react";
import "./ConfirmDialog.css";

interface ConfirmDialogProps {
    open: boolean;
    title: string;
    message: ReactNode;
    confirmLabel: string;
    busy: boolean;
    error: string | null;
    onConfirm: () => void;
    onClose: () => void;
}

export default function ConfirmDialog({
    open,
    title,
    message,
    confirmLabel,
    busy,
    error,
    onConfirm,
    onClose,
}: ConfirmDialogProps) {
    const dialogRef = useRef<HTMLDialogElement>(null);

    useEffect(() => {
        const dialog = dialogRef.current;

        if (!dialog) {
            return;
        }

        if (open && !dialog.open) {
            dialog.showModal();
        } else if (!open && dialog.open) {
            dialog.close();
        }
    }, [open]);

    return (
        <dialog
            ref={dialogRef}
            className="confirm-dialog"
            aria-labelledby="confirm-dialog-title"
            onClose={onClose}
            onCancel={(event) => {
                if (busy) {
                    event.preventDefault();
                }
            }}
        >
            <h2 id="confirm-dialog-title">{title}</h2>
            <p>{message}</p>
            {error && <p role="alert" className="confirm-dialog-error">{error}</p>}

            <div className="confirm-dialog-actions">
                <button type="button" className="confirm-dialog-cancel" disabled={busy} onClick={onClose}>
                    Cancel
                </button>
                <button type="button" className="confirm-dialog-confirm" disabled={busy} onClick={onConfirm}>
                    {busy ? "Deleting..." : confirmLabel}
                </button>
            </div>
        </dialog>
    );
}
