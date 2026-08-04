"use client";

import {
  AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
} from "recharts";
import type { ChartPoint } from "@/lib/types";

const AXIS_STYLE = { fontSize: 11, fill: "#8996A9", fontFamily: "var(--font-mono)" };
const TOOLTIP_STYLE = {
  background: "#141B27",
  border: "1px solid rgba(148,163,184,0.2)",
  borderRadius: 8,
  fontSize: 12,
  color: "#E7ECF4",
};

export function ArticlesPerDayChart({ data }: { data: ChartPoint[] }) {
  return (
    <ResponsiveContainer width="100%" height={220}>
      <AreaChart data={data}>
        <defs>
          <linearGradient id="signalFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#2FD6C0" stopOpacity={0.35} />
            <stop offset="100%" stopColor="#2FD6C0" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid stroke="rgba(148,163,184,0.08)" vertical={false} />
        <XAxis dataKey="label" tick={AXIS_STYLE} axisLine={false} tickLine={false} />
        <YAxis tick={AXIS_STYLE} axisLine={false} tickLine={false} width={28} />
        <Tooltip contentStyle={TOOLTIP_STYLE} />
        <Area type="monotone" dataKey="value" stroke="#2FD6C0" strokeWidth={2} fill="url(#signalFill)" />
      </AreaChart>
    </ResponsiveContainer>
  );
}

const THREAT_COLORS: Record<string, string> = {
  low: "#2FD6C0",
  medium: "#4C8DFF",
  high: "#F0A83C",
  critical: "#EF5B4E",
};

export function ThreatDistributionChart({ data }: { data: ChartPoint[] }) {
  return (
    <ResponsiveContainer width="100%" height={220}>
      <PieChart>
        <Pie data={data} dataKey="value" nameKey="label" innerRadius={55} outerRadius={85} paddingAngle={3}>
          {data.map((entry) => (
            <Cell key={entry.label} fill={THREAT_COLORS[entry.label] || "#586376"} stroke="none" />
          ))}
        </Pie>
        <Tooltip contentStyle={TOOLTIP_STYLE} />
      </PieChart>
    </ResponsiveContainer>
  );
}

export function TopEntitiesChart({ data, color = "#4C8DFF" }: { data: ChartPoint[]; color?: string }) {
  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart data={data} layout="vertical" margin={{ left: 8 }}>
        <CartesianGrid stroke="rgba(148,163,184,0.08)" horizontal={false} />
        <XAxis type="number" tick={AXIS_STYLE} axisLine={false} tickLine={false} />
        <YAxis dataKey="label" type="category" tick={AXIS_STYLE} axisLine={false} tickLine={false} width={110} />
        <Tooltip contentStyle={TOOLTIP_STYLE} cursor={{ fill: "rgba(148,163,184,0.06)" }} />
        <Bar dataKey="value" fill={color} radius={[0, 4, 4, 0]} barSize={14} />
      </BarChart>
    </ResponsiveContainer>
  );
}
