export function HomeHero() {
  return (
    <main className="flex min-h-screen items-center justify-center px-6 py-16">
      <section className="w-full max-w-3xl rounded-3xl border border-slate-200 bg-white p-8 text-center shadow-sm md:p-12">
        <p className="mb-3 text-sm font-semibold uppercase tracking-[0.3em] text-blue-600">
          AI Kubernetes Agent
        </p>
        <h1 className="text-4xl font-bold tracking-tight text-slate-950 md:text-5xl">
          Troubleshoot Kubernetes with AI
        </h1>
        <p className="mx-auto mt-4 max-w-2xl text-base leading-7 text-slate-600">
          Start an on-demand investigation from one place. Kubernetes and AI
          logic will be connected in future implementation steps.
        </p>

        <button
          type="button"
          className="mt-8 rounded-full bg-blue-600 px-6 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          Investigate Cluster
        </button>

        <div className="mt-8 inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-4 py-2 text-sm font-medium text-emerald-700">
          <span className="h-2 w-2 rounded-full bg-emerald-500" />
          System Status: Ready
        </div>
      </section>
    </main>
  );
}
