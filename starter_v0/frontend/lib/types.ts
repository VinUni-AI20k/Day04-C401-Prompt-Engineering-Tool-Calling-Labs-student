export type ConceptMastery = {
  evaluation: number;
  prompting: number;
  reasoning: number;
  tool_use: number;
  agentic_loops: number;
};

export type Student = {
  student_id: string;
  name: string;
  background: string;
  lab_completed: boolean;
  lab_score: number;
  diagnostic_score: number;
  variant_question_result: "correct" | "wrong";
  activity_level: "high" | "medium" | "low";
  journey_log: string;
  concept_mastery: ConceptMastery;
};

export type CohortSummary = {
  average_score: number;
  completion_rate: number;
  at_risk_count: number;
  total_students: number;
};

export type WeakConcept = {
  concept: string;
  average_mastery: number;
  weak_student_count: number;
  weak_percentage: number;
};

export type StudentGroupMember = {
  student_id: string;
  name: string;
};

export type StudentGroup = {
  group_name: string;
  students: StudentGroupMember[];
  reason: string;
  weak_concepts: string[];
};

export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: number;
  thinkingSteps?: SimulatedStep[];
  isSimulating?: boolean;
};

export type SimulatedStep = {
  id: string;
  title: string;
  kind: "thought" | "tool" | "observation" | "final" | "error";
  content: string;
  toolName?: string;
  status: "pending" | "running" | "completed";
  durationMs?: number;
  input?: unknown;
  output?: unknown;
  errorCode?: string;
};

export type ChatSession = {
  id: string;
  title: string;
  lastMessage: string;
  timestamp: number;
  messageCount: number;
};
