import { NextResponse } from "next/server";
import weakConcepts from "@/data/weak_concepts.json";

export async function GET() {
  return NextResponse.json(weakConcepts);
}
