LIB_NAME=sst
VERSION?=local
REPORTS=${PWD}/.reports
IMAGE=${LIB_NAME}:${VERSION}

.PHONY: build test test_clean release version

build:
	echo "${VERSION}" > VERSION.txt
	docker build -t ${IMAGE} .

test: test_clean
	docker run --rm -v "${REPORTS}":/app/.reports ${IMAGE}

test_clean:
	mkdir -p ${REPORTS}
	rm -f ${REPORTS}/*

release:
	python setup.py sdist bdist_wheel
	twine upload -r azazo --skip-existing dist/*

version:
	echo "0.3.${BUILD_IDENTIFIER}"
