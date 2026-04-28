import argparse
import datetime as dt
import os
import re
import subprocess
from pathlib import Path


def _run_git(args: list[str], cwd: Path) -> str:
    res = subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=False,
    )
    if res.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} failed ({res.returncode}):\n{res.stderr.strip()}"
        )
    return res.stdout


def _git_root() -> Path:
    res = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=False,
    )
    if res.returncode != 0:
        raise RuntimeError("Not a git repository (git rev-parse failed).")
    return Path(res.stdout.strip())


def _slugify(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s or "commit"


def _parse_name_status(raw: str) -> list[tuple[str, str]]:
    items: list[tuple[str, str]] = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        # Format: <status>\t<path> OR for renames: R100\told\tnew
        parts = line.split("\t")
        status = parts[0]
        if status.startswith("R") and len(parts) >= 3:
            path = f"{parts[1]} -> {parts[2]}"
        else:
            path = parts[1] if len(parts) > 1 else ""
        items.append((status, path))
    return items


def _safe_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def generate_for_commit(repo: Path, sha: str, out_dir: Path) -> Path:
    meta = _run_git(
        [
            "show",
            "-s",
            "--date=short",
            "--format=%H%n%h%n%ad%n%an%n%s%n%b",
            sha,
        ],
        cwd=repo,
    ).splitlines()

    full_sha = meta[0].strip() if len(meta) > 0 else sha
    short_sha = meta[1].strip() if len(meta) > 1 else sha[:7]
    date = meta[2].strip() if len(meta) > 2 else ""
    author = meta[3].strip() if len(meta) > 3 else ""
    subject = meta[4].strip() if len(meta) > 4 else ""
    body = "\n".join(meta[5:]).strip() if len(meta) > 5 else ""

    name_status_raw = _run_git(["show", "--name-status", "--format=", sha], cwd=repo)
    name_status = _parse_name_status(name_status_raw)

    stat = _run_git(["show", "--stat", "--format=", sha], cwd=repo).strip()

    summary = subject if subject else "Mensaje no descriptivo"
    slug = _slugify(subject)
    filename = f"{date}-{short_sha}-{slug}.md" if date else f"{short_sha}-{slug}.md"
    out_path = out_dir / filename

    lines: list[str] = []
    lines.append(f"# {summary}")
    lines.append("")
    lines.append("## Metadata")
    lines.append(f"- **Commit**: `{full_sha}`")
    if date:
        lines.append(f"- **Fecha**: `{date}`")
    if author:
        lines.append(f"- **Autor**: {author}")
    lines.append("")

    lines.append("## Resumen")
    if body:
        # Keep it small: first non-empty paragraph
        paras = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
        lines.append(paras[0])
    else:
        lines.append("(Sin cuerpo de mensaje; se usa sólo el subject del commit.)")
    lines.append("")

    lines.append("## Archivos modificados")
    if name_status:
        for st, p in name_status:
            lines.append(f"- `{st}` {p}")
    else:
        lines.append("- (No se detectaron archivos; commit vacío o metadata-only)")
    lines.append("")

    lines.append("## Diffstat")
    lines.append("```")
    lines.append(stat if stat else "(sin diffstat)")
    lines.append("```")
    lines.append("")

    _safe_write(out_path, "\n".join(lines))
    return out_path


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Generate per-commit change summaries into commit-changes/"
    )
    ap.add_argument(
        "--range",
        dest="range_",
        help='Git range, e.g. "v1.0.0..HEAD" or "sha1..sha2"',
    )
    ap.add_argument(
        "--last",
        type=int,
        help="Last N commits (reverse chronological). Generated in chronological order.",
    )
    ap.add_argument(
        "--since-last-pull",
        action="store_true",
        help="Generate for commits introduced since the last pull/merge/rebase (uses HEAD@{1}..HEAD).",
    )
    ap.add_argument(
        "--out-dir",
        default="commit-changes",
        help="Output directory (relative to repo root). Default: commit-changes",
    )
    args = ap.parse_args()

    # Default behavior: since last pull (HEAD@{1}..HEAD)
    default_since_last_pull = not args.range_ and not args.last and not args.since_last_pull

    repo = _git_root()
    out_dir = repo / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.since_last_pull or default_since_last_pull:
        # HEAD@{1} is the previous position of HEAD in reflog.
        # This works for pull with merge or rebase; if reflog doesn't have it, fall back to last 1.
        try:
            revs_raw = _run_git(["rev-list", "--reverse", "HEAD@{1}..HEAD"], cwd=repo)
            shas = [l.strip() for l in revs_raw.splitlines() if l.strip()]
        except RuntimeError:
            # Reflog might be unavailable (e.g., fresh clone). Fallback: just last commit.
            revs_raw = _run_git(["rev-list", "--reverse", "--max-count=1", "HEAD"], cwd=repo)
            shas = [l.strip() for l in revs_raw.splitlines() if l.strip()]
    elif args.range_:
        revs_raw = _run_git(["rev-list", "--reverse", args.range_], cwd=repo)
        shas = [l.strip() for l in revs_raw.splitlines() if l.strip()]
    else:
        revs_raw = _run_git(
            ["rev-list", "--reverse", f"--max-count={args.last}", "HEAD"], cwd=repo
        )
        shas = [l.strip() for l in revs_raw.splitlines() if l.strip()]

    if not shas:
        print("No commits found for the given range.")
        return 0

    generated: list[Path] = []
    for sha in shas:
        generated.append(generate_for_commit(repo=repo, sha=sha, out_dir=out_dir))

    # INDEX.md
    idx_lines: list[str] = []
    idx_lines.append("# Commit Changes")
    idx_lines.append("")
    idx_lines.append(
        f"Generado: {dt.datetime.now().isoformat(timespec='seconds')} (local)"
    )
    idx_lines.append("")
    idx_lines.append("## Documentos")
    for p in generated:
        rel = os.path.relpath(p, out_dir)
        idx_lines.append(f"- [{p.name}]({rel.replace('\\\\', '/')})")
    idx_lines.append("")
    _safe_write(out_dir / "INDEX.md", "\n".join(idx_lines))

    print(f"Generated {len(generated)} files in {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
