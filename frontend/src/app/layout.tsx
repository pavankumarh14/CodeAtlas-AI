import React from "react";
import type { Metadata } from "next";
import ClientShell from "./client-shell";
import "./globals.css";

export const metadata: Metadata = {
  title: "CodeAtlas AI - The Living Engineering Ontology & Knowledge Graph",
  description: "AI-powered Knowledge Graph & Living Ontology Platform for Engineering Organizations",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full bg-slate-950 text-slate-100 dark">
      <ClientShell>{children}</ClientShell>
    </html>
  );
}
