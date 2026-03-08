'use client'

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Settings,
  Zap,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Activity,
  Clock,
  Server,
  Database,
  Cpu,
  HardDrive,
  Network,
  BarChart4,
  TrendingUp,
  TrendingDown,
  RefreshCw,
  Play,
  Pause,
  Eye,
  Bell
} from 'lucide-react'
import DashboardNavigation from '@/components/DashboardNavigation'
import { GlassCard } from '@/components/ui/GlassCard'

interface OpsCardProps { title: string; value: string; change?: string; trend?: 'up' | 'down'; icon: React.ElementType; color?: 'blue' | 'green' | 'red' | 'amber' | 'purple'; status?: string; }
const OperationsMetricCard = ({ title, value, change, trend, icon: Icon, color = "blue", status }: OpsCardProps) => (
  <GlassCard className="p-6 group relative overflow-hidden">
    {/* Status indicator */}
    {status && (
      <div className="absolute top-3 right-3">
        <div className={`w-2 h-2 rounded-full animate-pulse ${status === 'healthy' ? 'bg-green-500' :
          status === 'warning' ? 'bg-amber-500' :
            'bg-red-500'
          }`} />
      </div>
    )}

    {/* Background gradient */}
    <div className={`absolute inset-0 bg-gradient-to-br ${color === 'green' ? 'from-green-500/20 to-emerald-500/20' :
      color === 'red' ? 'from-red-500/20 to-pink-500/20' :
        color === 'amber' ? 'from-amber-500/20 to-orange-500/20' :
          color === 'purple' ? 'from-purple-500/20 to-pink-500/20' :
            'from-blue-500/20 to-purple-500/20'
      } opacity-0 group-hover:opacity-100 transition-opacity duration-500`} />

    <div className="relative z-10">
      <div className="flex items-start justify-between mb-4">
        <div className={`p-3 rounded-xl bg-gradient-to-r ${color === 'green' ? 'from-green-500/20 to-emerald-500/20' :
          color === 'red' ? 'from-red-500/20 to-pink-500/20' :
            color === 'amber' ? 'from-amber-500/20 to-orange-500/20' :
              color === 'purple' ? 'from-purple-500/20 to-pink-500/20' :
                'from-blue-500/20 to-purple-500/20'
          }`}>
          <Icon className={`w-6 h-6 ${color === 'green' ? 'text-green-400' :
            color === 'red' ? 'text-red-400' :
              color === 'amber' ? 'text-amber-400' :
                color === 'purple' ? 'text-purple-400' :
                  'text-blue-400'
            }`} />
        </div>

        {trend && (
          <div className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs font-semibold ${trend === 'up' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
            }`}>
            {trend === 'up' ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
            {change}
          </div>
        )}
      </div>

      <div className="space-y-2">
        <h3 className="text-white/80 text-sm font-medium">{title}</h3>
        <p className="text-3xl font-bold text-white">{value}</p>
      </div>
    </div>
  </GlassCard>
)

const AutomationPerformance = () => {
  const automations = [
    {
      name: 'Compliance Check Automation',
      runs: 1247,
      success: 98.5,
      failures: 18,
      avgTime: '2.3s',
      status: 'healthy'
    },
    {
      name: 'Risk Assessment Pipeline',
      runs: 892,
      success: 96.2,
      failures: 34,
      avgTime: '4.7s',
      status: 'warning'
    },
    {
      name: 'Report Generation',
      runs: 645,
      success: 99.1,
      failures: 6,
      avgTime: '12.4s',
      status: 'healthy'
    },
    {
      name: 'Bias Detection Scan',
      runs: 423,
      success: 94.8,
      failures: 22,
      avgTime: '8.9s',
      status: 'warning'
    },
    {
      name: 'Model Card Updates',
      runs: 234,
      success: 99.6,
      failures: 1,
      avgTime: '1.8s',
      status: 'healthy'
    }
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'text-green-400 bg-green-500/20'
      case 'warning': return 'text-amber-400 bg-amber-500/20'
      case 'error': return 'text-red-400 bg-red-500/20'
      default: return 'text-gray-400 bg-gray-500/20'
    }
  }

  return (
    <GlassCard className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Zap className="w-6 h-6 text-purple-400" />
          <h3 className="text-2xl font-bold text-white">Automation Performance</h3>
        </div>
        <div className="flex items-center gap-2">
          <button className="p-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors">
            <RefreshCw className="w-4 h-4 text-white/70" />
          </button>
          <button className="p-2 rounded-lg bg-green-500/20 hover:bg-green-500/30 transition-colors">
            <Play className="w-4 h-4 text-green-400" />
          </button>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-white/10">
              <th className="text-left py-3 text-white/70 font-medium">Automation</th>
              <th className="text-center py-3 text-white/70 font-medium">Runs</th>
              <th className="text-center py-3 text-white/70 font-medium">Success Rate</th>
              <th className="text-center py-3 text-white/70 font-medium">Failures</th>
              <th className="text-center py-3 text-white/70 font-medium">Avg Time</th>
              <th className="text-center py-3 text-white/70 font-medium">Status</th>
            </tr>
          </thead>
          <tbody>
            {automations.map((automation, index) => (
              <motion.tr
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="border-b border-white/5 hover:bg-white/5 transition-colors"
              >
                <td className="py-4">
                  <span className="text-white font-medium">{automation.name}</span>
                </td>
                <td className="py-4 text-center text-white/80">{automation.runs.toLocaleString()}</td>
                <td className="py-4 text-center">
                  <span className={`font-semibold ${automation.success >= 98 ? 'text-green-400' :
                    automation.success >= 95 ? 'text-amber-400' :
                      'text-red-400'
                    }`}>
                    {automation.success}%
                  </span>
                </td>
                <td className="py-4 text-center text-red-400 font-semibold">{automation.failures}</td>
                <td className="py-4 text-center text-white/80">{automation.avgTime}</td>
                <td className="py-4 text-center">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(automation.status)}`}>
                    {automation.status}
                  </span>
                </td>
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>
    </GlassCard>
  )
}

