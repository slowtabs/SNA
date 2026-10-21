# Network Lens dashboard

An interactive, browser-local companion to the Social Network Analysis project. It exposes the same Karate Club example and analysis concepts used in the notebooks:

- graph summary statistics and an interactive network view;
- degree, closeness, betweenness, eigenvector, and PageRank centrality;
- deterministic label-propagation community detection;
- a sequential high-betweenness removal resilience experiment; and
- JSON export of the complete analysis.

## Run as a website

```bash
cd dashboard
npm install
npm run dev
```

Import a `.csv`, `.txt`, or edge-list file containing one relationship per line, for example `alice,bob` or `alice bob`. Comments beginning with `#` or `%` are ignored. The dashboard processes the selected file entirely in the browser; it does not upload it anywhere. Toggle **Directed graph** before importing directed data.

## Deploy to Vercel

Import this repository into Vercel and set the project Root Directory to `dashboard`. Vercel detects the included `vercel.json`, runs `npm run build`, and publishes `dist`. Or deploy from this folder with the Vercel CLI.

```bash
cd dashboard
npx vercel
```

## Run as a desktop app

Electron wraps the same React renderer for a local desktop experience:

```bash
npm run electron:dev
```

For a production desktop shell, run `npm run build` and then `npm run electron`.

Electron is not itself deployable to Vercel. The shared renderer is: Vercel hosts the web version, while Electron runs the desktop version locally.
