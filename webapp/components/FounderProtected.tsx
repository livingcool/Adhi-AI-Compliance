'use client'

import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Shield, Crown, Lock, Database, Users, FileText, AlertTriangle } from 'lucide-react'
import { useFounderAuth, FounderLoginModal } from '@/lib/founder-auth'

interface FounderProtectedProps {
  children: React.ReactNode
  title?: string
  description?: string
  requiresAuth?: boolean
  showPreview?: boolean
  fallbackContent?: React.ReactNode
}

const SensitiveDataPreview: React.FC = () => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Sensitive data cards - blurred for preview */}
        <div className="bg-black/40 backdrop-blur-lg border border-white/10 rounded-2xl p-4 relative overflow-hidden">
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm z-10 flex items-center justify-center">
            <Lock className="w-8 h-8 text-amber-400" />
          </div>
          <div className="blur-sm">
            <div className="flex items-center gap-3 mb-3">
              <Database className="w-5 h-5 text-blue-400" />
              <span className="text-white font-medium">Financial Data</span>
            </div>
            <div className="text-2xl font-bold text-white">$2.4M</div>
            <div className="text-sm text-white/60">Revenue Pipeline</div>
          </div>
        </div>

        <div className="bg-black/40 backdrop-blur-lg border border-white/10 rounded-2xl p-4 relative overflow-hidden">
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm z-10 flex items-center justify-center">
            <Lock className="w-8 h-8 text-amber-400" />
          </div>
          <div className="blur-sm">
            <div className="flex items-center gap-3 mb-3">
              <Users className="w-5 h-5 text-green-400" />
              <span className="text-white font-medium">Client Data</span>
            </div>
            <div className="text-2xl font-bold text-white">47</div>
            <div className="text-sm text-white/60">Enterprise Clients</div>
          </div>
        </div>

        <div className="bg-black/40 backdrop-blur-lg border border-white/10 rounded-2xl p-4 relative overflow-hidden">
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm z-10 flex items-center justify-center">
            <Lock className="w-8 h-8 text-amber-400" />
          </div>
          <div className="blur-sm">
            <div className="flex items-center gap-3 mb-3">
              <FileText className="w-5 h-5 text-purple-400" />
              <span className="text-white font-medium">Contracts</span>
            </div>
            <div className="text-2xl font-bold text-white">$850K</div>
            <div className="text-sm text-white/60">Active Contracts</div>
          </div>
        </div>

        <div className="bg-black/40 backdrop-blur-lg border border-white/10 rounded-2xl p-4 relative overflow-hidden">
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm z-10 flex items-center justify-center">
            <Lock className="w-8 h-8 text-amber-400" />
          </div>
          <div className="blur-sm">
            <div className="flex items-center gap-3 mb-3">
              <AlertTriangle className="w-5 h-5 text-red-400" />
              <span className="text-white font-medium">Risk Exposure</span>
            </div>
            <div className="text-2xl font-bold text-white">Medium</div>
            <div className="text-sm text-white/60">Overall Risk</div>
          </div>
        </div>
      </div>

      {/* Additional sensitive sections */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-black/40 backdrop-blur-lg border border-white/10 rounded-2xl p-6 relative overflow-hidden">
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm z-10 flex flex-col items-center justify-center gap-2">
            <Lock className="w-8 h-8 text-amber-400" />
            <span className="text-amber-400 text-sm font-medium">Sensitive Financial Data</span>
          </div>
          <div className="blur-sm">
            <h3 className="text-xl font-bold text-white mb-4">Revenue Analytics</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-white/70">Q4 2024 Revenue</span>
                <span className="text-green-400 font-medium">$450K</span>
              </div>
              <div className="flex justify-between">
                <span className="text-white/70">Projected Q1 2025</span>
                <span className="text-blue-400 font-medium">$620K</span>
              </div>
              <div className="flex justify-between">
                <span className="text-white/70">Annual Growth Rate</span>
                <span className="text-green-400 font-medium">+38%</span>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-black/40 backdrop-blur-lg border border-white/10 rounded-2xl p-6 relative overflow-hidden">
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm z-10 flex flex-col items-center justify-center gap-2">
            <Lock className="w-8 h-8 text-amber-400" />
            <span className="text-amber-400 text-sm font-medium">Confidential Client Information</span>
          </div>
          <div className="blur-sm">
            <h3 className="text-xl font-bold text-white mb-4">Top Clients</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-white/70">[REDACTED] Corp</span>
                <span className="text-green-400 font-medium">$180K</span>
              </div>
              <div className="flex justify-between">
                <span className="text-white/70">[REDACTED] Industries</span>
                <span className="text-blue-400 font-medium">$145K</span>
              </div>
              <div className="flex justify-between">
                <span className="text-white/70">[REDACTED] Systems</span>
                <span className="text-purple-400 font-medium">$120K</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  )
}