const SystemHealth = () => {
  const systems = [
    { name: 'API Gateway', cpu: 45, memory: 62, disk: 34, status: 'healthy' },
    { name: 'Database Cluster', cpu: 78, memory: 84, disk: 67, status: 'warning' },
    { name: 'AI Processing', cpu: 92, memory: 89, disk: 23, status: 'warning' },
    { name: 'Background Jobs', cpu: 34, memory: 45, disk: 56, status: 'healthy' },
    { name: 'File Storage', cpu: 12, memory: 28, disk: 89, status: 'error' }
  ]

  const getHealthColor = (value: number, type: string) => {
    if (type === 'disk') {
      if (value >= 85) return 'text-red-400'
      if (value >= 70) return 'text-amber-400'
      return 'text-green-400'
    }

    if (value >= 85) return 'text-red-400'
    if (value >= 70) return 'text-amber-400'
    return 'text-green-400'
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy': return <CheckCircle className="w-4 h-4 text-green-400" />
      case 'warning': return <AlertTriangle className="w-4 h-4 text-amber-400" />
      case 'error': return <XCircle className="w-4 h-4 text-red-400" />
      default: return <Activity className="w-4 h-4 text-gray-400" />
    }
  }

  return (
    <GlassCard className="p-6">
      <div className="flex items-center gap-3 mb-6">
        <Server className="w-6 h-6 text-blue-400" />
        <h3 className="text-2xl font-bold text-white">System Health</h3>
      </div>

      <div className="space-y-4">
        {systems.map((system, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="p-4 rounded-xl border border-white/10 hover:bg-white/5 transition-colors"
          >
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                {getStatusIcon(system.status)}
                <span className="text-white font-medium">{system.name}</span>
              </div>
              <span className={`text-sm font-semibold ${system.status === 'healthy' ? 'text-green-400' :
                system.status === 'warning' ? 'text-amber-400' :
                  'text-red-400'
                }`}>
                {system.status.toUpperCase()}
              </span>
            </div>

            <div className="grid grid-cols-3 gap-4 text-sm">
              <div>
                <div className="flex items-center gap-1 mb-1">
                  <Cpu className="w-3 h-3 text-white/50" />
                  <span className="text-white/70">CPU</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="flex-1 bg-white/10 rounded-full h-1.5">
                    <div
                      className={`h-full rounded-full ${system.cpu >= 85 ? 'bg-red-500' :
                        system.cpu >= 70 ? 'bg-amber-500' :
                          'bg-green-500'
                        }`}
                      style={{ width: `${system.cpu}%` }}
                    />
                  </div>
                  <span className={`font-semibold ${getHealthColor(system.cpu, 'cpu')}`}>
                    {system.cpu}%
                  </span>
                </div>
              </div>

              <div>
                <div className="flex items-center gap-1 mb-1">
                  <Database className="w-3 h-3 text-white/50" />
                  <span className="text-white/70">Memory</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="flex-1 bg-white/10 rounded-full h-1.5">
                    <div
                      className={`h-full rounded-full ${system.memory >= 85 ? 'bg-red-500' :
                        system.memory >= 70 ? 'bg-amber-500' :
                          'bg-green-500'
                        }`}
                      style={{ width: `${system.memory}%` }}
                    />
                  </div>
                  <span className={`font-semibold ${getHealthColor(system.memory, 'memory')}`}>
                    {system.memory}%
                  </span>
                </div>
              </div>

              <div>
                <div className="flex items-center gap-1 mb-1">
                  <HardDrive className="w-3 h-3 text-white/50" />
                  <span className="text-white/70">Disk</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="flex-1 bg-white/10 rounded-full h-1.5">
                    <div
                      className={`h-full rounded-full ${system.disk >= 85 ? 'bg-red-500' :
                        system.disk >= 70 ? 'bg-amber-500' :
                          'bg-green-500'
                        }`}
                      style={{ width: `${system.disk}%` }}
                    />
                  </div>
                  <span className={`font-semibold ${getHealthColor(system.disk, 'disk')}`}>
                    {system.disk}%
                  </span>
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </GlassCard>
  )
}

const OperationalMetrics = () => {
  const metricsData = [
    { label: 'Uptime', value: '99.94%', color: 'text-green-400' },
    { label: 'Avg Response Time', value: '145ms', color: 'text-blue-400' },
    { label: 'Error Rate', value: '0.02%', color: 'text-green-400' },
    { label: 'Throughput', value: '2.4K req/s', color: 'text-purple-400' }
  ]

  const incidentData = [
    { type: 'Critical', count: 0, color: 'text-green-400' },
    { type: 'High', count: 2, color: 'text-amber-400' },
    { type: 'Medium', count: 5, color: 'text-blue-400' },
    { type: 'Low', count: 12, color: 'text-gray-400' }
  ]

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <GlassCard className="p-6">
        <div className="flex items-center gap-3 mb-6">
          <BarChart4 className="w-6 h-6 text-green-400" />
          <h3 className="text-xl font-bold text-white">Performance Metrics</h3>
        </div>

        <div className="grid grid-cols-2 gap-4">
          {metricsData.map((metric, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="text-center p-4 rounded-xl bg-white/5"
            >
              <p className="text-white/70 text-sm mb-2">{metric.label}</p>
              <p className={`text-2xl font-bold ${metric.color}`}>{metric.value}</p>
            </motion.div>
          ))}
        </div>
      </GlassCard>

      <GlassCard className="p-6" delay={0.2}>
        <div className="flex items-center gap-3 mb-6">
          <AlertTriangle className="w-6 h-6 text-amber-400" />
          <h3 className="text-xl font-bold text-white">Open Incidents</h3>
        </div>

        <div className="space-y-3">
          {incidentData.map((incident, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="flex items-center justify-between p-3 rounded-xl bg-white/5"
            >
              <span className="text-white font-medium">{incident.type} Priority</span>
              <span className={`text-xl font-bold ${incident.color}`}>{incident.count}</span>
            </motion.div>
          ))}
        </div>

        <div className="mt-4 pt-4 border-t border-white/10 text-center">
          <p className="text-white/60 text-sm">Total Active Incidents: <span className="text-white font-semibold">19</span></p>
        </div>
      </GlassCard>
    </div>
  )
}

const RecentActivity = () => {
  const activities = [
    {
      type: 'success',
      message: 'Automated deployment completed successfully',
      timestamp: '2 minutes ago',
      details: 'Version 2.1.4 deployed to production'
    },
    {
      type: 'warning',
      message: 'High memory usage detected on Database Cluster',
      timestamp: '8 minutes ago',
      details: '84% memory utilization - monitoring'
    },
    {
      type: 'info',
      message: 'Scheduled maintenance started',
      timestamp: '15 minutes ago',
      details: 'Background job optimization in progress'
    },
    {
      type: 'error',
      message: 'File Storage disk space critical',
      timestamp: '32 minutes ago',
      details: '89% disk utilization - immediate action required'
    },
    {
      type: 'success',
      message: 'Bias detection automation completed',
      timestamp: '1 hour ago',
      details: 'Processed 1,247 records with 98.5% success rate'
    }
  ]

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'success': return <CheckCircle className="w-4 h-4 text-green-400" />
      case 'warning': return <AlertTriangle className="w-4 h-4 text-amber-400" />
      case 'error': return <XCircle className="w-4 h-4 text-red-400" />
      default: return <Activity className="w-4 h-4 text-blue-400" />
    }
  }

  return (
    <GlassCard className="p-6" delay={0.3}>
      <div className="flex items-center gap-3 mb-6">
        <Clock className="w-6 h-6 text-blue-400" />
        <h3 className="text-2xl font-bold text-white">Recent Activity</h3>
        <div className="ml-auto">
          <button className="p-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors">
            <Bell className="w-4 h-4 text-white/70" />
          </button>
        </div>
      </div>

      <div className="space-y-4 max-h-96 overflow-y-auto">
        {activities.map((activity, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className="flex items-start gap-3 p-3 rounded-xl hover:bg-white/5 transition-colors"
          >
            <div className="mt-0.5">{getActivityIcon(activity.type)}</div>
            <div className="flex-1 min-w-0">
              <p className="text-white font-medium mb-1">{activity.message}</p>
              <p className="text-white/60 text-sm mb-1">{activity.details}</p>
              <p className="text-white/50 text-xs">{activity.timestamp}</p>
            </div>
          </motion.div>
        ))}
      </div>
    </GlassCard>
  )
}

