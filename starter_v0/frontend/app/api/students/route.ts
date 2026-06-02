import { NextResponse } from "next/server";
import students from "@/data/students.json";

export async function GET() {
  return NextResponse.json(students);
}
