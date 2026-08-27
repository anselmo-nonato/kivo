import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "KIVO — A Chave da sua Virada Financeira",
  description: "Plataforma completa de gestão financeira para indivíduos e famílias.",
  icons: {
    icon: "/assets/favicon_32.png",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR">
      <body className="antialiased min-h-screen bg-slate-50 text-slate-900">
        {children}
      </body>
    </html>
  );
}
