import fs from "fs";
import path from "path";

export function getAllVideos(id: string) {
  const dir = path.join(
    process.cwd(),
    "public",
    "media",
    id,
    "videos"
  );

  try {
    const files = fs.readdirSync(dir)
      .filter(f => /\.(mp4|mov|avi|mkv)$/i.test(f))
      .sort();

    if (!files.length) return ["/fallback.jpg"];

    // Devuelve un array con las rutas completas
    return files.map(f => `/media/${id}/videos/${f}`);
  } catch {
    return ["/fallback.jpg"];
  }
}
