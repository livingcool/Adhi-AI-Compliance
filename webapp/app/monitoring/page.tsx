'use client'

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Activity,
  Zap,
  Cpu,
  Database,
  Network,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
  Users,
  Globe,
  Monitor,
  Server,
  Eye,
  Bell,
  Pause,
  Play,
  RotateCcw,
  TrendingUp,
  Waves,
  Signal,
  HardDrive
} from 'lucide-react'
import DashboardNavigation from '@/components/DashboardNavigation'
import { GlassCard } from '@/components/ui/GlassCard'

interface SystemHealthCardProps { title: string; status: string; value: string | number; unit: string; icon: React.ElementType; details?: { label: string; value: string }[]; }
const SystemHealthCard = ({ title, status, value, unit, icon: Icon, details = [] }: SystemHealthCardProps) => {
  const getStatusColor = () => {
    switch (status) {
      case 'healthy': return { bg: 'bg-green-500/20 border-green-500/30', text: 'text-green-400', dot: 'bg-green-500' }
      case 'warning': return { bg: 'bg-amber-500/20 border-amber-500/30', text: 'text-amber-400', dot: 'bg-amber-500' }
      case 'critical': return { bg: 'bg-red-500/20 border-red-500/30', text: 'text-red-400', dot: 'bg-red-500' }
      default: return { bg: 'bg-gray-500/20 border-gray-500/30', text: 'text-gray-400', dot: 'bg-gray-500' }
    }
  }

  const colors = getStatusColor()

  return (
    <GlassCard className={`${colors.bg} border ${colors.bg.split(' ')[1]} p-6 group`}>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${colors.bg}`}>
            <Icon className={`w-5 h-5 ${colors.text}`} />
          </div>
          <h3 className="text-white font-medium">{title}</h3>
        </div>
        <div className={`w-3 h-3 rounded-full ${colors.dot} animate-pulse`}></div>
      </div>

      <div className="flex items-end gap-2 mb-4">
        <span className={`text-3xl font-bold ${colors.text}`}>{value}</span>
        <span className="text-white/60 text-sm mb-1">{unit}</span>
      </div>

      <div className="space-y-1">
        {details.map((detail, index) => (
          <div key={index} className="flex justify-between text-sm">
            <span className="text-white/60">{detail.label}</span>
            <span className="text-white/80">{detail.value}</span>
          </div>
        ))}
      </div>
    </GlassCard>
  )
}

const LiveMetricsStream = () => {
  const [metrics, setMetrics] = useState([
    { id: 1, timestamp: new Date().toLocaleTimeString(), event: 'AI System Health Check', status: 'success', system: 'Voter Verification' },
    { id: 2, timestamp: new Date(Date.now() - 30000).toLocaleTimeString(), event: 'Compliance Score Updated', status: 'info', system: 'Resume Screening' },
    { id: 3, timestamp: new Date(Date.now() - 60000).toLocaleTimeString(), event: 'Bias Audit Completed', status: 'success', system: 'Fraud Detection' },
    { id: 4, timestamp: new Date(Date.now() - 90000).toLocaleTimeString(), event: 'High Response Time Detected', status: 'warning', system: 'Content Moderation' },
    { id: 5, timestamp: new Date(Date.now() - 120000).toLocaleTimeString(), event: 'Database Backup Completed', status: 'success', system: 'System' },
  ])

  const [isLive, setIsLive] = useState(true)

  useEffect(() => {
    if (!isLive) return

    const interval = setInterval(() => {
      const events = [
        'System Health Check Passed',
        'API Response Time Measured',
        'Database Query Optimized',
        'Security Scan Completed',
        'Compliance Monitor Updated',
        'Bias Test Executed',
        'Model Performance Checked',
        'User Activity Logged',
        'Audit Trail Updated',
        'Risk Assessment Calculated'
      ]

      const systems = ['Voter Verification', 'Resume Screening', 'Fraud Detection', 'Content Moderation', 'Predictive Analytics']
      const statuses = ['success', 'info', 'warning']

      const newEvent = {
        id: Date.now() + Math.random(),
        timestamp: new Date().toLocaleTimeString(),
        event: events[Math.floor(Math.random() * events.length)],
        status: statuses[Math.floor(Math.random() * statuses.length)],
        system: systems[Math.floor(Math.random() * systems.length)]
      }

      setMetrics(prev => [newEvent, ...prev.slice(0, 9)])
    }, 3000)

    return () => clearInterval(interval)
  }, [isLive, metrics.length])

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success': return <CheckCircle className="w-4 h-4 text-green-400" />
      case 'warning': return <AlertTriangle className="w-4 h-4 text-amber-400" />
      case 'error': return <XCircle className="w-4 h-4 text-red-400" />
      default: return <Activity className="w-4 h-4 text-blue-400" />
    }
  }

  return (
    <GlassCard className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Waves className="w-5 h-5 text-blue-400" />
          <h3 className="text-xl font-bold text-white">Live Activity Stream</h3>
          {isLive && <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>}
        </div>

        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setIsLive(!isLive)}
          className={`p-2 rounded-lg border transition-colors ${isLive
            ? 'bg-green-500/20 border-green-500/30 text-green-400'
            : 'bg-gray-500/20 border-gray-500/30 text-gray-400'
            }`}
        >
          {isLive ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
        </motion.button>
      </div>

      <div className="space-y-3 max-h-96 overflow-y-auto">
        <AnimatePresence>
          {metrics.map((metric) => (
            <motion.div
              key={metric.id}
              initial={{ opacity: 0, y: -10, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 10, scale: 0.95 }}
              className="flex items-center gap-3 p-3 rounded-xl hover:bg-white/5 transition-colors"
            >
              {getStatusIcon(metric.status)}
              <div className="flex-1 min-w-0">
                <p className="text-white text-sm font-medium">{metric.event}</p>
                <div className="flex items-center gap-3 text-xs text-white/60 mt-1">
                  <span>{metric.timestamp}</span>
                  <span>•</span>
                  <span>{metric.system}</span>
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </GlassCard>
  )
}

const NetworkTopology = () => {
  const nodes = [
    { id: 'api', label: 'API Gateway', status: 'healthy', x: 50, y: 20 },
    { id: 'auth', label: 'Auth Service', status: 'healthy', x: 20, y: 50 },
    { id: 'db', label: 'Database', status: 'healthy', x: 80, y: 50 },
    { id: 'ai1', label: 'AI Engine 1', status: 'warning', x: 30, y: 80 },
    { id: 'ai2', label: 'AI Engine 2', status: 'healthy', x: 70, y: 80 },
  ]

  const connections = [
    { from: 'api', to: 'auth' },
    { from: 'api', to: 'db' },
    { from: 'api', to: 'ai1' },
    { from: 'api', to: 'ai2' },
    { from: 'ai1', to: 'db' },
    { from: 'ai2', to: 'db' },
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'border-green-500 bg-green-500/20'
      case 'warning': return 'border-amber-500 bg-amber-500/20'
      case 'critical': return 'border-red-500 bg-red-500/20'
      default: return 'border-gray-500 bg-gray-500/20'
    }
  }

  return (
    <GlassCard className="p-6">
      <div className="flex items-center gap-3 mb-6">
        <Network className="w-5 h-5 text-blue-400" />
        <h3 className="text-xl font-bold text-white">System Topology</h3>
      </div>

      <div className="relative h-64 bg-black/20 rounded-xl overflow-hidden">
        {/* Connection lines */}
        <svg className="absolute inset-0 w-full h-full">
          {connections.map((conn, index) => {
            const fromNode = nodes.find(n => n.id === conn.from)
            const toNode = nodes.find(n => n.id === conn.to)
            return (
              <motion.line
                key={index}
                initial={{ pathLength: 0 }}
                animate={{ pathLength: 1 }}
                transition={{ duration: 1, delay: index * 0.1 }}
                x1={`${fromNode?.x || 0}%`}
                y1={`${fromNode?.y || 0}%`}
                x2={`${toNode?.x || 0}%`}
                y2={`${toNode?.y || 0}%`}
                stroke="rgba(59, 130, 246, 0.3)"
                strokeWidth="2"
                className="animate-pulse"
              />
            )
          })}
        </svg>

        {/* Nodes */}
        {nodes.map((node) => (
          <motion.div
            key={node.id}
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.5 }}
            className={`absolute transform -translate-x-1/2 -translate-y-1/2 
                       border-2 ${getStatusColor(node.status)} rounded-xl p-3 backdrop-blur-lg`}
            style={{ left: `${node.x}%`, top: `${node.y}%` }}
          >
            <div className="text-white text-xs font-medium text-center">{node.label}</div>
          </motion.div>
        ))}
      </div>
    </GlassCard>
  )
}

const RealTimeCharts = () => {
  const [chartData, setChartData] = useState([
    { time: '00:00', value: 85 },
    { time: '00:01', value: 88 },
    { time: '00:02', value: 92 },
    { time: '00:03', value: 87 },
    { time: '00:04', value: 91 },
    { time: '00:05', value: 89 },
  ])

  useEffect(() => {
    const interval = setInterval(() => {
      setChartData(prev => {
        const newData = [...prev.slice(1), {
          time: new Date().toLocaleTimeString('en-US', {
            hour12: false,
            minute: '2-digit',
            second: '2-digit'
          }).slice(3),
          value: 85 + Math.random() * 15
        }]
        return newData
      })
    }, 2000)

    return () => clearInterval(interval)
  }, [])

  return (
    <GlassCard className="p-6">
      <div className="flex items-center gap-3 mb-6">
        <TrendingUp className="w-5 h-5 text-green-400" />
        <h3 className="text-xl font-bold text-white">Performance Metrics</h3>
        <div className="ml-auto flex items-center gap-2 text-sm text-green-400">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          Real-time
        </div>
      </div>

      <div className="relative h-48">
        <svg className="w-full h-full">
          {/* Grid lines */}
          {[0, 25, 50, 75, 100].map((y, i) => (
            <line
              key={i}
              x1="0"
              y1={`${y}%`}
              x2="100%"
              y2={`${y}%`}
              stroke="rgba(255,255,255,0.1)"
              strokeWidth="1"
            />
          ))}

          {/* Chart line */}
          <motion.polyline
            fill="none"
            stroke="url(#gradient)"
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
            points={chartData.map((point, i) =>
              `${(i / (chartData.length - 1)) * 100},${100 - point.value}`
            ).join(' ')}
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 1 }}
          />

          {/* Gradient definition */}
          <defs>
            <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="rgb(34, 197, 94)" />
              <stop offset="100%" stopColor="rgb(59, 130, 246)" />
            </linearGradient>
          </defs>

          {/* Data points */}
          {chartData.map((point, i) => (
            <motion.circle
              key={i}
              cx={`${(i / (chartData.length - 1)) * 100}%`}
              cy={`${100 - point.value}%`}
              r="4"
              fill="rgb(59, 130, 246)"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: i * 0.1 }}
              className="drop-shadow-lg"
            />
          ))}
        </svg>

        {/* Y-axis labels */}
        <div className="absolute left-0 top-0 h-full flex flex-col justify-between text-xs text-white/60 -ml-8">
          <span>100%</span>
          <span>75%</span>
          <span>50%</span>
          <span>25%</span>
          <span>0%</span>
        </div>
      </div>

      {/* Current value display */}
      <div className="mt-4 text-center">
        <span className="text-2xl font-bold text-green-400">
          {Math.round(chartData[chartData.length - 1]?.value || 0)}%
        </span>
        <p className="text-white/60 text-sm">Current Performance Score</p>
      </div>
    </GlassCard>
  )
}

export default function RealTimeMonitoring() {
  const [refreshRate, setRefreshRate] = useState(3)
  const [isPaused, setIsPaused] = useState(false)

  const systemHealth = [
    {
      title: 'API Gateway', status: 'healthy', value: '99.9', unit: '% uptime', icon: Server,
      details: [{ label: 'Requests/sec', value: '1.2K' }, { label: 'Avg Response', value: '45ms' }]
    },
    {
      title: 'Database', status: 'healthy', value: '87', unit: '% CPU', icon: Database,
      details: [{ label: 'Connections', value: '234' }, { label: 'Query Time', value: '12ms' }]
    },
    {
      title: 'AI Models', status: 'warning', value: '2.1', unit: 'GB memory', icon: Cpu,
      details: [{ label: 'Active Models', value: '5' }, { label: 'GPU Usage', value: '78%' }]
    },
    {
      title: 'Network', status: 'healthy', value: '156', unit: 'Mbps', icon: Globe,
      details: [{ label: 'Latency', value: '23ms' }, { label: 'Packet Loss', value: '0.1%' }]
    },
  ]

  return (
    <div className="min-h-screen relative overflow-hidden">

      <div className="relative z-10 p-6 space-y-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between"
        >
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-green-400 to-blue-400 
                           bg-clip-text text-transparent">
              Real-Time Monitoring
            </h1>
            <p className="text-white/60 mt-2 flex items-center gap-2">
              <Eye className="w-4 h-4" />
              Live system monitoring and performance analytics
            </p>
          </div>

          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-sm text-white/70">
              <Clock className="w-4 h-4" />
              <span>Refresh every {refreshRate}s</span>
            </div>

            <select
              value={refreshRate}
              onChange={(e) => setRefreshRate(Number(e.target.value))}
              className="bg-black/40 backdrop-blur-lg border border-white/10 rounded-xl px-3 py-2
                         text-white text-sm focus:outline-none focus:border-green-400/50"
            >
              <option value={1}>1 second</option>
              <option value={3}>3 seconds</option>
              <option value={5}>5 seconds</option>
              <option value={10}>10 seconds</option>
            </select>

            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setIsPaused(!isPaused)}
              className={`px-4 py-2 rounded-xl font-medium transition-all duration-300 ${isPaused
                ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                : 'bg-green-500/20 text-green-400 border border-green-500/30'
                }`}
            >
              {isPaused ? 'Resume' : 'Pause'}
            </motion.button>
          </div>
        </motion.div>

        {/* Dashboard Navigation */}
        <DashboardNavigation />

        {/* System Health Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {systemHealth.map((system, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <SystemHealthCard {...system} />
            </motion.div>
          ))}
        </div>

        {/* Main Monitoring Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <RealTimeCharts />
          <LiveMetricsStream />
        </div>

        {/* Network Topology */}
        <NetworkTopology />

        {/* Bottom Status Panel */}
        <GlassCard className="p-6" delay={0.5}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-6">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-white font-medium">All Systems Operational</span>
              </div>

              <div className="flex items-center gap-4 text-sm text-white/60">
                <span>Last check: {new Date().toLocaleTimeString()}</span>
                <span>•</span>
                <span>5 systems monitored</span>
                <span>•</span>
                <span>0 critical alerts</span>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="flex items-center gap-2 bg-white/10 border border-white/20 rounded-xl px-4 py-2 
                           text-white hover:bg-white/20 transition-all duration-300"
              >
                <Bell className="w-4 h-4" />
                Alerts
              </motion.button>

              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="flex items-center gap-2 bg-gradient-to-r from-green-600 to-blue-600 
                           text-white px-4 py-2 rounded-xl font-medium hover:shadow-lg 
                           hover:shadow-green-500/25 transition-all duration-300"
              >
                <RotateCcw className="w-4 h-4" />
                Force Refresh
              </motion.button>
            </div>
          </div>
        </GlassCard>
      </div>
    </div>
  )
}