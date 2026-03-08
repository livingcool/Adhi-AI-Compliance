'use client'

import React, { createContext, useContext, useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Eye, EyeOff, Shield, Lock, Crown } from 'lucide-react'

// Founder authentication configuration
const FOUNDER_PASSWORD = 'G22a05n@03'
const SESSION_KEY = 'adhi_founder_session'
const SESSION_DURATION = 4 * 60 * 60 * 1000 // 4 hours

interface FounderAuthContextType {
  isAuthenticated: boolean
  login: (password: string) => boolean
  logout: () => void
  timeRemaining: number
}

const FounderAuthContext = createContext<FounderAuthContextType | null>(null)

export const useFounderAuth = () => {
  const context = useContext(FounderAuthContext)
  if (!context) {
    throw new Error('useFounderAuth must be used within FounderAuthProvider')
  }
  return context
}

interface FounderSession {
  timestamp: number
  expiresAt: number
}

export const FounderAuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [timeRemaining, setTimeRemaining] = useState(0)

  // Check existing session on mount
  useEffect(() => {
    const savedSession = localStorage.getItem(SESSION_KEY)
    if (savedSession) {
      try {
        const session: FounderSession = JSON.parse(savedSession)
        const now = Date.now()
        
        if (now < session.expiresAt) {
          setIsAuthenticated(true)
          setTimeRemaining(Math.max(0, session.expiresAt - now))
        } else {
          // Session expired
          localStorage.removeItem(SESSION_KEY)
        }
      } catch (error) {
        localStorage.removeItem(SESSION_KEY)
      }
    }
  }, [])

  // Update time remaining every second
  useEffect(() => {
    if (!isAuthenticated) return

    const interval = setInterval(() => {
      const savedSession = localStorage.getItem(SESSION_KEY)
      if (savedSession) {
        try {
          const session: FounderSession = JSON.parse(savedSession)
          const now = Date.now()
          const remaining = Math.max(0, session.expiresAt - now)
          
          if (remaining > 0) {
            setTimeRemaining(remaining)
          } else {
            // Session expired
            logout()
          }
        } catch (error) {
          logout()
        }
      }
    }, 1000)

    return () => clearInterval(interval)
  }, [isAuthenticated])

  const login = (password: string): boolean => {
    if (password === FOUNDER_PASSWORD) {
      const now = Date.now()
      const session: FounderSession = {
        timestamp: now,
        expiresAt: now + SESSION_DURATION
      }
      
      localStorage.setItem(SESSION_KEY, JSON.stringify(session))
      setIsAuthenticated(true)
      setTimeRemaining(SESSION_DURATION)
      
      return true
    }
    return false
  }

  const logout = () => {
    localStorage.removeItem(SESSION_KEY)
    setIsAuthenticated(false)
    setTimeRemaining(0)
  }

  return (
    <FounderAuthContext.Provider value={{ isAuthenticated, login, logout, timeRemaining }}>
      {children}
    </FounderAuthContext.Provider>
  )
}

// Founder Login Modal Component
interface FounderLoginModalProps {
  isOpen: boolean
  onClose?: () => void
  title?: string
  description?: string
}

export const FounderLoginModal: React.FC<FounderLoginModalProps> = ({ 
  isOpen, 
  onClose,
  title = "Founder Access Required",
  description = "This section contains sensitive organizational data accessible only to the founder."
}) => {
  const { login } = useFounderAuth()
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')

    // Simulate network delay for security
    await new Promise(resolve => setTimeout(resolve, 1500))

    const success = login(password)
    if (success) {
      setPassword('')
      onClose?.()
    } else {
      setError('Invalid founder password. Access denied.')
      // Clear password on error
      setPassword('')
    }
    
    setIsLoading(false)
  }

  const handleClose = () => {
    setPassword('')
    setError('')
    onClose?.()
  }

  if (!isOpen) return null

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4"
        onClick={handleClose}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          onClick={(e) => e.stopPropagation()}
          className="bg-gradient-to-br from-black/90 to-black/70 backdrop-blur-xl border border-white/20 
                     rounded-3xl p-8 w-full max-w-md"
        >
          {/* Header */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl 
                            bg-gradient-to-r from-amber-500/20 to-orange-500/20 mb-4">
              <Crown className="w-8 h-8 text-amber-400" />
            </div>
            
            <h2 className="text-2xl font-bold bg-gradient-to-r from-amber-400 to-orange-400 
                           bg-clip-text text-transparent mb-2">
              {title}
            </h2>
            
            <p className="text-white/70 text-sm leading-relaxed">
              {description}
            </p>
          </div>

          {/* Login Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <label className="block text-sm font-medium text-white/80">
                Founder Password
              </label>
              
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-4 py-3 pr-12 bg-white/10 border border-white/20 rounded-xl 
                           text-white placeholder-white/50 focus:outline-none focus:border-amber-400/50 
                           transition-colors"
                  placeholder="Enter founder password"
                  required
                  autoComplete="current-password"
                />
                
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-white/50 hover:text-white/70 
                           transition-colors"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>

            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="p-3 rounded-xl bg-red-500/20 border border-red-500/30 text-red-400 text-sm"
              >
                {error}
              </motion.div>
            )}

            <div className="flex gap-3">
              <button
                type="button"
                onClick={handleClose}
                className="flex-1 px-6 py-3 bg-white/10 border border-white/20 rounded-xl 
                         text-white hover:bg-white/20 transition-colors font-medium"
              >
                Cancel
              </button>
              
              <button
                type="submit"
                disabled={isLoading}
                className="flex-1 px-6 py-3 bg-gradient-to-r from-amber-600 to-orange-600 
                         text-white rounded-xl font-medium hover:shadow-lg hover:shadow-amber-500/25 
                         transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed
                         flex items-center justify-center gap-2"
              >
                {isLoading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Verifying...
                  </>
                ) : (
                  <>
                    <Lock className="w-4 h-4" />
                    Access
                  </>
                )}
              </button>
            </div>
          </form>

          {/* Security Notice */}
          <div className="mt-6 p-3 rounded-xl bg-blue-500/10 border border-blue-500/20">
            <div className="flex items-center gap-2 text-blue-400 text-xs">
              <Shield className="w-4 h-4" />
              <span>Session expires automatically after 4 hours for security</span>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}

// Session Status Component
export const FounderSessionStatus: React.FC = () => {
  const { isAuthenticated, logout, timeRemaining } = useFounderAuth()

  if (!isAuthenticated) return null

  const formatTime = (ms: number) => {
    const hours = Math.floor(ms / (1000 * 60 * 60))
    const minutes = Math.floor((ms % (1000 * 60 * 60)) / (1000 * 60))
    const seconds = Math.floor((ms % (1000 * 60)) / 1000)
    return `${hours}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      className="fixed top-4 right-4 z-40 bg-gradient-to-r from-amber-500/20 to-orange-500/20 
                 backdrop-blur-lg border border-amber-500/30 rounded-xl p-3 flex items-center gap-3"
    >
      <div className="flex items-center gap-2">
        <div className="w-2 h-2 bg-amber-400 rounded-full animate-pulse" />
        <Crown className="w-4 h-4 text-amber-400" />
        <span className="text-amber-400 text-sm font-medium">Founder Access</span>
      </div>
      
      <div className="text-white/60 text-xs">
        {formatTime(timeRemaining)}
      </div>
      
      <button
        onClick={logout}
        className="text-white/60 hover:text-white transition-colors text-xs"
      >
        Logout
      </button>
    </motion.div>
  )
}