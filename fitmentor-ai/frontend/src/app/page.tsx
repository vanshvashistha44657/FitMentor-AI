import Link from "next/link";

export default function LandingPage() {
  return (
    <main className="min-h-screen flex flex-col">
      <nav className="flex items-center justify-between px-8 py-6 max-w-7xl mx-auto w-full">
        <span className="font-display font-bold text-xl tracking-tight">
          FitMentor <span className="text-ember-500">AI</span>
        </span>
        <div className="flex items-center gap-3">
          <Link href="/login" className="text-mute hover:text-bone transition-colors px-4 py-2">
            Log in
          </Link>
          <Link href="/register" className="btn-primary text-sm">
            Start free
          </Link>
        </div>
      </nav>

      <section className="flex-1 flex flex-col items-center justify-center text-center px-6 py-20">
        <span className="ai-badge mb-6">Trained on your data, not a template</span>
        <h1 className="font-display font-bold text-5xl md:text-7xl leading-[1.05] max-w-4xl">
          A coach that adjusts <span className="text-ember-500">every rep</span>,
          <br /> not just every week.
        </h1>
        <p className="text-mute text-lg md:text-xl max-w-2xl mt-6">
          FitMentor AI builds your workout, your diet, and your recovery plan from
          your actual body, schedule, and goals — then rewrites them as you
          check in, every single day.
        </p>
        <div className="flex items-center gap-4 mt-10">
          <Link href="/register" className="btn-primary">
            Build my plan
          </Link>
          <Link href="/login" className="btn-secondary">
            I already have an account
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-24 max-w-4xl w-full">
          {[
            {
              title: "Live AI Coach",
              copy: "Guides every set with form cues, rep counting, and real-time load adjustments.",
            },
            {
              title: "Adaptive Nutrition",
              copy: "Meal plans that shift with your budget, cuisine, and yesterday's calories.",
            },
            {
              title: "Weekly Reviews",
              copy: "Strength trend, adherence, and recovery — explained, not just charted.",
            },
          ].map((f) => (
            <div key={f.title} className="glass-panel p-6 text-left">
              <h3 className="font-display font-semibold text-lg mb-2">{f.title}</h3>
              <p className="text-mute text-sm leading-relaxed">{f.copy}</p>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
