# TKA Game Dev with Python — Web Games

Pygame games built to run in the browser (via [pygbag](https://pygame-web.github.io/) + WebAssembly),
hosted for free on GitHub Pages.

## Games

| Folder        | Game                |
|---------------|---------------------|
| `maze-runner` | Maze Runner (Justin Vitu) |
| `space-shooter` | Space Shooter (Nanta) |
| `cowboy`      | Cowboy / Pony Express (Sovannvibol) |
| `drone-hunter` | Drone Hunter (Thakraknint) |

Each game folder contains a `main.py` entry point plus its `images/` and `audio/` assets.

## Run a game locally (desktop)

```bash
cd maze-runner
pip install pygame-ce
python main.py
```

## Deploy for free on GitHub Pages

1. Create a **public** GitHub repository (e.g. `tka-games`). GitHub Pages is free for public repos.
2. Copy the whole contents of this folder (the `.github/` folder included) into the repo and push:

   ```bash
   git init
   git add .
   git commit -m "Add games"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/tka-games.git
   git push -u origin main
   ```

3. In the repo on GitHub: **Settings → Pages → Source → "GitHub Actions"**.
4. Push again (or run the workflow manually from the **Actions** tab). The workflow
   `.github/workflows/deploy.yml` builds every game and deploys to Pages.

Your games will be live at:

- `https://YOUR_USERNAME.github.io/tka-games/maze-runner/`
- `https://YOUR_USERNAME.github.io/tka-games/space-shooter/`
- `https://YOUR_USERNAME.github.io/tka-games/cowboy/`
- `https://YOUR_USERNAME.github.io/tka-games/drone-hunter/`

## Notes

- **Audio**: pygbag supports OGG in the browser best. The games currently load WAV/MP3 defensively
  (sound is skipped if it can't be loaded). To restore sound on the web, convert the sounds to
  `.ogg` and use that filename in the code. On desktop the original WAV/MP3 files still work.
- **Filenames are case-sensitive** on GitHub Pages (Linux). The code uses the exact casing of the
  asset files.
