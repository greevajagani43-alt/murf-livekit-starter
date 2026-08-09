'use client';

import React from 'react';
import { type MotionProps, motion } from 'motion/react';
import { useVoiceAssistant } from '@livekit/components-react';
import { AgentAudioVisualizerAura } from '@/components/agents-ui/agent-audio-visualizer-aura';
import { AgentAudioVisualizerBar } from '@/components/agents-ui/agent-audio-visualizer-bar';
import { AgentAudioVisualizerGrid } from '@/components/agents-ui/agent-audio-visualizer-grid';
import { AgentAudioVisualizerRadial } from '@/components/agents-ui/agent-audio-visualizer-radial';
import { AgentAudioVisualizerWave } from '@/components/agents-ui/agent-audio-visualizer-wave';
import { cn } from '@/lib/shadcn/utils';

const MotionAgentAudioVisualizerAura = motion.create(AgentAudioVisualizerAura);
const MotionAgentAudioVisualizerBar = motion.create(AgentAudioVisualizerBar);
const MotionAgentAudioVisualizerGrid = motion.create(AgentAudioVisualizerGrid);
const MotionAgentAudioVisualizerRadial = motion.create(AgentAudioVisualizerRadial);
const MotionAgentAudioVisualizerWave = motion.create(AgentAudioVisualizerWave);

interface AudioVisualizerProps extends MotionProps {
  isChatOpen: boolean;
  audioVisualizerType?: 'bar' | 'wave' | 'grid' | 'radial' | 'aura' | 'robot';
  audioVisualizerColor?: `#${string}`;
  audioVisualizerColorShift?: number;
  audioVisualizerWaveLineWidth?: number;
  audioVisualizerGridRowCount?: number;
  audioVisualizerGridColumnCount?: number;
  audioVisualizerRadialBarCount?: number;
  audioVisualizerRadialRadius?: number;
  audioVisualizerBarCount?: number;
  className?: string;
}

