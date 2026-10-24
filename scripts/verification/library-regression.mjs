// Manual local check; uses the existing isolated Playwright installation, no skill activation.
const { chromium } = await import(process.env.PLAYWRIGHT_MODULE || '/Users/hamza/runtimes/playwright/node_modules/playwright/index.mjs');
import { readFileSync, mkdirSync, writeFileSync } from 'node:fs';
const evidence = 'docs/verification/library-2026-10-24';
mkdirSync(evidence + '/screenshots', { recursive: true });
const browser = await chromium.launch({ channel: 'chrome', headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 1100 } });
const errors = [];
page.on('pageerror', error => errors.push(error.message));
const assert = (value, message) => { if (!value) throw new Error(message); };
const result = { films: [], scope: 'Actual seeks and displayed source text; not listening approval or a complete accessibility audit.' };
try {
  await page.goto('http://127.0.0.1:3000');
  await page.waitForFunction(() => document.querySelector('video')?.readyState >= 1);
  assert(await page.locator('#film-choice option').count() === 3, 'Three films available');
  await page.locator('.cue-row').nth(10).click();
  await page.getByRole('button', { name: 'Rich', exact: true }).click();
  await page.getByRole('button', { name: 'Preview this cue in the video', exact: true }).click();
  await page.locator('.caption-preview-notice').waitFor({ state: 'visible' });
  for (const id of ['sintel', 'tears-of-steel']) {
    const data = JSON.parse(readFileSync('data/captions/' + id + '.json', 'utf8'));
    await page.locator('#film-choice').selectOption(id);
    await page.waitForFunction(identity => document.querySelector('video')?.getAttribute('src') === '/media/' + identity + '.mp4' && document.querySelector('video')?.readyState >= 1, id);
    assert(await page.locator('.caption-preview-notice').count() === 0, 'Old preview cleared');
    assert(await page.locator('.cue-row:not(.dialogue-row)').count() === 0, 'Old film sound cues cleared');
    assert(await page.locator('.caption-lines').count() === 0, 'No invented sound cues');
    assert(await page.locator('#detail').isDisabled(), 'Unavailable sound preferences disabled');
    assert((await page.locator('.page-footer').innerText()).includes(data.title), 'Credits follow selected title');
    assert((await page.locator('video').getAttribute('poster')).endsWith(id + '-poster.jpg'), 'Poster follows film');
    const duration = await page.locator('video').evaluate(el => el.duration);
    assert(Math.abs(duration - data.duration_seconds) < .1, 'Exact media duration');
    for (const cue of data.dialogue) {
      const seconds = (cue.start_s + cue.end_s) / 2;
      const expected = data.dialogue.filter(item => item.start_s <= seconds && seconds < item.end_s).map(item => item.text).join('');
      await page.locator('video').evaluate((el, time) => { el.currentTime = time; }, seconds);
      await page.waitForFunction(text => document.querySelector('.dialogue-lines')?.textContent === text, expected);
      await page.waitForFunction(() => !document.querySelector('video').seeking && document.querySelector('video').readyState >= 2);
    }
    await page.locator('.dialogue-row').first().click();
    await page.waitForFunction(text => document.querySelector('.dialogue-lines')?.textContent === text, data.dialogue[0].text);
    await page.locator('#timeline').fill('0');
    await page.waitForFunction(() => !document.querySelector('.dialogue-lines'));
    await page.getByRole('button', { name: 'Play video', exact: true }).first().click();
    await page.waitForFunction(() => !document.querySelector('video').paused && document.querySelector('video').currentTime > .1);
    await page.getByRole('button', { name: 'Pause video', exact: true }).click();
    await page.locator('#timeline').fill(String(Math.round((data.dialogue[0].start_s + data.dialogue[0].end_s) / 2 * 10) / 10));
    await page.locator('.dialogue-lines').waitFor();
    await page.waitForFunction(() => !document.querySelector('video').seeking && document.querySelector('video').readyState >= 2);
    await page.evaluate(() => scrollTo(0, 0));
    await page.screenshot({ path: evidence + '/screenshots/' + id + '.png', fullPage: true });
    result.films.push({ id, duration, dialogueCuesChecked: data.dialogue.length, noCrossFilmCaptions: true, playPause: true, creditsAndPoster: true });
  }
  await page.setViewportSize({ width: 390, height: 844 });
  assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), 'No narrow layout overflow');
  await page.screenshot({ path: evidence + '/screenshots/mobile.png', fullPage: true });
  await page.setViewportSize({ width: 1440, height: 1100 });
  await page.locator('#film-choice').selectOption('big-buck-bunny');
  await page.waitForFunction(() => document.querySelector('video')?.readyState >= 1 && document.querySelectorAll('.cue-row').length === 87);
  // Synthetic dialogue verifies stacking and mismatch suppression; it is never saved into a real track.
  const fixture = JSON.parse(readFileSync('data/captions/big-buck-bunny.json', 'utf8'));
  fixture.dialogue = [{ cue_id: 'test-dialogue-only', start_s: 83.624, end_s: 84.999, text: 'TEST ONLY: fixed dialogue overlay' }];
  await page.getByLabel('Choose local video', { exact: true }).setInputFiles('public/media/big-buck-bunny.mp4');
  const upload = async data => page.getByLabel('Choose caption JSON', { exact: true }).setInputFiles({ name: 'synthetic-overlay-check.json', mimeType: 'application/json', buffer: Buffer.from(JSON.stringify(data)) });
  await upload(fixture);
  await page.waitForFunction(() => document.querySelectorAll('.cue-row').length === 87);
  await page.locator('#timeline').fill('83.9');
  await page.waitForFunction(() => document.querySelector('.dialogue-lines')?.textContent === 'TEST ONLY: fixed dialogue overlay' && !!document.querySelector('.caption-lines'));
  assert(await page.locator('.caption-overlay').count() === 1, 'Dialogue and sound share one stack');
  await page.getByRole('button', { name: 'Essential', exact: true }).click();
  await page.getByRole('button', { name: 'Apply preferences', exact: true }).click();
  assert(await page.locator('.dialogue-lines').textContent() === fixture.dialogue[0].text, 'Sound preferences preserve dialogue');
  await upload({ ...fixture, duration_seconds: fixture.duration_seconds + 20 });
  await page.getByRole('alert').filter({ hasText: 'Caption timing does not match' }).waitFor();
  assert(await page.locator('.caption-overlay').count() === 0, 'Duration mismatch suppresses both caption types');
  await page.locator('#film-choice').selectOption('sintel');
  await page.locator('#film-choice').selectOption('big-buck-bunny');
  await page.waitForFunction(() => document.querySelector('video')?.readyState >= 1 && document.querySelectorAll('.cue-row').length === 87);
  result.syntheticDialogueStackAndMismatch = true;
  await page.getByLabel('I agree to record this demo’s player interactions locally.').check();
  await page.getByRole('button', { name: 'Start rehearsal', exact: false }).click();
  assert(await page.locator('#film-choice').isDisabled(), 'Rehearsal fixes the film');
  await page.getByRole('button', { name: 'Stop recording', exact: true }).click();
  assert(await page.locator('#film-choice').isDisabled(), 'Stopped rehearsal still fixes the film until reload');
  assert(errors.length === 0, 'No uncaught browser errors: ' + errors.join('; '));
  result.rehearsalSelectionLocked = true;
  result.narrowLayout = true;
  writeFileSync(evidence + '/reports/browser-results.json', JSON.stringify(result, null, 2) + '\n');
  console.log(JSON.stringify(result));
} finally { await browser.close(); }
