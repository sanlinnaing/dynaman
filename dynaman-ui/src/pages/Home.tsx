export default function Home() {
  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-4">Welcome to Dynaman Admin</h1>
      <p className="text-muted-foreground mb-8">
        Manage your No-Code entities and data records. Select a schema from the sidebar to start exploring data.
      </p>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="p-6 rounded-lg border bg-card text-card-foreground shadow-sm">
          <h3 className="font-semibold text-lg mb-2">Schemas</h3>
          <p className="text-sm text-muted-foreground">Define and manage your data models dynamically.</p>
        </div>
        <div className="p-6 rounded-lg border bg-card text-card-foreground shadow-sm">
          <h3 className="font-semibold text-lg mb-2">Data Explorer</h3>
          <p className="text-sm text-muted-foreground">View, search, and edit records for any entity.</p>
        </div>
        <div className="p-6 rounded-lg border bg-card text-card-foreground shadow-sm">
          <h3 className="font-semibold text-lg mb-2">API Ready</h3>
          <p className="text-sm text-muted-foreground">All data is instantly available via the execution API.</p>
        </div>
      </div>
    </div>
  );
}
