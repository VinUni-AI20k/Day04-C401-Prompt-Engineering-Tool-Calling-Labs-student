import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const sessionId = searchParams.get("session_id");
  
  const transcriptsDir = path.join(process.cwd(), "..", "transcripts");
  let watcher: fs.FSWatcher | null = null;

  const responseStream = new ReadableStream({
    start(controller) {
      if (!fs.existsSync(transcriptsDir)) {
        try {
          fs.mkdirSync(transcriptsDir, { recursive: true });
        } catch {
          controller.enqueue("data: {\"error\":\"No transcripts folder\"}\n\n");
          controller.close();
          return;
        }
      }

      const sendLatest = () => {
        try {
          if (sessionId) {
            // Find specific session file
            const filePath = path.join(transcriptsDir, `${sessionId}.transcript.json`);
            if (fs.existsSync(filePath)) {
              const content = fs.readFileSync(filePath, "utf-8");
              controller.enqueue(`data: ${content.replace(/\r?\n/g, "")}\n\n`);
              return;
            }
          }
          
          // Global fallback: Send latest transcript file
          const files = fs.readdirSync(transcriptsDir).filter(f => f.endsWith(".json"));
          if (files.length > 0) {
            const fileDetails = files.map(file => {
              const filePath = path.join(transcriptsDir, file);
              const stats = fs.statSync(filePath);
              return { fileName: file, mtime: stats.mtime.getTime(), filePath };
            });
            fileDetails.sort((a, b) => b.mtime - a.mtime);
            const content = fs.readFileSync(fileDetails[0].filePath, "utf-8");
            controller.enqueue(`data: ${content.replace(/\r?\n/g, "")}\n\n`);
          }
        } catch (e) {
          // ignore
        }
      };

      // Send initial data immediately on connect
      sendLatest();

      // Watch directory for changes
      watcher = fs.watch(transcriptsDir, (eventType, filename) => {
        if (filename && filename.endsWith(".json")) {
          // If a specific session is tracked, only trigger when it changes (or if it's new)
          if (sessionId) {
            if (filename === `${sessionId}.transcript.json`) {
              sendLatest();
            }
          } else {
            // Otherwise push any latest change
            sendLatest();
          }
        }
      });
    },
    cancel() {
      if (watcher) {
        watcher.close();
      }
    }
  });

  return new Response(responseStream, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      "Connection": "keep-alive",
    },
  });
}
