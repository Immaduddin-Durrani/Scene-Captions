export function GET() { return Response.json({ status: "ok", app: "SceneCaptions" }); }
export function HEAD() { return new Response(null, { status: 200 }); }
