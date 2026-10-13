import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const posts = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/posts' }),
  schema: z.object({
    title: z.string(),
    date: z.coerce.date(),
    categories: z.array(z.string()).default([]),
    // YouTube URL or 11-character ID. Rendered as a click-to-load embed.
    youtube: z.string().optional(),
    // Local path (/uploads/...) or full URL.
    image: z.string().optional(),
    imageAlt: z.string().optional(),
    // Per-post meta description (search snippet + social card). Falls back to the site description.
    description: z.string().optional(),
    draft: z.boolean().default(false),
  }),
});

const pages = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/pages' }),
  schema: z.object({
    title: z.string(),
    description: z.string().optional(),
    youtube: z.string().optional(),
  }),
});

export const collections = { posts, pages };
