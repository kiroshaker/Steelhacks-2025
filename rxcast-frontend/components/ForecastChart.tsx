"use client";

import type { ForecastPoint } from "@/src/types";
import {
    AreaChart,
    Area,
    Line,
    XAxis,
    YAxis,
    Tooltip,
    ResponsiveContainer,
    CartesianGrid,
} from "recharts";

export default function ForecastChart({ data }: { data: ForecastPoint[] }) {
    return (
        <div className = "h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
                <AreaChart data = {data}>
                    <CartesianGrid strokeDasharray = "3 3" />
                    <XAxis dataKey = "date" />
                    <YAxis allowDecimals = {false} />
                    <Tooltip />
                    <Area type = "monotone" dataKey = "p95" stroke = "#f59e0b" fill = "#fde68a" fillOpacity = {0.6} />
                    <Area type = "monotone" dataKey = "p05" stroke = "#f59e0b" fill = "#fff" fillOpacity = {1} /> 
                    <Line type = "monotone" dataKey = "p50" stroke = "#111827" dot = {false} />
                </AreaChart>
            </ResponsiveContainer>
        </div>
    );
}
