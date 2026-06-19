import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const testConfig: any = {
  globals: true,
  environment: 'jsdom',
  setupFiles: ['./src/test/setup.ts'],
  css: false,
  // 'forks' pool isolates each test file in its own child process.
  // Heap limit is raised via NODE_OPTIONS in the npm test script so the flag
  // is inherited by all forked workers (vitest 4 removed poolOptions.forks).
  // singleFork runs all test files in one worker process — MUI's module graph
  // is loaded once instead of once per file, avoiding per-fork OOM.
  pool: 'forks',
  forks: { singleFork: true },
};

export default defineConfig({
  plugins: [react()],
  test: testConfig,
});
