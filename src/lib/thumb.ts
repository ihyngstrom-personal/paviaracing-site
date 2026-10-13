import fs from 'node:fs';
import path from 'node:path';

// Maps /uploads/... or /galleries/... to its small WebP thumbnail in /thumbs/ when one exists
// (made by scripts/optimize-images.py). Falls back to the original path otherwise.
export function thumb(src: string | undefined): string | undefined {
  if (!src || !/^\/(uploads|galleries)\//.test(src)) return src;
  const rel = '/thumbs' + src + '.webp';
  return fs.existsSync(path.join(process.cwd(), 'public', rel)) ? rel : src;
}
