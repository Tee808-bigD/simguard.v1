import React, { useState } from "react"
import Dashboard from "./components/Dashboard"
import AgentPortal from "./components/AgentPortal"
import { Shield, LayoutDashboard, UserCircle } from "lucide-react"
const tabs = [
  { id:"dashboard", label:"Dashboard", icon:LayoutDashboard },
  { id:"agent", label:"Agent Portal", icon:UserCircle },
]
export default function App() {
  const [tab, setTab] = useState("dashboard")
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-brand-600 rounded-xl"><Shield size={22} className="text-white"/></div>
              <div>
                <h1 className="text-lg font-bold text-gray-900 leading-tight">SimGuard</h1>
                <p className="text-xs text-gray-400 leading-tight">SIM Swap Fraud Prevention</p>
              </div>
            </div>
            <nav className="flex items-center gap-1">
              {tabs.map(t=>{
                const Icon=t.icon
                return (
                  <button key={t.id} onClick={()=>setTab(t.id)}
                    className={"flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors " + (tab===t.id?"bg-brand-50 text-brand-700":"text-gray-500 hover:text-gray-700 hover:bg-gray-50")}>
                    <Icon size={16}/><span className="hidden sm:inline">{t.label}</span>
                  </button>
                )
              })}
            </nav>
            <div className="hidden md:flex items-center gap-2">
              <span className="text-xs px-2.5 py-1 bg-gray-100 rounded-full text-gray-600">3 CAMARA APIs</span>
              <span className="text-xs px-2.5 py-1 bg-purple-50 rounded-full text-purple-600">Claude AI</span>
            </div>
          </div>
        </div>
      </header>
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {tab==="dashboard" && <Dashboard/>}
        {tab==="agent" && <AgentPortal/>}
      </main>
      <footer className="border-t border-gray-200 bg-white mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <p className="text-xs text-gray-400 text-center">SimGuard - Africa Ignite Hackathon 2026 | Nokia CAMARA + Anthropic Claude | SIM Swap + Device Swap + Number Verification</p>
        </div>
      </footer>
    </div>
  )
}
