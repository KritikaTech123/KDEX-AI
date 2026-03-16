import './globals.css';
import ClientBodyFix from '../components/ClientBodyFix';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body suppressHydrationWarning={true}>
        {children}
        <ClientBodyFix />
      </body>
    </html>
  );
}
