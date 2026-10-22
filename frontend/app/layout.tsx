export const metadata = {
  title: 'BrewContent: Autonomous AI Knowledge Agent',
  description: 'BrewContent is an autonomous AI knowledge agent by Vikranth Reddy. Chat with the BrewContent knowledge base: brand kits, campaigns, audience, billing, scheduling and content flows, running fully client-side in demo mode.',
  keywords: 'BrewContent, AI agent, knowledge base, autonomous agent, content automation, Vikranth Reddy',
  authors: [{ name: 'Vikranth Reddy' }],
  robots: 'index, follow',
  openGraph: {
    type: 'website',
    url: 'https://brewcontent-autonomous-agent.vercel.app/',
    title: 'BrewContent: Autonomous AI Knowledge Agent',
    description: 'Chat with the BrewContent knowledge base: brand kits, campaigns, audience, billing, scheduling and content flows.',
    siteName: 'BrewContent',
    images: ['https://brewcontent-autonomous-agent.vercel.app/og.png'],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'BrewContent: Autonomous AI Knowledge Agent',
    description: 'Chat with the BrewContent knowledge base: brand kits, campaigns, audience, billing and more.',
    images: ['https://brewcontent-autonomous-agent.vercel.app/og.png'],
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        {children}
        <script defer src="/_vercel/insights/script.js"></script>
      </body>
    </html>
  )
}
