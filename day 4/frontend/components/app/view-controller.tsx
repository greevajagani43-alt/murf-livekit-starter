'use client';

<<<<<<< HEAD
import { useEffect, useRef, useState } from 'react';
import { useTheme } from 'next-themes';
import { AnimatePresence, motion } from 'motion/react';
import { toast } from 'sonner';
import { useSessionContext } from '@livekit/components-react';
import type { AppConfig } from '@/app-config';
import { AgentSessionView_01 } from '@/components/agents-ui/blocks/agent-session-view-01';
import { CallEndedView } from '@/components/app/call-ended-view';
=======
import React, { useEffect, useState } from 'react';
import { useTheme } from 'next-themes';
import { AnimatePresence, motion } from 'motion/react';
import { useSessionContext } from '@livekit/components-react';
import type { AppConfig } from '@/app-config';
import { AgentSessionView_01 } from '@/components/agents-ui/blocks/agent-session-view-01';
>>>>>>> ec29265f25fcb9e3403fb8b594c72d56a28810bd
import { WelcomeView } from '@/components/app/welcome-view';

const MotionWelcomeView = motion.create(WelcomeView);
const MotionSessionView = motion.create(AgentSessionView_01);
<<<<<<< HEAD
const MotionCallEndedView = motion.create(CallEndedView);
=======
>>>>>>> ec29265f25fcb9e3403fb8b594c72d56a28810bd

const VIEW_MOTION_PROPS = {
  variants: {
    visible: {
      opacity: 1,
    },
    hidden: {
      opacity: 0,
    },
  },
  initial: 'hidden',
  animate: 'visible',
  exit: 'hidden',
  transition: {
    duration: 0.5,
    ease: 'linear',
  },
};

interface ViewControllerProps {
  appConfig: AppConfig;
}

export function ViewController({ appConfig }: ViewControllerProps) {
<<<<<<< HEAD
  const { isConnected, start, end } = useSessionContext();
  const { resolvedTheme } = useTheme();
  const [isConnecting, setIsConnecting] = useState(false);
  const [hasEnded, setHasEnded] = useState(false);
  const wasConnected = useRef(false);

  useEffect(() => {
    if (isConnected) {
      wasConnected.current = true;
      setIsConnecting(false);
      setHasEnded(false);
    } else if (wasConnected.current) {
      setHasEnded(true);
      wasConnected.current = false;
    }
  }, [isConnected]);

    const handleStartCall = async () => {
    setIsConnecting(true);
    setHasEnded(false);

    try {
      await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch (err) {
      setIsConnecting(false);
      const error = err as DOMException;
      if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
        toast.error('Microphone access is blocked', {
          description:
            'Click the lock icon in your browser address bar, allow microphone access, then refresh the page and try again.',
          duration: 15000,
        });
      } else {
        toast.error('Could not access microphone', {
          description: 'Please check that a microphone is connected and try again.',
          duration: 10000,
        });
      }
      return;
    }

    try {
      await start();
    } catch {
      setIsConnecting(false);
    }
  };
  return (
    <AnimatePresence mode="wait">
      {/* Call ended view */}
      {!isConnected && hasEnded && (
        <MotionCallEndedView key="call-ended" {...VIEW_MOTION_PROPS} onStartCall={handleStartCall} />
      )}
      {/* Welcome / Ready view */}
      {!isConnected && !hasEnded && (
        <MotionWelcomeView
          key="welcome"
          {...VIEW_MOTION_PROPS}
          startButtonText={appConfig.startButtonText}
          onStartCall={handleStartCall}
          isConnecting={isConnecting}
        />
      )}
      {/* Session view (Listening / Speaking happen inside here) */}
=======
  const { isConnected, start } = useSessionContext();
  const { resolvedTheme } = useTheme();

  // Track if a call has ended previously
  const [hasCallEnded, setHasCallEnded] = useState(false);

  useEffect(() => {
    if (isConnected) {
      setHasCallEnded(true);
    }
  }, [isConnected]);

  return (
    <AnimatePresence mode="wait">
      {/* Welcome view */}
      {!isConnected && (
        <MotionWelcomeView
          key="welcome"
          {...VIEW_MOTION_PROPS}
          startButtonText={hasCallEnded ? 'Start Again' : appConfig.startButtonText}
          hasCallEnded={hasCallEnded}
          onStartCall={start}
        />
      )}
      {/* Session view */}
>>>>>>> ec29265f25fcb9e3403fb8b594c72d56a28810bd
      {isConnected && (
        <MotionSessionView
          key="session-view"
          {...VIEW_MOTION_PROPS}
          supportsChatInput={appConfig.supportsChatInput}
          supportsVideoInput={appConfig.supportsVideoInput}
          supportsScreenShare={appConfig.supportsScreenShare}
          isPreConnectBufferEnabled={appConfig.isPreConnectBufferEnabled}
          audioVisualizerType={appConfig.audioVisualizerType}
          audioVisualizerColor={
            resolvedTheme === 'dark'
              ? appConfig.audioVisualizerColorDark
              : appConfig.audioVisualizerColor
          }
          audioVisualizerColorShift={appConfig.audioVisualizerColorShift}
          audioVisualizerBarCount={appConfig.audioVisualizerBarCount}
          audioVisualizerGridRowCount={appConfig.audioVisualizerGridRowCount}
          audioVisualizerGridColumnCount={appConfig.audioVisualizerGridColumnCount}
          audioVisualizerRadialBarCount={appConfig.audioVisualizerRadialBarCount}
          audioVisualizerRadialRadius={appConfig.audioVisualizerRadialRadius}
          audioVisualizerWaveLineWidth={appConfig.audioVisualizerWaveLineWidth}
          className="fixed inset-0"
        />
      )}
    </AnimatePresence>
  );
<<<<<<< HEAD
}
=======
}
>>>>>>> ec29265f25fcb9e3403fb8b594c72d56a28810bd
