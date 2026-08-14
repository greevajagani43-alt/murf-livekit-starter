import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Call Analytics Dashboard — Ratan Kirana Store',
  description:
    'Track call outcomes, success rates, and performance metrics for the Saathi voice agent.',
};

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
