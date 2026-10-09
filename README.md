# Hadalird

Optional small and medium application integrations for Hadalis: TLP, Thinkfan
and Obsidian. Hadalis owns generic Battery, Power Profiles, Todo, Notes,
configuration and UI primitives. Hadalird owns the integration workers,
application-specific settings, byte-safe vault helpers and privileged helper
payloads. Existing integration preferences and application data are retained.

Install a committed revision with `make install`. Installation does not enable
an integration, launch Obsidian, change fan/charge policies, or stop existing
system services. Each integration loads one disposable QML tree when explicitly
enabled in Hadalis. Missing packages report unavailable rather than claiming an
operation succeeded. `make uninstall` deactivates only this package's owned
link; releases, user configuration, vaults and system services are preserved.

Privileged helper installation is separate: `sudo make install-helpers`.
This installs helper/polkit/schema files and does not enable services or create
TLP configuration overrides. Prefixes and `DESTDIR` are supported for packaging.
`LIBEXECDIR`, `POLKIT_ACTIONS_DIR`, `INIR_SYSTEM_SHAREDIR` and `TLP_CONFDIR`
control helper, policy, schema and profile locations; helper installation does
not create profile directories or overrides. TLP (including its optional
Radio Device Wizard), Thinkfan and Obsidian remain separately installed apps.

Run `make test` for scoped filesystem/helper and installation contracts.
Initial provenance is recorded in `manifest.json`. Host cutover and native
integration qualification are tracked in Hadalis `to-do/cloud-bot/ABYSS.md`.

Classic and Waffle TLP editors and Obsidian task/capture settings are owned
here. Hadalis retains navigation, optional loaders, generic Battery controls
and the preserved internal Todo store. The version 0.2 settings entrypoints
are additive for host API 1; update Hadalird before the corresponding host
cutover. Integration enable switches remain off by default.
