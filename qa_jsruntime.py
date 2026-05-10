"""Run the new TAC-rendering JS functions inside node with mocked DOM stubs,
to verify they don't throw on real bridge.py output."""
import re, json, subprocess, sys, os, tempfile

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.join(ROOT, "files (1)")

# 1. Get a real bridge.py response
with tempfile.NamedTemporaryFile("w", suffix=".ml", delete=False, encoding="utf-8") as f:
    f.write("""int a = 3;
int b = 4;
int c = a + b;
if (c > 5) { print(c); } else { print(0); }
while (a < 10) { a = a + 1; }
""")
    tmp = f.name

r = subprocess.run([sys.executable, os.path.join(PROJ, "bridge.py"), tmp],
                   capture_output=True, text=True, encoding="utf-8")
os.unlink(tmp)
data = json.loads(r.stdout)
print(f"Sample run: tokens={len(data['tokens'])}, tac={len(data['tac'])}->{len(data['tac_optimizado'])}")

# 2. Extract the JS functions we want to exercise (escH + renderIntermediate + helpers)
with open(os.path.join(PROJ, "index.php"), "r", encoding="utf-8") as f:
    php = f.read()
js_block = re.search(r"<script>(.*?)</script>", php, re.S).group(1)

# Build a mock DOM and execute the relevant code
mock = """
// --- minimal DOM mock so renderIntermediate doesn't throw ---
const _doc = { _store: new Map() };
function _el(id) {
  if (!_doc._store.has(id)) {
    _doc._store.set(id, {
      id, _txt: '', _html: '', style: {},
      classList: { _set: new Set(), add(x){this._set.add(x);}, remove(x){this._set.delete(x);}, contains(x){return this._set.has(x);}, toggle(x,b){if(b)this.add(x);else this.remove(x);} },
      get textContent() { return this._txt; }, set textContent(v) { this._txt = v; },
      get innerHTML() { return this._html; }, set innerHTML(v) { this._html = v; },
    });
  }
  return _doc._store.get(id);
}
global.document = {
  getElementById: _el,
  querySelectorAll: (sel) => {
    // Return matching ir-sub stubs and ir-view stubs
    if (sel === '.ir-sub') {
      return ['orig','opt','cmp','info'].map(s => ({
        dataset:{sub:s},
        classList:{toggle:function(){}, add:function(){}, remove:function(){}, contains:function(){return false;}}
      }));
    }
    if (sel === '.ir-view') {
      return ['ir-view-orig','ir-view-opt','ir-view-cmp','ir-view-info'].map(id => _el(id));
    }
    return [];
  },
  addEventListener: () => {},
  querySelector: (sel) => ({ addEventListener: () => {} }),
};

// stub escH (simplified, JS uses a function in index.php — replicate here)
function escH(s){ return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
"""

# Pull just the helper functions we need from the JS block via regex
def extract_fn(name):
    pat = re.compile(r"(function\s+" + name + r"\s*\([^)]*\)\s*\{)", re.M)
    m = pat.search(js_block)
    if not m:
        return ""
    start = m.start()
    depth = 0
    i = m.end() - 1  # position of '{'
    while i < len(js_block):
        c = js_block[i]
        if c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return js_block[start:i+1]
        i += 1
    return ""

# Extract: _irRowHtml, _irPretty, renderIntermediate, switchIRSub
fns = []
for name in ["_irRowHtml", "_irPretty", "renderIntermediate", "switchIRSub"]:
    f = extract_fn(name)
    if not f:
        print(f"  WARN: could not extract {name}")
    else:
        fns.append(f)

# Need _irCurrentSub global
prelude = "let _irCurrentSub = 'orig';\n"

# Wire up the test
test = mock + prelude + "\n".join(fns) + f"""

const data = {json.dumps(data, ensure_ascii=False)};
try {{
  renderIntermediate(data.tac, data.tac_optimizado, data.metricas, data.traza_optimizacion);
  console.log('OK renderIntermediate ran without throwing');
  console.log('  ir-count:    ', _el('ir-count').textContent);
  console.log('  ir-stats:    ', _el('ir-stats').innerHTML.replace(/<[^>]+>/g, '').replace(/\\s+/g, ' '));
  console.log('  ir-body-orig: ', _el('ir-body-orig').innerHTML.length, 'chars');
  console.log('  ir-body-opt:  ', _el('ir-body-opt').innerHTML.length, 'chars');
  console.log('  ir-pre-orig:  ', _el('ir-pre-orig').textContent.split('\\n').length, 'lines');
  console.log('  ir-traza-body:', _el('ir-traza-body').innerHTML.length, 'chars');

  // Test empty case
  renderIntermediate([], [], {{}}, []);
  console.log('OK renderIntermediate handled empty arrays');

  // Test switchIRSub
  ['orig','opt','cmp','info'].forEach(s => {{
    switchIRSub(s);
    console.log('  switchIRSub("' + s + '") ok');
  }});
}} catch (e) {{
  console.error('FAIL:', e.message);
  console.error(e.stack);
  process.exit(1);
}}
"""

out_path = os.path.join(tempfile.gettempdir(), "qa_render_test.js")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(test)

r = subprocess.run(["node", out_path], capture_output=True, text=True, encoding="utf-8")
print(r.stdout)
if r.returncode != 0:
    print(r.stderr)
    sys.exit(1)
