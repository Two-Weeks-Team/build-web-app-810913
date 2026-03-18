export default function ReferenceShelf() {
  const lanes = [
    "Guided Planning Lane: assumptions → target users → problem framing",
    "Study Sprint Builder: 2-week validation checkpoints",
    "Syllabus Board: what to learn before build commitment",
    "Review Cadence Rail: weekly brief refinement and decision logs"
  ];

  return (
    <section className="sheet p-4 md:p-5">
      <h2 className="text-xl font-bold">Planning Rails & Trust Surfaces</h2>
      <ul className="mt-3 space-y-2 text-sm">
        {lanes.map((lane) => (
          <li key={lane} className="rounded-md border bg-white/60 p-2">
            {lane}
          </li>
        ))}
      </ul>
    </section>
  );
}
