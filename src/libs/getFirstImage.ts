import fs from "fs";
import path from "path";

export function getFirstImage(id: string) {
  const dir = path.join(
    process.cwd(),
    "public",
    "media",
    id,
    "images"
  );

  try {
    const files = fs.readdirSync(dir)
      .filter(f => /\.(jpg|jpeg|png|webp)$/i.test(f))
      .sort();

    if (!files.length) return "/fallback.jpg";

    return `/media/${id}/images/${files[0]}`;
  } catch {
    return "/fallback.jpg";
  }
}