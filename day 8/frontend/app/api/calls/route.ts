import { NextRequest, NextResponse } from "next/server";

const DASHBOARD_API = "http://localhost:8003";

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const limit = searchParams.get("limit") || "50";
  try {
    const res = await fetch(`${DASHBOARD_API}/api/calls?limit=${limit}`, {
      cache: "no-store",
    });
    if (!res.ok) {
      throw new Error(`FastAPI responded with ${res.status}`);
    }
    const data = await res.json();
    return NextResponse.json(data);
  } catch (e: any) {
    return NextResponse.json([], { status: 200 });
  }
}

export async function DELETE() {
  try {
    const res = await fetch(`${DASHBOARD_API}/api/calls/reset`, {
      method: "DELETE",
    });
    const data = await res.json();
    return NextResponse.json(data);
  } catch (e: any) {
    return NextResponse.json({ error: "Reset failed" }, { status: 500 });
  }
}
