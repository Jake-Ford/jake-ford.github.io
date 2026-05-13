---
name: site-rebuild-python
description: jake-ford.github.io rebuilt as Python static site generator in May 2026
metadata:
  type: project
---

Rebuilt the personal blog from R Distill to a custom Python static site generator.

**Why:** User wanted a techy/minimal look and a simpler workflow; R/Distill required RStudio and knitting.

**Stack:**
- `build.py` — main build script (Jinja2 + python-frontmatter + markdown)
- `content/posts/YYYY-MM-DD-slug.md` — blog posts in plain Markdown with YAML frontmatter
- `content/pages/` — about.md, projects.md, resources.md
- `templates/` — base.html, index.html, post.html, page.html (Jinja2)
- `static/style.css` — clean minimal light theme (monospace, HN/lobsters vibe)
- Output to `docs/` for GitHub Pages

**How to apply:** When the user wants to add a post, edit templates, or change CSS, work in `content/`, `templates/`, or `static/`, then run `python3 build.py` to regenerate `docs/`.

**Adding a new post:**
1. Create `content/posts/YYYY-MM-DD-slug.md` with `title:` and optional `description:` frontmatter
2. Run `python3 build.py`
3. Commit and push — GitHub Pages serves from `docs/`
