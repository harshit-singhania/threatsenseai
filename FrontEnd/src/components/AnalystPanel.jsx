import React from 'react';
import { motion } from 'framer-motion';
import { Activity, CheckCircle } from 'lucide-react';

const AnalystPanel = ({ report }) => {
  if (!report) return null;

  const getSeverityColor = (score) => {
    if (score >= 8) return 'text-red-500';
    if (score >= 5) return 'text-orange-500';
    return 'text-green-500';
  };

  const getSeverityBg = (score) => {
    if (score >= 8) return 'bg-red-500';
    if (score >= 5) return 'bg-orange-500';
    return 'bg-green-500';
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
      className="mt-6 border border-indigo-500/30 bg-indigo-900/10 rounded-xl overflow-hidden"
    >
      {/* Header */}
      <div className="bg-indigo-900/30 p-4 flex items-center gap-3 border-b border-indigo-500/20">
        <Activity className="w-6 h-6 text-indigo-400" />
        <h3 className="text-lg font-bold text-white">Smart Analyst Report</h3>
        <span className="ml-auto text-xs px-2 py-1 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
          Gemini 1.5 Flash
        </span>
      </div>

      <div className="p-6 space-y-6">
        {/* Severity Score */}
        <div className="flex items-center justify-between">
          <span className="text-slate-400 font-medium">Threat Severity</span>
          <div className="flex items-center gap-2">
            <span className={`text-2xl font-bold ${getSeverityColor(report.severity_score)}`}>
              {report.severity_score}/10
            </span>
            <div className="w-24 h-2 bg-slate-800 rounded-full overflow-hidden">
              <div 
                className={`h-full ${getSeverityBg(report.severity_score)}`} 
                style={{ width: `${report.severity_score * 10}%` }}
              />
            </div>
          </div>
        </div>

        {/* Summary */}
        <div className="bg-slate-900/40 p-4 rounded-lg border border-slate-700/50">
          <p className="text-slate-300 leading-relaxed italic">
            "{report.summary}"
          </p>
        </div>

        {/* Actions */}
        <div>
          <h4 className="text-sm uppercase tracking-wider text-slate-500 font-semibold mb-3">
            Recommended Protocols
          </h4>
          <ul className="space-y-3">
            {report.actions && report.actions.map((action, idx) => (
              <li key={idx} className="flex items-start gap-3 text-slate-300">
                <CheckCircle className="w-5 h-5 text-indigo-400 shrink-0 mt-0.5" />
                <span>{action}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </motion.div>
  );
};

export default AnalystPanel;
