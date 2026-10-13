import { getCollection } from 'astro:content';
import { CATEGORIES, SITE } from '../config';

export async function GET() {
  const posts = (await getCollection('posts', (p) => !p.data.draft)).sort((a, b) => b.data.date.valueOf() - a.data.date.valueOf());
  const pages = (await getCollection('pages')).filter((p) => p.id !== 'home');
  const day = (d: Date) => d.toISOString().slice(0, 10);
  const newest = posts.length ? day(posts[0].data.date) : undefined;
  const urls: { loc: string; lastmod?: string }[] = [
    { loc: `${SITE.url}/`, lastmod: newest },
    { loc: `${SITE.url}/our-winners/`, lastmod: newest },
    ...pages.map((p) => ({ loc: `${SITE.url}/${p.id}/` })),
    ...Object.keys(CATEGORIES)
      .filter((c) => posts.some((p) => p.data.categories.includes(c)))
      .map((c) => ({
        loc: `${SITE.url}/category/${c}/`,
        lastmod: day(posts.find((p) => p.data.categories.includes(c))!.data.date),
      })),
    ...posts.map((p) => ({ loc: `${SITE.url}/${p.id}/`, lastmod: day(p.data.date) })),
  ];
  const xml =
    `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n` +
    urls.map((u) => `  <url><loc>${u.loc}</loc>${u.lastmod ? `<lastmod>${u.lastmod}</lastmod>` : ''}</url>`).join('\n') +
    `\n</urlset>\n`;
  return new Response(xml, { headers: { 'Content-Type': 'application/xml; charset=utf-8' } });
}
