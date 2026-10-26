async (page) => {
  const assert = (value, message) => { if (!value) throw new Error(message); };
  const base = new URL(page.url()).origin;
  await page.goto(base);
  await page.setViewportSize({ width: 1440, height: 1100 });
  await page.waitForFunction(() => document.querySelector('video').readyState >= 1);
  const track = await (await page.request.get(base + '/research/demo-captions.json')).json();
  await page.getByRole('button', { name: 'Personalized', exact: true }).click();
  await page.getByLabel('Follow cue density', { exact: true }).uncheck();
  const apply = async () => {
    const b = page.getByRole('button', { name: 'Apply preferences', exact: true });
    if (await b.count()) await b.click();
  };
  await apply();
  const checked = [];
  for (const id of ['bbb-sdh-002', 'bbb-sdh-020', 'bbb-sdh-061']) {
    const cue = track.cues.find(c => c.cue_id === id);
    await page.locator('.cue-row').nth(track.cues.indexOf(cue)).click();
    for (const [label, key] of [['Essential','1-1'],['Balanced','2-2'],['Rich','3-3']]) {
      await page.getByRole('button', { name: label, exact: true }).click();
      await apply();
      await page.waitForFunction(text => document.querySelector('.caption-lines')?.textContent === text, cue.grid[key]);
    }
    const before = await page.locator('video').evaluate(v => v.currentTime);
    await page.getByRole('button', { name: 'Show reference', exact: true }).click();
    await page.waitForFunction(text => document.querySelector('.caption-lines')?.textContent === text, cue.reference_text);
    assert(Math.abs(await page.locator('video').evaluate(v => v.currentTime) - before) < .05, 'Reference toggle must preserve the comparison time');
    await page.getByText('Fetched reference captions', { exact: true }).waitFor();
    await page.getByText('Showing fetched reference captions', { exact: true }).waitFor();
    await page.getByRole('button', { name: 'Reference on', exact: true }).click();
    await page.waitForFunction(text => document.querySelector('.caption-lines')?.textContent === text, cue.grid['3-3']);
    checked.push(id);
  }
  const dir = 'artifacts/nim-phase1-2026-10-26';
  await page.screenshot({ path: dir + '/comparison-desktop.png' });
  await page.setViewportSize({ width: 390, height: 844 });
  assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), 'Mobile overflow');
  await page.screenshot({ path: dir + '/comparison-mobile.png', fullPage: true });
  // A narrower CSS viewport checks reflow; CSS zoom does not change media queries
  // and is not a faithful replacement for native browser zoom.
  await page.setViewportSize({ width: 720, height: 550 });
  assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), 'Reflow overflow');
  const fits = await page.locator('.caption-lines').evaluate(el => {
    const r = el.getBoundingClientRect(), frame = el.closest('.video-frame').getBoundingClientRect();
    return r.left >= frame.left && r.right <= frame.right && r.top >= frame.top && r.bottom <= frame.bottom;
  });
  assert(fits, 'Caption must fit inside the reflowed video');
  await page.getByRole('button', { name: 'Show reference', exact: true }).focus();
  await page.keyboard.press('Enter');
  await page.getByRole('button', { name: 'Reference on', exact: true }).waitFor();
  await page.screenshot({ path: dir + '/comparison-reflow.png' });
  return { checked, detailPresets: 3, referencePreservesTime: true, keyboardReference: true, mobileOverflow: false, reflow: '720 CSS-pixel viewport; native browser zoom unverified', dataset: 'Existing local Qwen/editorial draft, not new NIM captions' };
}
