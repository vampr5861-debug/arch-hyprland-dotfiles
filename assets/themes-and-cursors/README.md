# Темы и курсоры

Включены из переданного архива (без перекодирования, без установки в текущую систему):

- `home/.local/share/themes/Dracula-pink-accent/` — тема GTK; полный исходный
  `LICENSE` GPL-3.0 и авторский `README.md` оставлены внутри каталога.
  Проект: https://github.com/dracula/gtk (Eliver Lara и участники).
- `home/.local/share/icons/Notwaita-Black/` — курсор. Сведения о происхождении
  и лицензии: `LICENSES/notwaita-cursor-NOTICE.md`.
- `home/.local/share/icons/default/index.theme` — указание курсора по умолчанию.

**Настройки в переданных `gtk-3.0/settings.ini`, `gtk-4.0/settings.ini` и
`xsettingsd.conf` указывают на `Materia-dark`, а не на `Dracula-pink-accent`.**
Тема Dracula установлена, но не подтверждена как текущая активная GTK-тема.
Не переключайте её автоматически при установке dotfiles.

**Не включены**: `Bibata-Modern-Ice` (каталог не предоставлен), системная тема
`Materia-dark`, `Papirus-Dark`, сторонние шрифты и сами обои с Wallhaven.
Их следует устанавливать отдельно из официальных пакетов и источников.

При распаковке на Linux важно сохранять символические ссылки внутри темы и
курсора. Они ссылаются только на файлы внутри переданных каталогов.
