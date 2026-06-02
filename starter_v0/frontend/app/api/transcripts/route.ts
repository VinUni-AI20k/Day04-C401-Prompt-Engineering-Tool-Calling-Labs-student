import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const sessionId = searchParams.get("session_id");
    const list = searchParams.get("list");

    const transcriptsDir = path.join(process.cwd(), "..", "transcripts");
    if (!fs.existsSync(transcriptsDir)) {
      return NextResponse.json({ error: "No transcripts folder found" }, { status: 404 });
    }

    // Support listing all sessions
    if (list === "true") {
      const files = fs.readdirSync(transcriptsDir).filter(f => f.endsWith(".json"));
      const sessionList = files.map(file => {
        const filePath = path.join(transcriptsDir, file);
        const stats = fs.statSync(filePath);
        try {
          const content = fs.readFileSync(filePath, "utf-8");
          const parsed = JSON.parse(content);
          const turns = parsed.turns || [];
          const lastTurn = turns[turns.length - 1];
          const rawId = parsed.transcript_id || file.replace(".transcript.json", "");
          
          let title = "Chat Session";
          if (rawId.startsWith("session-new-")) {
            const tsStr = rawId.replace("session-new-", "");
            const ts = parseInt(tsStr, 10);
            title = !isNaN(ts) ? `Chat ${new Date(ts).toLocaleTimeString()}` : "New Chat";
          } else if (rawId.startsWith("session-")) {
            title = rawId.replace("session-", "Session ");
          }

          return {
            id: rawId,
            title: title,
            lastMessage: lastTurn ? (lastTurn.assistant_text || lastTurn.user || "No messages") : "Empty Chat",
            timestamp: stats.mtime.getTime(),
            messageCount: turns.length,
          };
        } catch {
          return {
            id: file.replace(".transcript.json", ""),
            title: "Chat Session",
            lastMessage: "Empty Chat",
            timestamp: stats.mtime.getTime(),
            messageCount: 0,
          };
        }
      });
      // Sort by mtime descending
      sessionList.sort((a, b) => b.timestamp - a.timestamp);
      return NextResponse.json(sessionList);
    }

    if (sessionId) {
      const filePath = path.join(transcriptsDir, `${sessionId}.transcript.json`);
      if (fs.existsSync(filePath)) {
        const content = fs.readFileSync(filePath, "utf-8");
        const parsed = JSON.parse(content);
        return NextResponse.json(parsed);
      }
      return NextResponse.json({ error: `Transcript not found for session ${sessionId}` }, { status: 404 });
    }

    const files = fs.readdirSync(transcriptsDir).filter(f => f.endsWith(".json"));

    if (files.length === 0) {
      return NextResponse.json({ error: "No transcripts found" }, { status: 404 });
    }
    
    // Sort files by mtime descending
    const fileDetails = files.map(file => {
      const filePath = path.join(transcriptsDir, file);
      const stats = fs.statSync(filePath);
      return {
        fileName: file,
        mtime: stats.mtime.getTime(),
        filePath
      };
    });
    fileDetails.sort((a, b) => b.mtime - a.mtime);
    
    const latestFile = fileDetails[0];
    const content = fs.readFileSync(latestFile.filePath, "utf-8");
    const parsed = JSON.parse(content);
    return NextResponse.json(parsed);
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}

