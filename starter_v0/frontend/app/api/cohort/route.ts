import { NextResponse } from "next/server";
import cohortSummary from "@/data/cohort_summary.json";

export async function GET() {
  return NextResponse.json(cohortSummary);
}
