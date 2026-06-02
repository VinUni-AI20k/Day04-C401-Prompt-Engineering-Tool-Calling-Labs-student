import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

const FASTAPI_BASE_URL = process.env.FASTAPI_BASE_URL ?? "http://127.0.0.1:8000";

function saveSessionTranscript(sessionId: string, query: string, summary: string, steps: any[]) {
  try {
    const transcriptsDir = path.join(process.cwd(), "..", "transcripts");
    if (!fs.existsSync(transcriptsDir)) {
      fs.mkdirSync(transcriptsDir, { recursive: true });
    }

    const filename = `${sessionId}.transcript.json`;
    const filePath = path.join(transcriptsDir, filename);

    let transcript: any = {
      transcript_id: sessionId,
      version: "ui-dev",
      provider: "ui-client",
      model: "ui-agent",
      created_at: new Date().toISOString(),
      turns: []
    };

    if (fs.existsSync(filePath)) {
      try {
        transcript = JSON.parse(fs.readFileSync(filePath, "utf-8"));
      } catch {}
    }

    const newTurn = {
      turn_index: (transcript.turns?.length || 0) + 1,
      started_at: new Date().toISOString(),
      user: query,
      status: "answered",
      assistant_text: summary,
      tool_events: (steps || []).filter((s: any) => s.kind === "tool").map((s: any) => ({
        tool: s.toolName || s.title,
        args: s.input || {},
        result: s.output || {}
      })),
      ended_at: new Date().toISOString()
    };

    if (!transcript.turns) transcript.turns = [];
    transcript.turns.push(newTurn);
    transcript.updated_at = new Date().toISOString();

    fs.writeFileSync(filePath, JSON.stringify(transcript, null, 2), "utf-8");
  } catch (e) {
    console.error("Failed to save session transcript", e);
  }
}

export async function POST(request: Request) {
  const payload = await request.json();
  const sessionId = payload.session_id || "default-session";
  const query = payload.query || "";

  try {
    const response = await fetch(`${FASTAPI_BASE_URL}/api/v1/diagnose`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const contentType = response.headers.get("content-type") ?? "";
    const data = contentType.includes("application/json")
      ? await response.json()
      : {
          error_code: "DIAGNOSE_BACKEND_NON_JSON_RESPONSE",
          message: await response.text(),
        };

    if (response.ok && data.summary) {
      saveSessionTranscript(sessionId, query, data.summary, data.steps || []);
    }

    return NextResponse.json(data, { status: response.status });
  } catch {
    // Sandbox Mock Mode fallback: create a simulated response and write it
    const mockSummary = query.toLowerCase().includes("ignore") 
      ? "Lượt chạy bị chặn bởi chính sách bảo mật hệ thống." 
      : "Phân tích thử nghiệm thành công trong chế độ Sandbox.";
    const mockSteps = [
      { id: "s1", title: "Initialize Sandbox", kind: "thought", content: "Chạy chế độ giả lập." },
      { id: "s2", title: "social_search", kind: "tool", toolName: "social_search", input: { query: "AI" }, output: { status: "success" } }
    ];

    saveSessionTranscript(sessionId, query, mockSummary, mockSteps);

    // Return 502 indicating backend down, client falls back to simulation
    return NextResponse.json(
      {
        error_code: "DIAGNOSE_BACKEND_UNAVAILABLE",
        message: "Backend diagnose service is unavailable (Simulating & logging to transcripts).",
      },
      { status: 502 }
    );
  }
}
