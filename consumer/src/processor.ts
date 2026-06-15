import { GoogleGenerativeAI } from "@google/generative-ai";
import { Job } from "bullmq";
import { DbClient } from "./database";

const genAI = new GoogleGenerativeAI(process.env.AI_API_KEY ?? "");
const AI_MODEL = process.env.AI_MODEL ?? "gemini-2.5-pro";

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

    const { summary, ai_generated } = await generateSummaryWithFallback(
      articleData.title,
      articleData.content
    );
    const newsId = await saveNews(dbClient, articleData, summary, ai_generated);
    await updateQueueStatus(dbClient, newsId, "processed");

    return { newsId, summary, ai_generated };
  };
}

async function generateSummaryWithFallback(
  title: string,
  content: string
): Promise<SummaryResult> {
  try {
    const model = genAI.getGenerativeModel({ model: AI_MODEL });
    const result = await model.generateContent(
      `Generate a concise summary (maximum 3 sentences) for the following news article:\n\nTitle: ${title}\n\nContent: ${content.slice(0, 1000)}`
    );
    return { summary: result.response.text(), ai_generated: true };
  } catch (error) {
    console.warn(`[processor] Gemini failed, using fallback: ${(error as Error).message}`);
    return { summary: extractFirstTwoSentences(content), ai_generated: false };
  }
}

function extractFirstTwoSentences(content: string): string {
  const sentences = content.match(/[^.!?]+[.!?]+/g) ?? [];
  const fallback = sentences.slice(0, 2).join(" ").trim();
  return fallback || content.slice(0, 200);
}

async function saveNews(
  dbClient: DbClient,
  articleData: ArticleData,
  summary: string,
  ai_generated: boolean
): Promise<string> {
  const categoryResult = await dbClient.query<{ id: string }>(
    "SELECT id FROM categories WHERE slug = $1",
    [articleData.category_slug]
  );

  const categoryId = categoryResult.rows[0]?.id;
  if (!categoryId) {
    throw new Error(`Category not found: ${articleData.category_slug}`);
  }

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
    ]
  );

  const newsId = newsResult.rows[0].id;

  await dbClient.query(
    `INSERT INTO news_queue (news_id, status) VALUES ($1, 'pending')`,
    [newsId]
  );

  return newsId;
}

async function updateQueueStatus(
  dbClient: DbClient,
  newsId: string,
  status: string
): Promise<void> {
  await dbClient.query(
    `UPDATE news_queue SET status = $1, processed_at = NOW() WHERE news_id = $2`,
    [status, newsId]
  );
}
