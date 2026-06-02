export type DiagnosticReportVersion = {
  version: string;
  date: string;
  averageScore: number;
  completionRate: number;
  atRiskCount: number;
  totalStudents: number;
  weakConcepts: { concept: string; score: number; weakPercent: number }[];
  groups: {
    name: string;
    reason: string;
    studentCount: number;
    actions: string[];
  }[];
};

export const mockReports: DiagnosticReportVersion[] = [
  {
    version: "v2 (Latest)",
    date: "2026-06-01",
    averageScore: 73,
    completionRate: 75,
    atRiskCount: 2,
    totalStudents: 8,
    weakConcepts: [
      { concept: "agentic_loops", score: 54, weakPercent: 75 },
      { concept: "reasoning", score: 59, weakPercent: 62 },
      { concept: "evaluation", score: 67, weakPercent: 50 },
      { concept: "tool_use", score: 71, weakPercent: 38 },
      { concept: "prompting", score: 76, weakPercent: 25 },
    ],
    groups: [
      {
        name: "Needs Foundation",
        reason: "Học viên đạt điểm dưới 50 trong bài kiểm tra chẩn đoán, chưa nắm vững khái niệm cơ bản.",
        studentCount: 2,
        actions: [
          "Tổ chức buổi học bổ sung về các khái niệm cơ bản (evaluation, prompting, reasoning).",
          "Cung cấp tài liệu học tập bổ sung và video hướng dẫn chi tiết.",
          "Lên lịch một-một mentoring với giảng viên để làm rõ khó khăn.",
        ],
      },
      {
        name: "Needs Practice",
        reason: "Học viên đạt điểm 50-75, hiểu được các khái niệm cơ bản nhưng cần luyện tập để cải thiện.",
        studentCount: 3,
        actions: [
          "Cung cấp bộ bài tập nâng cao về agentic loops và reasoning.",
          "Tổ chức các phiên thực hành nhóm nhỏ với sự hướng dẫn.",
        ],
      },
      {
        name: "Ready for Advanced",
        reason: "Học viên đạt điểm trên 75, nắm vững các khái niệm và sẵn sàng cho các bài tập nâng cao.",
        studentCount: 3,
        actions: [
          "Giao các dự án phức tạp liên quan đến tích hợp nhiều khái niệm.",
          "Mời học viên trở thành peer mentor cho các nhóm khác.",
        ],
      },
    ],
  },
  {
    version: "v1",
    date: "2026-05-31",
    averageScore: 68,
    completionRate: 62,
    atRiskCount: 4,
    totalStudents: 8,
    weakConcepts: [
      { concept: "agentic_loops", score: 48, weakPercent: 88 },
      { concept: "reasoning", score: 52, weakPercent: 75 },
      { concept: "tool_use", score: 63, weakPercent: 50 },
    ],
    groups: [
      {
        name: "Needs Foundation",
        reason: "Học viên đạt điểm dưới 50 trong bài kiểm tra chẩn đoán.",
        studentCount: 4,
        actions: [
          "Hỗ trợ cài đặt công cụ thực hành ban đầu.",
          "Giao bài tập cơ bản về lập trình python.",
        ],
      },
      {
        name: "Needs Practice",
        reason: "Học viên đạt điểm 50-75.",
        studentCount: 2,
        actions: [
          "Luyện tập viết các prompt cơ bản.",
        ],
      },
      {
        name: "Ready for Advanced",
        reason: "Học viên đạt điểm trên 75.",
        studentCount: 2,
        actions: [
          "Đọc thêm các paper nghiên cứu về AI Agent.",
        ],
      },
    ],
  },
];
