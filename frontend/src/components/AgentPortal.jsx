import React from "react"
import TransactionForm from "./TransactionForm"
export default function AgentPortal({ onResult }) {
  return (
    <div>
      <div className="mb-6">
        <h2 className="text-xl font-bold text-gray-900">Agent Portal</h2>
        <p className="text-sm text-gray-500 mt-1">Check transactions before processing. SimGuard runs real-time SIM swap detection, device verification, and AI-powered fraud analysis.</p>
      </div>
      <TransactionForm onResult={onResult}/>
    </div>
  )
}
