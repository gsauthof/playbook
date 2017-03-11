

.PHONY: all


all: ks.cfg


MSCONF = config.yaml


%: %.mustache $(MSCONF)
	mustache $(MSCONF) $< > $@
	ksvalidator $@
