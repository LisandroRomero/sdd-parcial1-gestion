import gzip
import json
import os

files = [
    ".engram/chunks/9f796ea8.jsonl.gz",
    ".engram/chunks/07bf3efc.jsonl.gz",
    ".engram/chunks/8dff9dcd.jsonl.gz",
]

def find_in_chunk(path, max_matches=20):
    print('\n--- Searching in', path, '---')
    if not os.path.exists(path):
        print('File not found:', path)
        return
    matches = 0
    try:
        with gzip.open(path, 'rt', encoding='utf-8') as fh:
            for i, line in enumerate(fh):
                if not line.strip():
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                # Check common session indicators
                if (
                    'session' in obj
                    or 'session_id' in obj
                    or obj.get('type') == 'session'
                    or 'sessions' in obj
                ):
                    matches += 1
                    print(f"MATCH {matches} at line {i}:")
                    # print a compact representation
                    compact = {k: obj.get(k) for k in ('type','session_id','created_at','author','created_by','title') if k in obj}
                    print(json.dumps(compact, ensure_ascii=False))
                    # also print the full object truncated
                    s = json.dumps(obj, ensure_ascii=False)
                    print(s[:2000])
                    if matches >= max_matches:
                        break
    except Exception as e:
        print('Error reading', path, str(e))
    if matches == 0:
        print('No session-like objects found in', path)

if __name__ == '__main__':
    for p in files:
        find_in_chunk(p)
