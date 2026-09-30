import { defineConfig, devices } from '@playwright/test';

const backendEnvironment = {
  ...process.env,
  NEXETL_DJANGO_DEBUG: 'true',
  NEXETL_DEV_SUPERADMIN_ENABLED: 'true',
  NEXETL_SESSION_COOKIE_SECURE: 'false',
  NEXETL_CSRF_COOKIE_SECURE: 'false',
  NEXETL_CSRF_TRUSTED_ORIGINS: 'http://localhost:5173',
};

export default defineConfig({
  testDir: './e2e',
  fullyParallel: false,
  globalSetup: './e2e/global-setup.ts',
  use: { baseURL: 'http://localhost:5173', ...devices['Desktop Chrome'] },
  webServer: [
    {
      command: 'cmd.exe /d /c "set NEXETL_DJANGO_DEBUG=true&& set NEXETL_DEV_SUPERADMIN_ENABLED=true&& set NEXETL_SESSION_COOKIE_SECURE=false&& set NEXETL_CSRF_COOKIE_SECURE=false&& set NEXETL_CSRF_TRUSTED_ORIGINS=http://localhost:5173&& uv run python manage.py runserver 127.0.0.1:8000 --noreload"',
      cwd: '../backend',
      env: backendEnvironment,
      url: 'http://127.0.0.1:8000/api/auth/session/',
      reuseExistingServer: false,
      timeout: 30_000,
    },
    {
      command: 'npm run dev -- --host 127.0.0.1',
      cwd: '.',
      url: 'http://127.0.0.1:5173',
      reuseExistingServer: false,
      timeout: 30_000,
    },
  ],
});
