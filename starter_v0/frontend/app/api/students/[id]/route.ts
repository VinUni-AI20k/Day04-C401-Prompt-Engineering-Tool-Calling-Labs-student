import { NextResponse } from "next/server";
import students from "@/data/students.json";
import studentGroups from "@/data/student_groups.json";
import type { Student } from "@/lib/types";

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  const student = (students as Student[]).find((s) => s.student_id === id);

  if (!student) {
    return NextResponse.json(
      { error: "Student not found" },
      { status: 404 }
    );
  }

  const group = studentGroups.find((g) =>
    g.students.some((s) => s.student_id === id)
  );

  const avgMastery = Math.round(
    Object.values(student.concept_mastery).reduce((a, b) => a + b, 0) / 5
  );

  return NextResponse.json({
    ...student,
    group_name: group?.group_name ?? "Unassigned",
    average_mastery: avgMastery,
    risk_level: avgMastery < 50 ? "high" : avgMastery < 70 ? "medium" : "low",
  });
}
