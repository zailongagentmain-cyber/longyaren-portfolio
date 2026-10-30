export default async function handler(req, res) {
  const slug = (req.query.slug || ['home'])[0];
  const target = `https://www.upwork.com/freelancers/longyaren?utm_source=longyaren&utm_medium=portfolio&utm_campaign=${encodeURIComponent(slug)}`;
  res.setHeader('Location', target);
  res.setHeader('Cache-Control', 'no-store');
  res.status(302).end();
}
