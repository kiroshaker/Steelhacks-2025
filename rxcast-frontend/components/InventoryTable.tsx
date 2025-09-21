 "use client";

 import { useMemo, useState } from "react";
 import type { InventoryItem } from "@/src/types";
 import { postPurchaseOrder } from "@/lib/api";

 type Props = { items: InventoryItem[]; onSelect: (ndc: string) => void };

 export default function InventoryTable({ items, onSelect }: Props) {
    const [q, setQ] = useState("");
    const [onlyRisk, setOnlyRisk] = useState(false);

    const filtered = useMemo(() => {
        const ql = q.toLowerCase();
        return items.filter((it) => {
            const match =
                it.drug_name.toLowerCase().includes(ql) || it.ndc.includes(q);
            const risk = !onlyRisk || it.risk;
            return match && risk;
        });
    }, [items, q, onlyRisk]);

    async function approve(ndc: string, qty: number) {
        if (qty <= 0) return;
        const ok = confirm(`Create purchase order for ${qty} units of ${ndc}?`);
        if (!ok) return;
        try {
            await postPurchaseOrder(ndc, qty);
            alert("Purchase order submitted");
        } catch (e: any) {
            alert(e.message ?? "Failed to submit PO");
        }
    }

    return (
        <div className = "space-y-3">
            <div className = "flex gap-3">
                <input
                    className = "border rounded px-3 py-2 w-full"
                    placeholder = "Search by drug or NDC"
                    value = {q}
                    onChange = {(e) => setQ(e.target.value)}
                />
                <label className = "flex items-center gap-2 text-sm">
                    <input
                        type = "checkbox"
                        checked = {onlyRisk}
                        onChange = {(e) => setOnlyRisk(e.target.checked)}
                    />
                    At Risk only
                </label>
            </div>

            <div className = "overflow-auto border rounded">
                <table className = "min-w-full text-sm">
                    <thead className = "bg-gray-50">
                        <tr>
                            <th className = "text-left p-2">Drug</th>
                            <th className = "text-right p-2">On-hand</th>
                            <th className = "text-right p-2">Pred 14d (p50)</th>
                            <th className = "text-right p-2">Lead time (d)</th>
                            <th className = "text-center p-2">Risk</th>
                            <th className = "text-right p-2">Suggested PO</th>
                            <th className = "text-right p-2">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filtered.map((it) => (
                            <tr key = {it.ndc} className = "border-t hover:bg-gray-50">
                                <td className="p-2">
                                    <button
                                        className="text-blue-600 hover:underline"
                                        onClick = {() => onSelect(it.ndc)}
                                    >
                                        {it.drug_name}
                                    </button>
                                    <div className = "text-xs text-gray-500">{it.ndc}</div>
                                </td>
                                <td className = "p-2 text-right">
                                    {it.on_hand.toLocaleString()}
                                </td>
                                <td className = "p-2 text-right">
                                    {it.pred14_p50.toLocaleString()}
                                </td>
                                <td className = "p-2 text-right">{it.lead_time_days}</td>
                                <td className = "p-2 text-center">
                                    {it.risk ? (
                                        <span className = "px-2 py-1 text-xs rounded bg-red-100 text-red-700">
                                            At Risk
                                        </span>
                                    ) : (
                                        <span className = "px-2 py-1 text-xs rounded bg-green-100 text-green-700">
                                            OK
                                        </span>
                                    )}
                                </td>
                                <td className = "p-2 text-right">{it.suggested_po_qty}</td>
                                <td className = "p-2 text-right">
                                    <button
                                        className="px-3 py-1 rounded bg-black text-white disabled:opacity-40"
                                        onClick = {() => approve(it.ndc, it.suggested_po_qty)}
                                        disabled = {it.suggested_po_qty <= 0}
                                    >
                                        Approve PO
                                    </button>
                                </td>
                            </tr>
                        ))}
                        {filtered.length === 0 && (
                            <tr>
                                <td colSpan = {7} className = "p-4 text-center text-gray-500">
                                    No items
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
 }