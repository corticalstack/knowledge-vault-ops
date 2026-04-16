# Prerequisites

## GitHub Repository

You need a standard git repository pushed to GitHub. No special configuration is required beyond that, with one exception: both Actions (`vault-ingest` and `luminary-scan`) push commits back to the repository, so they need `contents: write` permission. This is declared at the top of each workflow YAML — GitHub-hosted runners honour it automatically.

If you intend to run on self-hosted runners or another CI platform, you will need to adapt the checkout and push steps accordingly. The Actions as written assume GitHub-hosted runners.

## SSH Key for GitHub

Obsidian Git pushes to your GitHub repository using SSH. You need an SSH key registered with GitHub before the plugin can authenticate.

If you do not already have one:

```bash
ssh-keygen -t ed25519 -C "your@email.com"
# Accept the default path (~/.ssh/id_ed25519) or choose your own
cat ~/.ssh/id_ed25519.pub
```

Copy the output and add it to GitHub: **GitHub → Settings → SSH and GPG keys → New SSH key**.

Then clone your vault repository using the SSH remote (not HTTPS):

```bash
git clone git@github.com:your-username/your-vault.git
```

If you already cloned with HTTPS, switch to SSH:

```bash
git remote set-url origin git@github.com:your-username/your-vault.git
```

Obsidian Git uses the SSH key from your system's default SSH agent. On Windows, ensure the key is added to your agent (`ssh-add ~/.ssh/id_ed25519`) or use a tool like Pageant. On macOS and Linux this is typically handled automatically.

## Obsidian Git Plugin

Install via: Obsidian → Settings → Community plugins → Browse → search "Obsidian Git" → Install → Enable.

Configuration used in this system:

- **Auto-pull on startup**: enabled — ensures you always start with the latest vault state
- **Auto-push after file change**: enabled (or set a short commit interval) — ensures new inbox files are pushed to GitHub promptly
- **Commit message**: `vault backup: {{date}}`

Why it matters: Obsidian Git is the trigger mechanism for `vault-ingest`. The full chain is: drop a file into `_inbox/` in Obsidian → Obsidian Git commits and pushes → GitHub sees the push → `vault-ingest` fires. Without auto-push, inbox files sit locally and nothing happens.

## Claude Code CLI Subscription

Install the CLI:

```bash
npm install -g @anthropic-ai/claude-code
```

Both Actions invoke `claude -p` (headless/non-interactive mode) and authenticate via the `CLAUDE_CODE_OAUTH_TOKEN` secret. This is a **Claude Code subscription token**, not a raw Anthropic API key from console.anthropic.com — the distinction matters:

- A Claude Code subscription token covers Action runs with no additional per-token cost.
- A raw API key would incur per-token charges on every Action run.

See [Costs](costs.md) for what this system would cost if you substituted a raw API key.

**How to get the token**: Claude.ai account settings → Claude Code → OAuth token. This is separate from anything at console.anthropic.com.

## Required GitHub Secrets

| Secret | Used by | What it is |
|--------|---------|------------|
| `CLAUDE_CODE_OAUTH_TOKEN` | Both Actions | Claude Code OAuth token from your Claude account |
| `VAULT_PAT` | luminary-scan only | GitHub PAT with `contents: write` scope |

Add via: GitHub repository → Settings → Secrets and variables → Actions → New repository secret.

**Why `VAULT_PAT` and not `GITHUB_TOKEN` for luminary-scan**: the standard `GITHUB_TOKEN` cannot trigger downstream workflow runs. `luminary-scan` pushes inbox files that should trigger `vault-ingest` — a PAT bypasses this restriction. The full reasoning is documented in [luminary-scan — Required Secrets](../reference/luminary-scan.md#required-secrets).
