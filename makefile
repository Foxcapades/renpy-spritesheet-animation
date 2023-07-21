LAST_TAG = $(shell git describe --tags --abbrev=0 | sed 's/v\(.\+\)/\1/')
CONFIG_VERSION = $(shell grep 'define config.version' game/options.rpy | sed 's/.\+"\(.\+\)"/\1/')

SLIM_ZIP_NAME := "releases/spritesheet-animations-slim-$(LAST_TAG).zip"
FULL_ZIP_NAME := "releases/spritesheet-animations-project-$(LAST_TAG).zip"

.PHONY: default
default:
	@echo "What are you doing here?"


.PHONY: release
release: clean
	@echo "LAST_TAG = $(LAST_TAG)"
	@echo "CONFIG_VERSION = $(CONFIG_VERSION)"
	@if [ "$(LAST_TAG)" != "$(CONFIG_VERSION)" ]; then echo "Version mismatch!"; exit 1; fi
	@mkdir -p "releases"
	@cp license spritesheet-animations-license
	@zip -r $(SLIM_ZIP_NAME) game/lib/fxcpds/spritesheet_animation spritesheet-animations-license
	@zip -r $(FULL_ZIP_NAME) game spritesheet-animations-license -x game/saves/**\* -x game/cache/**\*
	@rm -f spritesheet-animations-license


.PHONY: clean
clean:
	@echo "Cleaning directory."
	@find . -name '*.rpyc' -o -name '*.rpyb' -o -name '*.rpymc' | xargs -I'{}' rm '{}'
	@rm -rf releases