import { test, expect } from '@playwright/test';

test.describe('Optimax frontend showcase', () => {
  test('renders capability section and footer links', async ({ page }) => {
    await page.goto('/');

    await expect(page.getByRole('heading', { name: 'What this frontend showcases' })).toBeVisible();
    await expect(page.getByText('Solve Linear Programming models via Simplex')).toBeVisible();

    const repoLink = page.getByRole('link', { name: 'GitHub Repository' });
    await expect(repoLink).toBeVisible();
    await expect(repoLink).toHaveAttribute('href', 'https://github.com/dhruvhaldar/optimax');

    const licenseLink = page.getByRole('link', { name: 'MIT License' });
    await expect(licenseLink).toHaveAttribute('href', 'https://github.com/dhruvhaldar/optimax/blob/main/LICENSE');

    const authorLink = page.getByRole('link', { name: 'Dhruv Haldar' });
    await expect(authorLink).toHaveAttribute('href', 'https://dhruvhaldar.vercel.app/');
  });

  test('supports keyboard tab navigation', async ({ page }) => {
    await page.goto('/');

    const ipTab = page.getByRole('tab', { name: 'IP (B&B)' });
    await ipTab.click();
    await expect(ipTab).toHaveAttribute('aria-selected', 'true');

    await ipTab.focus();
    await page.keyboard.press('ArrowRight');

    const colGenTab = page.getByRole('tab', { name: 'Column Generation' });
    await expect(colGenTab).toBeFocused();
    await expect(colGenTab).toHaveAttribute('aria-selected', 'true');
  });
});
