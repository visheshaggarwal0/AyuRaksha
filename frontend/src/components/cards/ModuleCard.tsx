import React from 'react';
import { ArrowRight } from 'lucide-react';

interface ModuleCardProps {
  title: string;
  subtitle: string;
  tag: string;
  icon: React.ReactNode;
  onClick: () => void;
}

export const ModuleCard: React.FC<ModuleCardProps> = ({
  title,
  subtitle,
  tag,
  icon,
  onClick,
}) => {
  return (
    <div
      onClick={onClick}
      className="bg-white rounded-2xl p-6 border border-ayush-border shadow-subtle hover:shadow-card hover:border-ayush-forest transition-all cursor-pointer group flex flex-col justify-between"
    >
      <div>
        <div className="flex items-center justify-between mb-4">
          <div className="w-11 h-11 rounded-xl bg-slate-100 text-ayush-forest flex items-center justify-center group-hover:bg-ayush-forest group-hover:text-white transition-colors">
            {icon}
          </div>
          <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-200">
            {tag}
          </span>
        </div>
        <h3 className="text-base font-bold text-ayush-navy group-hover:text-ayush-forest transition-colors mb-2">
          {title}
        </h3>
        <p className="text-xs text-ayush-slate leading-relaxed">
          {subtitle}
        </p>
      </div>

      <div className="pt-4 mt-4 border-t border-slate-100 flex items-center justify-between text-xs font-bold text-ayush-forest">
        <span>Launch Module</span>
        <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
      </div>
    </div>
  );
};
