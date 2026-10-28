async (page) => {
  const assert = (value, message) => { if (!value) throw new Error(message); };
  const base = new URL(page.url()).origin;
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.goto(base);
  await page.setViewportSize({ width: 1440, height: 1100 });
  const results = [];
  for (const id of ['big-buck-bunny', 'sintel', 'tears-of-steel']) {
    await page.getByLabel('Choose a film', { exact: true }).selectOption(id);
    await page.waitForFunction(() => document.querySelector('video')?.readyState >= 1);
    const response = await page.request.get(`${base}/research/media-only/${id}.json`);
    assert(response.ok(), `${id}: generated JSON missing`);
    const track = await response.json();
    const existing = page.getByRole('button', { name: 'Use existing captions', exact: true });
    const generated = page.getByRole('button', { name: 'Use media-only AI subtitles', exact: true });
    assert(await existing.getAttribute('aria-pressed') === 'true', `${id}: existing track must be default`);
    await page.locator('video').evaluate(v => { v.pause(); v.currentTime = 35; });
    await page.waitForFunction(() => Math.abs(document.querySelector('video').currentTime - 35) < .1);
    const source = await page.locator('video').getAttribute('src');
    await generated.focus();
    await page.keyboard.press('Enter');
    assert(await generated.getAttribute('aria-pressed') === 'true', `${id}: generated selection failed`);
    assert(await page.locator('video').getAttribute('src') === source, `${id}: track switch replaced video`);
    assert(Math.abs(await page.locator('video').evaluate(v => v.currentTime) - 35) < .1, `${id}: track switch changed time`);
    await page.getByText('Experimental media-only AI subtitles selected.', { exact: true }).waitFor();
    assert(await page.getByRole('button', { name: 'Reference baseline', exact: true }).count() === 0, `${id}: reference controls leaked into experimental mode`);
    const cue = track.cues.find(c => c.end_s - c.start_s > 1);
    assert(cue, `${id}: no usable sound draft for comparison`);
    await page.locator('.cue-row').nth(track.cues.indexOf(cue)).click();
    for (const [name, key] of [['Essential', '1-1'], ['Balanced', '2-2'], ['Rich', '3-3']]) {
      await page.getByRole('button', { name, exact: true }).click();
      const apply = page.getByRole('button', { name: 'Apply preferences', exact: true });
      if (await apply.count()) await apply.click();
      await page.waitForFunction(text => document.querySelector('.caption-lines')?.textContent === text, cue.grid[key]);
    }
    await page.getByRole('button', { name: 'Show fixed draft', exact: true }).click();
    await page.waitForFunction(text => document.querySelector('.caption-lines')?.textContent === text, cue.original_text);
    await existing.click();
    assert(await generated.getAttribute('aria-pressed') === 'false', `${id}: generated mode not cleared`);
    assert(await page.locator('.experimental-notice').count() === 0, `${id}: stale warning after restoring existing captions`);
    await generated.click();
    await page.screenshot({ path: `artifacts/media-only-ui/${id}-desktop.png`, fullPage: true });
    await page.setViewportSize({ width: 390, height: 844 });
    assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), `${id}: mobile horizontal overflow`);
    await page.screenshot({ path: `artifacts/media-only-ui/${id}-mobile.png`, fullPage: true });
    await page.setViewportSize({ width: 1440, height: 1100 });
    for (const level of [1, 2, 3]) {
      const download = await page.request.get(`${base}/research/media-only/${id}-detail-${level}.srt`);
      assert(download.ok() && (await download.text()).includes('-->'), `${id}: missing detail ${level} SRT`);
    }
    results.push({ video: id, soundCues: track.cues.length, dialogueCues: track.dialogue.length,
      defaultPreserved: true, keyboardSelection: true, timePreserved: true, threeDetails: true,
      fixedDraft: true, restoreExisting: true, mobileOverflow: false, downloads: 3 });
  }
  await page.getByLabel('I agree to record this demo’s player interactions locally.', { exact: true }).check();
  await page.getByRole('button', { name: 'Start rehearsal', exact: false }).click();
  assert(await page.getByRole('button', { name: 'Use existing captions', exact: true }).isDisabled(), 'Source can change during rehearsal');
  assert(await page.getByRole('button', { name: 'Use media-only AI subtitles', exact: true }).isDisabled(), 'Generated source can change during rehearsal');
  assert(await page.getByLabel('Choose a film', { exact: true }).isDisabled(), 'Film can change during rehearsal');
  const [download] = await Promise.all([
    page.waitForEvent('download'), page.getByRole('button', { name: 'Export rehearsal JSON', exact: false }).click(),
  ]);
  await download.saveAs('artifacts/media-only-ui/rehearsal.json');
  assert(errors.length === 0, 'Browser errors: ' + errors.join('; '));
  return { results, rehearsalLocks: true, rehearsalExport: 'artifacts/media-only-ui/rehearsal.json', browserErrors: errors,
    scope: 'UI/transport/timing selection only; NOT acoustic accuracy, full listening or DHH validation' };
}
