'use client';

import { useState } from 'react';
import { GlassCard } from '@/components/ui/GlassCard';

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState('general');

  const tabs = [
    { id: 'general', label: 'General' },
    { id: 'notifications', label: 'Notifications' },
    { id: 'integrations', label: 'Integrations' },
    { id: 'api', label: 'API Keys' },
  ];

  return (
    <main className="min-h-screen bg-[rgb(5,5,5)] text-white p-8">
      <h1 className="text-3xl font-bold italic mb-8">Settings</h1>

      <div className="flex gap-2 mb-8">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 rounded-full text-sm transition-all ${activeTab === tab.id
                ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                : 'bg-white/5 text-white/60 hover:text-white hover:bg-white/10'
              }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <GlassCard className="p-6">
        {activeTab === 'general' && (
          <div className="space-y-6">
            <div>
              <label className="block text-sm text-white/60 mb-2">Company Name</label>
              <input type="text" placeholder="RootedAI" className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-blue-400" />
            </div>
            <div>
              <label className="block text-sm text-white/60 mb-2">Industry</label>
              <select className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-blue-400">
                <option>Technology</option>
                <option>Healthcare</option>
                <option>Finance</option>
                <option>Education</option>
                <option>Manufacturing</option>
              </select>
            </div>
            <div>
              <label className="block text-sm text-white/60 mb-2">Primary Jurisdictions</label>
              <div className="flex flex-wrap gap-2">
                {['EU', 'US', 'India', 'UK', 'China'].map((j) => (
                  <span key={j} className="px-3 py-1 rounded-full text-sm bg-blue-500/20 text-blue-400 border border-blue-500/30">{j}</span>
                ))}
              </div>
            </div>
          </div>
        )}
        {activeTab === 'notifications' && (
          <div className="space-y-4">
            <p className="text-white/60">Configure alert channels for compliance notifications.</p>
            {['Slack Webhook', 'Teams Webhook', 'Email (SMTP)'].map((ch) => (
              <div key={ch}>
                <label className="block text-sm text-white/60 mb-2">{ch}</label>
                <input type="text" placeholder={`Enter ${ch} URL`} className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-blue-400" />
              </div>
            ))}
          </div>
        )}
        {activeTab === 'integrations' && (
          <div className="space-y-4">
            <p className="text-white/60">Connect external services for compliance automation.</p>
            {['Supabase', 'GitHub Actions', 'Jira', 'Slack'].map((svc) => (
              <div key={svc} className="flex items-center justify-between p-4 bg-white/5 border border-white/10 rounded-xl hover:bg-white/10 transition-colors">
                <span className="text-white">{svc}</span>
                <button className="px-4 py-1 rounded-full text-sm bg-blue-500/20 text-blue-400 border border-blue-500/30 hover:bg-blue-500/30 transition-all">Connect</button>
              </div>
            ))}
          </div>
        )}
        {activeTab === 'api' && (
          <div className="space-y-4">
            <p className="text-white/60">Manage API keys for external integrations.</p>
            <div className="p-4 bg-white/5 border border-white/10 rounded-xl">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-white">Production API Key</p>
                  <p className="text-sm text-white/60">adhi_pk_••••••••••••</p>
                </div>
                <button className="px-4 py-1 rounded-full text-sm bg-red-500/20 text-red-400 border border-red-500/30 hover:bg-red-500/30 transition-all">Regenerate</button>
              </div>
            </div>
            <button className="px-6 py-2 rounded-full bg-blue-500/20 text-blue-400 border border-blue-500/30 hover:bg-blue-500/30 transition-all">Generate New Key</button>
          </div>
        )}
      </GlassCard>
    </main>
  );
}
