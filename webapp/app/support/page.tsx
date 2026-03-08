'use client'

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Headphones,
  Clock,
  Users,
  CheckCircle,
  AlertCircle,
  XCircle,
  TrendingUp,
  TrendingDown,
  MessageSquare,
  Star,
  Filter,
  Search,
  Plus,
  MoreHorizontal,
  User,
  Calendar
} from 'lucide-react'
import DashboardNavigation from '@/components/DashboardNavigation'

interface SupportCardProps { title: string; value: string; change?: string; trend?: 'up' | 'down'; icon: React.ElementType; color?: 'blue' | 'green' | 'red' | 'amber'; }
const SupportMetricCard = ({ title, value, change, trend, icon: Icon, color = "blue" }: SupportCardProps) => (
  <motion.div
    initial={{ opacity: 0, scale: 0.95 }}
    animate={{ opacity: 1, scale: 1 }}
    className="bg-black/40 backdrop-blur-lg border border-white/10 rounded-2xl p-6 
               hover:border-white/20 transition-all duration-300 group"
  >
    <div className="flex items-start justify-between mb-4">
      <div className={`p-3 rounded-xl bg-gradient-to-r ${color === 'green' ? 'from-green-500/20 to-emerald-500/20' :
          color === 'red' ? 'from-red-500/20 to-pink-500/20' :
            color === 'amber' ? 'from-amber-500/20 to-orange-500/20' :
              'from-blue-500/20 to-purple-500/20'
        }`}>
        <Icon className={`w-6 h-6 ${color === 'green' ? 'text-green-400' :
            color === 'red' ? 'text-red-400' :
              color === 'amber' ? 'text-amber-400' :
                'text-blue-400'
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
  </motion.div>
)

const TicketList = () => {
  const [activeTab, setActiveTab] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')

  const tickets = [
    {
      id: 'T-001',
      title: 'AI System Performance Issues',
      customer: 'TechCorp Industries',
      priority: 'High',
      status: 'In Progress',
      assignee: 'Sarah Chen',
      created: '2 hours ago',
      category: 'Technical'
    },
    {
      id: 'T-002',
      title: 'Compliance Report Generation Error',
      customer: 'Global Dynamics',
      priority: 'Medium',
      status: 'New',
      assignee: 'Unassigned',
      created: '4 hours ago',
      category: 'Bug'
    },
    {
      id: 'T-003',
      title: 'Feature Request: Custom Dashboard',
      customer: 'Innovation Systems',
      priority: 'Low',
      status: 'Under Review',
      assignee: 'Mike Johnson',
      created: '1 day ago',
      category: 'Feature Request'
    },
    {
      id: 'T-004',
      title: 'Login Issues for Multiple Users',
      customer: 'DataFlow Corp',
      priority: 'High',
      status: 'Resolved',
      assignee: 'Emily Rodriguez',
      created: '2 days ago',
      category: 'Technical'
    },
    {
      id: 'T-005',
      title: 'Billing Inquiry - Contract Terms',
      customer: 'AI Solutions Inc',
      priority: 'Medium',
      status: 'Pending',
      assignee: 'David Kim',
      created: '3 days ago',
      category: 'Billing'
    }
  ]

  const tabs = [
    { id: 'all', label: 'All Tickets', count: tickets.length },
    { id: 'new', label: 'New', count: tickets.filter(t => t.status === 'New').length },
    { id: 'progress', label: 'In Progress', count: tickets.filter(t => t.status === 'In Progress').length },
    { id: 'resolved', label: 'Resolved', count: tickets.filter(t => t.status === 'Resolved').length }
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'New': return 'bg-blue-500/20 text-blue-400 border-blue-500/30'
      case 'In Progress': return 'bg-amber-500/20 text-amber-400 border-amber-500/30'
      case 'Under Review': return 'bg-purple-500/20 text-purple-400 border-purple-500/30'
      case 'Resolved': return 'bg-green-500/20 text-green-400 border-green-500/30'
      case 'Pending': return 'bg-gray-500/20 text-gray-400 border-gray-500/30'
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30'
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'High': return 'text-red-400'
      case 'Medium': return 'text-amber-400'
      case 'Low': return 'text-green-400'
      default: return 'text-gray-400'
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-black/40 backdrop-blur-lg border border-white/10 rounded-2xl p-6"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <MessageSquare className="w-6 h-6 text-blue-400" />
          <h3 className="text-2xl font-bold text-white">Support Tickets</h3>
        </div>

        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="w-4 h-4 text-white/50 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search tickets..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-white/10 border border-white/20 rounded-xl pl-10 pr-4 py-2 text-white 
                       placeholder-white/50 focus:outline-none focus:border-blue-400/50 text-sm"
            />
          </div>

          <button className="flex items-center gap-2 bg-white/10 border border-white/20 rounded-xl px-3 py-2 
                           text-white hover:bg-white/20 transition-colors text-sm">
            <Filter className="w-4 h-4" />
            Filter
          </button>

          <button className="flex items-center gap-2 bg-gradient-to-r from-blue-600 to-purple-600 
                           rounded-xl px-4 py-2 text-white hover:shadow-lg hover:shadow-blue-500/25 
                           transition-all duration-300 text-sm font-medium">
            <Plus className="w-4 h-4" />
            New Ticket
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-1 mb-6 bg-white/5 rounded-xl p-1">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all duration-200 text-sm ${activeTab === tab.id
                ? 'bg-blue-500/20 text-blue-400 font-medium'
                : 'text-white/70 hover:text-white hover:bg-white/10'
              }`}
          >
            {tab.label}
            <span className="bg-white/20 px-2 py-0.5 rounded-full text-xs">
              {tab.count}
            </span>
          </button>
        ))}
      </div>

      {/* Tickets Table */}
      <div className="space-y-3">
        {tickets.map((ticket, index) => (
          <motion.div
            key={ticket.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className="flex items-center gap-4 p-4 rounded-xl hover:bg-white/5 transition-colors border border-white/5"
          >
            {/* Priority Indicator */}
            <div className={`w-3 h-3 rounded-full ${ticket.priority === 'High' ? 'bg-red-500' :
                ticket.priority === 'Medium' ? 'bg-amber-500' :
                  'bg-green-500'
              }`} />

            {/* Ticket Info */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-3 mb-1">
                <span className="text-white/50 text-sm font-mono">{ticket.id}</span>
                <h4 className="text-white font-medium">{ticket.title}</h4>
              </div>
              <div className="flex items-center gap-4 text-sm text-white/60">
                <span>{ticket.customer}</span>
                <span>•</span>
                <span>{ticket.category}</span>
                <span>•</span>
                <span>{ticket.created}</span>
              </div>
            </div>

            {/* Status */}
            <div className={`px-3 py-1 rounded-lg text-xs font-medium border ${getStatusColor(ticket.status)}`}>
              {ticket.status}
            </div>

            {/* Priority */}
            <div className={`text-sm font-medium ${getPriorityColor(ticket.priority)}`}>
              {ticket.priority}
            </div>

            {/* Assignee */}
            <div className="flex items-center gap-2 min-w-0">
              <User className="w-4 h-4 text-white/50" />
              <span className="text-white/70 text-sm truncate">{ticket.assignee}</span>
            </div>

            {/* Actions */}
            <button className="p-2 rounded-lg hover:bg-white/10 transition-colors">
              <MoreHorizontal className="w-4 h-4 text-white/50" />
            </button>
          </motion.div>
        ))}
      </div>
    </motion.div>
  )
}

