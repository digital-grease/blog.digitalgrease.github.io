# Contributing to the Blog

Thank you for your interest in contributing! Here are some guidelines to help you get started.

## Writing Blog Posts

### Post Format

All blog posts should be placed in `docs/posts/` with the following format:

```markdown
---
date: YYYY-MM-DD
authors:
  - digitalgrease
categories:
  - Category1
  - Category2
tags:
  - tag1
  - tag2
  - tag3
---

# Post Title

Brief introduction that will appear in the post preview...

<!-- more -->

## Main Content

The rest of your post goes here...
```

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
