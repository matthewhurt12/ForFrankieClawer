#!/usr/bin/env node
// page-map.mjs - Dump the accessibility tree of a web page
// Usage: node page-map.mjs <url> [output.json] [--headed]

import { chromium } from 'playwright';
import { writeFile, mkdir } from 'node:fs/promises';
import { dirname } from 'node:path';

const args = process.argv.slice(2);
const headed = args.includes('--headed');
const url = args.find(a => a.startsWith('http'));
const outputPath = args.find(a => a.endsWith('.json')) || `/tmp/page-map-${Date.now()}.json`;

if (!url) {
  console.error('Usage: page-map.mjs <url> [output.json] [--headed]');
  process.exit(1);
}

const profileDir = '/home/matthew/siro-browser-profile';

console.log(`Mapping: ${url}`);
console.log(`Output: ${outputPath}`);

const browser = await chromium.launchPersistentContext(profileDir, {
  headless: !headed,
  executablePath: '/snap/bin/chromium',
  viewport: { width: 1280, height: 900 },
  args: ['--disable-blink-features=AutomationControlled'],
});

const page = browser.pages()[0] || await browser.newPage();

try {
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.waitForTimeout(2000); // settle

  // Get the ARIA snapshot (modern Playwright way - YAML-like accessibility tree)
  const ariaSnapshot = await page.locator('body').ariaSnapshot();

  // Also extract a flat list of interactive elements via DOM evaluation
  const interactive = await page.evaluate(() => {
    const interactiveSelectors = [
      'button', 'a[href]', 'input', 'textarea', 'select',
      '[role="button"]', '[role="link"]', '[role="textbox"]',
      '[role="checkbox"]', '[role="radio"]', '[role="combobox"]',
      '[role="menuitem"]', '[contenteditable="true"]',
    ];
    const elements = document.querySelectorAll(interactiveSelectors.join(','));
    const results = [];
    for (const el of elements) {
      const tag = el.tagName.toLowerCase();
      const role = el.getAttribute('role') || tag;
      const name = el.getAttribute('aria-label') || 
                   el.getAttribute('placeholder') ||
                   el.getAttribute('title') ||
                   el.getAttribute('alt') ||
                   el.value ||
                   el.innerText?.trim().slice(0, 80) ||
                   el.getAttribute('name') ||
                   '';
      const id = el.id || '';
      const className = typeof el.className === 'string' ? el.className.split(' ').slice(0, 3).join(' ') : '';
      const type = el.getAttribute('type') || '';
      const value = el.value || '';
      const visible = el.offsetParent !== null;
      const rect = el.getBoundingClientRect();
      
      // Build selector hints
      const hints = [];
      if (id) hints.push(`#${id}`);
      if (el.getAttribute('name')) hints.push(`${tag}[name="${el.getAttribute('name')}"]`);
      if (el.getAttribute('aria-label')) hints.push(`[aria-label="${el.getAttribute('aria-label')}"]`);
      if (name && ['button', 'a', 'link'].includes(role)) hints.push(`${role}:has-text("${name}")`);
      if (type) hints.push(`${tag}[type="${type}"]`);
      
      results.push({
        tag,
        role,
        type,
        name,
        value,
        id,
        className,
        visible,
        x: Math.round(rect.x),
        y: Math.round(rect.y),
        selectorHints: hints,
      });
    }
    return results;
  });

  const result = {
    url: page.url(),
    title: await page.title(),
    timestamp: new Date().toISOString(),
    interactiveCount: interactive.length,
    interactive,
    ariaSnapshot,
  };

  await mkdir(dirname(outputPath), { recursive: true });
  await writeFile(outputPath, JSON.stringify(result, null, 2));
  
  // Also save a screenshot
  const screenshotPath = outputPath.replace(/\.json$/, '.png');
  await page.screenshot({ path: screenshotPath, fullPage: false });

  console.log(`\nFound ${interactive.length} interactive elements`);
  console.log(`Tree saved to: ${outputPath}`);
  console.log(`Screenshot:    ${screenshotPath}`);
  console.log(`\nInteractive elements (visible only):`);
  interactive.filter(el => el.visible).forEach((el, i) => {
    const label = el.name ? `"${el.name}"` : '(no label)';
    console.log(`  ${i+1}. [${el.role}${el.type ? `:${el.type}` : ''}] ${label}${el.value ? ` = "${el.value}"` : ''}`);
    if (el.selectorHints?.length) console.log(`     hints: ${el.selectorHints.slice(0, 2).join(' | ')}`);
  });
} finally {
  await browser.close();
}
