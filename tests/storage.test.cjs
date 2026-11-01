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
