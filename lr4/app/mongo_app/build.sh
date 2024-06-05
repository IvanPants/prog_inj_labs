#!/bin/bash

echo "Building image..."

docker build \
-f Dockerfile \
-t mongo_work:"0.2" \
.

echo "Built image: sof_stats:${version}"