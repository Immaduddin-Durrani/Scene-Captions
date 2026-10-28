async (page) => {
  const assert = (v, message) => { if (!v) throw Error(message); };
  const base = new URL(page.url()).origin;
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.goto(base);
  await page.setViewportSize({width:1440,height:1100});
  await page.waitForFunction(() => document.querySelector('video')?.readyState >= 1);
  const response = await page.request.get(base+'/research/source-richness/big-buck-bunny.json');
  assert(response.ok(),'Source-guided track missing');
  const track = await response.json();
  await page.locator('video').evaluate(v=>{v.pause();v.currentTime=83.8});
  await page.waitForFunction(()=>Math.abs(document.querySelector('video').currentTime-83.8)<.05);
  const source = page.getByRole('button',{name:'Use source-guided captions',exact:true});
  await source.focus();await page.keyboard.press('Enter');
  assert(await source.getAttribute('aria-pressed')==='true','Source mode not selected');
  assert(Math.abs(await page.locator('video').evaluate(v=>v.currentTime)-83.8)<.05,'Source switch changed playback time');
  await page.getByText('Simple source-guided captions selected.',{exact:true}).waitFor();
  const checked=[];
  for(const id of ['bbb-sdh-002','bbb-sdh-020','bbb-sdh-054','bbb-sdh-061']) {
    const index=track.cues.findIndex(c=>c.cue_id===id),cue=track.cues[index];
    await page.locator('.cue-row').nth(index).click();
    for(const [label,detail] of [['Essential',1],['Balanced',2],['Rich',3]]) {
      const preset=page.getByRole('button',{name:label,exact:true});await preset.click();
      assert(await preset.getAttribute('aria-pressed')==='true','Conservative preset pressed state is wrong');
      const apply=page.getByRole('button',{name:'Apply preferences',exact:true});if(await apply.count())await apply.click();
      await page.waitForFunction(text=>document.querySelector('.caption-lines')?.textContent===text,cue.grid[`${detail}-2`]);
    }
    await page.getByRole('button',{name:'Show reference',exact:true}).click();
    await page.waitForFunction(text=>document.querySelector('.caption-lines')?.textContent===text,cue.reference_text);
    await page.getByRole('button',{name:'Reference on',exact:true}).click();
    checked.push(id);
  }
  await page.screenshot({path:'artifacts/source-richness-ui/desktop.png',fullPage:true});
  await page.setViewportSize({width:390,height:844});
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'Mobile overflow');
  await page.screenshot({path:'artifacts/source-richness-ui/mobile.png',fullPage:true});
  for(const d of [1,2,3])assert((await page.request.get(`${base}/research/source-richness/big-buck-bunny-detail-${d}.srt`)).ok(),'Missing SRT');
  for(const id of ['sintel','tears-of-steel']) {
    await page.getByLabel('Choose a film',{exact:true}).selectOption(id);
    assert(await source.count()===0,`${id}: source-only sound expansion must be unavailable`);
    assert(await page.getByRole('button',{name:'Use existing captions',exact:true}).getAttribute('aria-pressed')==='true','Film switch leaked source track');
  }
  await page.getByLabel('Choose a film',{exact:true}).selectOption('big-buck-bunny');await source.click();
  await page.getByLabel('I agree to record this demo’s player interactions locally.',{exact:true}).check();
  await page.getByRole('button',{name:'Start rehearsal',exact:false}).click();
  assert(await source.isDisabled(),'Source can change after rehearsal starts');
  const [download]=await Promise.all([page.waitForEvent('download'),page.getByRole('button',{name:'Export rehearsal JSON',exact:false}).click()]);
  await download.saveAs('artifacts/source-richness-ui/rehearsal.json');
  assert(errors.length===0,errors.join('; '));
  return {checked,threeDetailLevels:true,presetPressedState:true,keyboardSelection:true,timePreserved:true,referenceComparison:true,
    sourceOnlyCoverage:true,mobileOverflow:false,rehearsalLocked:true,downloads:3,pageErrors:errors,
    limits:'UI and source-text checks, not listening/DHH validation'};
}
