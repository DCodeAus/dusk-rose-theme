# Security

Found a security problem in the installers or workflows? Please report it
privately with **Security › Report a vulnerability** on this repo instead of
opening a public issue.

## What's scanned automatically

| Tool | Checks |
|---|---|
| CodeQL | `build.py` and the GitHub Actions workflows |
| PSScriptAnalyzer | `install.ps1`, `install-putty.ps1` |
| ShellCheck | `install.sh` |
| Secret scanning + push protection | Blocks pushes that contain API keys or tokens |
| Dependabot | Alerts and update PRs for the GitHub Actions used here |