export const FounderProtected: React.FC<FounderProtectedProps> = ({
  children,
  title = "Founder Access Required",
  description = "This data contains sensitive organizational information accessible only to the founder.",
  requiresAuth = true,
  showPreview = true,
  fallbackContent
}) => {
  const { isAuthenticated } = useFounderAuth()
  const [showLoginModal, setShowLoginModal] = useState(false)

  // If auth not required, always show content
  if (!requiresAuth || isAuthenticated) {
    return <>{children}</>
  }

  // Show fallback content if provided
  if (fallbackContent) {
    return <>{fallbackContent}</>
  }

  return (
    <div className="space-y-8">
      {/* Access Required Notice */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-br from-amber-500/20 to-orange-500/20 backdrop-blur-lg 
                   border border-amber-500/30 rounded-3xl p-8 text-center"
      >
        <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl 
                        bg-gradient-to-r from-amber-500/30 to-orange-500/30 mb-6">
          <Crown className="w-10 h-10 text-amber-400" />
        </div>
        
        <h2 className="text-3xl font-bold bg-gradient-to-r from-amber-400 to-orange-400 
                       bg-clip-text text-transparent mb-4">
          {title}
        </h2>
        
        <p className="text-white/70 text-lg leading-relaxed mb-8 max-w-2xl mx-auto">
          {description}
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setShowLoginModal(true)}
            className="bg-gradient-to-r from-amber-600 to-orange-600 text-white px-8 py-4 
                       rounded-xl font-medium hover:shadow-lg hover:shadow-amber-500/25 
                       transition-all duration-300 flex items-center justify-center gap-2"
          >
            <Shield className="w-5 h-5" />
            Access Founder Data
          </motion.button>
          
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => window.location.href = '/'}
            className="bg-white/10 border border-white/20 text-white px-8 py-4 
                       rounded-xl font-medium hover:bg-white/20 transition-all duration-300"
          >
            Return to Dashboard
          </motion.button>
        </div>
        
        {/* Security Information */}
        <div className="mt-8 p-4 rounded-xl bg-blue-500/10 border border-blue-500/20 max-w-md mx-auto">
          <div className="flex items-center gap-2 text-blue-400 text-sm">
            <Shield className="w-4 h-4" />
            <span>Protected by enterprise-grade security • Session timeout: 4 hours</span>
          </div>
        </div>
      </motion.div>

      {/* Preview of sensitive data (blurred) */}
      {showPreview && (
        <div className="space-y-6">
          <div className="flex items-center gap-3">
            <Lock className="w-5 h-5 text-amber-400" />
            <h3 className="text-xl font-bold text-white">Protected Data Preview</h3>
            <span className="text-white/60 text-sm">(Authentication required to view)</span>
          </div>
          
          <SensitiveDataPreview />
        </div>
      )}

      {/* Login Modal */}
      <FounderLoginModal
        isOpen={showLoginModal}
        onClose={() => setShowLoginModal(false)}
        title={title}
        description={description}
      />
    </div>
  )
}