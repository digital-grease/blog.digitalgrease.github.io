# Contributing to the Blog

Thank you for your interest in contributing! Here are some guidelines to help you get started.

## Writing Blog Posts

### Post Format

All blog posts go in `docs/posts/posts/` (the MkDocs blog plugin sets `blog_dir: posts`, which is why the directory nests). Use this frontmatter:

```markdown
---
date: YYYY-MM-DD
slug: url-slug
description: One-line summary used for SEO, social cards, and the blog index excerpt.
authors:
  - digitalgrease
categories:
  - Digital            # or Analog (pick one — categories carry the medium dichotomy)
tags:
  - engineering        # topic-only tags from the canonical set below
  - security
comments: true         # set false to disable Giscus comments
---

# Post Title

Brief introduction that will appear in the post preview...

<!-- more -->

## Main Content

The rest of your post goes here...
```

### Tag Glossary

The Digital ↔ Analog dichotomy is the spine of the site and is expressed deliberately in **both** layers:

- **Categories** (`Digital` / `Analog`) — pick exactly one. Drives the auto-generated `/posts/category/<world>/` pages and the per-post DIGITAL/ANALOG pill.
- **Prose tags** (`digital-prose` / `analog-prose`) — keep the medium-specific prose distinction; `/tags/prose/` is the merged cross-cutting view.

Canonical topic tags:

- `digital-prose` — essays, reflection, culture, retro-tech (Digital side)
- `analog-prose` — essays, reflection, land, craft (Analog side)
- `engineering` — software/systems write-ups, tooling, architecture
- `security` — offensive/defensive security, vulnerabilities, threat models
- `ai` — LLMs, ML systems, model behavior
- `privacy` — surveillance, anti-tracking, data minimization
- `transparency` — public audits, accountability tooling
- `homesteading` — land work, animals, infrastructure
- `blacksmithing` — forge, steel, metalwork

New tags are fine — singletons today may recur as the archive grows. Don't aggressively merge low-frequency tags into broader ones; let the taxonomy reflect what was actually written about.

### Style Guidelines

1. **Use clear, descriptive titles**
2. **Include proper frontmatter** with date, authors, categories, and tags
3. **Add the `<!-- more -->` marker** after your introduction to create a proper excerpt
4. **Use code blocks** with appropriate language tags for syntax highlighting
5. **Include examples** where relevant
6. **Use admonitions** for important notes, tips, and warnings

### Code Examples

Always specify the language for code blocks:

````markdown
```python
def example():
    return "Hello, World!"
```
````

### Admonitions

Use admonitions to highlight important information:

```markdown
!!! note "Important Note"
    This is important information readers should know.

!!! warning
    This is a warning about potential issues.

!!! tip
    This is a helpful tip for readers.
```

## Testing Locally

Before submitting:

1. Test your post locally with `mkdocs serve`
2. Verify all links work
3. Check that code examples are properly highlighted
4. Ensure images display correctly
5. Preview on different screen sizes if possible

## Pull Request Process

1. Fork the repository
2. Create a new branch for your post
3. Write your content
4. Test locally
5. Submit a pull request
6. Wait for review

## Questions?

If you have questions or need help, feel free to open an issue or reach out via the main site.

Thanks for contributing!
