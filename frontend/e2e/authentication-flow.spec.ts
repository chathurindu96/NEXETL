import AxeBuilder from '@axe-core/playwright';
import { expect, test } from '@playwright/test';

test('uses the real Django session for login, Pipeline registration, inspection, and logout', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveURL(/\/login\?next=%2Fpipelines%2Fnew$/);
  await expect(page.getByRole('heading', { name: 'Welcome to NEXETL' })).toBeVisible();
  await expect(page.getByRole('navigation')).toHaveCount(0);
  expect((await new AxeBuilder({ page }).analyze()).violations.filter((violation) => violation.impact === 'critical')).toEqual([]);

  await page.getByLabel('Username').fill('admin');
  await page.getByLabel('Password').fill('123');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page).toHaveURL(/\/pipelines\/new$/);
  await expect(page.getByRole('main')).toContainText('Create Pipeline Definition');
  await expect(page.getByRole('navigation', { name: 'Primary navigation' })).toBeVisible();
  expect((await new AxeBuilder({ page }).analyze()).violations.filter((violation) => violation.impact === 'critical')).toEqual([]);

  await page.getByRole('button', { name: 'Create Pipeline Definition' }).click();
  await expect(page).toHaveURL(/\/pipelines\/[0-9a-f-]{36}$/);
  const id = page.url().split('/').at(-1)!;
  await expect(page.getByRole('main')).toContainText(id);

  await page.getByRole('button', { name: 'Sign out' }).click();
  await expect(page).toHaveURL(/\/login$/);
  await page.goto(`/pipelines/${id}`);
  await expect(page).toHaveURL(/\/login\?next=/);
});
