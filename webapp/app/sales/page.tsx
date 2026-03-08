'use client'

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  DollarSign,
  TrendingUp,
  TrendingDown,
  Target,
  Users,
  ShoppingCart,
  BarChart3,
  PieChart,
  Calendar,
  ArrowUpRight,
  ArrowDownRight,
  Eye,
  Phone,
  Mail,
  Building
} from 'lucide-react'
import DashboardNavigation from '@/components/DashboardNavigation'

interface SalesCardProps { title: string; value: string; change?: string; trend?: 'up' | 'down'; icon: React.ElementType; color?: 'blue' | 'green' | 'red' | 'amber' | 'purple'; subtitle?: string; }
const SalesMetricCard = ({ title, value, change, trend, icon: Icon, color = "blue", subtitle }: SalesCardProps) => (
  <motion.div
    initial={{ opacity: 0, scale: 0.95 }}
    animate={{ opacity: 1, scale: 1 }}
    className="bg-black/40 backdrop-blur-lg border border-white/10 rounded-2xl p-6 
               hover:border-white/20 transition-all duration-300 group relative overflow-hidden"
  >
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
            {trend === 'up' ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
            {change}
          </div>
        )}
      </div>

      <div className="space-y-2">
        <h3 className="text-white/80 text-sm font-medium">{title}</h3>
        <p className="text-3xl font-bold text-white">{value}</p>
        {subtitle && <p className="text-white/60 text-xs">{subtitle}</p>}
      </div>
    </div>
  </motion.div>
)

const SalesPipeline = () => {
  const pipelineStages = [
    { stage: 'Lead', count: 45, value: '$540K', color: 'bg-blue-500' },
    { stage: 'Qualified', count: 28, value: '$420K', color: 'bg-indigo-500' },
    { stage: 'Proposal', count: 18, value: '$310K', color: 'bg-purple-500' },
    { stage: 'Negotiation', count: 12, value: '$240K', color: 'bg-pink-500' },
    { stage: 'Closed Won', count: 8, value: '$160K', color: 'bg-green-500' }
  ]

  const totalValue = '$1.67M'
  const conversionRate = '18%'

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-black/40 backdrop-blur-lg border border-white/10 rounded-2xl p-6"
    >
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Target className="w-6 h-6 text-purple-400" />
          <h3 className="text-2xl font-bold text-white">Sales Pipeline</h3>
        </div>
        <div className="text-right">
          <p className="text-2xl font-bold text-white">{totalValue}</p>
          <p className="text-white/60 text-sm">Total Pipeline Value</p>
        </div>
      </div>

      {/* Pipeline Visualization */}
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-4">
          {pipelineStages.map((stage, index) => (
            <motion.div
              key={stage.stage}
              initial={{ width: 0 }}
              animate={{ width: `${100 / pipelineStages.length}%` }}
              transition={{ duration: 1, delay: index * 0.1 }}
              className={`h-3 ${stage.color} rounded-full relative`}
            >
              {index < pipelineStages.length - 1 && (
                <div className="absolute -right-1 top-1/2 w-2 h-2 bg-white/20 rounded-full transform -translate-y-1/2" />
              )}
            </motion.div>
          ))}
        </div>

        <div className="grid grid-cols-5 gap-4">
          {pipelineStages.map((stage, index) => (
            <motion.div
              key={stage.stage}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="text-center"
            >
              <div className={`w-3 h-3 ${stage.color} rounded-full mx-auto mb-2`} />
              <p className="text-white font-medium text-sm mb-1">{stage.stage}</p>
              <p className="text-white/60 text-xs">{stage.count} deals</p>
              <p className="text-white/80 text-xs font-semibold">{stage.value}</p>
            </motion.div>
          ))}
        </div>
      </div>

      <div className="flex items-center justify-between pt-4 border-t border-white/10">
        <div className="text-center">
          <p className="text-xl font-bold text-green-400">{conversionRate}</p>
          <p className="text-white/60 text-sm">Conversion Rate</p>
        </div>
        <div className="text-center">
          <p className="text-xl font-bold text-blue-400">32</p>
          <p className="text-white/60 text-sm">Avg. Days to Close</p>
        </div>
        <div className="text-center">
          <p className="text-xl font-bold text-purple-400">$48K</p>
          <p className="text-white/60 text-sm">Avg. Deal Size</p>
        </div>
      </div>
    </motion.div>
  )
}

