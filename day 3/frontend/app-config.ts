export interface AppConfig {
  pageTitle: string;
  pageDescription: string;
  companyName: string;

  supportsChatInput: boolean;
  supportsVideoInput: boolean;
  supportsScreenShare: boolean;
  isPreConnectBufferEnabled: boolean;

  logo: string;
  startButtonText: string;
  accent?: string;
  logoDark?: string;
  accentDark?: string;

  audioVisualizerType?: 'bar' | 'wave' | 'grid' | 'radial' | 'aura';
  audioVisualizerColor?: `#${string}`;
  audioVisualizerColorDark?: `#${string}`;
  audioVisualizerColorShift?: number;
  audioVisualizerBarCount?: number;
  audioVisualizerGridRowCount?: number;
  audioVisualizerGridColumnCount?: number;
  audioVisualizerRadialBarCount?: number;
  audioVisualizerRadialRadius?: number;
  audioVisualizerWaveLineWidth?: number;

  // agent dispatch configuration
  agentName?: string;

  // LiveKit Cloud Sandbox configuration
  sandboxId?: string;
}

export const APP_CONFIG_DEFAULTS: AppConfig = {
<<<<<<< HEAD
  companyName: 'Voice Counter',
  pageTitle: 'VoiceCounter — Voice Assistant for Shop Owners',
  pageDescription: 'Manage your orders and customer inquiries by voice, powered by Murf Falcon', 
=======
  companyName: 'Mera Kirana',
  pageTitle: 'Mera Kirana AI',
  pageDescription: 'Your friendly neighborhood shop assistant',
>>>>>>> ec29265f25fcb9e3403fb8b594c72d56a28810bd

  supportsChatInput: true,
  supportsVideoInput: true,
  supportsScreenShare: true,
  isPreConnectBufferEnabled: true,

  logo: '/murf-logo.svg',
<<<<<<< HEAD
  accent: '#EA580C',
  logoDark: '/murf-logo-dark.svg',
  accentDark: '#FB923C',
  startButtonText: 'Talk to VoiceCounter',
=======
  accent: '#f97316', // Orange theme
  logoDark: '/murf-logo-dark.svg',
  accentDark: '#fdba74',
  startButtonText: 'Start Shopping',
>>>>>>> ec29265f25fcb9e3403fb8b594c72d56a28810bd

  // optional: audio visualization configuration
  // audioVisualizerType: 'bar',
  // audioVisualizerColor: '#002cf2',
  // audioVisualizerColorDark: '#1fd5f9',
  // audioVisualizerColorShift: 0.3,
  // audioVisualizerBarCount: 5,
  // audioVisualizerType: 'radial',
  // audioVisualizerRadialBarCount: 24,
  // audioVisualizerRadialRadius: 100,
  // audioVisualizerType: 'grid',
  // audioVisualizerGridRowCount: 25,
  // audioVisualizerGridColumnCount: 25,
<<<<<<< HEAD
  // audioVisualizerType: 'wave',
  // audioVisualizerWaveLineWidth: 3,
=======
  audioVisualizerType: 'wave',
  audioVisualizerWaveLineWidth: 4,
  audioVisualizerColor: '#f97316',
  audioVisualizerColorDark: '#fdba74',
>>>>>>> ec29265f25fcb9e3403fb8b594c72d56a28810bd
  // audioVisualizerType: 'aura',

  // agent dispatch configuration
  agentName: process.env.AGENT_NAME ?? undefined,

  // LiveKit Cloud Sandbox configuration
  sandboxId: undefined,
};
