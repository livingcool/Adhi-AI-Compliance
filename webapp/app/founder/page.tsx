'use client'

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Crown,
  DollarSign,
  Users,
  Building2,
  TrendingUp,
  TrendingDown,
  FileText,
  Shield,
  AlertTriangle,
  Database,
  Target,
  Calendar,
  Eye,
  Lock,
  Zap,
  Globe,
  BarChart4,
  PieChart,
  Activity,
  Clock,
  Award,
  Download,
  Mail,
  Phone,
  MapPin
} from 'lucide-react'
import { FounderProtected } from '@/components/FounderProtected'
import DashboardNavigation from '@/components/DashboardNavigation'
import { GlassCard } from '@/components/ui/GlassCard'

interface FounderCardProps { title: string; value: string; change?: string; trend?: 'up' | 'down'; icon: React.ElementType; color?: 'blue' | 'green' | 'red' | 'amber' | 'purple'; sensitive?: boolean; }
const FounderMetricCard = ({ title, value, change, trend, icon: Icon, color = "blue", sensitive = false }: FounderCardProps) => (
  <GlassCard className="p-6 group relative overflow-hidden">
    {/* Sensitive data indicator */}
    {sensitive && (
      <div className="absolute top-3 right-3">
        <Lock className="w-4 h-4 text-amber-400" />
      </div>
    )}

    {/* Background gradient */}
    <div className={`absolute inset-0 bg-gradient-to-br ${color === 'green' ? 'from-green-500/20 to-emerald-500/20' :
      color === 'red' ? 'from-red-500/20 to-pink-500/20' :
        color === 'amber' ? 'from-amber-500/20 to-orange-500/20' :
          'from-blue-500/20 to-purple-500/20'
      } opacity-0 group-hover:opacity-100 transition-opacity duration-500`} />

    <div className="relative z-10">
      <div className="flex items-start justify-between mb-4">
        <div className={`p-3 rounded-2xl bg-gradient-to-r ${color === 'green' ? 'from-green-500/30 to-emerald-500/30' :
          color === 'red' ? 'from-red-500/30 to-pink-500/30' :
            color === 'amber' ? 'from-amber-500/30 to-orange-500/30' :
              'from-blue-500/30 to-purple-500/30'
          }`}>
          <Icon className={`w-6 h-6 ${color === 'green' ? 'text-green-400' :
            color === 'red' ? 'text-red-400' :
              color === 'amber' ? 'text-amber-400' :
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

const ClientPortfolio = () => {
  const clients = [
    { name: 'TechCorp Industries', contract: '$180,000', status: 'Active', renewal: '2024-06-15', risk: 'Low' },
    { name: 'Global Dynamics Ltd', contract: '$145,000', status: 'Active', renewal: '2024-08-22', risk: 'Medium' },
    { name: 'Innovation Systems', contract: '$120,000', status: 'Active', renewal: '2024-04-10', risk: 'Low' },
    { name: 'DataFlow Corp', contract: '$95,000', status: 'Negotiating', renewal: '2024-05-30', risk: 'High' },
    { name: 'AI Solutions Inc', contract: '$85,000', status: 'Active', renewal: '2024-07-18', risk: 'Low' },
    { name: 'CloudTech Systems', contract: '$75,000', status: 'Pending', renewal: '2024-09-05', risk: 'Medium' }
  ]

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active': return 'text-green-400 bg-green-500/20'
      case 'negotiating': return 'text-amber-400 bg-amber-500/20'
      case 'pending': return 'text-blue-400 bg-blue-500/20'
      default: return 'text-gray-400 bg-gray-500/20'
    }
  }

  const getRiskColor = (risk: string) => {
    switch (risk.toLowerCase()) {
      case 'low': return 'text-green-400'
      case 'medium': return 'text-amber-400'
      case 'high': return 'text-red-400'
      default: return 'text-gray-400'
    }
  }

  return (
    <GlassCard className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Building2 className="w-6 h-6 text-blue-400" />
          <h3 className="text-2xl font-bold text-white">Client Portfolio</h3>
          <Lock className="w-4 h-4 text-amber-400" />
        </div>
        <div className="text-right">
          <p className="text-2xl font-bold text-white">$700K</p>
          <p className="text-white/60 text-sm">Total Value</p>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-white/10">
              <th className="text-left py-3 px-2 text-white/70 font-medium">Client</th>
              <th className="text-right py-3 px-2 text-white/70 font-medium">Contract Value</th>
              <th className="text-center py-3 px-2 text-white/70 font-medium">Status</th>
              <th className="text-center py-3 px-2 text-white/70 font-medium">Renewal</th>
              <th className="text-center py-3 px-2 text-white/70 font-medium">Risk</th>
            </tr>
          </thead>
          <tbody>
            {clients.map((client, index) => (
              <motion.tr
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="border-b border-white/5 hover:bg-white/5 transition-colors"
              >
                <td className="py-4 px-2">
                  <span className="text-white font-medium">{client.name}</span>
                </td>
                <td className="py-4 px-2 text-right">
                  <span className="text-green-400 font-semibold">{client.contract}</span>
                </td>
                <td className="py-4 px-2 text-center">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(client.status)}`}>
                    {client.status}
                  </span>
                </td>
                <td className="py-4 px-2 text-center text-white/70 text-sm">
                  {client.renewal}
                </td>
                <td className="py-4 px-2 text-center">
                  <span className={`text-sm font-medium ${getRiskColor(client.risk)}`}>
                    {client.risk}
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

const FinancialBreakdown = () => {
  const financialData = {
    revenue: {
      q4_2024: 450000,
      q1_2025_projected: 620000,
      growth_rate: 38,
      recurring: 65
    },
    expenses: {
      personnel: 180000,
      infrastructure: 45000,
      marketing: 25000,
      operations: 30000
    },
    profitability: {
      gross_margin: 72,
      net_margin: 31,
      ebitda: 285000
    }
  }

  return (
    <GlassCard className="p-6">
      <div className="flex items-center gap-3 mb-6">
        <DollarSign className="w-6 h-6 text-green-400" />
        <h3 className="text-2xl font-bold text-white">Financial Overview</h3>
        <Lock className="w-4 h-4 text-amber-400" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Revenue */}
        <div className="space-y-4">
          <h4 className="text-lg font-semibold text-white">Revenue</h4>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-white/70">Q4 2024 Actual</span>
              <span className="text-green-400 font-semibold">${(financialData.revenue.q4_2024 / 1000).toFixed(0)}K</span>
            </div>
            <div className="flex justify-between">
              <span className="text-white/70">Q1 2025 Projected</span>
              <span className="text-blue-400 font-semibold">${(financialData.revenue.q1_2025_projected / 1000).toFixed(0)}K</span>
            </div>
            <div className="flex justify-between">
              <span className="text-white/70">Growth Rate</span>
              <span className="text-green-400 font-semibold">+{financialData.revenue.growth_rate}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-white/70">Recurring Revenue</span>
              <span className="text-green-400 font-semibold">{financialData.revenue.recurring}%</span>
            </div>
          </div>
        </div>

        {/* Expenses */}
        <div className="space-y-4">
          <h4 className="text-lg font-semibold text-white">Expenses</h4>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-white/70">Personnel</span>
              <span className="text-red-400 font-semibold">${(financialData.expenses.personnel / 1000).toFixed(0)}K</span>
            </div>
            <div className="flex justify-between">
              <span className="text-white/70">Infrastructure</span>
              <span className="text-amber-400 font-semibold">${(financialData.expenses.infrastructure / 1000).toFixed(0)}K</span>
            </div>
            <div className="flex justify-between">
              <span className="text-white/70">Marketing</span>
              <span className="text-purple-400 font-semibold">${(financialData.expenses.marketing / 1000).toFixed(0)}K</span>
            </div>
            <div className="flex justify-between">
              <span className="text-white/70">Operations</span>
              <span className="text-blue-400 font-semibold">${(financialData.expenses.operations / 1000).toFixed(0)}K</span>
            </div>
          </div>
        </div>

        {/* Profitability */}
        <div className="space-y-4">
          <h4 className="text-lg font-semibold text-white">Profitability</h4>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-white/70">Gross Margin</span>
              <span className="text-green-400 font-semibold">{financialData.profitability.gross_margin}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-white/70">Net Margin</span>
              <span className="text-green-400 font-semibold">{financialData.profitability.net_margin}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-white/70">EBITDA</span>
              <span className="text-green-400 font-semibold">${(financialData.profitability.ebitda / 1000).toFixed(0)}K</span>
            </div>
            <div className="flex justify-between">
              <span className="text-white/70">Cash Flow</span>
              <span className="text-green-400 font-semibold">Positive</span>
            </div>
          </div>
        </div>
      </div>
    </GlassCard>
  )
}

