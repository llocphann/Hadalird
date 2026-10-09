LIBEXECDIR ?= /usr/libexec
POLKIT_ACTIONS_DIR ?= /usr/share/polkit-1/actions
INIR_SYSTEM_SHAREDIR ?= /usr/share/inir
TLP_CONFDIR ?= /etc/tlp.d

.PHONY: test install uninstall install-helpers
test:
	@python3 scripts/test-install.py
	@sh scripts/test-battery-charge-limit-helper.sh
	@bash scripts/test-thinkfan-helper.sh
	@python3 scripts/test-todo-obsidian-helper.py
	@python3 scripts/test-todo-obsidian-daily-helper.py
	@python3 scripts/test-todo-obsidian-tasks-runtime.py
	@python3 scripts/test-obsidian-theme.py
	@python3 scripts/test-zettelkasten-quicknote.py
	@python3 scripts/test-qml.py
	@python3 scripts/test-host-runtime.py

install:
	@python3 scripts/install.py install
uninstall:
	@python3 scripts/install.py uninstall

# Installation never changes hardware state, stops services or writes profiles.
install-helpers:
	@set -eu; stage=$$(mktemp -d); trap 'rm -rf "$$stage"' EXIT HUP INT TERM; \
	 sed -e 's|^config_dir=.*|config_dir=$(TLP_CONFDIR)|' \
	     -e 's|^tlp_settings_schema=.*|tlp_settings_schema=$(INIR_SYSTEM_SHAREDIR)/tlp-settings-schema.json|' \
	     assets/helpers/inir-battery-charge-limit > "$$stage/battery"; \
	 install -Dm755 "$$stage/battery" "$(DESTDIR)$(LIBEXECDIR)/inir-battery-charge-limit"; \
	 install -Dm755 assets/helpers/inir-thinkfan "$(DESTDIR)$(LIBEXECDIR)/inir-thinkfan"; \
	 sed 's|/usr/libexec/inir-battery-charge-limit|$(LIBEXECDIR)/inir-battery-charge-limit|g' assets/polkit/org.inir.battery-charge-limit.policy > "$$stage/tlp.policy"; \
	 install -Dm644 "$$stage/tlp.policy" "$(DESTDIR)$(POLKIT_ACTIONS_DIR)/org.inir.battery-charge-limit.policy"; \
	 sed 's|/usr/libexec/inir-thinkfan|$(LIBEXECDIR)/inir-thinkfan|g' assets/polkit/org.inir.thinkfan.policy > "$$stage/fan.policy"; \
	 install -Dm644 "$$stage/fan.policy" "$(DESTDIR)$(POLKIT_ACTIONS_DIR)/org.inir.thinkfan.policy"; \
	 install -Dm644 assets/tlp/tlp-settings-schema.json "$(DESTDIR)$(INIR_SYSTEM_SHAREDIR)/tlp-settings-schema.json"
