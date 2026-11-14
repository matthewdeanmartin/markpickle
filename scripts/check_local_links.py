"""Check local links in Markdown files without installing a separate link checker."""

from __future__ import annotations

import argparse
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

import mistune


class HTMLLinks(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.urls: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"a", "img"}:
            wanted = "href" if tag == "a" else "src"
            self.urls.extend(value for key, value in attrs if key == wanted and value)


def urls_in(nodes: list[dict]) -> list[str]:
    urls: list[str] = []
    for node in nodes:
        if node.get("type") in {"link", "image"}:
            urls.append(node["attrs"]["url"])
        if node.get("type") in {"inline_html", "block_html"}:
            html = HTMLLinks()
            html.feed(node.get("raw", ""))
            urls.extend(html.urls)
        urls.extend(urls_in(node.get("children", [])))
    return urls


def markdown_files(paths: list[Path]) -> list[Path]:
    return sorted({file for path in paths for file in (path.rglob("*.md") if path.is_dir() else [path])})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    parse = mistune.create_markdown(renderer="ast")
    failures: list[str] = []
    files = markdown_files(args.paths)
    for file in files:
        if not file.is_file():
            failures.append(f"{file}: missing input file")
            continue
        for url in urls_in(parse(file.read_text(encoding="utf-8"))):
            parsed = urlsplit(url)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            target = unquote(parsed.path)
            resolved = (repo_root / target.lstrip("/") if target.startswith("/") else file.parent / target).resolve()
            if not resolved.is_file() and not resolved.is_dir():
                failures.append(f"{file}: {url} -> missing {resolved}")
    for failure in failures:
        print(failure)
    print(f"Checked local links in {len(files)} Markdown files; {len(failures)} broken.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
