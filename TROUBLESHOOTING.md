Troubleshooting the generated TopEmbed site

Common issues and how to diagnose them:

- Player shows "No channel loaded" or the iframe is blank
  - Click the "Open" link on the card to open the channel URL in a new tab. If that fails, TopEmbed may be refusing direct navigation for that channel.
  - Some channels are blocked by X-Frame-Options or CSP (frame-ancestors). If the channel page sets those headers, the channel cannot be shown in an iframe.

- Streams play but audio/video not present
  - Modern browsers may block autoplay. Try clicking inside the iframe or use the browser's play button. Allow autoplay in user settings if needed.

- Some channels work intermittently
  - These are third-party relays; availability changes frequently. The generator pulls a snapshot of available channels daily — some channels will be stale.

- I see CORS / Mixed Content errors in the console
  - If your site is HTTPS but the stream or TopEmbed resources use HTTP, the browser will block them. Ensure the generated page is served over HTTPS.

- Tips for debugging
  - Open the browser console (F12) to inspect network and console errors when trying a channel.
  - Use the generated `channels.json` in the output folder to see the raw list of channels fetched by the generator.

If a channel is blocked by the origin (TopEmbed) there is no reliable server-side fix — you may need to pick a different channel source or host a proxy (note: proxies raise legal and policy issues).
