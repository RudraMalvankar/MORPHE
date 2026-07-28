"use client";

import { Button } from "@/components/ui/button";

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center max-w-2xl mx-auto space-y-6">
      <div className="p-4 rounded-full bg-primary/10 text-primary border border-primary/20">
        <span className="font-mono text-sm font-semibold">FOUNDATION INITIALIZED — VERSION 1.0</span>
      </div>
      <h1 className="text-4xl font-extrabold tracking-tight">
        MORPHE Document Intelligence Platform
      </h1>
      <p className="text-muted-foreground text-lg">
        The monorepo foundation, FastAPI modular backend, Next.js frontend, database models, Redis streams, and container specs have been successfully configured.
      </p>
      <div className="flex items-center gap-4">
        <Button variant="default">API Health Status</Button>
        <Button variant="outline">Docs & Architecture</Button>
      </div>
    </div>
  );
}
