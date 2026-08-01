export default function Sidebar() {
  return (
    <aside className="w-64 bg-slate-900 text-white min-h-screen p-6">
      <h1 className="text-2xl font-bold mb-8">
        AI Software Company
      </h1>

      <nav className="space-y-4">
        <div>📊 Dashboard</div>
        <div>📁 Projects</div>
        <div>🤖 AI Office</div>
        <div>📋 Tasks</div>
        <div>⚙️ Settings</div>
      </nav>
    </aside>
  );
}