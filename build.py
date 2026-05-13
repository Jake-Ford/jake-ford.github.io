#!/usr/bin/env python3
"""
Simple static site generator.
Usage:  python build.py
Output: docs/  (GitHub Pages source)
"""

import shutil
from pathlib import Path

import markdown
import frontmatter
from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).parent
POSTS_DIR = ROOT / "content" / "posts"
PAGES_DIR = ROOT / "content" / "pages"
TEMPLATES_DIR = ROOT / "templates"
STATIC_DIR = ROOT / "static"
OUTPUT_DIR = ROOT / "docs"

MD_EXT = [
    "extra", "codehilite", "toc", "tables",
    "fenced_code", "nl2br", "attr_list", "def_list",
]


def parse_md(path):
    post = frontmatter.load(path)
    md = markdown.Markdown(extensions=MD_EXT)
    return post, md.convert(post.content)


def load_posts():
    posts = []
    for path in sorted(POSTS_DIR.glob("*.md"), reverse=True):
        post, html = parse_md(path)
        stem = path.stem
        # filename format: YYYY-MM-DD-slug.md
        parts = stem.split("-", 3)
        date = f"{parts[0]}-{parts[1]}-{parts[2]}" if len(parts) >= 4 else ""
        slug = parts[3] if len(parts) >= 4 else stem
        posts.append({
            "title": post.get("title", slug),
            "description": post.get("description", ""),
            "date": date,
            "slug": slug,
            "filename": f"{stem}.html",
            "content": html,
        })
    return posts


def load_pages():
    pages = []
    for path in sorted(PAGES_DIR.glob("*.md")):
        post, html = parse_md(path)
        stem = path.stem
        pages.append({
            "title": post.get("title", stem),
            "slug": stem,
            "filename": f"{stem}.html",
            "content": html,
        })
    return pages


def clean_output():
    for f in OUTPUT_DIR.glob("*.html"):
        f.unlink()
    posts_out = OUTPUT_DIR / "posts"
    if posts_out.exists():
        shutil.rmtree(posts_out)
    static_out = OUTPUT_DIR / "static"
    if static_out.exists():
        shutil.rmtree(static_out)
    OUTPUT_DIR.mkdir(exist_ok=True)
    posts_out.mkdir(exist_ok=True)


def build():
    clean_output()
    shutil.copytree(STATIC_DIR, OUTPUT_DIR / "static")

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=False,
    )
    posts = load_posts()
    pages = load_pages()
    base_ctx = {"posts": posts, "pages": pages}

    # Index
    t = env.get_template("index.html")
    (OUTPUT_DIR / "index.html").write_text(t.render(**base_ctx, root=""))

    # Static pages
    t = env.get_template("page.html")
    for page in pages:
        (OUTPUT_DIR / page["filename"]).write_text(
            t.render(page=page, **base_ctx, root="")
        )

    # Posts
    t = env.get_template("post.html")
    for post in posts:
        (OUTPUT_DIR / "posts" / post["filename"]).write_text(
            t.render(post=post, **base_ctx, root="../")
        )

    print(f"Built {len(posts)} posts, {len(pages)} pages → {OUTPUT_DIR}/")


if __name__ == "__main__":
    build()
