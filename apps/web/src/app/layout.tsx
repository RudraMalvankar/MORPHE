import type { Metadata } from "next";
import "./globals.css";
import { QueryProvider } from "@/lib/query-provider";
import { NavShell } from "@/components/layout/nav-shell";

export const metadata: Metadata = {
  title: "MORPHE — Research Document Intelligence Platform",
  description: "Transform. Format. Publish.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="font-sans antialiased">
        <QueryProvider>
          <NavShell>{children}</NavShell>
        </QueryProvider>
      </body>
    </html>
  );
}
