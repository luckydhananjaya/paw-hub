const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const html = fs.readFileSync('index.html', 'utf8');
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];

function harness() {
  const data = new Map();
  const context = vm.createContext({console, setTimeout, clearTimeout,
    localStorage: {getItem: k => data.get(k) ?? null, setItem: (k,v) => data.set(k,v)},
    document: {addEventListener() {}}, window: {addEventListener() {}}
  });
  vm.runInContext(script.replace(/initNotes\(\);\s*$/, ''), context);
  return {context, run: code => vm.runInContext(code, context)};
}

test('embedded app JavaScript parses', () => { new vm.Script(script); });

for (const method of ['idbPut', 'idbDelete', 'idbBulkPut']) {
  test(`${method} waits for transaction commit and rejects an abort`, async () => {
    const {run, context} = harness();
    let transaction;
    const request = {result: 'saved'};
    context.fakeDB = {transaction() {
      transaction = {objectStore: () => ({put: () => request, delete: () => request})};
      return transaction;
    }};
    run('dbInstance = fakeDB');
    const arg = method === 'idbBulkPut' ? '[]' : '{}';
    let settled = false;
    const saving = run(`${method}(${arg})`).then(() => {settled = true});
    if (request.onsuccess) request.onsuccess();
    await Promise.resolve();
    assert.equal(settled, false);
    transaction.oncomplete();
    await saving;
    const failing = run(`${method}(${arg})`);
    transaction.error = new Error('disk full');
    transaction.onabort();
    await assert.rejects(failing, /disk full/);
  });
}

test('deleting the final note does not reseed sample notes on restart', async () => {
  const {run} = harness();
  run(`localStorage.setItem(INITIALIZED_KEY, 'yes');
    idbGetAll = async () => []; idbBulkPut = async () => { throw Error('must not seed') };
    renderNotes = () => {}; initCapacitorAndAdMob = () => {};`);
  await run('initNotes()');
  assert.equal(run('notes.length'), 0);
});

test('first installation seeds plain-text samples once', async () => {
  const {run} = harness();
  run(`idbGetAll = async () => []; idbBulkPut = async () => {};
    renderNotes = () => {}; initCapacitorAndAdMob = () => {};`);
  await run('initNotes()');
  assert.ok(run('notes.length') > 0);
  assert.equal(run("notes.some(n => n.type === 'checklist')"), false);
  assert.equal(run('localStorage.getItem(INITIALIZED_KEY)'), 'yes');
});

test('preference quota failure does not replace notes loaded from IndexedDB', async () => {
  const {run} = harness();
  run(`idbGetAll = async () => [{id:'retained',updatedAt:1}];
    localStorage.setItem = () => { throw Error('quota exceeded'); };
    console = {warn() {}};
    renderNotes = () => {}; initCapacitorAndAdMob = () => {};`);
  await run('initNotes()');
  assert.equal(run('notes[0].id'), 'retained');
  assert.equal(run('notes.length'), 1);
});

test('malformed backups are rejected before writes', () => {
  const {run, context} = harness();
  for (const text of ['{}','not json','[{"id":"bad"}]']) {
    context.backup = text;
    assert.throws(() => run('validateBackupText(backup)'));
  }
});

test('Android backup bridge uses nativePromise for every method', async () => {
  const {context, run} = harness();
  const calls = [];
  context.window.Capacitor = {isNativePlatform: () => true,
    nativePromise: async (...args) => calls.push(args)};
  for (const method of ['status', 'chooseFolder', 'write', 'list', 'read']) {
    await run(`folderBackupPlugin().${method}({data:'[]',id:'backup'})`);
  }
  assert.deepEqual(calls.map(c => c.slice(0,2)),
    ['status','chooseFolder','write','list','read'].map(m => ['PawBackup',m]));
});

test('Appearance mode defaults to system and persists choices', () => {
  const {run, context} = harness();
  assert.equal(run('getAppearanceMode()'), 'system');
  run("setAppearanceMode('dark')");
  assert.equal(run('getAppearanceMode()'), 'dark');
  run("setAppearanceMode('light')");
  assert.equal(run('getAppearanceMode()'), 'light');
});

test('PawReview bridge invokes native PawReview.requestReview', async () => {
  const {context, run} = harness();
  const calls = [];
  context.window.Capacitor = {isNativePlatform: () => true,
    nativePromise: async (...args) => calls.push(args)};
  await run('reviewPlugin().requestReview()');
  assert.deepEqual(calls.map(c => c.slice(0,2)), [['PawReview', 'requestReview']]);
});

