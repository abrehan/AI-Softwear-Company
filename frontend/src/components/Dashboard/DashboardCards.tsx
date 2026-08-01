export default function DashboardCards() {
  return (
    <div className="grid grid-cols-4 gap-6">
      <div className="bg-white rounded-xl shadow p-6">
        <h3>CEO Agent</h3>
        <p>🟢 Online</p>
      </div>

      <div className="bg-white rounded-xl shadow p-6">
        <h3>Backend Team</h3>
        <p>Idle</p>
      </div>

      <div className="bg-white rounded-xl shadow p-6">
        <h3>Frontend Team</h3>
        <p>Idle</p>
      </div>

      <div className="bg-white rounded-xl shadow p-6">
        <h3>QA Team</h3>
        <p>Ready</p>
      </div>
    </div>
  );
}