# Maintaining and Publishing Updates

The project is already publicly available:

**https://github.com/vampr5861-debug/arch-hyprland-dotfiles**

## Update the local clone

From the original machine, the working clone is located at:

~~~bash
cd ~/Downloads/dotfiles-final/arch-hyprland-dotfiles
git pull --ff-only
~~~

Changes to files in your live `~/.config/` directory **do not automatically update this clone**. Review any changed configuration and copy only the intended, non-sensitive files into the matching paths under `home/.config/`.

## Review changes before pushing

~~~bash
git status --short
git diff
git diff --cached --check
~~~

Check for secrets, private paths, personal data, binaries with uncertain licenses and unintentional backup files. Also verify that third-party licenses and attributions are preserved. Do not commit whole application profiles, session data, tokens or SSH keys.

## Commit and push

~~~bash
git add README.md
git commit -m "Update documentation"
git push
~~~

The example stages **README.md only**. To publish other files, specify their paths explicitly rather than using `git add -A` without review.

If Git reports an unknown author identity, configure the repository-local author name and a GitHub-verified email address or the correct GitHub `noreply` address. If GitHub requires authentication, use GitHub CLI (`gh auth login` and `gh auth setup-git`) rather than your account password.

## Repository-specific notes

- Wlogout's unverified PNG icons were excluded and replaced with text labels.
- Dracula GTK and Notwaita cursor files retain upstream licensing and attribution notices.
- Wallpapers from Wallhaven are not shipped because redistribution permissions have not been verified.
- Some provided screenshots show a local LAN address. Review screenshots before publication.
- The published configuration has not been tested on every system; avoid promising universal one-command installation.

The repository is a **manual, reproducible reference**, not a turnkey installer.
