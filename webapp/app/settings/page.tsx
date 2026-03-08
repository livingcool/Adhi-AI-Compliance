'use client';

import { useState } from 'react';

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
            className={`px-4 py-2 rounded-full text-sm transition-all ${
              activeTab === tab.id
                ? 'bg-[rgb(59,130,246)] text-white'
                : 'bg-[rgba(255,255,255,0.06)] text-[rgb(163,163,163)] hover:text-white'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className="bg-[rgba(255,255,255,0.06)] backdrop-blur-md rounded-2xl p-6 border border-[rgba(255,255,255,0.1)]">
        {activeTab === 'general' && (
          <div className="space-y-6">
            <div>
              <label className="block text-sm text-[rgb(163,163,163)] mb-2">Company Name</label>
              <input type="text" placeholder="RootedAI" className="w-full bg-[rgba(255,255,255,0.06)] border border-[rgba(255,255,255,0.1)] rounded-xl px-4 py-3 text-white focus:outline-none focus:border-[rgb(59,130,246)]" />
            </div>
            <div>
              <label className="block text-sm text-[rgb(163,163,163)] mb-2">Industry</label>
              <select className="w-full bg-[rgba(255,255,255,0.06)] border border-[rgba(255,255,255,0.1)] rounded-xl px-4 py-3 text-white focus:outline-none focus:border-[rgb(59,130,246)]">
                <option>Technology</option>
                <option>Healthcare</option>
                <option>Finance</option>
                <option>Education</option>
                <option>Manufacturing</option>
              </select>
            </div>
            <div>
              <label className="block text-sm text-[rgb(163,163,163)] mb-2">Primary Jurisdictions</label>
              <div className="flex flex-wrap gap-2">
                {['EU', 'US', 'India', 'UK', 'China'].map((j) => (
                  <span key={j} className="px-3 py-1 rounded-full text-sm bg-[rgba(59,130,246,0.2)] text-[rgb(96,165,250)] border border-[rgba(59,130,246,0.3)]">{j}</span>
                ))}
              </div>
            </div>
          </div>
        )}
        {activeTab === 'notifications' && (
          <div className="space-y-4">
            <p className="text-[rgb(163,163,163)]">Configure alert channels for compliance notifications.</p>
            {['Slack Webhook', 'Teams Webhook', 'Email (SMTP)'].map((ch) => (
              <div key={ch}>
                <label className="block text-sm text-[rgb(163,163,163)] mb-2">{ch}</label>
                <input type="text" placeholder={`Enter ${ch} URL`} className="w-full bg-[rgba(255,255,255,0.06)] border border-[rgba(255,255,255,0.1)] rounded-xl px-4 py-3 text-white focus:outline-none focus:border-[rgb(59,130,246)]" />
              </div>
            ))}
          </div>
        )}
        {activeTab === 'integrations' && (
          <div className="space-y-4">
            <p className="text-[rgb(163,163,163)]">Connect external services for compliance automation.</p>
            {['Supabase', 'GitHub Actions', 'Jira', 'Slack'].map((svc) => (
              <div key={svc} className="flex items-center justify-between p-4 bg-[rgba(255,255,255,0.03)] rounded-xl">
                <span>{svc}</span>
                <button className="px-4 py-1 rounded-full text-sm bg-[rgba(255,255,255,0.1)] hover:bg-[rgba(59,130,246,0.3)] transition-all">Connect</button>
              </div>
            ))}
          </div>
        )}
        {activeTab === 'api' && (
          <div className="space-y-4">
            <p className="text-[rgb(163,163,163)]">Manage API keys for external integrations.</p>
            <div className="p-4 bg-[rgba(255,255,255,0.03)] rounded-xl">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Production API Key</p>
                  <p className="text-sm text-[rgb(163,163,163)]">adhi_pk_••••••••••••</p>
                </div>
                <button className="px-4 py-1 rounded-full text-sm bg-[rgba(239,68,68,0.2)] text-[rgb(239,68,68)] hover:bg-[rgba(239,68,68,0.3)] transition-all">Regenerate</button>
              </div>
            </div>
            <button className="px-6 py-2 rounded-full bg-[rgb(59,130,246)] text-white hover:bg-[rgb(96,165,250)] transition-all">Generate New Key</button>
          </div>
        )}
      </div>
    </main>
  );
}