const CustomerSatisfaction = () => {
  const satisfactionData = [
    { rating: 5, count: 45, percentage: 60 },
    { rating: 4, count: 20, percentage: 27 },
    { rating: 3, count: 8, percentage: 11 },
    { rating: 2, count: 2, percentage: 2 },
    { rating: 1, count: 0, percentage: 0 }
  ]

  const totalRatings = satisfactionData.reduce((sum, item) => sum + item.count, 0)
  const averageRating = satisfactionData.reduce((sum, item) => sum + (item.rating * item.count), 0) / totalRatings

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="bg-black/40 backdrop-blur-lg border border-white/10 rounded-2xl p-6"
    >
      <div className="flex items-center gap-3 mb-6">
        <Star className="w-6 h-6 text-amber-400" />
        <h3 className="text-xl font-bold text-white">Customer Satisfaction</h3>
      </div>

      <div className="text-center mb-6">
        <div className="text-4xl font-bold text-white mb-2">{averageRating.toFixed(1)}</div>
        <div className="flex items-center justify-center gap-1 mb-2">
          {[1, 2, 3, 4, 5].map((star) => (
            <Star
              key={star}
              className={`w-5 h-5 ${star <= Math.round(averageRating) ? 'text-amber-400 fill-current' : 'text-white/20'
                }`}
            />
          ))}
        </div>
        <p className="text-white/60 text-sm">Based on {totalRatings} reviews</p>
      </div>

      <div className="space-y-3">
        {satisfactionData.map((item, index) => (
          <motion.div
            key={item.rating}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className="flex items-center gap-3"
          >
            <div className="flex items-center gap-1">
              <span className="text-white/70 text-sm">{item.rating}</span>
              <Star className="w-3 h-3 text-amber-400 fill-current" />
            </div>

            <div className="flex-1 bg-white/10 rounded-full h-2">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${item.percentage}%` }}
                transition={{ duration: 1, delay: index * 0.1 }}
                className="h-full bg-gradient-to-r from-amber-500 to-orange-500 rounded-full"
              />
            </div>

            <span className="text-white/60 text-sm w-8">{item.count}</span>
          </motion.div>
        ))}
      </div>
    </motion.div>
  )
}

export default function SupportDashboard() {
  return (
    <div className="min-h-screen bg-[rgb(5,5,5)] relative overflow-hidden">
      {/* Background pattern */}
      <div
        className="absolute inset-0 opacity-20"
        style={{
          backgroundImage: 'radial-gradient(circle, rgba(34,197,94,0.3) 1px, transparent 1px)',
          backgroundSize: '24px 24px'
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
              <Headphones className="w-8 h-8 text-green-400" />
            </div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-green-400 to-emerald-400 
                           bg-clip-text text-transparent">
              Support Dashboard
            </h1>
          </div>
          <p className="text-white/60 text-lg">
            Track support volume, response times, and customer satisfaction
          </p>
        </motion.div>

        {/* Dashboard Navigation */}
        <DashboardNavigation />

        {/* Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <SupportMetricCard
            title="Open Tickets"
            value="23"
            change="-12%"
            trend="down"
            icon={MessageSquare}
            color="blue"
          />
          <SupportMetricCard
            title="Avg Response Time"
            value="2.4h"
            change="-25%"
            trend="down"
            icon={Clock}
            color="green"
          />
          <SupportMetricCard
            title="Customer Satisfaction"
            value="4.6"
            change="+8%"
            trend="up"
            icon={Star}
            color="amber"
          />
          <SupportMetricCard
            title="Resolution Rate"
            value="94%"
            change="+3%"
            trend="up"
            icon={CheckCircle}
            color="green"
          />
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          <div className="lg:col-span-3">
            <TicketList />
          </div>
          <div className="space-y-6">
            <CustomerSatisfaction />

            {/* Quick Stats */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-black/40 backdrop-blur-lg border border-white/10 rounded-2xl p-6"
            >
              <h3 className="text-lg font-bold text-white mb-4">Quick Stats</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-white/70">Today's Tickets</span>
                  <span className="text-blue-400 font-semibold">8</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/70">Resolved Today</span>
                  <span className="text-green-400 font-semibold">12</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/70">Escalated</span>
                  <span className="text-red-400 font-semibold">2</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/70">First Response SLA</span>
                  <span className="text-green-400 font-semibold">96%</span>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  )
}