const TeamAndOperations = () => {
  const teamData = [
    { name: 'Ganesh Khovalan', role: 'Founder & CEO', location: 'Hosur, India', status: 'Active' },
    { name: 'Senior AI Engineer', role: 'Technical Lead', location: 'Bangalore, India', status: 'Hiring' },
    { name: 'Compliance Manager', role: 'Operations', location: 'Chennai, India', status: 'Hiring' },
    { name: 'Sales Director', role: 'Business Development', location: 'Coimbatore, India', status: 'Planned' }
  ]

  const operations = {
    locations: ['Hosur', 'Coimbatore', 'Bangalore', 'Chennai'],
    infrastructure: {
      cloud_spend: 2400,
      ai_compute: 1800,
      security: 600,
      monitoring: 400
    },
    compliance: {
      certifications: ['ISO 27001 (Planned)', 'SOC 2 (In Progress)', 'GDPR Compliant'],
      audits: 2,
      last_security_review: '2024-02-15'
    }
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Team Structure */}
      <GlassCard className="p-6">
        <div className="flex items-center gap-3 mb-6">
          <Users className="w-6 h-6 text-purple-400" />
          <h3 className="text-2xl font-bold text-white">Team & Hiring</h3>
          <Lock className="w-4 h-4 text-amber-400" />
        </div>

        <div className="space-y-4">
          {teamData.map((member, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="flex items-center justify-between p-3 rounded-xl hover:bg-white/5 transition-colors"
            >
              <div>
                <p className="text-white font-medium">{member.name}</p>
                <p className="text-white/60 text-sm">{member.role}</p>
                <p className="text-white/50 text-xs flex items-center gap-1">
                  <MapPin className="w-3 h-3" />
                  {member.location}
                </p>
              </div>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${member.status === 'Active' ? 'bg-green-500/20 text-green-400' :
                member.status === 'Hiring' ? 'bg-blue-500/20 text-blue-400' :
                  'bg-amber-500/20 text-amber-400'
                }`}>
                {member.status}
              </span>
            </motion.div>
          ))}
        </div>
      </GlassCard>

      {/* Operations */}
      <GlassCard className="p-6">
        <div className="flex items-center gap-3 mb-6">
          <Activity className="w-6 h-6 text-amber-400" />
          <h3 className="text-2xl font-bold text-white">Operations</h3>
          <Lock className="w-4 h-4 text-amber-400" />
        </div>

        <div className="space-y-6">
          {/* Infrastructure Costs */}
          <div>
            <h4 className="text-white font-medium mb-3">Monthly Infrastructure</h4>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-white/70">Cloud Services</span>
                <span className="text-blue-400 font-medium">${operations.infrastructure.cloud_spend}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-white/70">AI Compute</span>
                <span className="text-purple-400 font-medium">${operations.infrastructure.ai_compute}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-white/70">Security & Compliance</span>
                <span className="text-green-400 font-medium">${operations.infrastructure.security}</span>
              </div>
            </div>
          </div>

          {/* Compliance Status */}
          <div>
            <h4 className="text-white font-medium mb-3">Compliance Status</h4>
            <div className="space-y-2">
              {operations.compliance.certifications.map((cert, index) => (
                <div key={index} className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="text-white/70 text-sm">{cert}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Locations */}
          <div>
            <h4 className="text-white font-medium mb-3">Office Locations</h4>
            <div className="grid grid-cols-2 gap-2">
              {operations.locations.map((location, index) => (
                <div key={index} className="flex items-center gap-2">
                  <MapPin className="w-3 h-3 text-blue-400" />
                  <span className="text-white/70 text-sm">{location}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </GlassCard>
    </div>
  )
}

const FounderDashboardContent = () => {
  return (
    <div className="space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center"
      >
        <div className="inline-flex items-center gap-3 mb-4">
          <div className="p-3 rounded-2xl bg-gradient-to-r from-amber-500/30 to-orange-500/30">
            <Crown className="w-8 h-8 text-amber-400" />
          </div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-amber-400 to-orange-400 bg-clip-text text-transparent">
            Founder Dashboard
          </h1>
        </div>
        <p className="text-white/70 text-lg">
          Complete organizational overview • Sensitive data • Founder access only
        </p>
        <p className="text-white/50 text-sm mt-2">
          Last updated: {new Date().toLocaleString()} • All data encrypted
        </p>
      </motion.div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <FounderMetricCard
          title="Total Revenue (Q4)"
          value="$450K"
          change="+38%"
          trend="up"
          icon={DollarSign}
          color="green"
          sensitive={true}
        />
        <FounderMetricCard
          title="Active Clients"
          value="6"
          change="+2"
          trend="up"
          icon={Building2}
          color="blue"
          sensitive={true}
        />
        <FounderMetricCard
          title="Contract Pipeline"
          value="$1.2M"
          change="+45%"
          trend="up"
          icon={Target}
          color="amber"
          sensitive={true}
        />
        <FounderMetricCard
          title="Team Size"
          value="1"
          change="+3 hiring"
          trend="up"
          icon={Users}
          color="purple"
          sensitive={true}
        />
      </div>

      {/* Financial Overview */}
      <FinancialBreakdown />

      {/* Client Portfolio */}
      <ClientPortfolio />

      {/* Team and Operations */}
      <TeamAndOperations />

      {/* Action Items */}
      <GlassCard className="p-8" delay={0.5}>
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3 mb-4">
              <AlertTriangle className="w-6 h-6 text-red-400" />
              <h3 className="text-2xl font-bold text-white">Priority Actions</h3>
            </div>
            <ul className="space-y-2 text-white/80">
              <li>• Hire Senior AI Engineer (Bangalore) - 2 candidates in final round</li>
              <li>• Complete SOC 2 certification - Target: March 2024</li>
              <li>• Renew DataFlow Corp contract - High priority ($95K at risk)</li>
              <li>• Expand Chennai office space - Team growth planning</li>
            </ul>
          </div>

          <div className="flex items-center gap-3">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 
                         rounded-xl font-medium hover:shadow-lg hover:shadow-blue-500/25 
                         transition-all duration-300 flex items-center gap-2"
            >
              <Download className="w-4 h-4" />
              Export Report
            </motion.button>
          </div>
        </div>
      </GlassCard>
    </div>
  )
}

export default function FounderDashboard() {
  return (
    <div className="min-h-screen relative overflow-hidden">

      <div className="relative z-10 p-6 space-y-8">
        {/* Dashboard Navigation */}
        <DashboardNavigation />

        {/* Protected Content */}
        <FounderProtected
          title="Founder Dashboard Access"
          description="This dashboard contains the complete organizational overview including financial data, client information, team details, and strategic business metrics. Access restricted to founder only."
          requiresAuth={true}
          showPreview={true}
        >
          <FounderDashboardContent />
        </FounderProtected>
      </div>
    </div>
  )
}