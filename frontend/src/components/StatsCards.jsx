import React from "react"
import { ShieldCheck, ShieldAlert, ShieldX, Activity, Clock, DollarSign, Globe } from "lucide-react"
const colors = {
  blue: "bg-brand-100 text-brand-600", green: "bg-success-100 text-success-600",
  red: "bg-danger-100 text-danger-600", yellow: "bg-warning-100 text-warning-600",
  purple: "bg-purple-100 text-purple-600", gray: "bg-gray-100 text-gray-600",
}
function Card({ title, value, icon: Icon, color, sub }) {
  return (
    <div className="card flex items-center gap-4">
      <div className={"p-3 rounded-xl " + (colors[color]||colors.gray)}><Icon size={24}/></div>
      <div className="min-w-0">
        <p className="text-sm text-gray-500 font-medium truncate">{title}</p>
        <p className="text-2xl font-bold text-gray-900 truncate">{value}</p>
        {sub && <p className="text-xs text-gray-400 mt-0.5 truncate">{sub}</p>}
      </div>
    </div>
  )
}
export default function StatsCards({ stats }) {
  if (!stats) return null
  const currList = Object.entries(stats.by_currency || {}).map(([c,v]) => c + ":" + v.count).join(", ") || "none"
  const protectedList = Object.entries(stats.by_currency || {}).map(([c,v]) => c + " " + v.total).join(" | ") || "$0"
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-7 gap-4">
      <Card title="Total Checked" value={stats.total_transactions} icon={Activity} color="blue"/>
      <Card title="Approved" value={stats.approved} icon={ShieldCheck} color="green" sub={stats.approval_rate + "% rate"}/>
      <Card title="Blocked" value={stats.blocked} icon={ShieldX} color="red"/>
      <Card title="Flagged" value={stats.flagged} icon={ShieldAlert} color="yellow"/>
      <Card title="Avg Response" value={stats.avg_response_time_ms + "ms"} icon={Clock} color="purple"/>
      <Card title="Funds Protected" value={protectedList} icon={DollarSign} color="green" sub={stats.fraud_prevention_rate + "% prevention"}/>
      <Card title="Currencies" value={currList} icon={Globe} color="blue"/>
    </div>
  )
}
