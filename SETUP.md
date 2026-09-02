# AdemDemirFE GitHub Profile — Reliable Version

## Why this version is different

The previous profile depended on external SVG/analytics providers. This version removes those fragile dependencies from the analytics section entirely.

The README is valid even if GitHub Actions has never run: there are no missing local image files and no broken statistics image URLs.

## Install

Repository must be:

`AdemDemirFE/AdemDemirFE`

Copy these files to the repository root:

- `README.md`
- `scripts/update_profile_metrics.py`
- `.github/workflows/profile-metrics.yml`

## Activate

1. Push the files to the `main` branch.
2. Open **Actions** in GitHub.
3. Open **Update GitHub Profile Metrics**.
4. Click **Run workflow** once.
5. Refresh the profile page.

The workflow runs every 6 hours afterward.

## Important repository setting

If GitHub prevents the workflow from pushing changes, open:

**Settings → Actions → General → Workflow permissions**

and select:

**Read and write permissions**

Then run the workflow again.

## Result

The profile no longer needs:

- `github-readme-stats.vercel.app`
- `github-readme-activity-graph.vercel.app`
- `github-profile-trophy.vercel.app`
- a local SVG assets folder for analytics
- a separate snake publishing branch

All live profile numbers are written directly into `README.md` by GitHub Actions.
