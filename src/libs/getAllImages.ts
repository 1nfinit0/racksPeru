import fs from "fs";
import path from "path";

export function getAllImages(id: string) {
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

    if (!files.length) return ["/fallback.jpg"];

    // Devuelve un array con las rutas completas
    return files.map(f => `/media/${id}/images/${f}`);
  } catch {
    return ["/fallback.jpg"];
  }
}
