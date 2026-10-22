export const metadata = {
  title: 'BrewContent: Autonomous AI Knowledge Agent',
  description: 'BrewContent is an autonomous AI knowledge agent by Vikranth Reddy. Chat with the BrewContent knowledge base — what BrewContent does, Studio and Motion Suite features, pricing and credits, integrations and getting started — compiled from BrewContent\'s public pages and running fully client-side.',
  keywords: 'BrewContent, AI agent, knowledge base, autonomous agent, content automation, Vikranth Reddy',
  authors: [{ name: 'Vikranth Reddy' }],
  robots: 'index, follow',
  openGraph: {
    type: 'website',
    url: 'https://brewcontent-autonomous-agent.vercel.app/',
    title: 'BrewContent: Autonomous AI Knowledge Agent',
    description: 'Chat with the BrewContent knowledge base: features, pricing and credits, integrations, billing and more.',
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
