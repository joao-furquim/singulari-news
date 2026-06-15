import * as dotenv from "dotenv";
dotenv.config();

import { Worker } from "bullmq";
import { createNewsProcessor } from "./processor";
import { createDbClient } from "./database";

const REDIS_URL = process.env.REDIS_URL ?? "redis://redis:6379";
const QUEUE_NAME = "news-processing";

async function main() {
  const dbClient = await createDbClient();

  const worker = new Worker(
    QUEUE_NAME,
    createNewsProcessor(dbClient),
    {
      connection: { url: REDIS_URL },
      concurrency: 3,
    }
  );

  worker.on("completed", (job) => {
    console.log(`[consumer] Job completed: ${job.id}`);
  });

  worker.on("failed", (job, error) => {
    console.error(`[consumer] Job failed: ${job?.id} — ${error.message}`);
  });

  console.log(`[consumer] Waiting for jobs in queue: ${QUEUE_NAME}`);
}

main().catch((error) => {
  console.error("[consumer] Fatal error:", error);
  process.exit(1);
});
