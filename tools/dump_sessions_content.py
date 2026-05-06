import json
import os
import sys

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

def dump_all(sessions, obs_by_session, max_obs_content=4000):
    for sid, s in sessions.items():
        print('\n' + '='*80)
        print(f"SESSION: {sid}")
        print(f"  project: {s.get('project')}")
        print(f"  directory: {s.get('directory')}")
        print(f"  started_at: {s.get('started_at')}")
        if s.get('metadata'):
            print(f"  metadata: {s.get('metadata')}")
        obs = obs_by_session.get(sid, [])
        print(f"  observations: {len(obs)}")
        for o in obs:
            print('\n  --- Observation ID: {}  Title: {}'.format(o.get('id'), o.get('title')))
            print(f"    type: {o.get('type')}")
            content = o.get('content','')
            if not content:
                print('    (no content)')
            else:
                # truncate very long contents but keep readable
                print('    content:')
                to_print = content if len(content) <= max_obs_content else content[:max_obs_content] + '\n...[truncated]'
                for line in to_print.splitlines():
                    print('      ' + line)

def main():
    export = load_export()
    sessions, obs_by_session = build_index(export)
    if not sessions:
        print('No sessions found in export.')
        return 0
    dump_all(sessions, obs_by_session)
    return 0

if __name__ == '__main__':
    sys.exit(main())
