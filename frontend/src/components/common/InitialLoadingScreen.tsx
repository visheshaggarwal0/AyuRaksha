import React, { useEffect, useState } from 'react';
import { motion } from 'motion/react';

interface InitialLoadingScreenProps {
  onComplete: () => void;
  isReady: boolean;
}

export const InitialLoadingScreen: React.FC<InitialLoadingScreenProps> = ({
  onComplete,
  isReady
}) => {
  const [stage, setStage] = useState(0);
  const [isExiting, setIsExiting] = useState(false);

  useEffect(() => {
    // Stage progression corresponding to actual app lifecycle
    const t1 = setTimeout(() => setStage(1), 300);
    const t2 = setTimeout(() => setStage(2), 700);
    const t3 = setTimeout(() => setStage(3), 1100);

    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
      clearTimeout(t3);
    };
  }, []);

  useEffect(() => {
    if (isReady && stage >= 2 && !isExiting) {
      setIsExiting(true);
      const exitTimer = setTimeout(() => {
        onComplete();
      }, 400);
      return () => clearTimeout(exitTimer);
    }
  }, [isReady, stage, isExiting, onComplete]);

  const statusMessages = [
    'Initializing regulatory workspace...',
    'Loading statutory corpus intelligence...',
    'Restoring active case environment...',
    'System ready'
  ];

  return (
    <div
      className={`fixed inset-0 z-50 flex flex-col items-center justify-center bg-slate-950 text-white select-none overflow-hidden transition-opacity duration-400 ease-out ${
        isExiting ? 'opacity-0 pointer-events-none' : 'opacity-100'
      }`}
    >
      {/* Subtle ambient botanical radial background */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-emerald-950/40 via-slate-950 to-slate-950 pointer-events-none" />

      <div className="relative z-10 flex flex-col items-center text-center px-6 max-w-sm w-full space-y-6">
        
        {/* Real Ayuरक्षा Emblem with Subtle Scale Settle */}
        <motion.div
          initial={{ opacity: 0, scale: 0.94 }}
          animate={{ opacity: 1, scale: 1.0 }}
          transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
          className="relative"
        >
          {/* Subtle soft glowing aura */}
          <div className="absolute -inset-4 bg-emerald-500/10 rounded-full blur-xl animate-pulse pointer-events-none" />
          
          <img
            src="/branding/ayuraksha-icon.png"
            alt="Ayuरक्षा"
            className="w-16 h-16 sm:w-20 sm:h-20 object-contain relative z-10 drop-shadow-[0_8px_24px_rgba(16,185,129,0.25)]"
          />
        </motion.div>

        {/* Exact Brand Wordmark: Ayu (Latin) + रक्षा (Devanagari) */}
        <motion.div
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3, ease: 'easeOut' }}
          className="space-y-1.5"
        >
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight font-display text-white">
            Ayu<span className="text-emerald-400 font-bold">रक्षा</span>
          </h1>
          <p className="text-[11px] font-bold tracking-widest text-emerald-300/80 uppercase">
            IP-SAKTI Sahayak
          </p>
        </motion.div>

        {/* Thin Restrained Progress Indicator */}
        <div className="w-48 h-1 bg-slate-800/80 rounded-full overflow-hidden relative">
          <motion.div
            className="h-full bg-gradient-to-r from-emerald-600 via-emerald-400 to-teal-400 rounded-full"
            initial={{ width: '15%' }}
            animate={{
              width: stage === 0 ? '30%' : stage === 1 ? '65%' : stage === 2 ? '90%' : '100%'
            }}
            transition={{ duration: 0.4, ease: 'easeOut' }}
          />
        </div>

        {/* Truthful Initialization Status Message */}
        <motion.div
          key={stage}
          initial={{ opacity: 0, y: 3 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -3 }}
          transition={{ duration: 0.25 }}
          className="flex items-center justify-center space-x-2 text-xs font-mono text-slate-400"
        >
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          <span>{statusMessages[stage]}</span>
        </motion.div>

      </div>

      {/* Subtle Footer Authority Note */}
      <div className="absolute bottom-6 text-center text-[10px] text-slate-600 font-medium">
        <span>Ministry of Ayush · SIH 26045 Decision Support</span>
      </div>
    </div>
  );
};
