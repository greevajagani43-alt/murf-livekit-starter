import { NextRequest, NextResponse } from "next/server";

const ESCALATIONS_API = "http://localhost:8002";

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const status = searchParams.get("status");
  const url = status
    ? `${ESCALATIONS_API}/escalations?status=${status}`
    : `${ESCALATIONS_API}/escalations`;

  try {
    const res = await fetch(url, { cache: "no-store" });
    const data = await res.json();
    return NextResponse.json(data);
  } catch {
    return NextResponse.json(
      { error: "Escalations service unavailable" },
      { status: 503 }
    );
  }
}
