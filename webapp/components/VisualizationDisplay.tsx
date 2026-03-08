"use client";

import {
    ResponsiveContainer,
    BarChart, Bar,
    LineChart, Line,
    PieChart, Pie,
    Cell,
    XAxis, YAxis,
    CartesianGrid,
    Tooltip,
    Legend
} from "recharts";
import { Table, LayoutGrid, PieChart as PieChartIcon, TrendingUp, BarChart3 } from "lucide-react";

export interface VizData {
    type: "bar" | "line" | "pie" | "table";
    title: string;
    data: any[];
    config?: {
        xKey?: string;
        yKey?: string;
        colors?: string[];
    };
}

const DEFAULT_COLORS = ["#00F5A0", "#00D9FF", "#7000FF", "#FF00D9", "#FFD900"];

export default function VisualizationDisplay({ viz }: { viz: VizData }) {
    const { type, title, data, config } = viz;

    const renderChart = () => {
        switch (type) {
            case "bar":
                return (
                    <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={data}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                            <XAxis dataKey={config?.xKey || "name"} stroke="#888" fontSize={10} />
                            <YAxis stroke="#888" fontSize={10} />
                            <Tooltip
                                contentStyle={{ backgroundColor: "#111", border: "1px solid #333", borderRadius: "8px" }}
                                itemStyle={{ color: "#fff" }}
                            />
                            <Legend verticalAlign="top" height={36} />
                            <Bar dataKey={config?.yKey || "value"} fill="#00F5A0" radius={[4, 4, 0, 0]} />
                        </BarChart>
                    </ResponsiveContainer>
                );
            case "line":
                return (
                    <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={data}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                            <XAxis dataKey={config?.xKey || "name"} stroke="#888" fontSize={10} />
                            <YAxis stroke="#888" fontSize={10} />
                            <Tooltip
                                contentStyle={{ backgroundColor: "#111", border: "1px solid #333", borderRadius: "8px" }}
                                itemStyle={{ color: "#fff" }}
                            />
                            <Legend verticalAlign="top" height={36} />
                            <Line type="monotone" dataKey={config?.yKey || "value"} stroke="#00D9FF" strokeWidth={2} dot={{ fill: "#00D9FF" }} />
                        </LineChart>
                    </ResponsiveContainer>
                );
            case "pie":
                return (
                    <ResponsiveContainer width="100%" height={300}>
                        <PieChart>
                            <Pie
                                data={data}
                                innerRadius={60}
                                outerRadius={80}
                                paddingAngle={5}
                                dataKey={config?.yKey || "value"}
                            >
                                {data.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={DEFAULT_COLORS[index % DEFAULT_COLORS.length]} />
                                ))}
                            </Pie>
                            <Tooltip
                                contentStyle={{ backgroundColor: "#111", border: "1px solid #333", borderRadius: "8px" }}
                                itemStyle={{ color: "#fff" }}
                            />
                            <Legend />
                        </PieChart>
                    </ResponsiveContainer>
                );
            case "table":
                if (!data || data.length === 0) return null;
                const headers = Object.keys(data[0]);
                return (
                    <div className="overflow-x-auto rounded-xl border border-white/5 bg-surface/50">
                        <table className="w-full text-left text-xs border-collapse">
                            <thead className="bg-white/5 uppercase tracking-wider text-[10px] font-bold text-muted">
                                <tr>
                                    {headers.map(h => (
                                        <th key={h} className="p-3 border-b border-white/5">{h}</th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-white/5">
                                {data.map((row, i) => (
                                    <tr key={i} className="hover:bg-white/5 transition-colors">
                                        {headers.map(h => (
                                            <td key={h} className="p-3 text-foreground/80">{row[h]}</td>
                                        ))}
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                );
            default:
                return null;
        }
    };

    const Icon = type === "bar" ? BarChart3 : type === "line" ? TrendingUp : type === "pie" ? PieChartIcon : Table;

    return (
        <div className="glass-card p-6 rounded-2xl border border-white/5 space-y-4 animate-in fade-in zoom-in-95 duration-500">
            <div className="flex items-center justify-between">
                <h3 className="font-bold text-sm flex items-center gap-2">
                    <Icon size={16} className="text-primary" />
                    {title}
                </h3>
                <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-md bg-primary/10 text-primary text-[10px] font-bold">
                    Dynamic Insight
                </div>
            </div>
            {renderChart()}
        </div>
    );
}
