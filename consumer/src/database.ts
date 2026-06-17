import { Pool } from 'pg';

export type DbClient = Pool;

export async function createDbClient(): Promise<DbClient> {
  const pool = new Pool({ connectionString: process.env.DATABASE_URL });
  await pool.query('SELECT 1');
  console.log('[consumer] PostgreSQL connection established');
  return pool;
}
