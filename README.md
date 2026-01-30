# The Public Desk - News Website

A simple, easy-to-manage news website built with Jekyll for GitHub Pages.

## Quick Start

### Setting Up on GitHub Pages

1. Go to your repository's **Settings** → **Pages**
2. Under "Source", select **Deploy from a branch**
3. Select **main** (or your branch) and **/ (root)**
4. Click **Save**
5. Your site will be live at `https://yourusername.github.io/repository-name/`

---

## How to Manage Content

### Adding a New News Story

1. Go to the `_posts` folder
2. Create a new file with this naming format: `YYYY-MM-DD-your-story-title.md`
   - Example: `2026-02-01-city-council-meeting-recap.md`
3. Add this at the top of your file:

```markdown
---
layout: post
title: "Your Story Title Here"
date: 2026-02-01
author: Your Name
---

Your story content goes here...
```

4. Write your story using Markdown formatting
5. Commit and push your changes

### Editing an Existing Story

1. Go to the `_posts` folder
2. Find and open the story file you want to edit
3. Make your changes
4. Commit and push

### Editing the About Page

1. Open `about.md` in the root folder
2. Edit the content (keep the header section between the `---` lines)
3. Commit and push

---

## Markdown Quick Reference

```markdown
# Big Heading
## Section Heading
### Smaller Heading

**bold text**
*italic text*

- Bullet point
- Another bullet

1. Numbered list
2. Second item

> This is a quote

[Link text](https://example.com)

![Image description](/assets/images/image-name.jpg)
```

---

## Adding Images to Stories

1. Upload your image to `/assets/images/`
2. Reference it in your story:

```markdown
![Description](/assets/images/your-image.jpg)
```

---

## File Structure

```
/
├── _config.yml          # Site settings (title, description)
├── _layouts/            # Page templates (don't edit unless needed)
│   ├── default.html
│   └── post.html
├── _posts/              # YOUR NEWS STORIES GO HERE
│   └── YYYY-MM-DD-title.md
├── assets/
│   └── images/          # Images including logo
│       └── logo.png
├── about.md             # EDIT THIS for About page
├── index.html           # Home page (auto-displays posts)
└── README.md            # This file
```

---

## Customizing

### Change Site Title/Description
Edit `_config.yml`:
```yaml
title: The Public Desk
description: Your description here
```

### Change Colors
Edit the `<style>` section in `_layouts/default.html`. The main colors are:
- `#1a3a5c` - Navy blue (main color)
- `#c9a227` - Gold accent
- `#ffffff` - White background

---

## Need Help?

- [Markdown Guide](https://www.markdownguide.org/basic-syntax/)
- [Jekyll Documentation](https://jekyllrb.com/docs/)
- [GitHub Pages Documentation](https://docs.github.com/en/pages)
