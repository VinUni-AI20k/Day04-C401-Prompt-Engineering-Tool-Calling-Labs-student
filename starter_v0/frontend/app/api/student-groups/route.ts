import { NextResponse } from "next/server";
import studentGroups from "@/data/student_groups.json";

export async function GET() {
  return NextResponse.json(studentGroups);
}