export default function OperationsDashboard() {
  return (
    <div className="min-h-screen relative overflow-hidden">

      <div className="relative z-10 p-6 space-y-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center"
        >
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="p-3 rounded-2xl bg-gradient-to-r from-amber-500/20 to-orange-500/20">
              <Settings className="w-8 h-8 text-amber-400" />
            </div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-amber-400 to-orange-400 
                           bg-clip-text text-transparent">
              Operations Dashboard
            </h1>
          </div>
          <p className="text-white/60 text-lg">
            Monitor automations, workflows, and system performance
          </p>
        </motion.div>

        {/* Dashboard Navigation */}
        <DashboardNavigation />

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <OperationsMetricCard
            title="Operational Load"
            value="$130,709"
            change="+5.2%"
            trend="up"
            icon={Activity}
            color="blue"
            status="healthy"
          />
          <OperationsMetricCard
            title="Active Automations"
            value="42"
            change="+3"
            trend="up"
            icon={Zap}
            color="purple"
            status="healthy"
          />
          <OperationsMetricCard
            title="System Health"
            value="96%"
            change="-2%"
            trend="down"
            icon={Server}
            color="amber"
            status="warning"
          />
          <OperationsMetricCard
            title="Failed Operations"
            value="18"
            change="-23%"
            trend="down"
            icon={XCircle}
            color="green"
            status="healthy"
          />
        </div>

        {/* Performance Metrics */}
        <OperationalMetrics />

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-8">
            <AutomationPerformance />
            <RecentActivity />
          </div>
          <div>
            <SystemHealth />
          </div>
        </div>
      </div>
    </div>
  )
}