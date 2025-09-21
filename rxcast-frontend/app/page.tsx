"use client";

import { useEffect, useState } from "react";
import InventoryTable from "@/components/InventoryTable";
import ForecastChart from "@/components/ForecastChart";
import { getForecast, getInventory } from "@/lib/api";
import type { InventoryItem, ForecastPoint } from "@/src/types";

export default function Page() {
    const [items, setItems] = useState<InventoryItem[]>([]);
    const [selectedNdc, setSelectedNdc] = useState<string | null>(null);
    const [forecast, setForecast] = useState<ForecastPoint[] | null>(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        getInventory().then(setItems).catch((e) => alert(e.message));
    }, []);

    useEffect(() => {
        if(!selectedNdc) {
            setForecast(null);
            return;
        }
        setLoading(true);
        getForecast(selectedNdc)
            .then((d) => {
                const norm = d.map((x) => ({ ...x, date: x.date.slice(0, 10) }));
                setForecast(norm);
            })
            .catch((e) => alert(e.message))
            .finally(() => setLoading(false));
    }, [selectedNdc]);

    return (
        <main className="p-6 max-w-7xl mx-auto space-y-6">
            <header className = "flex items-baseline justify-between">
                <h1 className = "text-2xl font-semibold">RxCast UPMC Presbyterian</h1>
                <div className = "text-sm text-gray-500">
                    Pittsburgh, PA {new Date().toLocaleDateString()}
                </div>
            </header>

            <InventoryTable items = {items} onSelect={setSelectedNdc} />

            <section className = "border rounded p-4">
                <h2 className = "font-semibold mb-2">Drug forecast</h2>
                {!selectedNdc && (
                    <div className = "text-gray-500 text-sm">
                        Select a drug name to view its 14-day forecast.
                    </div>
                )}
                {loading && <div className="text-sm">Loading forecast...</div>}
                {forecast && (
                    <div className = "space-y-2">
                        <div className = "text-sm text-gray-600">NDC: {selectedNdc}</div>
                        <ForecastChart data = {forecast} />
                    </div>
                )}
            </section>
        </main>
    );
}


