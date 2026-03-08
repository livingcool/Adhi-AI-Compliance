'use client'

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  Shield,
  Brain,
  Users,
  Globe,
  Activity,
  PieChart,
  BarChart3,
  LineChart,
  Zap
} from 'lucide-react'
import DashboardNavigation from '@/components/DashboardNavigation'
import { GlassCard } from '@/components/ui/GlassCard'

// Chart components (you can integrate Chart.js, Recharts, or D3.js)
interface MetricCardProps {
  title: string;
  value: string;
  change?: string;
  trend?: 'up' | 'down';
  icon: React.ElementType;
  color?: 'blue' | 'green' | 'red' | 'amber';
}

const MetricCard = ({ title, value, change, trend, icon: Icon, color = "blue" }: MetricCardProps) => (
  <GlassCard className="p-6">
    <div className="flex items-start justify-between mb-4">
      <div className={`p-3 rounded-xl bg-gradient-to-r ${color === 'blue' ? 'from-blue-500/20 to-purple-500/20' :
        color === 'green' ? 'from-green-500/20 to-emerald-500/20' :
          color === 'red' ? 'from-red-500/20 to-pink-500/20' :
            'from-amber-500/20 to-orange-500/20'
        }`}>
        <Icon className={`w-6 h-6 ${color === 'blue' ? 'text-blue-400' :
          color === 'green' ? 'text-green-400' :
            color === 'red' ? 'text-red-400' :
              'text-amber-400'
          }`} />
      </div>
      {trend && (
        <div className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${trend === 'up' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
          }`}>
          {trend === 'up' ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
          {change}
        </div>
      )}
    </div>

    <div className="space-y-2">
      <h3 className="text-white/70 text-sm font-medium">{title}</h3>
      <p className="text-3xl font-bold text-white">{value}</p>
    </div>
  </GlassCard>
)

const ComplianceHeatmap = () => {
  const regulations = [
    { name: 'EU AI Act', systems: ['High', 'Limited', 'Minimal', 'High', 'Limited'] },
    { name: 'GDPR', systems: ['Compliant', 'Compliant', 'Partial', 'Compliant', 'Compliant'] },
    { name: 'NIST AI RMF', systems: ['Compliant', 'Partial', 'Compliant', 'Non-compliant', 'Partial'] },
    { name: 'CCPA', systems: ['Compliant', 'Compliant', 'Compliant', 'Partial', 'Compliant'] },
    { name: 'AAA', systems: ['Partial', 'Non-compliant', 'Compliant', 'Compliant', 'Partial'] },
  ]

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'compliant': return 'bg-green-500'
      case 'partial': return 'bg-amber-500'
      case 'non-compliant': return 'bg-red-500'
      case 'high': return 'bg-red-500'
      case 'limited': return 'bg-amber-500'
      case 'minimal': return 'bg-green-500'
      default: return 'bg-gray-500'
    }
  }

  return (
    <GlassCard className="p-6">
      <h3 className="text-xl font-bold text-white mb-6">Compliance Heatmap</h3>

      <div className="space-y-3">
        {regulations.map((reg, index) => (
          <div key={index} className="flex items-center gap-4">
            <div className="w-24 text-sm text-white/70 font-medium">{reg.name}</div>
            <div className="flex-1 flex gap-2">
              {reg.systems.map((status, systemIndex) => (
                <motion.div
                  key={systemIndex}
                  initial={{ opacity: 0, scale: 0 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: index * 0.1 + systemIndex * 0.05 }}
                  className={`flex-1 h-8 rounded-lg ${getStatusColor(status)} 
                             hover:scale-105 transition-transform cursor-pointer
                             flex items-center justify-center`}
                  title={`System ${systemIndex + 1}: ${status}`}
                >
                  <span className="text-xs font-medium text-white opacity-80">
                    S{systemIndex + 1}
                  </span>
                </motion.div>
              ))}
            </div>
          </div>
        ))}
      </div>

      <div className="flex items-center gap-4 mt-6 pt-4 border-t border-white/10">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded bg-green-500"></div>
          <span className="text-xs text-white/60">Compliant</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded bg-amber-500"></div>
          <span className="text-xs text-white/60">Partial</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded bg-red-500"></div>
          <span className="text-xs text-white/60">Non-compliant</span>
        </div>
      </div>
    </GlassCard>
  )
}

const RealTimeActivity = () => {
  const activities = [
    { type: 'audit', message: 'Bias audit completed for Resume Screening AI', time: '2 min ago', status: 'success' },
    { type: 'incident', message: 'New incident reported: Fraud Detection false positives', time: '5 min ago', status: 'warning' },
    { type: 'compliance', message: 'EU AI Act compliance check updated', time: '12 min ago', status: 'info' },
    { type: 'system', message: 'New AI system registered: Content Moderation v2', time: '28 min ago', status: 'success' },
    { type: 'alert', message: 'Compliance deadline approaching: AAA Review', time: '1 hour ago', status: 'warning' },
  ]

  return (
    <GlassCard className="p-6" delay={0.1}>
      <div className="flex items-center gap-2 mb-6">
        <Activity className="w-5 h-5 text-blue-400" />
        <h3 className="text-xl font-bold text-white">Real-Time Activity</h3>
        <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse ml-auto"></div>
      </div>

      <div className="space-y-4 max-h-80 overflow-y-auto">
        {activities.map((activity, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className="flex items-start gap-3 p-3 rounded-xl hover:bg-white/5 transition-colors"
          >
            <div className={`w-2 h-2 rounded-full mt-2 ${activity.status === 'success' ? 'bg-green-500' :
              activity.status === 'warning' ? 'bg-amber-500' :
                activity.status === 'error' ? 'bg-red-500' :
                  'bg-blue-500'
              }`}></div>

            <div className="flex-1 min-w-0">
              <p className="text-white text-sm">{activity.message}</p>
              <p className="text-white/50 text-xs mt-1">{activity.time}</p>
            </div>
          </motion.div>
        ))}
      </div>
    </GlassCard>
  )
}

const RiskDistributionChart = () => {
  const riskData = [
    { level: 'Unacceptable', count: 0, percentage: 0, color: 'from-red-600 to-red-500' },
    { level: 'High', count: 1, percentage: 20, color: 'from-red-500 to-pink-500' },
    { level: 'Limited', count: 2, percentage: 40, color: 'from-amber-500 to-orange-500' },
    { level: 'Minimal', count: 2, percentage: 40, color: 'from-green-500 to-emerald-500' },
    { level: 'Unclassified', count: 0, percentage: 0, color: 'from-gray-500 to-gray-400' },
  ]

  return (
    <GlassCard className="p-6" delay={0.2}>
      <h3 className="text-xl font-bold text-white mb-6">AI Risk Distribution</h3>

      <div className="space-y-4">
        {riskData.map((risk, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, scale: 0 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.1 }}
            className="flex items-center gap-4"
          >
            <div className="w-16 text-sm text-white/70 font-medium">{risk.level}</div>
            <div className="flex-1 bg-white/5 rounded-full h-3 overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${risk.percentage}%` }}
                transition={{ duration: 1, delay: index * 0.1 }}
                className={`h-full bg-gradient-to-r ${risk.color} rounded-full`}
              />
            </div>
            <div className="w-12 text-right">
              <span className="text-white font-medium">{risk.count}</span>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="mt-6 pt-4 border-t border-white/10 text-center">
        <p className="text-white/60 text-sm">Total AI Systems: 5</p>
      </div>
    </GlassCard>
  )
}

