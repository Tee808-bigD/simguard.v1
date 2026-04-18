import React from "react"
import { ArrowRightLeft, Clock, ShieldCheck, ShieldX, ShieldAlert } from "lucide-react"
const cfg = {
  approved: { icon:<ShieldCheck size={16} className="text-success-500"/>, badge:"badge-green", bg:"" },
  blocked: { icon:<ShieldX size={16} className="text-danger-500"/>, badge:"badge-red", bg:"bg-danger-50/30" },
  flagged: { icon:<ShieldAlert size={16} className="text-warning-500"/>, badge:"badge-yellow", bg:"bg-warning-50/30" },
  pending: { icon:<Clock size={16} className="text-gray-400"/>, badge:"badge-blue", bg:"" },
}
function ago(d) {
  const s = Math.floor((Date.now()-new Date(d))/1000)
  if(s<60) return s+"s ago"; if(s<3600) return Math.floor(s/60)+"m ago"; if(s<86400) return Math.floor(s/3600)+"h ago"; return Math.floor(s/86400)+"d ago"
}
function Row({ tx }) {
  const c = cfg[tx.status] || cfg.pending
  return (
    <div className={"flex items-center gap-3 px-4 py-3 rounded-lg " + c.bg + " hover:bg-gray-50 transition-colors"}>
      {c.icon}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="font-medium text-sm text-gray-900">{tx.phone_number}</span>
          <ArrowRightLeft size={14} className="text-gray-400"/>
          <span className="text-sm text-gray-500">{tx.recipient||"-"}</span>
        </div>
        <div className="flex items-center gap-3 mt-0.5">
          <span className="text-xs text-gray-400">{ago(tx.created_at)}</span>
          {tx.response_time_ms && <span className="text-xs text-gray-400">{tx.response_time_ms}ms</span>}
        </div>
      </div>
      <div className="text-right">
        <p className="font-semibold text-sm text-gray-900">{tx.currency} {Number(tx.amount).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2})}</p>
        <span className={c.badge}>{tx.status?.toUpperCase()}</span>
      </div>
    </div>
  )
}
export default function TransactionMonitor({ transactions }) {
  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center gap-2">
        <ArrowRightLeft size={20} className="text-brand-500"/>
        Transaction Monitor {transactions?.length > 0 && <span className="text-xs font-normal text-gray-400">({transactions.length})</span>}
      </h3>
      {!transactions?.length ? (
        <div className="text-center py-8 text-gray-400">
          <ArrowRightLeft size={40} className="mx-auto mb-2 opacity-30"/><p>No transactions yet</p>
          <p className="text-xs mt-1">Use the Agent Portal to check transactions</p>
        </div>
      ) : (
        <div className="space-y-1 max-h-96 overflow-y-auto">{transactions.map(tx=><Row key={tx.id} tx={tx}/>)}</div>
      )}
    </div>
  )
}
