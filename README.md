# Firefly Cottage

Direct booking website for Firefly Cottage, a vacation rental in Pigeon Forge, Tennessee, owned and
operated by MGB Investments LLC. Live at https://fireflycottagetn.com.

- `index.html` is the whole site. All property content lives in the `CONFIG` block near the bottom.
- `calendar.json` holds availability and per-date minimum stays. The site ignores it once it is more
  than 72 hours old. Automatic 6-hourly refresh is ready in `ops/deploy-workflow.yml`; to switch it
  on, move that file to `.github/workflows/deploy.yml`, set Pages to deploy from GitHub Actions, and
  add the `HOSPITABLE_TOKEN` repository secret (read-only token).
- Booking, payments and every booking rule are enforced by Hospitable Direct, not by this site.

Note: GitHub pauses scheduled workflows after 60 days with no repository activity and emails the
owner first. Re-enable it from the Actions tab if that happens.
