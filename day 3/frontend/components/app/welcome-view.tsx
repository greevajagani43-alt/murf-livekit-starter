import { useState } from 'react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';

function WelcomeImage() {
  return (
    <svg
      width="64"
      height="64"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="text-primary mb-4 size-16"
    >
      <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
      <polyline points="9 22 9 12 15 12 15 22" />
    </svg>
  );
}

interface WelcomeViewProps {
  startButtonText: string;
  hasCallEnded?: boolean;
  onStartCall: () => void;
}

export const WelcomeView = ({
  startButtonText,
  hasCallEnded,
  onStartCall,
  ref,
}: React.ComponentProps<'div'> & WelcomeViewProps) => {
  const [isConnecting, setIsConnecting] = useState(false);

  const handleStart = async () => {
    try {
      setIsConnecting(true);
      await onStartCall();
    } catch (err: unknown) {
      const error = err as Error;
      setIsConnecting(false);
      // Handle microphone permission errors
      if (
        error?.message?.includes('Permission') ||
        error?.message?.includes('NotAllowedError') ||
        error?.name === 'NotAllowedError'
      ) {
        toast.error('Microphone access denied', {
          description:
            'Please enable microphone access in your browser settings to talk to the agent.',
          duration: 8000,
        });
      } else {
        toast.error('Could not connect', {
          description: error?.message || 'An unknown error occurred.',
        });
      }
    }
  };

  return (
    <div ref={ref}>
      <section className="bg-background flex flex-col items-center justify-center text-center">
        <WelcomeImage />

        <p className="text-foreground max-w-prose pt-1 leading-6 font-medium">
          Mera Kirana AI: Your Local Shop Assistant
        </p>

        <Button
          size="lg"
          onClick={handleStart}
          disabled={isConnecting}
          className="mt-6 w-64 rounded-full font-mono text-xs font-bold tracking-wider uppercase"
        >
          {isConnecting ? 'Connecting...' : startButtonText}
        </Button>
      </section>

      <div className="fixed bottom-5 left-0 flex w-full flex-col items-center justify-center gap-2">
        {hasCallEnded && (
          <p className="text-muted-foreground max-w-prose text-sm font-medium text-pretty md:text-base">
            Call ended.
          </p>
        )}
        <p className="text-muted-foreground max-w-prose pt-1 text-xs leading-5 font-normal text-pretty md:text-sm">
          Want to add items to your store? Check out the{' '}
          <a target="_blank" rel="noopener noreferrer" href="#" className="underline">
            Inventory Guide
          </a>
          .
        </p>
      </div>
    </div>
  );
};
