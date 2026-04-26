# Digital Grease Blog

A cyberpunk-themed technical blog built with Material for MkDocs, covering cybersecurity, software development, and technology.

## Features

- **Dark Cyberpunk Theme**: Custom CSS with neon colors, glow effects, and animated elements
- **Material for MkDocs**: Modern, responsive documentation framework
- **Blog Plugin**: Full-featured blogging with categories, tags, and archives
- **GitHub Pages**: Automated deployment via GitHub Actions
- **Rich Content**: Code highlighting, admonitions, diagrams, and more

## Setup

### Prerequisites

- Python 3.x
- pip

### Local Development

1. Clone the repository:

```bash
git clone https://github.com/digitalgrease/blog.digitalgrease.github.io.git
cd blog.digitalgrease.github.io
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the development server:

```bash
mkdocs serve
```

4. Open your browser to `http://127.0.0.1:8000`

The site will auto-reload when you make changes to the documentation.

### Building the Site

To build the static site:

```bash
mkdocs build
```

The built site will be in the `site/` directory.

## Writing Blog Posts

Blog posts live in `docs/posts/posts/` (the double-nesting is the MkDocs blog plugin's `blog_dir: posts` convention) and use the following format:

```markdown
---
date: 2026-01-15
slug: post-slug-for-url
description: One-line summary used for SEO, social cards, and the blog index excerpt.
authors:
  - digitalgrease
categories:
  - Digital            # or Analog — pick one (the world the post belongs to)
tags:
  - engineering        # topic only — see CONTRIBUTING.md for the canonical tag glossary
  - security
comments: true         # set false to disable Giscus comments on this post
---

# Post Title

Introduction paragraph that becomes the excerpt on the blog index...

<!-- more -->

Main content goes here...
```

### Post Guidelines

- Place posts in `docs/posts/posts/`
- Use the YAML frontmatter shown above
- Add `<!-- more -->` to create an excerpt for the blog index
- Pick exactly one of `Digital` or `Analog` for the category; tags are topic-only
- Include code examples with proper syntax highlighting

## Project Structure

```
.
├── .github/
│   └── workflows/
│       └── deploy.yml          # GitHub Actions deployment
├── docs/
│   ├── posts/
│   │   ├── index.md            # Blog landing page
│   │   └── posts/              # Actual post markdown files
│   ├── stylesheets/            # Custom CSS (forge-*.css)
│   ├── assets/                 # Images, icons, etc.
│   ├── tags/                   # Per-tag landing pages
│   ├── .authors.yml            # Author information
│   ├── index.md                # Homepage
│   ├── about.md                # About page
│   ├── projects.md             # Projects index
│   ├── tags.md                 # All-tags page
│   └── 404.md                  # Not-found page
├── overrides/                  # Theme overrides
│   ├── main.html               # Adds preconnect + Share Tech Mono font
│   ├── blog-post.html          # Adds previous/next post navigation
│   └── partials/               # Header, comments, series-nav
├── mkdocs.yml                  # MkDocs configuration
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Customization

### Theme Colors

Theme tokens live in `docs/stylesheets/forge-variables.css`. The stylesheet stack is split by concern:

- `forge-variables.css` — color tokens, glow shadows
- `forge-base.css` — body, header, main content backgrounds
- `forge-typography.css` — headings, links, code
- `forge-components.css` — buttons, search, articles, tags, admonitions, footer
- `forge-navigation.css` — sidebar and nav
- `forge-effects.css` — atmospheric overlays + `prefers-reduced-motion` block
- `forge-home.css` — home-page-specific (hero, embers, category tiles, project tiles)
- `forge-light.css` — light-mode overrides
- `forge-mobile.css` — responsive breakpoints
- `extra.css` — small utilities (reading-progress bar, post-nav, series-nav)

### Configuration

Main configuration is in `mkdocs.yml`. Key sections:

- **theme**: Material theme settings and features
- **plugins**: Enabled plugins (blog, search, tags)
- **markdown_extensions**: Enabled Markdown features
- **nav**: Site navigation structure

## Deployment

The site automatically deploys to GitHub Pages when you push to the `main` branch.

### Initial Setup

1. Enable GitHub Pages in your repository settings
2. Set source to "gh-pages" branch
3. Push to main branch to trigger deployment

The GitHub Actions workflow will:
- Install dependencies
- Build the site with MkDocs
- Deploy to the `gh-pages` branch

## Contributing

Feel free to open issues or submit pull requests for improvements.

## License

Content is licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).

## Links

- **Blog**: [blog.digitalgrease.dev](https://blog.digitalgrease.dev)
- **Homepage**: [digitalgrease.dev](https://digitalgrease.dev)
- **GitHub**: [github.com/digitalgrease](https://github.com/digitalgrease)

---

Built with [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
