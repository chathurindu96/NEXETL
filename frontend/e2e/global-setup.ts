import { execFileSync } from 'node:child_process';
import { resolve } from 'node:path';

export default function globalSetup(): void {
  execFileSync('cmd.exe', [
    '/d', '/c',
    'set NEXETL_DJANGO_DEBUG=true&& set NEXETL_DEV_SUPERADMIN_ENABLED=true&& set NEXETL_SESSION_COOKIE_SECURE=false&& set NEXETL_CSRF_COOKIE_SECURE=false&& set NEXETL_CSRF_TRUSTED_ORIGINS=http://localhost:5173&& uv run python manage.py bootstrap_dev_superadmin',
  ], {
    cwd: resolve(import.meta.dirname, '../../backend'),
    env: process.env,
    stdio: 'inherit',
  });
}
