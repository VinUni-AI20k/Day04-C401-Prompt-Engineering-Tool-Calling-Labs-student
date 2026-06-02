import { NextResponse } from "next/server";

export async function GET() {
  const fastapiBaseUrl = process.env.FASTAPI_BASE_URL || "http://127.0.0.1:8000";
  try {
    const res = await fetch(`${fastapiBaseUrl}/api/v1/version-log`, {
      cache: "no-store",
    });
    if (!res.ok) {
      return NextResponse.json(
        { error: "BACKEND_ERROR", details: `Backend returned status ${res.status}` },
        { status: 502 }
      );
    }
    const data = await res.json();
    return NextResponse.json(data);
  } catch (error: any) {
    console.error("Failed to fetch version-log from backend:", error);
    return NextResponse.json(
      { error: "BACKEND_UNAVAILABLE" },
      { status: 502 }
    );
  }
}
