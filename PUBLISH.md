# Maintaining and Publishing Updates

The project is already publicly available:

**https://github.com/vampr5861-debug/arch-hyprland-dotfiles**

## Inspect the local clone

From your own checkout directory:

~~~bash
cd arch-hyprland-dotfiles
git status --short
git branch --show-current
git log --oneline -5
~~~

Changes to files in your live `~/.config/` directory **do not automatically update this clone**. Review any changed configuration and copy only the intended, non-sensitive files into the matching paths under `home/.config/`.

Preserve existing local changes. With a clean tree, fetch remote updates and choose an appropriate base before starting a dedicated branch. Reuse a suitable existing work branch rather than repeating completed work. Do not reset or rewrite history to synchronize the clone.

## Prepare and review a working branch

For a new change, choose an unused branch name:

~~~bash
git switch -c docs/refine-installation
~~~

Review both unstaged and staged changes:

~~~bash
git status --short
git diff --check
git diff
git diff --cached --check
git diff --cached
~~~

Check for secrets, private paths, personal data, binaries with uncertain licenses and unintentional backup files. Also verify that third-party licenses and attributions are preserved. Do not commit whole application profiles, session data, tokens or SSH keys.

## Commit and publish only after review

These are manual maintainer steps, not instructions for an assistant to commit or publish without authorization. Keep changes uncommitted until their owner approves them. Never commit directly to `main`, force-push, automatically merge or create releases as part of routine cleanup.

Once approved, stage specific paths and inspect the staged diff before committing:

~~~bash
git add README.md
git diff --cached --check
git diff --cached
git commit -m "Update documentation"
~~~

The example stages **README.md only**. To publish other files, specify their paths explicitly rather than using `git add -A` without review.

After a separate publication decision, push the reviewed working branch explicitly (replace the example with your actual branch) and open a pull request:

~~~bash
git push --set-upstream origin docs/refine-installation
~~~

If Git reports an unknown author identity, configure a repository-local author name and a GitHub-verified email address or the correct GitHub `noreply` address. Reuse existing authentication. On a personal machine without configured access, GitHub CLI or SSH can establish it; never put credentials in tracked files or remote URLs.

## Repository-specific notes

- Wlogout's unverified PNG icons were excluded and replaced with text labels.
- Dracula GTK and Notwaita cursor files retain upstream licensing and attribution notices. The optional Dracula archive has missing resources; see [AUDIT.md](AUDIT.md#repository-review--november-5-2026).
- Wallpapers from Wallhaven are not shipped because redistribution permissions have not been verified.
- The three supplied screenshots show a local LAN address; the desktop preview also exposes a username / hostname and system details. Review the privacy and wallpaper redistribution implications before publication.
- Cava shader provenance and redistribution terms are not fully established; retain notices and resolve the [audit findings](AUDIT.md#repository-review--november-5-2026) before claiming complete license compliance.
- The published configuration has not been tested on every system; avoid promising universal one-command installation.

The repository is a **manual configuration reference**, not a turnkey installer or a verified reproducible system image.


## Automated checks

Pushes to `main` and pull requests run the workflow in `.github/workflows/validate.yml`; pushes to other branches alone do not trigger it. It checks JSON (including the Wlogout object stream), TOML, selected INI / XML files, Hyprland Lua syntax and archived shell helper syntax. It can also be started manually with `workflow_dispatch` where available.

Wait for the workflow to finish before treating a change as validated. These are static checks only; they do not test the desktop on different hardware or display layouts.
