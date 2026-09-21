const { test, expect } = require('@playwright/test');

test.describe('Responsiveness and UI Checks', () => {
  const pages = [
    '/',
    '/platform',
    '/solutions',
    '/enterprise',
    '/pricing',
  ];

  const viewports = [
    { name: 'Mobile (iPhone 12)', width: 390, height: 844 },
    { name: 'Tablet (iPad Mini)', width: 768, height: 1024 },
    { name: 'Desktop (1080p)', width: 1920, height: 1080 },
  ];

  for (const pageUrl of pages) {
    test.describe(`Page: ${pageUrl}`, () => {
      for (const vp of viewports) {
        test(`Renders correctly on ${vp.name}`, async ({ page }) => {
          await page.setViewportSize({ width: vp.width, height: vp.height });
          await page.goto(pageUrl);
          
          // Basic check to ensure the page loaded and didn't crash
          await expect(page.locator('body')).toBeVisible();

          // Wait for any animations to settle
          await page.waitForTimeout(1000);

          // Check for horizontal scrolling (usually an indicator of broken responsiveness)
          const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
          const clientWidth = await page.evaluate(() => document.documentElement.clientWidth);
          expect(scrollWidth).toBeLessThanOrEqual(clientWidth + 1); // +1 for subpixel rounding
        });
      }
    });
  }

  test('Mobile Navigation Drawer (Landing)', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto('/');

    // Hamburger button should be visible
    const hamburger = page.locator('button[aria-label="Open menu"], button[aria-label="Close menu"]');
    await expect(hamburger).toBeVisible();

    // Click hamburger to open
    await hamburger.click();

    // Mobile nav drawer should now be visible
    const mobileNav = page.locator('nav#mobile-nav');
    await expect(mobileNav).toBeVisible();
    
    // Check if links are inside
    await expect(mobileNav.getByRole('link', { name: 'Platform' })).toBeVisible();
  });
});
