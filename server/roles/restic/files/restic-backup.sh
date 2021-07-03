#!/bin/bash

# Backup system with restic (e.g. to Backblaze b2 object storage)
# according to a backup schedule and prune some incrementals
# each week.
#
# Required environment variables:
#
# - RESTIC_REPOSITORY=b2:somebucket:prefix
# - RESTIC_PASSWORD=
#
# If using Backblaze b2:
#
# - B2_ACCOUNT_ID=backblaze_api_key_id
# - B2_ACCOUNT_KEY=the_actual_api_key
#
#
# 2019, Georg Sauthoff <mail@gms.tf>

set -eux

/usr/local/bin/restic-cap_dac_read_search backup /etc /home /opt /root /srv /var \
        --exclude=/home/restic/.cache --exclude=/var/tmp

if [ $(date +%u) -eq 1 ] ; then
    restic forget --prune --keep-daily 7 --keep-weekly 4 --keep-monthly 6 --keep-yearly 2 --host $HOSTNAME
fi
