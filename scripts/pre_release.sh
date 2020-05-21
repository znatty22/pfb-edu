#/bin/bash

set -eo pipefail

VERSION=$1

echo "Updating version to $VERSION in Python package"
echo "__version__ = '$VERSION'" > pfb_exporter/__init__.py