test('In-app review prompt respects qualification rules and quota', async () => {
  const {context, run} = harness();
  let requested = false;
  context.reviewPlugin = () => ({ requestReview: async () => { requested = true; } });

  // 1. Fewer than 5 notes: no prompt
  run("notes = [{id:1},{id:2},{id:3},{id:4}]");
  run("localStorage.setItem('paw_active_days', JSON.stringify(['2026-11-01','2026-11-02','2026-11-03']))");
  await run('maybePromptInAppReview()');
  assert.equal(requested, false);

  // 2. 5 notes but fewer than 3 active days: no prompt
  run("notes = [{id:1},{id:2},{id:3},{id:4},{id:5}]");
  run("localStorage.setItem('paw_active_days', JSON.stringify(['2026-11-01','2026-11-02']))");
  await run('maybePromptInAppReview()');
  assert.equal(requested, false);

  // 3. 5 notes and 3 days: prompts!
  run("localStorage.setItem('paw_active_days', JSON.stringify(['2026-11-01','2026-11-02','2026-11-03']))");
  await run('maybePromptInAppReview()');
  assert.equal(requested, true);

  // 4. Repeated prompt within 30 days is blocked by quota
  requested = false;
  await run('maybePromptInAppReview()');
  assert.equal(requested, false);
});

test('PawAds bridge retrieves native ad config', async () => {
  const {context, run} = harness();
  const mockConfig = {
    isDebug: false,
    bannerAdUnitId: 'ca-app-pub-9251474250306859/9607926427',
    interstitialAdUnitId: 'ca-app-pub-9251474250306859/7873219107',
    isTesting: false
  };
  context.window.Capacitor = {
    isNativePlatform: () => true,
    nativePromise: async (plugin, method) => {
      if (plugin === 'PawAds' && method === 'getAdConfig') return mockConfig;
      return null;
    }
  };
  const config = await run('getAdConfig()');
  assert.deepEqual(config, mockConfig);
});

test('Consent flow checks UMP status before initializing ads', async () => {
  const {context, run} = harness();
  let initialized = false;
  let bannerShown = false;
  let canRequest = false;

  context.window.Capacitor = {
    isNativePlatform: () => true,
    Plugins: {
      AdMob: {
        requestConsentInfo: async () => ({ canRequestAds: canRequest, privacyOptionsRequirementStatus: 'REQUIRED' }),
        showConsentForm: async () => ({ canRequestAds: canRequest, privacyOptionsRequirementStatus: 'REQUIRED' }),
        initialize: async () => { initialized = true; },
        showBanner: async () => { bannerShown = true; },
        prepareInterstitial: async () => {}
      }
    }
  };

  // 1. When canRequestAds is false, ads are NOT initialized
  await run('checkConsentState(true)');
  assert.equal(run('adsInitialized'), false);
  assert.equal(initialized, false);
  assert.equal(bannerShown, false);
  assert.equal(run('privacyOptionsRequired'), true);

  // 2. When canRequestAds is true, ads initialize and banner is shown
  canRequest = true;
  await run('checkConsentState(true)');
  assert.equal(run('adsInitialized'), true);
  assert.equal(initialized, true);
  assert.equal(bannerShown, true);
});

test('Interstitial enforces frequency cap and does not show on launch', async () => {
  const {context, run} = harness();
  let interstitialShown = false;

  context.window.Capacitor = {
    isNativePlatform: () => true,
    Plugins: {
      AdMob: {
        prepareInterstitial: async () => {},
        showInterstitial: async () => { interstitialShown = true; }
      }
    }
  };

  run('adsInitialized = true; interstitialReady = true;');

  // Immediately on launch / right after app starts: frequency cap blocks it
  await run('maybeShowInterstitial()');
  assert.equal(interstitialShown, false);

  // Advance time past the 3-minute frequency cap: now it shows
  run('lastInterstitialTime = Date.now() - (4 * 60 * 1000);');
  await run('maybeShowInterstitial()');
  assert.equal(interstitialShown, true);

  // Subsequent call immediately after is blocked again
  interstitialShown = false;
  await run('maybeShowInterstitial()');
  assert.equal(interstitialShown, false);
});
