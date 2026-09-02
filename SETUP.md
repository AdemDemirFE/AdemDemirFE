# GitHub Profile Setup

This version removes the unreliable external analytics image endpoints.

## 1. Repository

Use this repository as the profile repository:

`AdemDemirFE/AdemDemirFE`

## 2. Replace README

Copy `README.md` to the root of the profile repository.

## 3. Add workflow files

Copy:

- `.github/workflows/metrics.yml`
- `.github/workflows/snake.yml`
- `scripts/generate_metrics.py`
- `assets/*.svg`

## 4. Enable Actions

Open **Settings → Actions → General** and make sure GitHub Actions can run and the workflow has permission to write repository contents.

The workflows use the repository's built-in `GITHUB_TOKEN`; no personal access token is required for public profile metrics.

## 5. Run once

Open **Actions** and manually run:

- `Update Profile Metrics`
- `Generate Profile Graphics`

After the first successful run, the README reads the generated SVG files directly from the repository, so there are no Vercel image dependencies.

## 6. Why this works

The README no longer depends on:

- github-readme-stats.vercel.app
- github-readme-activity-graph.vercel.app
- github-profile-trophy.vercel.app

Those services can be unavailable, rate-limited or paused. The profile cards are now generated and committed by your own GitHub Actions workflow.
