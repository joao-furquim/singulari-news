import { GoogleGenerativeAI } from '@google/generative-ai';
import { Job } from 'bullmq';
import { DbClient } from './database';

const genAI = new GoogleGenerativeAI(process.env.AI_API_KEY ?? '');
const AI_MODEL = process.env.AI_MODEL ?? 'gemini-2.5-pro';

interface ArticleData {
  title: string;
  source: string;
  content: string;
  published_at: string;
  category_slug: string;
}

interface SummaryResult {
  summary: string;
  ai_generated: boolean;
}

export function createNewsProcessor(dbClient: DbClient) {
  return async (job: Job<ArticleData>) => {
    const articleData = job.data;
    console.log(`[processor] Processing: ${articleData.title}`);
    console.log(`[processor] Category slug from agent: ${articleData.category_slug}`);

    const { summary, ai_generated } = await generateSummaryWithFallback(
      articleData.title,
      articleData.content,
    );
    const newsId = await saveNews(dbClient, articleData, summary, ai_generated);
    await updateQueueStatus(dbClient, newsId, 'processed');

    return { newsId, summary, ai_generated };
  };
}

/**
 * Fetches an existing category by slug, or creates it if it doesn't exist.
 * Guarantees the pipeline never drops an article due to a missing category.
 */
async function getOrCreateCategory(dbClient: DbClient, slug: string): Promise<string> {
  const existing = await dbClient.query<{ id: string }>(
    'SELECT id FROM categories WHERE slug = $1',
    [slug],
  );
  if (existing.rows.length > 0) {
    return existing.rows[0].id;
  }

  // Capitalise slug to create a readable display name (e.g. "health" → "Health")
  const name = slug.charAt(0).toUpperCase() + slug.slice(1);
  const result = await dbClient.query<{ id: string }>(
    `INSERT INTO categories (id, name, slug, created_at)
     VALUES (gen_random_uuid(), $1, $2, NOW())
     RETURNING id`,
    [name, slug],
  );
  console.log(`[processor] New category created: ${slug} (name: "${name}")`);
  return result.rows[0].id;
}

async function generateSummaryWithFallback(
  title: string,
  content: string,
): Promise<SummaryResult> {
  try {
    const model = genAI.getGenerativeModel({ model: AI_MODEL });
    const result = await model.generateContent(
      `Generate a concise summary (maximum 3 sentences) for the following news article:\n\nTitle: ${title}\n\nContent: ${content.slice(0, 1000)}`,
    );
    return { summary: result.response.text(), ai_generated: true };
  } catch (error) {
    console.warn(
      `[processor] Gemini failed, using fallback: ${(error as Error).message}`,
    );
    return { summary: extractFirstTwoSentences(content), ai_generated: false };
  }
}

function extractFirstTwoSentences(content: string): string {
  const sentences = content.match(/[^.!?]+[.!?]+/g) ?? [];
  const fallback = sentences.slice(0, 2).join(' ').trim();
  return fallback || content.slice(0, 200);
}

async function saveNews(
  dbClient: DbClient,
  articleData: ArticleData,
  summary: string,
  ai_generated: boolean,
): Promise<string> {
  // get_or_create the category — never throw on unknown slugs
  const categoryId = await getOrCreateCategory(dbClient, articleData.category_slug);

  const newsResult = await dbClient.query<{ id: string }>(
    `INSERT INTO news (category_id, title, source, summary, content, published_at, ai_generated)
     VALUES ($1, $2, $3, $4, $5, $6, $7)
     RETURNING id`,
    [
      categoryId,
      articleData.title,
      articleData.source,
      summary,
      articleData.content,
      articleData.published_at,
      ai_generated,
    ],
  );

  const newsId = newsResult.rows[0].id;

  await dbClient.query(
    `INSERT INTO news_queue (news_id, status) VALUES ($1, 'pending')`,
    [newsId],
  );

  return newsId;
}

async function updateQueueStatus(
  dbClient: DbClient,
  newsId: string,
  status: string,
): Promise<void> {
  await dbClient.query(
    `UPDATE news_queue SET status = $1, processed_at = NOW() WHERE news_id = $2`,
    [status, newsId],
  );
}
