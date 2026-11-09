#!/usr/bin/env bash
# =============================================================================
# Dusk Rose - install / update on macOS or Linux
#
# WHAT IT DOES   Downloads the newest Dusk Rose release from GitHub and installs
#                it into VS Code. Run it again any time to update.
# YOU NEED       VS Code with the `code` command available. If `code` isn't found:
#                open VS Code > Cmd+Shift+P > "Shell Command: Install 'code'
#                command in PATH", then run this again.
# HOW TO RUN     curl -fsSL https://raw.githubusercontent.com/DCodeAus/dusk-rose-theme/main/install.sh | bash
# AFTERWARDS     In VS Code: Cmd+Shift+P > "Developer: Reload Window".
#                Pick the theme with Cmd+K Cmd+T if it isn't already selected.
# =============================================================================
set -euo pipefail

REPO="DCodeAus/dusk-rose-theme"

# Stop early with a clear message if VS Code's command-line tool is missing.
if ! command -v code >/dev/null 2>&1; then
  echo "Can't find the 'code' command - see 'YOU NEED' at the top of this script." >&2
  exit 1
fi

# Ask GitHub for the newest release and pick out the .vsix download link.
echo "Finding the latest Dusk Rose release..."
URL=$(curl -fsSL "https://api.github.com/repos/$REPO/releases/latest" \
      | grep -o '"browser_download_url": *"[^"]*\.vsix"' | head -1 | cut -d'"' -f4)
if [ -z "$URL" ]; then
  echo "Couldn't find a release to download. Check https://github.com/$REPO/releases" >&2
  exit 1
fi

# Download into a throwaway folder that's cleaned up afterwards.
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
echo "Downloading $(basename "$URL")..."
curl -fsSL "$URL" -o "$TMP/dusk-rose.vsix"

# --force replaces any older copy.
code --install-extension "$TMP/dusk-rose.vsix" --force
echo "Done. Reload VS Code (Cmd+Shift+P > Developer: Reload Window)."
