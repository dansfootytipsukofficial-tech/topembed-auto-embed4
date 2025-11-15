TopEmbed automatic embed generator

What this does

- Fetches the TopEmbed JSON API (https://topembed.pw/api.php?format=json)
- Builds a lightweight static HTML page (index.html) with a grid of channels
- The grid uses a lightweight lazy-load player: clicking a tile loads the TopEmbed channel in a single iframe (minimizes resource use)
- A GitHub Action runs daily and publishes the generated files to the gh-pages branch so you get a public URL (https://<user>.github.io/<repo>/)

Why use this

- Avoids CORS/referrer issues by serving a static page from your own origin
- Keeps your site light by lazy-loading a single player iframe
- Automates daily refresh of the channel list

Important legal and AdSense notes

- Many TopEmbed channels mirror paid/copyrighted streams. Make sure you have rights to reproduce or embed streams on your site. Hosting or redistributing copyrighted content without permission may get you in legal trouble and could violate Google AdSense policy.
- This generator does NOT add or manipulate any AdSense code. If you display Google AdSense on pages that embed third-party streams, verify that doing so complies with AdSense and local law. If unsure, keep AdSense disabled on the pages that display third-party streams.

How to use (quick)

1. Create a new GitHub repository (public or private). Clone it locally.
2. Copy the contents of this folder into the repo root and push.
3. In the repo on GitHub, enable Actions; the workflow will run on commit and on the scheduled cron.
4. The workflow publishes the generated site to the gh-pages branch. You can enable GitHub Pages to serve the gh-pages branch (or use Netlify pointing at gh-pages).
5. Embed the generated page into your website using an iframe, for example in a post or the page where you want streams:

<iframe src="https://<your-gh-username>.github.io/<repo>/" width="100%" height="900" style="border:0;"></iframe>

Files in this package

- generate.py — generator script (fetch API and write index.html)
- .github/workflows/generate.yml — GitHub Action to run daily and publish to gh-pages
- README.md — this file

Customization

- Change the number of channels or filtering in generate.py (max channels variable).
- Adjust styles in the HTML template inside generate.py.

Support / next steps

If you want I can:
- Create and push this repo to your GitHub (I won't do that without your permission).
- Modify the generator to create per-channel detail pages or thumbnails.
- Convert to a serverless function approach instead of static site if you prefer dynamic on-demand embeds.

Troubleshooting

See `TROUBLESHOOTING.md` for common issues (empty iframe, CSP/X-Frame-Options blocks, CORS/mixed-content, and debugging tips). The generator also emits a `channels.json` file next to the generated `index.html` which lists the raw channel URLs it fetched.
