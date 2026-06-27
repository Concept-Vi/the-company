"""Wizard run-1 substrate — SQLite (JSON1). Single-writer; idempotent; provenance-stamped."""
import sqlite3, json, os, time
DB = os.path.expanduser("~/wizard-run-1/wizard.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS files(
  rel TEXT PRIMARY KEY, form TEXT, frontmatter TEXT, has_fm INTEGER,
  principle TEXT, framing TEXT, reach TEXT, surface_claims TEXT, form_specific TEXT,
  substance INTEGER, run_id TEXT, ts REAL);
CREATE TABLE IF NOT EXISTS links(src TEXT, dst TEXT, UNIQUE(src,dst));
CREATE TABLE IF NOT EXISTS blocks(rel TEXT, kind TEXT, content TEXT);
CREATE TABLE IF NOT EXISTS marks(
  id INTEGER PRIMARY KEY AUTOINCREMENT, target TEXT, mark_type TEXT, value TEXT,
  confidence REAL, source_pass TEXT, source_tier TEXT, evidence TEXT,
  status TEXT DEFAULT 'proposed', ts REAL);
CREATE TABLE IF NOT EXISTS runs(run_id TEXT PRIMARY KEY, kind TEXT, model TEXT, ts REAL, params TEXT);
CREATE INDEX IF NOT EXISTS ix_files_form ON files(form);
CREATE INDEX IF NOT EXISTS ix_links_src ON links(src);
CREATE INDEX IF NOT EXISTS ix_links_dst ON links(dst);
CREATE INDEX IF NOT EXISTS ix_marks_target ON marks(target);
CREATE INDEX IF NOT EXISTS ix_marks_type ON marks(mark_type);
"""
def conn():
    c = sqlite3.connect(DB, timeout=60); c.execute("PRAGMA journal_mode=WAL"); return c
def init():
    c = conn(); c.executescript(SCHEMA); c.commit(); c.close()
def _j(x): return json.dumps(x, ensure_ascii=False)
def upsert_file(c, rel, **f):
    c.execute("""INSERT INTO files(rel,form,frontmatter,has_fm,principle,framing,reach,surface_claims,form_specific,substance,run_id,ts)
      VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
      ON CONFLICT(rel) DO UPDATE SET form=excluded.form,frontmatter=excluded.frontmatter,has_fm=excluded.has_fm,
        principle=excluded.principle,framing=excluded.framing,reach=excluded.reach,surface_claims=excluded.surface_claims,
        form_specific=excluded.form_specific,substance=excluded.substance,run_id=excluded.run_id,ts=excluded.ts""",
      (rel, f.get("form"), _j(f.get("frontmatter",{})), int(f.get("has_fm",0)), f.get("principle"), f.get("framing"),
       f.get("reach"), _j(f.get("surface_claims",[])), _j(f.get("form_specific",{})), int(f.get("substance",1)),
       f.get("run_id"), time.time()))
def add_link(c, src, dst):
    c.execute("INSERT OR IGNORE INTO links(src,dst) VALUES(?,?)", (src, dst))
def add_block(c, rel, kind, content):
    c.execute("INSERT INTO blocks(rel,kind,content) VALUES(?,?,?)", (rel, kind, content))
def propose_mark(c, target, mark_type, value, confidence, source_pass, source_tier, evidence):
    c.execute("INSERT INTO marks(target,mark_type,value,confidence,source_pass,source_tier,evidence,status,ts) VALUES(?,?,?,?,?,?,?,?,?)",
      (target, mark_type, str(value), confidence, source_pass, source_tier, _j(evidence), 'proposed', time.time()))
def log_run(c, run_id, kind, model, params):
    c.execute("INSERT OR REPLACE INTO runs(run_id,kind,model,ts,params) VALUES(?,?,?,?,?)", (run_id, kind, model, time.time(), _j(params)))

if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        if os.path.exists(DB): os.remove(DB)
        init(); c = conn()
        upsert_file(c, "test/a.md", form="prose-design", frontmatter={"type":"design","tags":["x"]}, has_fm=1,
                    principle="the system should resolve content not act as an agent", framing="stated as a law",
                    reach="a universal composition substrate", surface_claims=["decision: use Supabase"], form_specific={}, substance=1, run_id="selftest")
        add_link(c,"test/a.md","other/b"); add_block(c,"test/a.md","json",'{"k":1}')
        propose_mark(c,"test/a.md","corroboration","7",0.8,"passA","embed",{"echoes":["x.md","y.md"]})
        log_run(c,"selftest","capture","none",{}); c.commit()
        r=c.execute("SELECT rel,form,json_extract(frontmatter,'$.type'),principle FROM files").fetchone()
        l=c.execute("SELECT count(*) FROM links").fetchone()[0]
        b=c.execute("SELECT count(*) FROM blocks").fetchone()[0]
        m=c.execute("SELECT mark_type,value,status FROM marks").fetchone()
        print("file:",r); print("links:",l,"blocks:",b,"mark:",m)
        print("SELFTEST OK" if r and r[2]=="design" and l==1 and b==1 and m[0]=="corroboration" else "SELFTEST FAIL")
        c.close()
    else:
        init(); print("db initialised at", DB)
