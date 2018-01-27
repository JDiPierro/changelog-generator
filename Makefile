build:
	docker build . -t jdipierro/yamlclog

changelog:
	@docker run \
		--rm \
		--mount src="$$(pwd)",target=/project,type=bind \
		jdipierro/yamlclog:latest \
		$$(VERSION)

test:
	nosetests