export const SITE = {
  name: 'Pavia Racing Stable',
  description:
    'Joe Pavia Jr. has trained and driven Standardbred harness racing horses for over 44 years. Stabled in Wind Gap, Pennsylvania and Delray Beach, Florida. Race wins, news and stable updates.',
  url: 'https://www.paviaracing.com',
  email: 'jp@paviaracing.com',
};

export const NAV = [
  { label: 'Home', href: '/' },
  { label: 'Qualifications', href: '/qualifications/' },
  { label: 'Our Winners', href: '/our-winners/' },
  { label: 'Stable Roster', href: '/training-horse-pavia-stable-stable-roster/' },
];

// slug -> label. Same slugs as the WordPress category URLs.
export const CATEGORIES: Record<string, string> = {
  wins: 'Wins',
  news: 'News',
  'training-updates': 'Training Updates',
};

export const CATEGORY_DESCRIPTIONS: Record<string, string> = {
  wins: 'Race wins for the Pavia Racing Stable: Standardbred harness racing results and videos from Pocono Downs, Yonkers, Tioga Downs, the Meadowlands and more.',
  news: 'News from the Pavia Racing Stable, a Standardbred harness racing stable run by trainer and driver Joe Pavia Jr.',
  'training-updates': 'Training updates and stable reports from the Pavia Racing Stable in Pennsylvania and Florida.',
};

// Placeholder used where a post has no photo of its own.
export const DEFAULT_IMAGE = '/uploads/2026/08/WP-Posts-Default-Image.png';

export const SOCIAL = [{ label: 'Facebook', href: 'https://www.facebook.com/paviastable' }];
