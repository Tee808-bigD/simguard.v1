import React, { useState } from "react"
import { Loader2, ShieldCheck, ShieldX, ShieldAlert, Phone, DollarSign, User, Send, Globe } from "lucide-react"
import api from "../api/client"
const CURRENCIES = [
  {code:"USD",name:"US Dollar",symbol:"$"},{code:"ZAR",name:"South African Rand",symbol:"R"},
  {code:"KES",name:"Kenyan Shilling",symbol:"KSh"},{code:"NGN",name:"Nigerian Naira",symbol:"N"},
  {code:"GHS",name:"Ghanaian Cedi",symbol:"GHs"},{code:"UGX",name:"Ugandan Shilling",symbol:"USh"},
  {code:"TZS",name:"Tanzanian Shilling",symbol:"TSh"},{code:"RWF",name:"Rwandan Franc",symbol:"FRw"},
  {code:"XOF",name:"West African CFA",symbol:"CFA"},{code:"XAF",name:"Central African CFA",symbol:"CFA"},
  {code:"MWK",name:"Malawian Kwacha",symbol:"MK"},{code:"ZMW",name:"Zambian Kwacha",symbol:"ZK"},
  {code:"MZN",name:"Mozambican Metical",symbol:"MT"},{code:"ETB",name:"Ethiopian Birr",symbol:"Br"},
]
const PRESETS = [
  { label:"Safe (APPROVED)", phone:"+99999991001", amount:50, currency:"USD", newRecipient:false, desc:"No SIM swap, low amount" },
  { label:"Fraud (BLOCKED)", phone:"+99999991000", amount:1000, currency:"USD", newRecipient:true, desc:"SIM swap + high value + new recipient" },
  { label:"Suspicious (FLAGGED)", phone:"+99999991000", amount:300, currency:"USD", newRecipient:false, desc:"SIM swap, medium amount" },
  { label:"ZAR Fraud", phone:"+99999991000", amount:15000, currency:"ZAR", newRecipient:true, desc:"R15,000 SIM swap fraud" },
  { label:"KES Safe", phone:"+99999991001", amount:5000, currency:"KES", newRecipient:false, desc:"KSh 5,000 normal transfer" },
]
const statusCfg = {
  approved: { color:"border-success-500 bg-success-50", icon:<ShieldCheck size={48} className="text-success-500"/>, label:"APPROVED", badge:"badge-green" },
  blocked: { color:"border-danger-500 bg-danger-50", icon:<ShieldX size={48} className="text-danger-500 risk-pulse"/>, label:"BLOCKED", badge:"badge-red" },
  flagged: { color:"border-warning-500 bg-warning-50", icon:<ShieldAlert size={48} className="text-warning-600"/>, label:"FLAGGED", badge:"badge-yellow" },
}
function getSymbol(code) { return CURRENCIES.find(c=>c.code===code)?.symbol || code + " " }
export default function TransactionForm({ onResult }) {
  const [form, setForm] = useState({ phone_number:"", amount:"", currency:"USD", transaction_type:"transfer", recipient:"", recipient_name:"", is_new_recipient:false })
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState("")
  const set = (k,v) => setForm(p=>({...p,[k]:v}))
  const sym = getSymbol(form.currency)
  const apply = (p) => { setForm(f=>({...f, phone_number:p.phone, amount:p.amount, currency:p.currency, is_new_recipient:p.newRecipient})); setResult(null); setError("") }
  const submit = async (e) => {
    e.preventDefault(); setLoading(true); setResult(null); setError("")
    try {
      const res = await api.post("/api/transactions", {
        phone_number: form.phone_number, amount: parseFloat(form.amount), currency: form.currency,
        transaction_type: form.transaction_type, recipient: form.recipient || undefined,
        recipient_name: form.recipient_name || undefined, is_new_recipient: form.is_new_recipient,
      })
      setResult(res.data); onResult?.(res.data)
    } catch(err) { setError(err.response?.data?.detail || "Transaction check failed") }
    finally { setLoading(false) }
  }
  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">Check Transaction</h3>
      <div className="flex flex-wrap gap-2 mb-4">
        {PRESETS.map((p,i)=>(
          <button key={i} onClick={()=>apply(p)} className="text-xs px-3 py-1.5 rounded-lg border border-gray-200 hover:border-brand-300 hover:bg-brand-50 transition-colors text-left" title={p.desc}>
            {p.label} <span className="text-gray-400 ml-1">({p.desc})</span>
          </button>
        ))}
      </div>
      <form onSubmit={submit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1"><Phone size={14} className="inline mr-1"/>Customer Phone *</label>
          <input type="tel" value={form.phone_number} onChange={e=>set("phone_number",e.target.value)} placeholder="+99999991001" required className="input-field"/>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1"><DollarSign size={14} className="inline mr-1"/>Amount *</label>
            <div className="relative">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 text-sm font-medium">{sym}</span>
              <input type="number" value={form.amount} onChange={e=>set("amount",e.target.value)} placeholder="100" min="0.01" step="0.01" required className="input-field pl-12"/>
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1"><Globe size={14} className="inline mr-1"/>Currency</label>
            <select value={form.currency} onChange={e=>set("currency",e.target.value)} className="input-field">
              {CURRENCIES.map(c=><option key={c.code} value={c.code}>{c.code} - {c.name}</option>)}
            </select>
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
          <select value={form.transaction_type} onChange={e=>set("transaction_type",e.target.value)} className="input-field">
            <option value="transfer">Transfer</option><option value="withdrawal">Withdrawal</option>
            <option value="payment">Payment</option><option value="bill_payment">Bill Payment</option>
          </select>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1"><User size={14} className="inline mr-1"/>Recipient Number</label>
            <input type="tel" value={form.recipient} onChange={e=>set("recipient",e.target.value)} placeholder="+99999992000" className="input-field"/>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Recipient Name</label>
            <input type="text" value={form.recipient_name} onChange={e=>set("recipient_name",e.target.value)} placeholder="John Doe" className="input-field"/>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <input type="checkbox" id="nr" checked={form.is_new_recipient} onChange={e=>set("is_new_recipient",e.target.checked)} className="w-4 h-4 rounded border-gray-300 text-brand-600 focus:ring-brand-500"/>
          <label htmlFor="nr" className="text-sm text-gray-700">New recipient (first-time transfer)</label>
        </div>
        <button type="submit" disabled={loading||!form.phone_number||!form.amount} className="btn-primary w-full flex items-center justify-center gap-2">
          {loading ? <><Loader2 size={18} className="animate-spin"/>Analyzing with CAMARA + AI...</> : <><Send size={18}/>Check for Fraud</>}
        </button>
      </form>
      {error && <div className="mt-4 border border-danger-200 bg-danger-50 rounded-xl p-4 text-danger-700 text-sm">{error}</div>}
      {result && !result.error && (
        <div className={"mt-6 border-2 rounded-xl p-5 " + (statusCfg[result.status]?.color||"border-gray-200")}>
          <div className="flex items-center gap-4">
            {statusCfg[result.status]?.icon}
            <div>
              <span className={statusCfg[result.status]?.badge}>{statusCfg[result.status]?.label}</span>
              <div className="flex items-center gap-3 mt-1 flex-wrap">
                <span className="text-sm text-gray-600">Risk: <strong>{result.risk_score}</strong>/100+</span>
                <span className="text-sm text-gray-600">Amount: <strong>{result.currency} {Number(result.amount).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2})}</strong></span>
                <span className="text-sm text-gray-600">Time: <strong>{result.response_time_ms}ms</strong></span>
                {result.ai_confidence != null && <span className="text-sm text-gray-600">AI: <strong>{(result.ai_confidence*100).toFixed(0)}%</strong></span>}
              </div>
            </div>
          </div>
          {result.ai_explanation && <p className="text-sm text-gray-700 mt-3 bg-white/60 rounded-lg p-3">AI: {result.ai_explanation}</p>}
        </div>
      )}
    </div>
  )
}
