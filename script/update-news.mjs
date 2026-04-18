import fs from "node:fs/promises";
import path from "node:path";

const API_KEY = process.env.NEWSDATAHUB_API_KEY;

if (!API_KEY) {
  console.error("Missing NEWSDATAHUB_API_KEY");
  process.exit(1);
}

const API_URL = "https://api.newsdatahub.com/v1/top-news";

const params = new URLSearchParams({
  require_media: "true",
  hours: "24",
  sort_by: "date",
  deduplicate: "true",
  per_page: "20",
  fields: [
    "id",
    "title",
    "description",
    "media_url",
    "pub_date",
    "source_title",
    "source",
    "source_link",
    "article_link",
    "topics",
    "keywords",
    "sentiment"
  ].join(",")
});

function inferLocationFromText(text) {
  const value = (text || "").toLowerCase();

  const patterns = [
    { match: /\bfrance|paris\b/, name: "France", lat: 46.2276, lng: 2.2137, country: "FR" },
    { match: /\bgermany|berlin\b/, name: "Germany", lat: 51.1657, lng: 10.4515, country: "DE" },
    { match: /\bukraine|kyiv|kiev\b/, name: "Ukraine", lat: 48.3794, lng: 31.1656, country: "UA" },
    { match: /\brussia|moscow\b/, name: "Russia", lat: 61.5240, lng: 105.3188, country: "RU" },
    { match: /\bjapan|tokyo\b/, name: "Japan", lat: 36.2048, lng: 138.2529, country: "JP" },
    { match: /\bchina|beijing\b/, name: "China", lat: 35.8617, lng: 104.1954, country: "CN" },
    { match: /\bindia|delhi|new delhi\b/, name: "India", lat: 20.5937, lng: 78.9629, country: "IN" },
    { match: /\bcanada|ottawa|toronto\b/, name: "Canada", lat: 56.1304, lng: -106.3468, country: "CA" },
    { match: /\baustralia|sydney|melbourne\b/, name: "Australia", lat: -25.2744, lng: 133.7751, country: "AU" },
    { match: /\brazil|brasil|rio de janeiro|sao paulo\b/, name: "Brazil", lat: -14.2350, lng: -51.9253, country: "BR" },
    { match: /\bmexico|mexico city\b/, name: "Mexico", lat: 23.6345, lng: -102.5528, country: "MX" },
    { match: /\bisrael|jerusalem|tel aviv\b/, name: "Israel", lat: 31.0461, lng: 34.8516, country: "IL" },
    { match: /\bturkey|ankara|istanbul\b/, name: "Turkey", lat: 38.9637, lng: 35.2433, country: "TR" },
    { match: /\bunited kingdom|britain|england|london|uk\b/, name: "United Kingdom", lat: 55.3781, lng: -3.4360, country: "GB" },
    { match: /\bunited states|u\.s\.|usa|washington|new york\b/, name: "United States", lat: 39.8283, lng: -98.5795, country: "US" }
  ];

  for (const pattern of patterns) {
    if (pattern.match.test(value)) {
      return {
        name: pattern.name,
        lat: pattern.lat,
        lng: pattern.lng,
        country: pattern.country
      };
    }
  }

  return {
    name: "Global",
    lat: 0,
    lng: 0,
    country: null
  };
}

function safeString(value) {
  return typeof value === "string" ? value.trim() : "";
}

function normalizeTopics(topics) {
  if (Array.isArray(topics)) return topics.filter(Boolean);
  if (typeof topics === "string" && topics.trim()) return [topics.trim()];
  return [];
}

function normalizeKeywords(keywords) {
  if (Array.isArray(keywords)) return keywords.filter(Boolean);
  if (typeof keywords === "string" && keywords.trim()) return [keywords.trim()];
  return [];
}

function normalizeArticle(article, index) {
  const title = safeString(article.title);
  const description = safeString(article.description);
  const location = inferLocationFromText(`${title} ${description}`);
  const topics = normalizeTopics(article.topics);
  const keywords = normalizeKeywords(article.keywords);

  return {
    id: safeString(article.id) || safeString(article.article_link) || `story-${index}`,
    title,
    description,
    image: safeString(article.media_url) || null,
    publishedAt: safeString(article.pub_date) || null,
    source: safeString(article.source_title) || safeString(article.source) || null,
    url: safeString(article.article_link) || safeString(article.source_link) || null,

    location: {
      name: location.name,
      lat: location.lat,
      lng: location.lng
    },

    meta: {
      country: location.country,
      topics,
      keywords,
      sentiment: article.sentiment ?? null
    }
  };
}

async function fetchNews() {
  const response = await fetch(`${API_URL}?${params.toString()}`, {
    method: "GET",
    headers: {
      "X-API-Key": API_KEY,
      "Accept": "application/json"
    }
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`NewsDataHub request failed: ${response.status} ${body}`);
  }

  return response.json();
}

function getArticlesFromResponse(raw) {
  if (Array.isArray(raw?.results)) return raw.results;
  if (Array.isArray(raw?.articles)) return raw.articles;
  if (Array.isArray(raw?.data)) return raw.data;
  return [];
}

async function writeNewsJson(payload) {
  const outputPath = path.join(process.cwd(), "public", "news.json");
  await fs.mkdir(path.dirname(outputPath), { recursive: true });
  await fs.writeFile(outputPath, JSON.stringify(payload, null, 2) + "\n", "utf8");
  console.log(`Wrote ${payload.count} stories to ${outputPath}`);
}

async function main() {
  const raw = await fetchNews();
  const articles = getArticlesFromResponse(raw);

  console.log(`Fetched ${articles.length} raw articles`);

  const stories = articles
    .filter((article) => safeString(article.title))
    .map(normalizeArticle)
    .filter((story) => story.image);

  console.log(`Normalized ${stories.length} stories`);

  const payload = {
    updatedAt: new Date().toISOString(),
    count: stories.length,
    stories
  };

  await writeNewsJson(payload);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});