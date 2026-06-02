import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const sessionId = searchParams.get("session_id");

    const transcriptsDir = path.join(process.cwd(), "..", "transcripts");
    if (!fs.existsSync(transcriptsDir)) {
      return NextResponse.json({ error: "No transcripts folder found" }, { status: 404 });
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

