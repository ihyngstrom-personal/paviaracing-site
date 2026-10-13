/** Plain-text meta description from a markdown/HTML body, cut at a word boundary. */
export function autoDescription(body = '', max = 155): string {
  let t = body
    .replace(/<figure[\s\S]*?<\/figure>/gi, ' ')
    .replace(/<style[\s\S]*?<\/style>/gi, ' ')
    .replace(/\[caption[^\]]*\][\s\S]*?\[\/caption\]/gi, ' ')
    .replace(/<[^>]+>/g, ' ')
    .replace(/!\[[^\]]*\]\([^)]*\)/g, ' ')
    .replace(/\[([^\]]+)\]\([^)]*\)/g, '$1')
    .replace(/^#{1,6}\s+.*$/gm, ' ')
    .replace(/^\s*\*?Watch the full race replay.*$/gim, ' ')
    .replace(/[*_`>]/g, '')
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/\s+/g, ' ')
    .trim();
  if (t.length <= max) return t;
  t = t.slice(0, max);
  const cut = t.lastIndexOf(' ');
  return (cut > 80 ? t.slice(0, cut) : t).replace(/[,;:\s-]+$/, '') + '…';
}
