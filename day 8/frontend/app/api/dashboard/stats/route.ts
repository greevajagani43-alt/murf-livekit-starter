import { NextResponse } from "next/server";

const DASHBOARD_API = "http://localhost:8003";

export async function GET() {
  try {
    const res = await fetch(`${DASHBOARD_API}/api/dashboard/stats`, {
      cache: "no-store",
    });
    if (!res.ok) {
      throw new Error(`FastAPI responded with ${res.status}`);
    }
    const data = await res.json();
    return NextResponse.json(data);
  } catch (e: any) {
    return NextResponse.json(
      {
        totalCalls: 0,
        successfulCalls: 0,
        failedCalls: 0,
        error: "Dashboard API unavailable on port 8003",
      },
      { status: 200 }
    );
  }
}
