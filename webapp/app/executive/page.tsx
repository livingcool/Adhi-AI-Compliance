'use client'

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  Shield,
  AlertCircle,
  CheckCircle2,
  Clock,
  Building,
  Target,
  Award,
  Users,
  Globe2,
  BarChart4,
  PieChart,
  ArrowUpRight,
  ArrowDownRight,
  Calendar,
  Bell,
  Download,
  Crown
} from 'lucide-react'
import DashboardNavigation from '@/components/DashboardNavigation'
import { useFounderAuth } from '@/lib/founder-auth'
import { FounderProtected } from '@/components/FounderProtected'

interface ExecCardProps { title: string; value: string; change?: string; trend?: 'up' | 'down'; icon: React.ElementType; color?: 'blue' | 'green' | 'red' | 'amber'; subtitle?: string; }
const ExecutiveMetricCard = ({ title, value, change, trend, icon: Icon, color = "blue", subtitle }: ExecCardProps) => (
  <motion.div
    initial={{ opacity: 0, scale: 0.95 }}
    animate={{ opacity: 1, scale: 1 }}
    className="bg-gradient-to-br from-black/60 to-black/40 backdrop-blur-xl border border-white/10 
               rounded-3xl p-8 hover:border-white/20 transition-all duration-500 group relative overflow-hidden"
  >
    {/* Background decoration */}
    <div className={`absolute inset-0 bg-gradient-to-br ${color === 'blue' ? 'from-blue-500/10 to-purple-500/10' :
      color === 'green' ? 'from-green-500/10 to-emerald-500/10' :
        color === 'red' ? 'from-red-500/10 to-pink-500/10' :
          'from-amber-500/10 to-orange-500/10'
      } opacity-0 group-hover:opacity-100 transition-opacity duration-500`} />

    <div className="relative z-10">
      <div className="flex items-start justify-between mb-6">
        <div className={`p-4 rounded-2xl bg-gradient-to-r ${color === 'blue' ? 'from-blue-500/20 to-purple-500/20' :
          color === 'green' ? 'from-green-500/20 to-emerald-500/20' :
            color === 'red' ? 'from-red-500/20 to-pink-500/20' :
              'from-amber-500/20 to-orange-500/20'
          }`}>
          <Icon className={`w-8 h-8 ${color === 'blue' ? 'text-blue-400' :
            color === 'green' ? 'text-green-400' :
              color === 'red' ? 'text-red-400' :
                'text-amber-400'
            }`} />
        </div>

        {trend && (
          <div className={`flex items-center gap-2 px-3 py-2 rounded-full text-sm font-semibold ${trend === 'up' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
            }`}>
            {trend === 'up' ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
            {change}
          </div>
        )}
      </div>

      <div className="space-y-3">
        <h3 className="text-white/80 text-lg font-medium">{title}</h3>
        <p className="text-5xl font-bold text-white">{value}</p>
        {subtitle && <p className="text-white/60 text-sm">{subtitle}</p>}
      </div>
    </div>
  </motion.div>
)

const ComplianceOverview = () => {
  const complianceData = [
    { regulation: 'EU AI Act', status: 87, issues: 2, deadline: '15 Mar 2024' },
    { regulation: 'GDPR', status: 96, issues: 0, deadline: 'Ongoing' },
    { regulation: 'NIST AI RMF', status: 89, issues: 1, deadline: '30 Apr 2024' },
    { regulation: 'CCPA', status: 92, issues: 1, deadline: 'Ongoing' },
    { regulation: 'Algorithmic Accountability', status: 78, issues: 3, deadline: '10 May 2024' },
  ]

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-gradient-to-br from-black/60 to-black/40 backdrop-blur-xl border border-white/10 rounded-3xl p-8"
    >
      <div className="flex items-center justify-between mb-8">
        <h3 className="text-2xl font-bold text-white">Regulatory Compliance</h3>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="text-blue-400 hover:text-blue-300 transition-colors"
        >
          View Details →
        </motion.button>
      </div>

      <div className="space-y-6">
        {complianceData.map((item, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className="flex items-center gap-6 p-4 rounded-2xl hover:bg-white/5 transition-colors"
          >
            <div className="flex-1">
              <div className="flex items-center justify-between mb-2">
                <span className="text-white font-medium">{item.regulation}</span>
                <span className={`text-sm font-semibold ${item.status >= 90 ? 'text-green-400' :
                  item.status >= 80 ? 'text-amber-400' :
                    'text-red-400'
                  }`}>
                  {item.status}%
                </span>
              </div>

              <div className="flex items-center gap-4 mb-3">
                <div className="flex-1 bg-white/10 rounded-full h-2 overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${item.status}%` }}
                    transition={{ duration: 1, delay: index * 0.1 }}
                    className={`h-full rounded-full ${item.status >= 90 ? 'bg-gradient-to-r from-green-500 to-emerald-500' :
                      item.status >= 80 ? 'bg-gradient-to-r from-amber-500 to-orange-500' :
                        'bg-gradient-to-r from-red-500 to-pink-500'
                      }`}
                  />
                </div>
              </div>

              <div className="flex items-center justify-between text-sm">
                <span className="text-white/60">
                  {item.issues} {item.issues === 1 ? 'issue' : 'issues'} remaining
                </span>
                <span className="text-white/60">Due: {item.deadline}</span>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  )
}

const RiskSummary = () => {
  const riskData = [
    { level: 'Critical', count: 2, percentage: 8, color: 'text-red-400 bg-red-500/20' },
    { level: 'High', count: 5, percentage: 20, color: 'text-amber-400 bg-amber-500/20' },
    { level: 'Medium', count: 12, percentage: 48, color: 'text-blue-400 bg-blue-500/20' },
    { level: 'Low', count: 6, percentage: 24, color: 'text-green-400 bg-green-500/20' },
  ]

  const totalRisks = riskData.reduce((sum, item) => sum + item.count, 0)

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
      className="bg-gradient-to-br from-black/60 to-black/40 backdrop-blur-xl border border-white/10 rounded-3xl p-8"
    >
      <div className="flex items-center justify-between mb-8">
        <h3 className="text-2xl font-bold text-white">Risk Assessment</h3>
        <div className="text-right">
          <p className="text-3xl font-bold text-white">{totalRisks}</p>
          <p className="text-white/60 text-sm">Total Risks</p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {riskData.map((risk, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, scale: 0 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.1 + 0.3 }}
            className={`p-4 rounded-2xl ${risk.color.split(' ')[1]} border border-white/10`}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-white font-medium">{risk.level}</span>
              <span className={`text-2xl font-bold ${risk.color.split(' ')[0]}`}>
                {risk.count}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <div className="flex-1 bg-white/20 rounded-full h-1">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${risk.percentage}%` }}
                  transition={{ duration: 1, delay: index * 0.1 + 0.5 }}
                  className={`h-full rounded-full ${risk.level === 'Critical' ? 'bg-red-400' :
                    risk.level === 'High' ? 'bg-amber-400' :
                      risk.level === 'Medium' ? 'bg-blue-400' :
                        'bg-green-400'
                    }`}
                />
              </div>
              <span className="text-xs text-white/60">{risk.percentage}%</span>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  )
}

const ExecutiveAlerts = () => {
  const alerts = [
    {
      type: 'critical',
      message: 'EU AI Act compliance deadline in 18 days',
      action: 'Review high-risk systems',
      time: '2 hours ago'
    },
    {
      type: 'warning',
      message: 'Bias detected in Resume Screening AI',
      action: 'Schedule audit review',
      time: '4 hours ago'
    },
    {
      type: 'info',
      message: '3 new regulations require assessment',
      action: 'Update compliance matrix',
      time: '1 day ago'
    },
    {
      type: 'success',
      message: 'Content Moderation AI passed fairness audit',
      action: 'Update documentation',
      time: '2 days ago'
    }
  ]

  const getAlertColor = (type: string) => {
    switch (type) {
      case 'critical': return 'border-l-red-500 bg-red-500/10'
      case 'warning': return 'border-l-amber-500 bg-amber-500/10'
      case 'info': return 'border-l-blue-500 bg-blue-500/10'
      case 'success': return 'border-l-green-500 bg-green-500/10'
      default: return 'border-l-gray-500 bg-gray-500/10'
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 0.3 }}
      className="bg-gradient-to-br from-black/60 to-black/40 backdrop-blur-xl border border-white/10 rounded-3xl p-8"
    >
      <div className="flex items-center gap-3 mb-8">
        <Bell className="w-6 h-6 text-blue-400" />
        <h3 className="text-2xl font-bold text-white">Priority Alerts</h3>
        <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse ml-auto"></div>
      </div>

      <div className="space-y-4">
        {alerts.map((alert, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 + 0.4 }}
            className={`border-l-4 ${getAlertColor(alert.type)} p-4 rounded-r-xl`}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <p className="text-white font-medium mb-1">{alert.message}</p>
                <p className="text-blue-400 text-sm font-medium cursor-pointer hover:text-blue-300">
                  {alert.action} →
                </p>
              </div>
              <span className="text-white/50 text-xs">{alert.time}</span>
            </div>
          </motion.div>
        ))}
      </div>

      <motion.button
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        className="w-full mt-6 bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 
                   rounded-xl font-medium hover:shadow-lg hover:shadow-blue-500/25 
                   transition-all duration-300"
      >
        View All Alerts
      </motion.button>
    </motion.div>
  )
}

const BusinessImpactSummary = () => {
  const metrics = [
    { label: 'Compliance Cost Savings', value: '$2.4M', change: '+15%', period: 'annually' },
    { label: 'Risk Reduction', value: '67%', change: '+12%', period: 'vs last quarter' },
    { label: 'Time to Compliance', value: '18 days', change: '-45%', period: 'average' },
    { label: 'Audit Readiness', value: '94%', change: '+8%', period: 'systems ready' },
  ]

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: 0.4 }}
      className="bg-gradient-to-br from-black/60 to-black/40 backdrop-blur-xl border border-white/10 rounded-3xl p-8"
    >
      <div className="flex items-center gap-3 mb-8">
        <Target className="w-6 h-6 text-green-400" />
        <h3 className="text-2xl font-bold text-white">Business Impact</h3>
      </div>

      <div className="grid grid-cols-2 gap-6">
        {metrics.map((metric, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 + 0.5 }}
            className="text-center"
          >
            <p className="text-white/60 text-sm mb-2">{metric.label}</p>
            <p className="text-3xl font-bold text-white mb-1">{metric.value}</p>
            <div className="flex items-center justify-center gap-2">
              <span className="text-green-400 text-sm font-semibold">{metric.change}</span>
              <span className="text-white/50 text-xs">{metric.period}</span>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  )
}

export default function ExecutiveDashboard() {
  const [isLoading, setIsLoading] = useState(false)
  const { isAuthenticated: isFounderAuth } = useFounderAuth()

  return (
    <div className="min-h-screen bg-[rgb(5,5,5)] relative overflow-hidden">
      {/* Enhanced dotted background */}
      <div
        className="absolute inset-0 opacity-20"
        style={{
          backgroundImage: 'radial-gradient(circle, rgba(59,130,246,0.3) 1px, transparent 1px)',
          backgroundSize: '32px 32px'
        }}
      />

      {/* Gradient overlays */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-900/20 via-transparent to-purple-900/20" />
      <div className="absolute inset-0 bg-gradient-to-tr from-transparent via-transparent to-blue-900/10" />

      <div className="relative z-10 p-8 space-y-10">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between"
        >
          <div>
            <h1 className="text-5xl font-bold bg-gradient-to-r from-white via-blue-200 to-purple-200 
                           bg-clip-text text-transparent mb-3">
              Executive Dashboard
            </h1>
            <p className="text-xl text-white/70">
              Strategic overview of AI compliance and governance across RootedAI
            </p>
            <p className="text-white/50 mt-2">
              Last updated: {new Date().toLocaleString()} • Real-time data
            </p>
          </div>

          <div className="flex items-center gap-4">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="flex items-center gap-2 bg-white/10 backdrop-blur-lg border border-white/20 
                         rounded-xl px-6 py-3 text-white hover:bg-white/20 transition-all duration-300"
            >
              <Calendar className="w-4 h-4" />
              Schedule Review
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="flex items-center gap-2 bg-gradient-to-r from-blue-600 to-purple-600 
                         text-white px-6 py-3 rounded-xl font-medium hover:shadow-lg 
                         hover:shadow-blue-500/25 transition-all duration-300"
            >
              <Download className="w-4 h-4" />
              Executive Report
            </motion.button>
          </div>
        </motion.div>

        {/* Dashboard Navigation */}
        <DashboardNavigation />

        {/* Key Executive Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          <ExecutiveMetricCard
            title="Overall Compliance"
            value="91.2%"
            change="+2.4%"
            trend="up"
            icon={Shield}
            color="green"
            subtitle="Across all regulations"
          />
          <ExecutiveMetricCard
            title="Risk Score"
            value="Medium"
            change="-15%"
            trend="down"
            icon={AlertCircle}
            color="amber"
            subtitle="2 critical, 5 high risks"
          />
          <ExecutiveMetricCard
            title="Cost Avoidance"
            value="$2.4M"
            change="+18%"
            trend="up"
            icon={DollarSign}
            color="green"
            subtitle="Annual savings from compliance"
          />
          <ExecutiveMetricCard
            title="AI Systems"
            value="5"
            change="+1"
            trend="up"
            icon={Building}
            color="blue"
            subtitle="Production systems monitored"
          />
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
          <ComplianceOverview />
          <ExecutiveAlerts />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
          <RiskSummary />
          <BusinessImpactSummary />
        </div>

        {/* Founder-Only Financial Data */}
        {isFounderAuth && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 }}
            className="bg-gradient-to-br from-amber-500/20 to-orange-500/20 backdrop-blur-xl 
                       border border-amber-500/30 rounded-3xl p-8"
          >
            <div className="flex items-center gap-3 mb-6">
              <Crown className="w-6 h-6 text-amber-400" />
              <h3 className="text-2xl font-bold text-white">Founder Financial Overview</h3>
              <div className="bg-amber-500/20 px-2 py-1 rounded-full">
                <span className="text-amber-400 text-xs font-medium">Sensitive Data</span>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="space-y-3">
                <h4 className="text-white font-medium">Revenue Breakdown</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-white/70">Q4 2024 Actual</span>
                    <span className="text-green-400 font-semibold">$450K</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-white/70">Q1 2025 Projected</span>
                    <span className="text-blue-400 font-semibold">$620K</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-white/70">Annual Target</span>
                    <span className="text-purple-400 font-semibold">$2.4M</span>
                  </div>
                </div>
              </div>

              <div className="space-y-3">
                <h4 className="text-white font-medium">Client Contracts</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-white/70">Active Contracts</span>
                    <span className="text-green-400 font-semibold">$700K</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-white/70">Pipeline</span>
                    <span className="text-blue-400 font-semibold">$1.2M</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-white/70">At Risk</span>
                    <span className="text-red-400 font-semibold">$95K</span>
                  </div>
                </div>
              </div>

              <div className="space-y-3">
                <h4 className="text-white font-medium">Operational Metrics</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-white/70">Monthly Burn</span>
                    <span className="text-red-400 font-semibold">$35K</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-white/70">Runway</span>
                    <span className="text-green-400 font-semibold">18 months</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-white/70">Team Cost/Month</span>
                    <span className="text-amber-400 font-semibold">$15K</span>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {/* Bottom Action Panel */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="bg-gradient-to-br from-black/60 to-black/40 backdrop-blur-xl border border-white/10 
                     rounded-3xl p-8"
        >
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-2xl font-bold text-white mb-2">Next Actions Required</h3>
              <p className="text-white/70">
                2 critical items need executive attention within the next 7 days
              </p>
            </div>

            <div className="flex items-center gap-4">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="bg-gradient-to-r from-red-600 to-pink-600 text-white px-8 py-3 
                           rounded-xl font-medium hover:shadow-lg hover:shadow-red-500/25 
                           transition-all duration-300"
              >
                Review Critical Items
              </motion.button>

              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-3 
                           rounded-xl font-medium hover:shadow-lg hover:shadow-blue-500/25 
                           transition-all duration-300"
              >
                Schedule Team Meeting
              </motion.button>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}