export function AudioVisualizer({
  audioVisualizerType = 'bar',
  audioVisualizerColor,
  audioVisualizerColorShift = 0.3,
  audioVisualizerBarCount = 5,
  audioVisualizerRadialRadius = 100,
  audioVisualizerRadialBarCount = 25,
  audioVisualizerGridRowCount = 15,
  audioVisualizerGridColumnCount = 15,
  audioVisualizerWaveLineWidth = 3,
  isChatOpen,
  className,
  ...props
}: AudioVisualizerProps) {
  const { state, audioTrack } = useVoiceAssistant();

  switch (audioVisualizerType) {
    case 'aura': {
      return (
        <MotionAgentAudioVisualizerAura
          state={state}
          audioTrack={audioTrack}
          color={audioVisualizerColor}
          colorShift={audioVisualizerColorShift}
          className={cn('size-[300px] md:size-[450px]', className)}
          {...props}
        />
      );
    }
    case 'robot': {
      const isSpeaking = state === 'speaking';
      return (
        <motion.div className={cn('size-[300px] md:size-[450px] flex items-center justify-center relative pointer-events-none', className)} {...props}>
          <motion.div
            animate={{ y: isSpeaking ? [0, -10, 0] : [0, -5, 0] }}
            transition={{ repeat: Infinity, duration: isSpeaking ? 0.5 : 2 }}
            className="relative flex flex-col items-center justify-center w-64 h-64"
          >
            {/* Arms */}
            <motion.div 
              animate={{ rotate: isSpeaking ? [0, 15, -15, 0] : 0 }}
              transition={{ repeat: Infinity, duration: 0.5 }}
              className="absolute left-[-20px] top-[100px] w-4 h-24 bg-teal-700 rounded-full origin-top" 
            />
            <motion.div 
              animate={{ rotate: isSpeaking ? [0, -15, 15, 0] : 0 }}
              transition={{ repeat: Infinity, duration: 0.5 }}
              className="absolute right-[-20px] top-[100px] w-4 h-24 bg-teal-700 rounded-full origin-top" 
            />
            
            {/* Body */}
            <div className="relative w-48 h-64 bg-[#69CDBF] rounded-[32px] border-4 border-teal-800 shadow-xl overflow-hidden flex flex-col items-center pt-6 z-10">
              
              {/* Screen */}
              <div className="w-36 h-28 bg-[#D3F5E4] rounded-xl border-4 border-teal-800 flex flex-col items-center justify-center relative overflow-hidden shadow-inner">
                {/* Eyes */}
                <div className="flex gap-8 mb-2">
                  <motion.div 
                    animate={{ scaleY: isSpeaking ? [1, 0.1, 1] : [1, 1, 0.1, 1] }}
                    transition={{ repeat: Infinity, duration: isSpeaking ? 2 : 4, times: isSpeaking ? [0, 0.5, 1] : [0, 0.9, 0.95, 1] }}
                    className="w-4 h-4 bg-teal-900 rounded-full" 
                  />
                  <motion.div 
                    animate={{ scaleY: isSpeaking ? [1, 0.1, 1] : [1, 1, 0.1, 1] }}
                    transition={{ repeat: Infinity, duration: isSpeaking ? 2 : 4, times: isSpeaking ? [0, 0.5, 1] : [0, 0.9, 0.95, 1] }}
                    className="w-4 h-4 bg-teal-900 rounded-full" 
                  />
                </div>
                
                {/* Mouth */}
                <motion.div 
                  animate={{ 
                    height: isSpeaking ? [4, 16, 8, 20, 4] : 4,
                    width: isSpeaking ? [20, 24, 20, 28, 20] : 20,
                    borderRadius: isSpeaking ? ["10px", "16px", "10px"] : "10px"
                  }}
                  transition={{ repeat: Infinity, duration: 0.3 }}
                  className="bg-teal-900 rounded-full" 
                />
              </div>
              
              {/* Buttons / Controls */}
              <div className="w-full flex-1 relative mt-4">
                {/* D-Pad */}
                <div className="absolute left-6 top-4">
                  <div className="w-12 h-12 relative">
                    <div className="absolute top-0 left-1/2 -translate-x-1/2 w-4 h-12 bg-[#FFD700] rounded-sm" />
                    <div className="absolute top-1/2 left-0 -translate-y-1/2 w-12 h-4 bg-[#FFD700] rounded-sm" />
                  </div>
                </div>
                
                {/* Action Buttons */}
                <div className="absolute right-6 top-8">
                  <div className="w-10 h-10 bg-[#FF0055] rounded-full shadow-sm border-2 border-[#CC0044]" />
                </div>
                <div className="absolute right-16 top-2">
                  <div className="w-0 h-0 border-l-8 border-l-transparent border-r-8 border-r-transparent border-b-[14px] border-b-cyan-500" />
                </div>
                <div className="absolute right-4 top-2">
                   <div className="w-4 h-4 bg-green-500 rounded-full" />
                </div>
                
                {/* Speaker Holes */}
                <div className="absolute left-16 bottom-4 flex gap-2">
                  <div className="w-1 h-6 bg-teal-800 rounded-full" />
                  <div className="w-1 h-6 bg-teal-800 rounded-full" />
                  <div className="w-1 h-6 bg-teal-800 rounded-full" />
                  <div className="w-1 h-6 bg-teal-800 rounded-full" />
                </div>
              </div>
            </div>
            
            {/* Legs */}
            <div className="flex gap-12 -mt-4 z-0">
              <div className="w-4 h-20 bg-teal-700 rounded-b-full" />
              <div className="w-4 h-20 bg-teal-700 rounded-b-full" />
            </div>
          </motion.div>
        </motion.div>
      );
    }
    case 'wave': {
      return (
        <motion.div className={className} {...props}>
          <MotionAgentAudioVisualizerWave
            state={state}
            audioTrack={audioTrack}
            color={audioVisualizerColor}
            colorShift={audioVisualizerColorShift}
            lineWidth={isChatOpen ? audioVisualizerWaveLineWidth * 2 : audioVisualizerWaveLineWidth}
            className="size-[300px] md:size-[450px]"
          />
        </motion.div>
      );
    }
    case 'grid': {
      const totalCount = audioVisualizerGridRowCount * audioVisualizerGridColumnCount;

      let size: 'icon' | 'sm' | 'md' | 'lg' | 'xl' = 'sm';
      if (totalCount < 100) {
        size = 'xl';
      } else if (totalCount < 200) {
        size = 'lg';
      } else if (totalCount < 300) {
        size = 'md';
      }

      return (
        <MotionAgentAudioVisualizerGrid
          size={size}
          state={state}
          color={audioVisualizerColor}
          audioTrack={audioTrack}
          rowCount={audioVisualizerGridRowCount}
          columnCount={audioVisualizerGridColumnCount}
          radius={Math.round(
            Math.min(audioVisualizerGridRowCount, audioVisualizerGridColumnCount) / 4
          )}
          className={cn('size-[350px] gap-0 p-8 *:place-self-center md:size-[450px]', className)}
          {...props}
        />
      );
    }
    case 'radial': {
      return (
        <motion.div className={className} {...props}>
          <MotionAgentAudioVisualizerRadial
            size="xl"
            state={state}
            color={audioVisualizerColor}
            audioTrack={audioTrack}
            radius={audioVisualizerRadialRadius}
            barCount={audioVisualizerRadialBarCount}
            className="size-[450px]"
          />
        </motion.div>
      );
    }
    default: {
      let size: 'icon' | 'sm' | 'md' | 'lg' | 'xl' = 'icon';
      let sizedClassName = cn('size-[300px] md:size-[450px]', className);

      if (audioVisualizerBarCount <= 5) {
        size = 'xl';
        sizedClassName = cn('size-[450px] *:min-h-[64px] *:w-[64px] gap-4', className);
      } else if (audioVisualizerBarCount <= 10) {
        size = 'lg';
        sizedClassName = cn('size-[450px]', className);
      } else if (audioVisualizerBarCount <= 15) {
        size = 'md';
        sizedClassName = cn('size-[350px] md:size-[450px]', className);
      } else if (audioVisualizerBarCount <= 30) {
        size = 'sm';
        sizedClassName = cn('size-[300px] md:size-[450px]', className);
      }

      return (
        <MotionAgentAudioVisualizerBar
          size={size}
          state={state}
          color={audioVisualizerColor}
          audioTrack={audioTrack}
          barCount={audioVisualizerBarCount}
          className={sizedClassName}
          {...props}
        >
          <span className="min-h-2.5 w-2.5 rounded-full bg-current/10 transition-colors duration-250 ease-linear data-[lk-highlighted=true]:bg-current" />
        </MotionAgentAudioVisualizerBar>
      );
    }
  }
}
