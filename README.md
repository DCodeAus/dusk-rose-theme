# Rosé All Night

*…and Rosé All Day.*

A VS Code theme for long coding sessions. It has a soft slate background, a dusty-rose accent and muted pastel syntax colours, plus a matching light version for daytime.

![icon](icon.png)

## Why it's easy on the eyes

- **No pure black or pure white.** The dark background is slate `#1d1e26` and the light one is warm off-white `#faf6f4`. Bright text on pure black tends to glow and blur. Pure white glares in a bright room.
- **Muted colours, not neon.** Every syntax colour is readable (at least 4.5:1 contrast) but not glaring (the dark theme stays under 13:1). `build.py` checks this every time it runs, so a tweak can't quietly make the theme worse.
- **One accent colour.** Dusty rose marks the important things: keywords, the cursor, the current line number and the active tab. Everything else stays calm, so your eye has a resting place.
- **Every part of VS Code is styled.** That includes ghost-text suggestions, inlay hints, diffs, merge conflicts, menus and the terminal, so nothing falls back to VS Code's default bright blue.

| Role | Dark | Light |
|---|---|---|
| Keywords / accent | `#e7a1c1` | `#b0396e` |
| Strings | `#a9d1a0` | `#4d7a3f` |
| Functions | `#8fbce6` | `#2f69a3` |
| Types / classes | `#c3aef0` | `#7650b8` |
| Numbers, constants, decorators (orange) | `#f4a466` | `#ad4f12` |
| Properties / keys | `#9fd4d2` | `#237873` |
| Comments | `#858aa0` | `#6f6a78` |

## Install

**macOS / Linux:**

```bash
curl -fsSL https://raw.githubusercontent.com/DCodeAus/dusk-rose-theme/main/install.sh | bash
```

**Windows (PowerShell):**

```powershell
irm https://raw.githubusercontent.com/DCodeAus/dusk-rose-theme/main/install.ps1 | iex
```

You can also download the `.vsix` file from [Releases](https://github.com/DCodeAus/dusk-rose-theme/releases) and install it with **Extensions › ⋯ › Install from VSIX…**.

Run the same command again to update. Settings Sync copies your *settings* between machines, but it won't install this theme for you, so run the installer once on each machine.

## PuTTY (Windows)

PuTTY gets the same colours as the VS Code terminal. Close any PuTTY windows, then run this in PowerShell:

```powershell
irm https://raw.githubusercontent.com/DCodeAus/dusk-rose-theme/main/install-putty.ps1 | iex
```

This themes **new sessions and every saved session**. It also turns off cursor blinking and switches to Consolas 12pt with ClearType smoothing. PuTTY's default is Courier New 10pt, which is small and thin.

**No admin rights needed.** PuTTY stores its settings in your own part of the registry, and the script uses plain PowerShell, not `reg.exe` or regedit, which work PCs often block.

**Undo:** before changing anything, it saves your current settings to `putty-backup-<date>.reg` in your user folder and prints the undo command, for example `.\install-putty.ps1 -Restore "$HOME\putty-backup-<date>.reg"`.

- **Options** (light version, keep your current font):
  ```powershell
  & ([scriptblock]::Create((irm https://raw.githubusercontent.com/DCodeAus/dusk-rose-theme/main/install-putty.ps1))) -Variant Light -KeepFont
  ```
  PuTTY can't follow Windows light/dark mode, so pick whichever suits the room you usually work in.
- **"Running scripts is disabled":** if you downloaded the file, run `powershell -ExecutionPolicy Bypass -File .\install-putty.ps1`. This applies to that one run only and doesn't need admin. The `irm` commands above aren't affected.
- **Preview first:** add `-WhatIf` to see every change without making it (download the file and run it with `.\install-putty.ps1 -WhatIf`).
- **Portable PuTTY** keeps its settings in a file instead of the registry, so this script can't theme it.
- **New sessions only, no script:** double-click [`putty/dusk-rose.reg`](putty/dusk-rose.reg) or [`putty/dusk-rose-light.reg`](putty/dusk-rose-light.reg), if your PC allows `.reg` files.

## Mac terminals

Both use the same colours as the VS Code terminal and PuTTY. Neither needs admin rights.

**iTerm2:** download [`iterm/Rosé All Night.itermcolors`](iterm/) and double-click it. That adds it to iTerm's colour list. Then go to **Settings › Profiles › Colors › Color Presets…** and choose **Rosé All Night**.
To switch with your Mac's light/dark mode, tick **Use separate colors for light and dark mode** on that tab. Choose **Rosé All Day** while the light side is selected and **Rosé All Night** while the dark side is selected.

**Terminal (built-in app):** download [`terminal-app/Rosé All Night.terminal`](terminal-app/) and double-click it. A window opens using it. Then go to **Terminal › Settings › Profiles**, select **Rosé All Night** and click **Default**. The cursor doesn't blink. For comfort, also click **Change…** under Font and pick SF Mono or Menlo at 13pt. Terminal can't switch with light/dark mode, so pick one.

## Recommended settings

These make VS Code switch to the light theme when your computer is in light mode and back to dark at night. They also give the text more room:

```jsonc
"window.autoDetectColorScheme": true,
"workbench.preferredDarkColorTheme": "Dusk Rose",
"workbench.preferredLightColorTheme": "Dusk Rose Light",
"workbench.colorTheme": "Dusk Rose",
// (Settings use the original IDs "Dusk Rose" / "Dusk Rose Light";
//  the theme picker shows them as Rosé All Night / Rosé All Day.)
"editor.fontSize": 14,
"editor.lineHeight": 1.6,
"editor.fontFamily": "'JetBrains Mono', Menlo, Consolas, monospace",
"editor.fontLigatures": false,
"terminal.integrated.fontFamily": "'JetBrains Mono', Menlo, Consolas, monospace",
"terminal.integrated.fontSize": 13,
"editor.cursorBlinking": "smooth",
"editor.renderLineHighlight": "gutter"
```

**Font:** [JetBrains Mono](https://www.jetbrains.com/lp/mono/) is free and has real italics. Menlo, the Mac default, only slants its upright letters, so the theme's italic comments and parameters look smeared. JetBrains Mono also has tall lowercase letters and makes `0/O` and `1/l/I` easy to tell apart. If a machine doesn't have it, VS Code falls back to Menlo or Consolas, so the settings are safe to sync everywhere.

- **Mac:** `brew install --cask font-jetbrains-mono`
- **Windows:** download it, unzip it, select the `.ttf` files in `fonts/ttf`, then right-click and choose **Install**. That's a per-user install, so no admin is needed.

Restart VS Code fully after installing the font.

## Change a colour

1. Edit the colour in `DARK` or `LIGHT` near the top of `build.py`.
2. Run `python3 build.py`. If a colour is too faint, it tells you.
3. Preview it locally:
   ```bash
   npx @vscode/vsce package
   code --install-extension dusk-rose-*.vsix --force
   ```
   Then in VS Code, run **Developer: Reload Window**. Open the files in `samples/` to see each language.
4. To release it to your other machines, bump `version` in `package.json` and merge the change. Then run `git tag vX.Y.Z && git push origin vX.Y.Z`. GitHub builds the release, and the install command picks it up.

## Licence

MIT
