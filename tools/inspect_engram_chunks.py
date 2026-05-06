import gzip
import json
import os

files = [
    ".engram/chunks/9f796ea8.jsonl.gz",
    ".engram/chunks/07bf3efc.jsonl.gz",
    ".engram/chunks/8dff9dcd.jsonl.gz",
]

def inspect(path, max_lines=40):
    print('\n=== FILE:', path, '===')
    if not os.path.exists(path):
        print('File not found:', path)
        return
    try:
        with gzip.open(path, 'rt', encoding='utf-8') as fh:
            for i, line in enumerate(fh):
                if i >= max_lines:
                    break
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    keys = ('type','session_id','created_at','author','created_by','title')
                    summary = {k: obj.get(k) for k in keys if k in obj}
                    print(f"LINE {i}:", json.dumps(summary, ensure_ascii=False))
                except Exception:
                    print(f"LINE {i}: NOT JSON: {line[:300]}")
    except Exception as e:
        print('Error reading', path, str(e))

if __name__ == '__main__':
    for p in files:
        inspect(p)
