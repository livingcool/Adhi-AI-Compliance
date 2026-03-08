import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test('login page renders correctly', async ({ page }) => {
    await page.goto('/login');

    // Branding
    await expect(page.getByText('ROOTEDAI')).toBeVisible();

    // Form fields
    await expect(page.locator('#email')).toBeVisible();
    await expect(page.locator('#password')).toBeVisible();
    await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible();

    // Helper links
    await expect(page.getByText(/forgot password/i)).toBeVisible();
    await expect(page.getByText(/contact your administrator/i)).toBeVisible();
  });

  test('password field toggles visibility', async ({ page }) => {
    await page.goto('/login');

    const passwordInput = page.locator('#password');
    await expect(passwordInput).toHaveAttribute('type', 'password');

    // Click the show/hide toggle button (Eye icon)
    const toggleBtn = page.locator('button[aria-label*="password"], button:near(#password)').first();
    await toggleBtn.click();
    await expect(passwordInput).toHaveAttribute('type', 'text');

    await toggleBtn.click();
    await expect(passwordInput).toHaveAttribute('type', 'password');
  });

  test('invalid login shows error message', async ({ page }) => {
    await page.goto('/login');

    await page.locator('#email').fill('bad@example.com');
    await page.locator('#password').fill('wrongpassword');
    await page.getByRole('button', { name: /sign in/i }).click();

    // Error state should appear (AlertCircle + message)
    await expect(
      page.locator('[role="alert"], .text-red-400, [class*="error"]').first()
    ).toBeVisible({ timeout: 10_000 });
  });

  test('empty form submission shows validation', async ({ page }) => {
    await page.goto('/login');

    await page.getByRole('button', { name: /sign in/i }).click();

    // HTML5 required validation or custom error
    const emailInput = page.locator('#email');
    await expect(emailInput).toBeFocused();
  });

  test('protected route /dashboard redirects to login when unauthenticated', async ({ page }) => {
    // Clear any stored auth state
    await page.context().clearCookies();
    await page.evaluate(() => localStorage.clear());

    await page.goto('/');
    // Should redirect to login
    await expect(page).toHaveURL(/\/login/, { timeout: 10_000 });
  });

  test('protected route /systems redirects to login when unauthenticated', async ({ page }) => {
    await page.context().clearCookies();
    await page.evaluate(() => localStorage.clear());

    await page.goto('/systems');
    await expect(page).toHaveURL(/\/login/, { timeout: 10_000 });
  });

  test('protected route /incidents redirects to login when unauthenticated', async ({ page }) => {
    await page.context().clearCookies();
    await page.evaluate(() => localStorage.clear());

    await page.goto('/incidents');
    await expect(page).toHaveURL(/\/login/, { timeout: 10_000 });
  });
});
