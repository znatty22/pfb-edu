#/bin/bash

set -eo pipefail

VERSION=$1

echo "New version: $VERSION"

mkdir assets
echo "my_asset" > assets/my_asset.txt
tar zcvf assets.tar.gz assets
echo "assets.tar.gz" > release_assets.txt

