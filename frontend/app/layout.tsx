export const metadata = {
  title: 'BrewContent — Autonomous AI Knowledge Agent',
  description: 'BrewContent is an autonomous AI knowledge agent by Vikranth Reddy. Chat with the BrewContent knowledge base: brand kits, campaigns, audience, billing, scheduling and content flows — running fully client-side in demo mode.',
  keywords: 'BrewContent, AI agent, knowledge base, autonomous agent, content automation, Vikranth Reddy',
  authors: [{ name: 'Vikranth Reddy' }],
  robots: 'index, follow',
  openGraph: {
    type: 'website',
    url: 'https://brewcontent-autonomous-agent.vercel.app/',
    title: 'BrewContent — Autonomous AI Knowledge Agent',
    description: 'Chat with the BrewContent knowledge base: brand kits, campaigns, audience, billing, scheduling and content flows.',
    siteName: 'BrewContent',
  },
  twitter: {
    card: 'summary',
    title: 'BrewContent — Autonomous AI Knowledge Agent',
    description: 'Chat with the BrewContent knowledge base — brand kits, campaigns, audience, billing and more.',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