const RecentDeals = () => {
  const deals = [
    {
      id: 1,
      company: 'TechCorp Industries',
      contact: 'Sarah Johnson',
      value: '$180K',
      stage: 'Negotiation',
      probability: 85,
      closeDate: '2024-03-15',
      source: 'Referral'
    },
    {
      id: 2,
      company: 'Global Dynamics',
      contact: 'Mike Chen',
      value: '$145K',
      stage: 'Proposal',
      probability: 70,
      closeDate: '2024-03-22',
      source: 'Website'
    },
    {
      id: 3,
      company: 'Innovation Systems',
      contact: 'Emily Davis',
      value: '$120K',
      stage: 'Qualified',
      probability: 60,
      closeDate: '2024-04-10',
      source: 'Cold Call'
    },
    {
      id: 4,
      company: 'DataFlow Corp',
      contact: 'Alex Rodriguez',
      value: '$95K',
      stage: 'Closed Won',
      probability: 100,
      closeDate: '2024-02-28',
      source: 'LinkedIn'
    }
  ]

  const getStageColor = (stage: string) => {
    switch (stage) {
      case 'Lead': return 'bg-blue-500/20 text-blue-400'
      case 'Qualified': return 'bg-indigo-500/20 text-indigo-400'
      case 'Proposal': return 'bg-purple-500/20 text-purple-400'
      case 'Negotiation': return 'bg-pink-500/20 text-pink-400'
      case 'Closed Won': return 'bg-green-500/20 text-green-400'
      default: return 'bg-gray-500/20 text-gray-400'
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      className="bg-black/40 backdrop-blur-lg border border-white/10 rounded-2xl p-6"
    >
      <div className="flex items-center gap-3 mb-6">
        <ShoppingCart className="w-6 h-6 text-green-400" />
        <h3 className="text-2xl font-bold text-white">Recent Deals</h3>
      </div>

      <div className="space-y-4">
        {deals.map((deal, index) => (
          <motion.div
            key={deal.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className="flex items-center gap-4 p-4 rounded-xl hover:bg-white/5 transition-colors border border-white/5"
          >
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <Building className="w-4 h-4 text-white/50" />
                <span className="text-white font-medium">{deal.company}</span>
                <span className={`px-2 py-1 rounded-lg text-xs font-medium ${getStageColor(deal.stage)}`}>
                  {deal.stage}
                </span>
              </div>

              <div className="flex items-center gap-4 text-sm text-white/60">
                <div className="flex items-center gap-1">
                  <Users className="w-3 h-3" />
                  <span>{deal.contact}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Calendar className="w-3 h-3" />
                  <span>{deal.closeDate}</span>
                </div>
                <span>via {deal.source}</span>
              </div>
            </div>

            <div className="text-right">
              <div className="text-lg font-bold text-green-400">{deal.value}</div>
              <div className="text-sm text-white/60">{deal.probability}% prob</div>
            </div>

            <div className="flex flex-col gap-2">
              <button className="p-2 rounded-lg bg-blue-500/20 text-blue-400 hover:bg-blue-500/30 transition-colors">
                <Eye className="w-4 h-4" />
              </button>
              <button className="p-2 rounded-lg bg-green-500/20 text-green-400 hover:bg-green-500/30 transition-colors">
                <Phone className="w-4 h-4" />
              </button>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  )
}

const SalesPerformance = () => {
  const performanceData = [
    { metric: 'Monthly Revenue', current: '$450K', target: '$500K', progress: 90 },
    { metric: 'New Customers', current: '28', target: '35', progress: 80 },
    { metric: 'Deal Velocity', current: '32 days', target: '28 days', progress: 75 },
    { metric: 'Win Rate', current: '18%', target: '22%', progress: 82 }
  ]

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-black/40 backdrop-blur-lg border border-white/10 rounded-2xl p-6"
    >
      <div className="flex items-center gap-3 mb-6">
        <BarChart3 className="w-6 h-6 text-blue-400" />
        <h3 className="text-xl font-bold text-white">Performance vs Target</h3>
      </div>

      <div className="space-y-4">
        {performanceData.map((item, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className="space-y-2"
          >
            <div className="flex justify-between items-center">
              <span className="text-white font-medium">{item.metric}</span>
              <div className="text-right">
                <span className="text-white font-semibold">{item.current}</span>
                <span className="text-white/60 text-sm ml-2">/ {item.target}</span>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="flex-1 bg-white/10 rounded-full h-2">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${item.progress}%` }}
                  transition={{ duration: 1, delay: index * 0.1 }}
                  className={`h-full rounded-full ${item.progress >= 90 ? 'bg-gradient-to-r from-green-500 to-emerald-500' :
                      item.progress >= 75 ? 'bg-gradient-to-r from-blue-500 to-purple-500' :
                        'bg-gradient-to-r from-amber-500 to-orange-500'
                    }`}
                />
              </div>
              <span className={`text-sm font-semibold ${item.progress >= 90 ? 'text-green-400' :
                  item.progress >= 75 ? 'text-blue-400' :
                    'text-amber-400'
                }`}>
                {item.progress}%
              </span>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  )
}

const RevenueChart = () => {
  const monthlyData = [
    { month: 'Jan', revenue: 320000, target: 350000 },
    { month: 'Feb', revenue: 385000, target: 400000 },
    { month: 'Mar', revenue: 450000, target: 500000 },
    { month: 'Apr', revenue: 420000, target: 480000 },
    { month: 'May', revenue: 510000, target: 550000 },
    { month: 'Jun', revenue: 580000, target: 600000 }
  ]

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="bg-black/40 backdrop-blur-lg border border-white/10 rounded-2xl p-6"
    >
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <TrendingUp className="w-6 h-6 text-green-400" />
          <h3 className="text-xl font-bold text-white">Revenue Trend</h3>
        </div>
        <div className="flex items-center gap-4 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-green-500 rounded-full" />
            <span className="text-white/70">Actual</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-blue-500 rounded-full" />
            <span className="text-white/70">Target</span>
          </div>
        </div>
      </div>

      <div className="h-64 flex items-end justify-between gap-4">
        {monthlyData.map((data, index) => (
          <motion.div
            key={data.month}
            initial={{ height: 0 }}
            animate={{ height: 'auto' }}
            transition={{ duration: 1, delay: index * 0.1 }}
            className="flex-1 flex flex-col items-center gap-2"
          >
            <div className="flex flex-col gap-1 items-center w-full">
              {/* Target bar (background) */}
              <div className="w-full bg-blue-500/20 rounded-t-lg relative" style={{ height: `${(data.target / 600000) * 200}px` }}>
                {/* Actual revenue bar */}
                <motion.div
                  initial={{ height: 0 }}
                  animate={{ height: `${(data.revenue / data.target) * 100}%` }}
                  transition={{ duration: 1, delay: index * 0.1 + 0.5 }}
                  className="w-full bg-gradient-to-t from-green-500 to-emerald-400 rounded-t-lg absolute bottom-0"
                />
              </div>
            </div>

            <div className="text-center">
              <p className="text-white/70 text-xs font-medium">{data.month}</p>
              <p className="text-green-400 text-xs font-semibold">${(data.revenue / 1000)}K</p>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  )
}

export default function SalesDashboard() {
  return (
    <div className="min-h-screen bg-[rgb(5,5,5)] relative overflow-hidden">
      {/* Background pattern */}
      <div
        className="absolute inset-0 opacity-20"
        style={{
          backgroundImage: 'radial-gradient(circle, rgba(34,197,94,0.3) 1px, transparent 1px)',
          backgroundSize: '28px 28px'
        }}
      />

      <div className="relative z-10 p-6 space-y-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center"
        >
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="p-3 rounded-2xl bg-gradient-to-r from-green-500/20 to-emerald-500/20">
              <DollarSign className="w-8 h-8 text-green-400" />
            </div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-green-400 to-emerald-400 
                           bg-clip-text text-transparent">
              Sales Dashboard
            </h1>
          </div>
          <p className="text-white/60 text-lg">
            Track revenue, conversions, and performance across products
          </p>
        </motion.div>

        {/* Dashboard Navigation */}
        <DashboardNavigation />

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <SalesMetricCard
            title="Monthly Revenue"
            value="$450K"
            change="+16.8%"
            trend="up"
            icon={DollarSign}
            color="green"
            subtitle="$50K above last month"
          />
          <SalesMetricCard
            title="New Deals"
            value="28"
            change="+22%"
            trend="up"
            icon={Target}
            color="blue"
            subtitle="7 closing this week"
          />
          <SalesMetricCard
            title="Conversion Rate"
            value="18%"
            change="+2.4%"
            trend="up"
            icon={TrendingUp}
            color="purple"
            subtitle="Above industry average"
          />
          <SalesMetricCard
            title="Pipeline Value"
            value="$1.67M"
            change="+12%"
            trend="up"
            icon={BarChart3}
            color="amber"
            subtitle="111 active opportunities"
          />
        </div>

        {/* Charts and Analytics */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <RevenueChart />
          <SalesPerformance />
        </div>

        {/* Pipeline and Deals */}
        <SalesPipeline />

        {/* Recent Activity */}
        <RecentDeals />
      </div>
    </div>
  )
}