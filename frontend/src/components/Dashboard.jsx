import React, { useState, useEffect, useCallback } from "react"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from "recharts"
import api from "../api/client"
import StatsCards from "./StatsCards"
import TransactionMonitor from "./TransactionMonitor"
import FraudAlertFeed from "./FraudAlertFeed"
import { useWebSocket } from "../hooks/useWebSocket"
const RISK_COLORS = { critical:"#dc2626", high:"#d97706", medium:"#2563eb", low:"#22c55e" }
export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [txns, setTxns] = useState([])
  const [alerts, setAlerts] = useState([])
  const [timeline, setTimeline] = useState([])
  const [riskDist, setRiskDist] = useState(null)
  const [loading, setLoading] = useState(true)
  const [wsConnected, setWsConnected] = useState(false)
  const fetchData = useCallback(async () => {
    try {
      const [s,t,a,tl,r] = await Promise.all([
        api.get("/api/dashboard/stats"), api.get("/api/transactions?limit=20"),
        api.get("/api/fraud/alerts?limit=20"), api.get("/api/dashboard/timeline"),
        api.get("/api/dashboard/risk-distribution"),
      ])
      setStats(s.data); setTxns(t.data.transactions); setAlerts(a.data.alerts)
      setTimeline(tl.data.timeline); setRiskDist(r.data)
    } catch(e) { console.error(e) }
    finally { setLoading(false) }
  }, [])
  useEffect(() => { fetchData() }, [fetchData])
  const onWs = useCallback((msg) => {
    if (msg.type === "fraud_alert") { setAlerts(prev => [msg.data, ...prev].slice(0,50)); fetchData() }
    if (msg.type === "dashboard_refresh") { fetchData() }
  }, [fetchData])
  useWebSocket(onWs)
  const pieData = riskDist ? Object.entries(riskDist).map(([k,v])=>({name:k.charAt(0).toUpperCase()+k.slice(1),value:v,color:RISK_COLORS[k]||"#94a3b8"})) : []
  if (loading) return <div className="flex items-center justify-center h-64 text-gray-400">Loading dashboard...</div>
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-gray-900">Fraud Dashboard</h2>
          <p className="text-sm text-gray-500 mt-0.5">
            Real-time SIM swap fraud monitoring
            {wsConnected && <span className="inline-flex items-center gap-1 ml-2 text-success-600"><span className="pulse-dot bg-success-500"/>Live</span>}
          </p>
        </div>
        <button onClick={fetchData} className="text-sm text-brand-600 hover:text-brand-700 font-medium">Refresh</button>
      </div>
      <StatsCards stats={stats}/>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="card lg:col-span-2">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">Transaction Timeline</h3>
          {timeline.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={timeline}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9"/>
                <XAxis dataKey="date" tick={{fontSize:11}}/>
                <YAxis tick={{fontSize:11}}/>
                <Tooltip contentStyle={{borderRadius:"8px",border:"1px solid #e2e8f0",fontSize:"12px"}}/>
                <Bar dataKey="approved" stackId="a" fill="#22c55e" name="Approved"/>
                <Bar dataKey="flagged" stackId="a" fill="#d97706" name="Flagged"/>
                <Bar dataKey="blocked" stackId="a" fill="#dc2626" name="Blocked" radius={[4,4,0,0]}/>
              </BarChart>
            </ResponsiveContainer>
          ) : <div className="h-64 flex items-center justify-center text-gray-400 text-sm">No data yet</div>}
        </div>
        <div className="card">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">Risk Distribution</h3>
          {pieData.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie data={pieData} cx="50%" cy="50%" innerRadius={50} outerRadius={85} dataKey="value"
                  label={({name,percent})=>name+" "+(percent*100).toFixed(0)+"%"} labelLine={false}>
                  {pieData.map((e,i)=><Cell key={i} fill={e.color}/>)}
                </Pie>
                <Legend verticalAlign="bottom" height={36} formatter={v=><span className="text-xs text-gray-600">{v}</span>}/>
              </PieChart>
            </ResponsiveContainer>
          ) : <div className="h-64 flex items-center justify-center text-gray-400 text-sm">No alerts yet</div>}
        </div>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <TransactionMonitor transactions={txns}/>
        <FraudAlertFeed alerts={alerts}/>
      </div>
    </div>
  )
}
