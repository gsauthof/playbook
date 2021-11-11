#!/bin/bash

cd /var/lib/radicale/collections
git add -A && (git diff --cached --quiet || git commit -m "Changes by $1")

exit 0
