"use client";

import {
  Activity,
  BookOpen,
  ChevronDown,
  Clock3,
  GraduationCap,
  ListTodo,
  TrendingUp,
  User,
  Users,
  Wrench,
  CheckCircle2,
  ShieldAlert,
  Bot,
  FileText,
} from "lucide-react";
import { useEffect, useState } from "react";
import type { CohortSummary, Student, StudentGroup } from "@/lib/types";
import { traces, type AgentTrace, type TraceStep } from "@/lib/mock-traces";

const stepIcons = {
  thought: Bot,
  tool: Wrench,
  observation: CheckCircle2,
  final: CheckCircle2,
  error: ShieldAlert,
};

type TabType = "students" | "trace" | "report";

export function StudentDashboard({
  activeSessionId,
}: {
  activeSessionId: string;
}) {
  const [activeTab, setActiveTab] = useState<TabType>("students");
  const [students, setStudents] = useState<Student[]>([]);
  const [cohort, setCohort] = useState<CohortSummary | null>(null);
  const [groups, setGroups] = useState<StudentGroup[]>([]);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  // Retrieve current active trace details
  const activeTrace: AgentTrace = (() => {
    if (activeSessionId === "session-security") {
      return traces.find((t) => t.id === "security-blocked") || traces[1];
    }
    if (activeSessionId === "session-student") {
      return traces.find((t) => t.id === "timeout-fallback") || traces[2];
    }
    return traces[0]; // success-cohort-diagnostic
  })();

  useEffect(() => {
    async function load() {
      const [studentsRes, cohortRes, groupsRes] = await Promise.all([
        fetch("/api/students"),
        fetch("/api/cohort"),
        fetch("/api/student-groups"),
      ]);
      setStudents(await studentsRes.json());
      setCohort(await cohortRes.json());
      setGroups(await groupsRes.json());
      setLoading(false);
    }
    load();
  }, []);

  const getGroupForStudent = (id: string) =>
    groups.find((g) => g.students.some((s) => s.student_id === id));

  if (loading) {
    return (
      <aside className="flex items-center justify-center rounded-2xl border border-[rgba(11,9,7,0.12)] bg-[#fffcf6] shadow-sm lg:min-h-0">
        <div className="flex flex-col items-center gap-3">
          <div className="size-6 animate-spin rounded-full border-2 border-[rgba(11,9,7,0.1)] border-t-[#3c3a39]" />
          <p className="text-xs font-mono text-[#ff7300] font-semibold">/loading-metrics...</p>
        </div>
      </aside>
    );
  }

  return (
    <aside className="flex flex-col rounded-2xl border border-[rgba(11,9,7,0.12)] bg-[#fffcf6] shadow-sm lg:min-h-0">
      {/* Dynamic Tab Headers */}
      <div className="border-b border-[rgba(11,9,7,0.12)] p-2.5 bg-[#fffcf6] rounded-t-2xl">
        <div className="grid grid-cols-3 gap-1.5 rounded-xl bg-[#fefcf5] border border-[rgba(11,9,7,0.08)] p-1">
          <TabButton
            active={activeTab === "students"}
            label="Students"
            icon={Users}
            onClick={() => setActiveTab("students")}
          />
          <TabButton
            active={activeTab === "trace"}
            label="Trace"
            icon={Clock3}
            onClick={() => setActiveTab("trace")}
          />
          <TabButton
            active={activeTab === "report"}
            label="Report"
            icon={FileText}
            onClick={() => setActiveTab("report")}
          />
        </div>
      </div>

      {/* Tab Content Panels */}
      <div className="flex-1 overflow-auto p-3">
        {activeTab === "students" && (
          <div className="space-y-3">
            {cohort && <CohortCards cohort={cohort} />}
            
            <div className="space-y-3">
              {groups.map((group) => {
                const groupStudents = students.filter((student) =>
                  group.students.some((s) => s.student_id === student.student_id)
                );

                const groupColors: Record<string, { border: string; bg: string; text: string; dot: string }> = {
                  "Needs Foundation": {
                    border: "border-[#ff272d]/30",
                    bg: "bg-[#ff272d]/[0.04]",
                    text: "text-[#ff272d] font-bold",
                    dot: "bg-[#ff272d]",
                  },
                  "Needs Practice": {
                    border: "border-[#ff7300]/30",
                    bg: "bg-[#ff7300]/[0.04]",
                    text: "text-[#ff7300] font-bold",
                    dot: "bg-[#ff7300]",
                  },
                  "Ready for Advanced": {
                    border: "border-[#22c55e]/30",
                    bg: "bg-[#22c55e]/[0.04]",
                    text: "text-[#22c55e] font-bold",
                    dot: "bg-[#22c55e]",
                  },
                };

                const colors = groupColors[group.group_name] || {
                  border: "border-[rgba(11,9,7,0.12)]",
                  bg: "bg-[#fffcf6]",
                  text: "text-[#3c3a39]",
                  dot: "bg-[#3c3a39]",
                };

                return (
                  <div
                    key={group.group_name}
                    className={`rounded-xl border p-2.5 space-y-2 ${colors.border} ${colors.bg} shadow-sm`}
                  >
                    <div className="flex items-center justify-between px-1">
                      <div className="flex items-center gap-2">
                        <span className={`size-2 rounded-full ${colors.dot}`} />
                        <span className={`text-[10px] font-mono uppercase tracking-wider ${colors.text}`}>
                          /{group.group_name.toLowerCase().replace(" ", "-")}
                        </span>
                      </div>
                      <span className="rounded-full bg-[#fefcf5] border border-[rgba(11,9,7,0.1)] px-1.5 py-0.5 text-[9px] text-[#3c3a39]/60 font-semibold shadow-xs">
                        {groupStudents.length} members
                      </span>
                    </div>

                    <div className="space-y-1.5">
                      {groupStudents.map((student) => (
                        <StudentCard
                          expanded={expandedId === student.student_id}
                          group={group}
                          key={student.student_id}
                          onToggle={() =>
                            setExpandedId(
                              expandedId === student.student_id ? null : student.student_id
                            )
                          }
                          student={student}
                        />
                      ))}
                      {groupStudents.length === 0 && (
                        <p className="text-[11px] text-[rgba(11,9,7,0.5)] text-center py-2">
                          No students in this group.
                        </p>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {activeTab === "trace" && (
          <div className="space-y-4">
            <div className="grid grid-cols-3 gap-2">
              <Metric label="Latency" value={`${activeTrace.latencyMs}ms`} warning={activeTrace.latencyMs > 5000} />
              <Metric label="Prompt" value={String(activeTrace.promptTokens)} />
              <Metric label="Output" value={String(activeTrace.completionTokens)} />
            </div>

            <div className="rounded-xl border border-[rgba(11,9,7,0.1)] bg-[#fefcf5] p-3 shadow-xs">
              <p className="font-mono text-[10px] uppercase tracking-wider text-[#817fff] font-bold">
                /telemetry-summary
              </p>
              <p className="mt-2 text-sm leading-6 text-[#3c3a39] font-medium">{activeTrace.summary}</p>
            </div>

            <div className="space-y-2">
              <p className="font-mono text-[10px] uppercase tracking-wider text-[#ff7300] font-bold">
                /mini-trace-steps
              </p>
              {activeTrace.steps.map((step, index) => (
                <TraceMiniStep index={index + 1} key={step.id} step={step} />
              ))}
            </div>
          </div>
        )}

        {activeTab === "report" && (
          <div className="space-y-4">
            <div className="rounded-xl border border-[rgba(11,9,7,0.12)] bg-[#fefcf5] p-4 text-center shadow-xs">
              <h3 className="text-sm font-bold text-[#3c3a39]">Cohort Remediation Strategy</h3>
              <p className="mt-1 font-mono text-[10px] text-[#2677ff] font-semibold">
                /tailored-intervention-plans
              </p>
            </div>

            <div className="space-y-3">
              {groups.map((group) => (
                <GroupPlanCard key={group.group_name} group={group} />
              ))}
            </div>
          </div>
        )}
      </div>
    </aside>
  );
}

function TabButton({
  active,
  label,
  icon: Icon,
  onClick,
}: {
  active: boolean;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  onClick: () => void;
}) {
  return (
    <button
      className={`flex items-center justify-center gap-1.5 rounded-lg py-1.5 text-xs font-semibold transition-all ${
        active
          ? "bg-[#3c3a39] text-[#fefcf5] shadow-md border border-[#3c3a39]"
          : "text-[rgba(11,9,7,0.5)] border border-transparent hover:text-[#3c3a39] hover:bg-[#eaeae2]/30"
      }`}
      onClick={onClick}
      type="button"
    >
      <Icon className="size-3.5" />
      <span>{label}</span>
    </button>
  );
}

function CohortCards({ cohort }: { cohort: CohortSummary }) {
  return (
    <div className="grid grid-cols-2 gap-2">
      <MiniMetric
        icon={Users}
        label="Students"
        value={String(cohort.total_students)}
      />
      <MiniMetric
        icon={TrendingUp}
        label="Avg Score"
        value={String(cohort.average_score)}
        accent={cohort.average_score >= 70 ? "emerald" : "amber"}
      />
      <MiniMetric
        icon={ShieldAlert}
        label="At Risk"
        value={String(cohort.at_risk_count)}
        accent={cohort.at_risk_count > 0 ? "red" : "emerald"}
      />
      <MiniMetric
        icon={GraduationCap}
        label="Completion"
        value={`${cohort.completion_rate}%`}
      />
    </div>
  );
}

function MiniMetric({
  icon: Icon,
  label,
  value,
  accent,
}: {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  value: string;
  accent?: "emerald" | "amber" | "red";
}) {
  const accentColors = {
    emerald: "text-[#22c55e]",
    amber: "text-[#ff7300]",
    red: "text-[#ff272d]",
  };

  return (
    <div className="rounded-xl border border-[rgba(11,9,7,0.06)] bg-[#fefcf5] p-3">
      <div className="flex items-center gap-1.5">
        <Icon className="size-3 text-[rgba(11,9,7,0.4)]" />
        <span className="font-mono text-[9px] uppercase tracking-wider text-[rgba(11,9,7,0.4)]">
          /{label.toLowerCase().replace(" ", "-")}
        </span>
      </div>
      <p
        className={`mt-1 text-base font-semibold ${
          accent ? accentColors[accent] : "text-[#3c3a39]"
        }`}
      >
        {value}
      </p>
    </div>
  );
}

function StudentCard({
  student,
  group,
  expanded,
  onToggle,
}: {
  student: Student;
  group?: StudentGroup;
  expanded: boolean;
  onToggle: () => void;
}) {
  const avgMastery = Math.round(
    Object.values(student.concept_mastery).reduce((a, b) => a + b, 0) / 5
  );
  const riskLevel =
    avgMastery < 50 ? "high" : avgMastery < 70 ? "medium" : "low";

  const riskStyles = {
    high: "border-[#ff272d]/20 bg-[#ff272d]/5 text-[#ff272d]",
    medium: "border-[#ff7300]/20 bg-[#ff7300]/5 text-[#ff7300]",
    low: "border-[#22c55e]/20 bg-[#22c55e]/5 text-[#22c55e]",
  };

  const activityColors = {
    high: "text-[#22c55e]",
    medium: "text-[#ff7300]",
    low: "text-[#ff272d]",
  };

  return (
    <div className="overflow-hidden rounded-xl border border-[rgba(11,9,7,0.06)] bg-[#fefcf5] transition-colors hover:bg-[#eaeae2]/30">
      <button
        className="flex w-full items-center gap-3 p-3 text-left"
        onClick={onToggle}
        type="button"
      >
        <div className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-[#fffcf6] border border-[rgba(11,9,7,0.08)] shadow-sm">
          <User className="size-3.5 text-[rgba(11,9,7,0.5)]" />
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex items-center justify-between">
            <span className="truncate text-sm font-semibold text-[#3c3a39]">
              {student.name}
            </span>
            <span
              className={`rounded-full border px-1.5 py-px text-[9px] font-medium ${riskStyles[riskLevel]}`}
            >
              {riskLevel}
            </span>
          </div>
          <div className="mt-0.5 flex items-center gap-2 text-[11px] text-[rgba(11,9,7,0.5)]">
            <span>Lab: {student.lab_score}</span>
            <span>·</span>
            <span>Diag: {student.diagnostic_score}</span>
            <span>·</span>
            <span className={`font-mono text-[10px] uppercase ${activityColors[student.activity_level]}`}>
              {student.activity_level}
            </span>
          </div>
        </div>
        <ChevronDown
          className={`size-4 shrink-0 text-[rgba(11,9,7,0.4)] transition-transform ${
            expanded ? "rotate-180" : ""
          }`}
        />
      </button>

      {expanded && (
        <div className="space-y-3 border-t border-[rgba(11,9,7,0.08)] p-3 bg-[#fffcf6]">
          <div>
            <p className="mb-2 font-mono text-[9px] font-semibold uppercase tracking-wider text-[rgba(11,9,7,0.4)]">
              /concept-mastery-index
            </p>
            <div className="space-y-1.5">
              {Object.entries(student.concept_mastery).map(
                ([concept, score]) => (
                  <ConceptBar concept={concept} key={concept} score={score} />
                )
              )}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-2">
            <div className="rounded-lg border border-[rgba(11,9,7,0.08)] bg-[#fefcf5] p-2">
              <p className="font-mono text-[8px] uppercase tracking-wider text-[rgba(11,9,7,0.4)]">
                /background
              </p>
              <p className="mt-0.5 text-xs font-semibold text-[#3c3a39]">
                {student.background}
              </p>
            </div>
            <div className="rounded-lg border border-[rgba(11,9,7,0.08)] bg-[#fefcf5] p-2">
              <p className="font-mono text-[8px] uppercase tracking-wider text-[rgba(11,9,7,0.4)]">
                /variant-q
              </p>
              <p
                className={`mt-0.5 text-xs font-semibold ${
                  student.variant_question_result === "correct"
                    ? "text-[#22c55e]"
                    : "text-[#ff272d]"
                }`}
              >
                {student.variant_question_result}
              </p>
            </div>
          </div>

          {group && (
            <div className="flex items-start gap-2 rounded-lg border border-[rgba(11,9,7,0.08)] bg-[#fefcf5] p-2">
              <BookOpen className="mt-0.5 size-3 shrink-0 text-[#2677ff]/70" />
              <div>
                <p className="text-[10px] font-bold text-[#2677ff]">
                  {group.group_name}
                </p>
                <p className="mt-0.5 text-[10px] leading-4 text-[rgba(11,9,7,0.5)]">
                  {group.reason}
                </p>
              </div>
            </div>
          )}

          <div className="flex items-start gap-2 rounded-lg border border-[rgba(11,9,7,0.08)] bg-[#fefcf5] p-2">
            <Activity className="mt-0.5 size-3 shrink-0 text-[rgba(11,9,7,0.4)]" />
            <p className="text-[10px] leading-4 text-[rgba(11,9,7,0.6)]">
              {student.journey_log}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

function ConceptBar({ concept, score }: { concept: string; score: number }) {
  // Pastel brand color mapping drawn from Tavily design palette
  const conceptColors: Record<string, string> = {
    evaluation: "bg-[#f49eff]",      // electric pink
    prompting: "bg-[#ffc753]",       // warm soft yellow
    reasoning: "bg-[#817fff]",       // lavender purple
    tool_use: "bg-[#2677ff]",        // primary blue
    agentic_loops: "bg-[#ff7300]",   // voltage orange
  };

  const barColor = conceptColors[concept] || "bg-[#ff272d]";

  const conceptLabels: Record<string, string> = {
    evaluation: "Evaluation",
    prompting: "Prompting",
    reasoning: "Reasoning",
    tool_use: "Tool Use",
    agentic_loops: "Agentic Loops",
  };

  return (
    <div className="flex items-center gap-2">
      <span className="w-20 shrink-0 text-[10px] font-medium text-[rgba(11,9,7,0.5)]">
        {conceptLabels[concept] ?? concept}
      </span>
      <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-[#eaeae2]">
        <div
          className={`h-full rounded-full transition-all ${barColor}`}
          style={{ width: `${score}%` }}
        />
      </div>
      <span className="w-7 shrink-0 text-right text-[10px] font-semibold text-[#3c3a39]">
        {score}
      </span>
    </div>
  );
}

function Metric({
  label,
  value,
  warning = false,
}: {
  label: string;
  value: string;
  warning?: boolean;
}) {
  return (
    <div
      className={`rounded-xl border p-3 bg-[#fefcf5] ${
        warning ? "border-[#ff272d]/30 bg-[#ff272d]/5 text-[#ff272d]" : "border-[rgba(11,9,7,0.06)]"
      }`}
    >
      <p className="font-mono text-[9px] uppercase tracking-wider text-[rgba(11,9,7,0.4)]">/{label.toLowerCase()}</p>
      <p className={`mt-1 text-sm font-semibold ${warning ? "text-[#ff272d]" : "text-[#3c3a39]"}`}>{value}</p>
    </div>
  );
}

function TraceMiniStep({ step, index }: { step: TraceStep; index: number }) {
  const Icon = stepIcons[step.kind] || Wrench;

  return (
    <div className="rounded-xl border border-[rgba(11,9,7,0.06)] bg-[#fefcf5] p-3 shadow-sm">
      <div className="flex items-start gap-3">
        <div className="flex size-7 shrink-0 items-center justify-center rounded-full border border-[rgba(11,9,7,0.1)] bg-[#fffcf6] text-xs text-[#3c3a39] font-mono">
          {index}
        </div>
        <div className="min-w-0 flex-1">
          <div className="mb-1 flex items-center gap-2">
            <Icon className="size-3.5 text-[rgba(11,9,7,0.4)]" />
            <p className="truncate text-sm font-semibold text-[#3c3a39]">{step.title}</p>
          </div>
          <p className="line-clamp-2 text-xs leading-5 text-[rgba(11,9,7,0.5)]">{step.content}</p>
          <div className="mt-2">
            {step.errorCode ? (
              <span className="rounded-full border border-[#ff272d]/30 bg-[#ff272d]/10 px-2 py-0.5 text-[9px] text-[#ff272d] font-semibold">
                {step.errorCode}
              </span>
            ) : (
              <span className="rounded-full border border-[#22c55e]/30 bg-[#22c55e]/10 px-2 py-0.5 text-[9px] text-[#22c55e] font-semibold">
                completed · {step.durationMs || 100}ms
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function GroupPlanCard({ group }: { group: StudentGroup }) {
  const mockActions: Record<string, string[]> = {
    "Needs Foundation": [
      "Tổ chức buổi học bổ sung về các khái niệm cơ bản (evaluation, prompting, reasoning)",
      "Cung cấp tài liệu học tập bổ sung và video hướng dẫn chi tiết",
      "Lên lịch một-một mentoring với giảng viên để làm rõ khó khăn",
      "Giao bài tập thực hành nhẹ nhàng và có hướng dẫn từng bước",
      "Theo dõi tiến độ hàng tuần và điều chỉnh chiến lược hỗ trợ",
    ],
    "Needs Practice": [
      "Cung cấp bộ bài tập nâng cao về agentic loops và reasoning",
      "Tổ chức các phiên thực hành nhóm nhỏ với sự hướng dẫn",
      "Khuyến khích tham gia các cuộc thảo luận và chia sẻ kinh nghiệm",
      "Đưa ra các project mini để áp dụng kiến thức vào thực tế",
      "Cấu trúc các bài học từ dễ đến khó để xây dựng sự tự tin",
    ],
    "Ready for Advanced": [
      "Giao các dự án phức tạp liên quan đến tích hợp nhiều khái niệm",
      "Mời học viên trở thành peer mentor cho các nhóm khác",
      "Cung cấp tài liệu nghiên cứu nâng cao và các case study thực tế",
      "Khuyến khích khám phá các ứng dụng tiên tiến của AI Agent",
      "Chuẩn bị cho các cơ hội thực tập hoặc dự án thực tế",
    ],
  };

  const borderStyles: Record<string, string> = {
    "Needs Foundation": "border-[#ff272d]/20 bg-[#ff272d]/[0.02]",
    "Needs Practice": "border-[#ff7300]/20 bg-[#ff7300]/[0.02]",
    "Ready for Advanced": "border-[#22c55e]/20 bg-[#22c55e]/[0.02]",
  };

  const textStyles: Record<string, string> = {
    "Needs Foundation": "text-[#ff272d]",
    "Needs Practice": "text-[#ff7300]",
    "Ready for Advanced": "text-[#22c55e]",
  };

  const actions = mockActions[group.group_name] || [];

  return (
    <div className={`rounded-xl border p-4 ${borderStyles[group.group_name] || "border-[rgba(11,9,7,0.1)]"}`}>
      <div className="flex items-center justify-between">
        <h4 className={`text-sm font-bold ${textStyles[group.group_name] || "text-[#3c3a39]"}`}>
          {group.group_name}
        </h4>
        <span className="rounded-full bg-[#fefcf5] border border-[rgba(11,9,7,0.06)] px-2 py-0.5 text-[9px] text-[rgba(11,9,7,0.5)]">
          {group.students.length} students
        </span>
      </div>
      <p className="mt-1 text-xs leading-4 text-[rgba(11,9,7,0.5)]">{group.reason}</p>

      {group.weak_concepts.length > 0 && (
        <div className="mt-2.5 flex flex-wrap gap-1.5">
          {group.weak_concepts.map((concept) => (
            <span
              key={concept}
              className="rounded-lg bg-[#f7f7f5] border border-[rgba(11,9,7,0.08)] px-2 py-0.5 font-mono text-[9px] text-[rgba(11,9,7,0.5)] uppercase tracking-wider"
            >
              {concept}
            </span>
          ))}
        </div>
      )}

      <div className="mt-3.5 space-y-2">
        <p className="font-mono text-[9px] font-semibold uppercase tracking-wider text-[rgba(11,9,7,0.4)] flex items-center gap-1">
          <ListTodo className="size-3" /> /action-plan
        </p>
        <ul className="space-y-1.5 pl-3 list-disc text-[11px] text-[rgba(11,9,7,0.6)] leading-4">
          {actions.map((action, i) => (
            <li key={i}>{action}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
