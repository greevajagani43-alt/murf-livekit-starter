import { Button } from '@/components/ui/button';

interface CallEndedViewProps {
  onStartCall: () => void;
}

export const CallEndedView = ({
  onStartCall,
  ref,
}: React.ComponentProps<'div'> & CallEndedViewProps) => {
  return (
    <div ref={ref}>
      <section className="bg-background flex flex-col items-center justify-center text-center">
        <p className="text-foreground max-w-prose pt-1 text-lg leading-6 font-medium">
          Call ended
        </p>
        <p className="text-muted-foreground max-w-prose pt-2 text-sm">
          Your conversation with VoiceCounter has ended.
        </p>

        <Button
          size="lg"
          onClick={onStartCall}
          className="mt-6 w-64 rounded-full font-mono text-xs font-bold tracking-wider uppercase"
        >
          Start again
        </Button>
      </section>
    </div>
  );
};