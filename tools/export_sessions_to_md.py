import json
import os
import sys

OUT_DIR = "engram_exports"

def load_export(path="debug-export.json"):
    if not os.path.exists(path):
        print(f"Export file not found: {path}. Run 'engram export {path}' first.")
        sys.exit(2)
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)

def build_index(export):
    sessions = {s['id']: s for s in export.get('sessions', [])}
    obs_by_session = {}
    for o in export.get('observations', []):
        sid = o.get('session_id')
        obs_by_session.setdefault(sid, []).append(o)
    return sessions, obs_by_session

def safe_filename(s):
    keep = "abcdefghijklmnopqrstuvwxyz0123456789-_"
    s = s.replace(' ', '_')
    s = s.lower()
    return ''.join(c for c in s if c in keep)[:120]

def write_session_md(sid, s, obs, out_dir=OUT_DIR):
    filename = f"{sid}.md"
    filepath = os.path.join(out_dir, filename)
    with open(filepath, "w", encoding="utf-8") as fh:
        fh.write(f"# Session {sid}\n\n")
        fh.write(f"- project: {s.get('project')}\n")
        fh.write(f"- directory: {s.get('directory')}\n")
        fh.write(f"- started_at: {s.get('started_at')}\n")
        fh.write("\n---\n\n")
        for o in obs:
            fh.write(f"## Observation {o.get('id')} — {o.get('title')}\n\n")
            fh.write(f"- type: {o.get('type')}\n\n")
            content = o.get('content','')
            if not content:
                fh.write("(no content)\n\n")
            else:
                fh.write(content)
                fh.write("\n\n")
    return filepath

def main():
    export = load_export()
    sessions, obs_by_session = build_index(export)
    os.makedirs(OUT_DIR, exist_ok=True)
    created = []
    for sid, s in sessions.items():
        obs = obs_by_session.get(sid, [])
        path = write_session_md(sid, s, obs)
        created.append(path)
    print(f"Wrote {len(created)} session files to {OUT_DIR}/")
    for p in created:
        print(p)
    return 0

if __name__ == '__main__':
    sys.exit(main())
