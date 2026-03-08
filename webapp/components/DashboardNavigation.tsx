'use client'

import React from 'react'
import { motion } from 'framer-motion'
import { usePathname, useRouter } from 'next/navigation'
import { 
  LayoutDashboard, 
  BarChart4, 
  Crown, 
  Activity, 
  TrendingUp,
  Eye,
  Zap,
  Shield
} from 'lucide-react'
import { useFounderAuth } from '@/lib/founder-auth'

const dashboards = [
  {
    id: 'main',
    name: 'Overview',
    description: 'Main compliance dashboard',
    icon: LayoutDashboard,
    href: '/',
    color: 'from-blue-500 to-purple-500'
  },
  {
    id: 'analytics',
    name: 'Advanced Analytics',
    description: 'Deep insights & compliance heatmaps',
    icon: BarChart4,
    href: '/analytics',
    color: 'from-purple-500 to-pink-500'
  },
  {
    id: 'executive',
    name: 'Executive Dashboard',
    description: 'Strategic overview for leadership',
    icon: Crown,
    href: '/executive',
    color: 'from-amber-500 to-orange-500'
  },
  {
    id: 'monitoring',
    name: 'Real-Time Monitoring',
    description: 'Live system health & performance',
    icon: Activity,
    href: '/monitoring',
    color: 'from-green-500 to-emerald-500'
  },
  {
    id: 'founder',
    name: 'Founder Dashboard',
    description: 'Complete organizational overview',
    icon: Shield,
    href: '/founder',
    color: 'from-amber-600 to-red-500',
    protected: true
  }
]

export default function DashboardNavigation() {
  const pathname = usePathname()
  const router = useRouter()
  const { isAuthenticated: isFounderAuth } = useFounderAuth()

  // Filter dashboards based on founder authentication
  const availableDashboards = dashboards.filter(dashboard => 
    !dashboard.protected || isFounderAuth
  )

  return (
    <div className="bg-black/40 backdrop-blur-lg border border-white/10 rounded-2xl p-6 mb-8">
      <div className="flex items-center gap-3 mb-6">
        <Zap className="w-6 h-6 text-blue-400" />
        <h2 className="text-xl font-bold text-white">Dashboard Hub</h2>
        {isFounderAuth && (
          <div className="bg-gradient-to-r from-amber-500/20 to-orange-500/20 px-3 py-1 rounded-full">
            <span className="text-amber-400 text-xs font-medium">Founder Access</span>
          </div>
        )}
        <div className="ml-auto text-sm text-white/60">
          Switch between different views
        </div>
      </div>
      
      <div className={`grid grid-cols-1 sm:grid-cols-2 gap-4 ${
        availableDashboards.length >= 4 ? 'lg:grid-cols-4' : 
        availableDashboards.length === 5 ? 'lg:grid-cols-5' : 'lg:grid-cols-3'
      }`}>
        {availableDashboards.map((dashboard) => {
          const isActive = pathname === dashboard.href
          const Icon = dashboard.icon
          
          return (
            <motion.button
              key={dashboard.id}
              onClick={() => router.push(dashboard.href)}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className={`p-4 rounded-xl border transition-all duration-300 text-left relative ${
                isActive
                  ? 'bg-gradient-to-br from-white/10 to-white/5 border-white/30 shadow-lg'
                  : 'bg-white/5 border-white/10 hover:border-white/20 hover:bg-white/10'
              } ${dashboard.protected ? 'ring-1 ring-amber-500/30' : ''}`}
            >
              {dashboard.protected && (
                <div className="absolute top-2 right-2">
                  <Shield className="w-3 h-3 text-amber-400" />
                </div>
              )}
              
              <div className="flex items-center gap-3 mb-3">
                <div className={`p-2 rounded-lg bg-gradient-to-r ${dashboard.color}/20`}>
                  <Icon className={`w-5 h-5 bg-gradient-to-r ${dashboard.color} bg-clip-text text-transparent`} 
                        style={{ filter: 'brightness(1.5)' }} />
                </div>
                {isActive && (
                  <motion.div
                    layoutId="activeIndicator"
                    className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"
                  />
                )}
              </div>
              
              <h3 className={`font-semibold mb-1 ${
                isActive ? 'text-white' : 'text-white/80'
              }`}>
                {dashboard.name}
              </h3>
              
              <p className={`text-sm ${
                isActive ? 'text-white/70' : 'text-white/60'
              }`}>
                {dashboard.description}
              </p>
            </motion.button>
          )
        })}
      </div>
      
      {/* Show message if founder dashboard is available but not visible */}
      {!isFounderAuth && (
        <div className="mt-4 p-3 rounded-xl bg-amber-500/10 border border-amber-500/20">
          <div className="flex items-center gap-2 text-amber-400 text-sm">
            <Shield className="w-4 h-4" />
            <span>Founder Dashboard available with authentication</span>
          </div>
        </div>
      )}
    </div>
  )
}