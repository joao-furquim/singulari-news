/**
 * BullMQ job processor for ingesting curated news articles.
 *
 * Consumes `process-news` jobs published by the Python curator agent.
 * For each job the processor:
 *   1. Generates an AI summary via the Gemini API (falls back to the first
 *      two sentences of the content when the API is unavailable or unconfigured).
 *   2. Resolves the article's category — creating it in the database if it
 *      does not already exist — to ensure no article is dropped due to a
 *      missing category.
 *   3. Persists the article to the `news` table and creates a `news_queue`
 *      tracking entry.
 *   4. Updates the queue entry status to `processed`.
 *
 * @module processor
 */

import { GoogleGenerativeAI } from '@google/generative-ai';
import { Job } from 'bullmq';
import { DbClient } from './database';

const genAI = new GoogleGenerativeAI(process.env.AI_API_KEY ?? '');
const AI_MODEL = process.env.AI_MODEL ?? 'gemini-2.0-flash-lite';

/** Shape of the article payload published by the Python curator agent. */
interface ArticleData {
  title: string;
  source: string;
  content: string;
  published_at: string;
  category_slug: string;
}

/** Return value of {@link generateSummaryWithFallback}. */
interface SummaryResult {
  summary: string;
  ai_generated: boolean;
}

/**
 * Creates the BullMQ processor function bound to a database client.
 *
 * Returns an async function compatible with `Worker`'s processor argument.
 * The closure captures `dbClient` so the processor can persist articles
 * without relying on module-level state.
 *
 * @param dbClient - Active PostgreSQL client used for all database writes.
 * @returns An async BullMQ processor that handles `process-news` jobs.
 */
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
 * Resolves a category by slug, creating a new record when none exists.
 *
 * Ensures the ingestion pipeline never fails due to an unknown category slug
 * sent by the agent. The display name is derived by capitalising the slug
 * (e.g. `"health"` → `"Health"`).
 *
 * @param dbClient - Active PostgreSQL client.
 * @param slug - Category slug string (e.g. `"technology"`, `"ai"`).
 * @returns The UUID of the existing or newly created category row.
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

/**
 * Generates a summary for a news article, falling back to extracted text.
 *
 * Attempts to call the Gemini API to produce a concise 3-sentence summary.
 * On any API error (network failure, missing key, quota exceeded) it falls
 * back to {@link extractFirstTwoSentences} so the pipeline never stalls.
 *
 * @param title - Article headline used as context for the prompt.
 * @param content - Full article body (only the first 1000 characters are sent).
 * @returns An object containing the summary text and a flag indicating
 *          whether the summary was AI-generated.
 */
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

/**
 * Extracts the first two complete sentences from a block of text.
 *
 * Used as a deterministic fallback summary when the AI API is unavailable.
 * Sentence boundaries are detected by `.`, `!`, or `?` followed by
 * whitespace or end-of-string. Returns up to 200 characters of raw content
 * when no sentence boundaries are found.
 *
 * @param content - Full article body text.
 * @returns A string containing the first two sentences, or the first 200
 *          characters if sentence detection yields no matches.
 */
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
