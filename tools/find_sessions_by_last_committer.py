import json
import subprocess
import os
import sys

def git_last_commit_author():
    try:
        out = subprocess.check_output(["git", "log", "-1", "--pretty=format:%H%n%an%n%ae%n%ad%n%s"], universal_newlines=True)
        sha, name, email, date, subject = out.split("\n", 4)
        return {"sha": sha, "name": name, "email": email, "date": date, "subject": subject}
    except Exception as e:
        return {"error": str(e)}

def load_debug_export(path="debug-export.json"):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)

def find_matches(export, author):
    matches = {"sessions": [], "observations": []}
    if not export:
        return matches
    key_terms = set()
    if author.get("name"):
        key_terms.add(author["name"].lower())
    if author.get("email"):
        key_terms.add(author["email"].lower())
        key_terms.add(author["email"].split("@")[0].lower())
    # also include simple username guesses
    # scan sessions
    for s in export.get("sessions", []):
        text = json.dumps(s).lower()
        if any(k in text for k in key_terms):
            matches["sessions"].append(s)
    for o in export.get("observations", []):
        text = json.dumps(o).lower()
        if any(k in text for k in key_terms):
            matches["observations"].append({"id": o.get("id"), "title": o.get("title"), "session_id": o.get("session_id")})
    return matches

def inspect_manifest(manifest_path=".engram/manifest.json", author=None):
    res = []
    try:
        with open(manifest_path, "r", encoding="utf-8") as fh:
            m = json.load(fh)
        for c in m.get("chunks", []):
            created_by = c.get("created_by", "")
            if not author:
                res.append(c)
            else:
                if author.get("name") and author["name"].lower() in created_by.lower():
                    res.append(c)
                elif author.get("email") and author["email"].split("@")[0].lower() in created_by.lower():
                    res.append(c)
    except Exception as e:
        return {"error": str(e)}
    return res

def main():
    author = git_last_commit_author()
    print("LAST_COMMIT_AUTHOR:")
    print(json.dumps(author, ensure_ascii=False, indent=2))

    export = load_debug_export()
    if export is None:
        print("debug-export.json not found. Run 'engram export debug-export.json' first.")
        return 2

    matches = find_matches(export, author)
    print('\nMATCHES FOUND:')
    print(json.dumps({"sessions_count": len(matches["sessions"]), "observations_count": len(matches["observations"])}, ensure_ascii=False, indent=2))

    if matches["sessions"]:
        print('\nSessions:')
        for s in matches["sessions"]:
            print(json.dumps(s, ensure_ascii=False))

    if matches["observations"]:
        print('\nObservations:')
        for o in matches["observations"]:
            print(json.dumps(o, ensure_ascii=False))

    manifest_hits = inspect_manifest(author=author)
    print('\nMANIFEST CHUNKS CREATED BY AUTHOR (if any):')
    print(json.dumps(manifest_hits, ensure_ascii=False, indent=2))

    return 0

if __name__ == '__main__':
    sys.exit(main())
