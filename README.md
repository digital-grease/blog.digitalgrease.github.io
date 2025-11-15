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

Blog posts are located in `docs/posts/` and use the following format:

```markdown
---
date: 2025-11-14
authors:
  - digitalgrease
categories:
  - Category Name
tags:
  - tag1
  - tag2
---

# Post Title

Introduction paragraph...

<!-- more -->

Main content goes here...
```

### Post Guidelines

- Place posts in `docs/posts/`
- Use the YAML frontmatter shown above
- Add `<!-- more -->` to create an excerpt for the blog index
- Use meaningful categories and tags
- Include code examples with proper syntax highlighting

## Project Structure

```
.
├── .github/
│   └── workflows/
│       └── deploy.yml          # GitHub Actions deployment
├── docs/
│   ├── posts/                  # Blog posts
│   ├── stylesheets/            # Custom CSS
│   ├── javascripts/            # Custom JS
│   ├── assets/                 # Images, icons, etc.
│   ├── .authors.yml            # Author information
│   ├── index.md                # Homepage
│   ├── about.md                # About page
│   └── tags.md                 # Tags/categories page
├── overrides/                  # Theme overrides
├── mkdocs.yml                  # MkDocs configuration
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Customization

### Theme Colors

Edit `docs/stylesheets/cyberpunk.css` to customize the cyberpunk color scheme:

```css
:root {
  --cyber-cyan: #00ffff;
  --cyber-magenta: #ff00ff;
  --cyber-green: #00ff41;
  /* Add more custom colors */
}
```

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
