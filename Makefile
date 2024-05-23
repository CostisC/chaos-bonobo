SHELL		:= /bin/bash
VENV 		:= .venv
DOCSOURCE 	:= Documentation
SERVERDIR 	:= server
DOCGENERTD	:= $(SERVERDIR)/docs
AGENTDIR	:= agent

include Version

.PHONY: build_docs build_server all clean


all: 	build_docs build_server build_agent


build_docs:	|$(VENV)
ifdef publish
	$(eval action := gh-deploy)
else
	$(eval action := build)
endif
	# set the Version in the About page
	sed "s/<version>/$(VERSION).$(RELEASE)/" \
		< $(DOCSOURCE)/docs/about.md_template > $(DOCSOURCE)/docs/about.md

	@source $(VENV)/bin/activate && cd $(DOCSOURCE) && mkdocs $(action)
	@rm -rf $(DOCGENERTD) && mv $(DOCSOURCE)/site $(DOCGENERTD) && \
		echo "Documentation generated in $(DOCGENERTD)/"
	@rm -rf $(DOCSOURCE)/docs/about.md

publish_docs:
	@$(MAKE) build_docs publish=ok

$(VENV):
	echo "*** Create the mkdocs enviroment"
	python -m venv $@
	source $@/bin/activate && pip install mkdocs

$(SERVERDIR)/node_modules:
	echo "*** Download the Node.js dependencies of the Server"
	cd $(SERVERDIR) && npm install



build_server: 	|$(SERVERDIR)/node_modules
	mkdir -p packages/BUILD
	cp -r server/* packages/BUILD
	rpmbuild -D="_topdir $${PWD}/packages" \
			 -D='_version $(VERSION)' \
			 -D='_release $(RELEASE)' \
			 -bb chaos-bonobo-server.spec
	find packages/RPMS -name '*.rpm' | xargs -i mv '{}' .
	rm -rf packages

build_agent:
	mkdir -p packages/BUILD
	cp -r $(AGENTDIR)/* packages/BUILD
	rpmbuild -D="_topdir $${PWD}/packages" \
			 -D='_version $(VERSION)' \
			 -D='_release $(RELEASE)' \
			 -bb chaos-bonobo-agent.spec
	find packages/RPMS -name '*.rpm' | xargs -i mv '{}' .
	rm -rf packages

clean:
	rm -rf *.rpm
	rm -rf $(DOCGENERTD)
