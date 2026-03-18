export default function StatsStrip({ runs, saved, promoted }: { runs: number; saved: number; promoted: number }) {
  return (
    <section className="grid grid-cols-3 gap-3">
      <div className="panel p-3"><p className="text-xs">Planning runs</p><p className="text-2xl font-bold">{runs}</p></div>
      <div className="panel p-3"><p className="text-xs">Saved snapshots</p><p className="text-2xl font-bold">{saved}</p></div>
      <div className="panel p-3"><p className="text-xs">Promoted insights</p><p className="text-2xl font-bold">{promoted}</p></div>
    </section>
  );
}