export default function AdvancedAnalytics() {
  const [timeRange, setTimeRange] = useState('30d')
  const [isLoading, setIsLoading] = useState(false)

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
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 
                           bg-clip-text text-transparent">
              Advanced Analytics
            </h1>
            <p className="text-white/60 mt-2">
              Deep insights into AI compliance across your organization
            </p>
          </div>

          <div className="flex items-center gap-4">
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="bg-black/40 backdrop-blur-lg border border-white/10 rounded-xl px-4 py-2
                         text-white text-sm focus:outline-none focus:border-blue-400/50"
            >
              <option value="7d">Last 7 days</option>
              <option value="30d">Last 30 days</option>
              <option value="90d">Last 90 days</option>
              <option value="1y">Last year</option>
            </select>

            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="bg-gradient-to-r from-blue-500 to-purple-500 text-white px-6 py-2 
                         rounded-xl font-medium hover:shadow-lg hover:shadow-blue-500/25 
                         transition-all duration-300"
            >
              Export Report
            </motion.button>
          </div>
        </motion.div>

        {/* Dashboard Navigation */}
        <DashboardNavigation />

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <MetricCard
            title="Compliance Score"
            value="91.2%"
            change="+2.4%"
            trend="up"
            icon={Shield}
            color="green"
          />
          <MetricCard
            title="Active AI Systems"
            value="5"
            change="+1"
            trend="up"
            icon={Brain}
            color="blue"
          />
          <MetricCard
            title="Critical Issues"
            value="2"
            change="-1"
            trend="down"
            icon={AlertTriangle}
            color="red"
          />
          <MetricCard
            title="Audits Completed"
            value="12"
            change="+3"
            trend="up"
            icon={Users}
            color="amber"
          />
        </div>

        {/* Charts and Analysis */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <ComplianceHeatmap />
          <RiskDistributionChart />
        </div>

        {/* Real-time Activity */}
        <RealTimeActivity />

        {/* Additional Insights */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <GlassCard className="p-6" delay={0.3}>
            <div className="flex items-center gap-2 mb-4">
              <Globe className="w-5 h-5 text-blue-400" />
              <h3 className="text-lg font-bold text-white">Global Compliance</h3>
            </div>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-white/70">EU Regulations</span>
                <span className="text-green-400 font-medium">92%</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-white/70">US Standards</span>
                <span className="text-amber-400 font-medium">88%</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-white/70">Asia-Pacific</span>
                <span className="text-green-400 font-medium">95%</span>
              </div>
            </div>
          </GlassCard>

          <GlassCard className="p-6" delay={0.4}>
            <div className="flex items-center gap-2 mb-4">
              <Zap className="w-5 h-5 text-purple-400" />
              <h3 className="text-lg font-bold text-white">Performance</h3>
            </div>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-white/70">Avg Response Time</span>
                <span className="text-green-400 font-medium">240ms</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-white/70">Uptime</span>
                <span className="text-green-400 font-medium">99.8%</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-white/70">Data Quality</span>
                <span className="text-blue-400 font-medium">96.5%</span>
              </div>
            </div>
          </GlassCard>

          <GlassCard className="p-6" delay={0.5}>
            <div className="flex items-center gap-2 mb-4">
              <PieChart className="w-5 h-5 text-amber-400" />
              <h3 className="text-lg font-bold text-white">Trends</h3>
            </div>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-white/70">Compliance Improving</span>
                <div className="flex items-center gap-1 text-green-400">
                  <TrendingUp className="w-4 h-4" />
                  <span className="font-medium">+5.2%</span>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-white/70">Issues Declining</span>
                <div className="flex items-center gap-1 text-green-400">
                  <TrendingDown className="w-4 h-4" />
                  <span className="font-medium">-12%</span>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-white/70">Audit Frequency</span>
                <div className="flex items-center gap-1 text-blue-400">
                  <TrendingUp className="w-4 h-4" />
                  <span className="font-medium">+8%</span>
                </div>
              </div>
            </div>
          </GlassCard>
        </div>
      </div>
    </div>
  )
}