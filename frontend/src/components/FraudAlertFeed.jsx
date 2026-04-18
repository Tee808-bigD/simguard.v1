import React, { useState } from "react"
import { AlertTriangle, ShieldX, Eye, ChevronDown, ChevronUp } from "lucide-react"
const styles = {
  critical: { border:"border-l-danger-500", bg:"bg-danger-50", badge:"badge-red", icon:<ShieldX size={18} className="text-danger-600"/> },
  high: { border:"border-l-warning-500", bg:"bg-warning-50", badge:"badge-yellow", icon:<AlertTriangle size={18} className="text-warning-600"/> },
  medium: { border:"border-l-blue-400", bg:"bg-blue-50", badge:"badge-blue", icon:<Eye size={18} className="text-blue-500"/> },
  low: { border:"border-l-gray-300", bg:"", badge:"badge-blue", icon:<Eye size={18} className="text-gray-400"/> },
}
const actionStyles = { blocked:"badge-red", flagged:"badge-yellow", approved:"badge-green" }
function Item({ alert, isNew }) {
  const [open, setOpen] = useState(false)
  const s = styles[alert.risk_level] || styles.low
  return (
    <div className={"border-l-4 " + s.border + " " + s.bg + " rounded-r-lg p-4 transition-all " + (isNew?"animate-pulse":"")}>
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3 flex-1">
          {s.icon}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <span className={"font-semibold text-sm " + s.badge}>{alert.risk_level?.toUpperCase()}</span>
              <span className={actionStyles[alert.action_taken]||"badge-blue"}>{alert.action_taken?.toUpperCase()}</span>
              <span className="text-xs text-gray-400">{alert.phone_number}</span>
              {alert.amount != null && <span className="text-xs font-medium text-gray-600">{alert.currency||"USD"} {Number(alert.amount).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2})}</span>}
            </div>
            <p className="text-sm text-gray-700 mt-1">{alert.explanation||"Fraud alert"}</p>
            {open && alert.recommended_actions?.length > 0 && (
              <div className="mt-2 space-y-1">
                <p className="text-xs font-medium text-gray-500 uppercase">Recommended:</p>
                {alert.recommended_actions.map((a,i)=><p key={i} className="text-xs text-gray-600 flex items-center gap-1"><span className="w-1 h-1 bg-gray-400 rounded-full"/>{a}</p>)}
              </div>
            )}
          </div>
        </div>
        <button onClick={()=>setOpen(!open)} className="text-gray-400 hover:text-gray-600 p-1">{open?<ChevronUp size={16}/>:<ChevronDown size={16}/>}</button>
      </div>
    </div>
  )
}
export default function FraudAlertFeed({ alerts }) {
  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center gap-2">
        <AlertTriangle size={20} className="text-warning-500"/>
        Fraud Alerts {alerts?.length > 0 && <span className="text-xs font-normal text-gray-400">({alerts.length})</span>}
      </h3>
      {!alerts?.length ? (
        <div className="text-center py-8 text-gray-400">
          <ShieldX size={40} className="mx-auto mb-2 opacity-30"/>
          <p>No fraud alerts yet</p>
          <p className="text-xs mt-1">Submit a transaction from Agent Portal</p>
        </div>
      ) : (
        <div className="space-y-3 max-h-96 overflow-y-auto pr-1">{alerts.map(a=><Item key={a.id} alert={a}/>)}</div>
      )}
    </div>
  )
}
