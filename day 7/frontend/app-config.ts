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
  companyName: 'Ratan Kirana Store',
  pageTitle: 'Ratan Store — Order by Voice',
  pageDescription: 'Your neighbourhood kirana store. Order groceries by talking to Saathi.',

  supportsChatInput: false,
  supportsVideoInput: false,
  supportsScreenShare: false,
  isPreConnectBufferEnabled: true,

  logo: '/ratan-logo.svg',
  logoDark: '/ratan-logo-dark.svg',
  accent: '#D97706',
  accentDark: '#FCD34D',
  startButtonText: 'Baat karo Saathi se',

  audioVisualizerType: 'wave',
  audioVisualizerColor: '#D97706',
  audioVisualizerColorDark: '#FCD34D',
  audioVisualizerWaveLineWidth: 2,

  agentName: 'my-agent',
  sandboxId: undefined,
};
