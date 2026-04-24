import React, { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'

export default function UserProfile() {
  const { user, logout, userStats, fetchUserStats, token } = useAuth()
  const [showDropdown, setShowDropdown] = useState(false)

  useEffect(() => {
    // Refresh stats every 5 seconds
    const interval = setInterval(() => {
      if (token) {
        fetchUserStats(token)
      }
    }, 5000)

    return () => clearInterval(interval)
  }, [token, fetchUserStats])

  if (!user) return null

  const getProgressColor = (used, limit) => {
    const percent = (used / limit) * 100
    if (percent >= 100) return 'bg-red-500'
    if (percent >= 80) return 'bg-yellow-500'
    return 'bg-green-500'
  }

  return (
    <div className="relative">
      <button
        onClick={() => setShowDropdown(!showDropdown)}
        className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gray-100 hover:bg-gray-200 transition"
      >
        {user.picture && (
          <img src={user.picture} alt={user.name} className="w-8 h-8 rounded-full" />
        )}
        <span className="hidden sm:inline text-sm font-medium">{user.name}</span>
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
        </svg>
      </button>

      {showDropdown && (
        <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-xl z-50 p-4 border border-gray-200">
          {/* User Info */}
          <div className="mb-4 pb-4 border-b">
            <p className="font-semibold text-gray-900">{user.name}</p>
            <p className="text-sm text-gray-600">{user.email}</p>
          </div>

          {/* Usage Stats */}
          {userStats && (
            <div className="space-y-4">
              <h3 className="font-semibold text-gray-900">📊 Usage Limits (72 hours)</h3>

              {/* Product Analysis */}
              <div>
                <div className="flex justify-between items-center mb-2">
                  <label className="text-sm font-medium text-gray-700">
                    Product Analysis
                  </label>
                  <span className="text-sm text-gray-600">
                    {userStats.usage.product_analysis.used}/{userStats.usage.product_analysis.limit}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all ${getProgressColor(
                      userStats.usage.product_analysis.used,
                      userStats.usage.product_analysis.limit
                    )}`}
                    style={{
                      width: `${Math.min(
                        (userStats.usage.product_analysis.used /
                          userStats.usage.product_analysis.limit) *
                          100,
                        100
                      )}%`
                    }}
                  ></div>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  {userStats.usage.product_analysis.remaining} analyses remaining
                </p>
              </div>

              {/* Batch Optimize */}
              <div>
                <div className="flex justify-between items-center mb-2">
                  <label className="text-sm font-medium text-gray-700">
                    Batch Optimization
                  </label>
                  <span className="text-sm text-gray-600">
                    {userStats.usage.batch_optimize.used}/{userStats.usage.batch_optimize.limit}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all ${getProgressColor(
                      userStats.usage.batch_optimize.used,
                      userStats.usage.batch_optimize.limit
                    )}`}
                    style={{
                      width: `${Math.min(
                        (userStats.usage.batch_optimize.used /
                          userStats.usage.batch_optimize.limit) *
                          100,
                        100
                      )}%`
                    }}
                  ></div>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  {userStats.usage.batch_optimize.remaining} batch operations remaining
                </p>
              </div>

              {/* Reset Time */}
              <div className="bg-blue-50 border border-blue-200 rounded p-3">
                <p className="text-xs text-blue-900">
                  ⏱️ Limits reset at: {new Date(userStats.usage.product_analysis.resets_at).toLocaleString()}
                </p>
              </div>
            </div>
          )}

          {/* Logout Button */}
          <button
            onClick={() => {
              logout()
              setShowDropdown(false)
            }}
            className="mt-4 w-full px-4 py-2 bg-red-50 hover:bg-red-100 text-red-700 rounded-lg transition font-medium text-sm"
          >
            Logout
          </button>
        </div>
      )}
    </div>
  )
}
