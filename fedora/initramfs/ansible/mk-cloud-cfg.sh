#!/bin/bash


cat <<EOF
#cloud-config
ssh_keys:
    ssh_deletekeys: true
    ssh_genkeytypes: ['ed25519']
    ed25519_private: |
$(sed 's/^/        /' work/early_ssh_host_ed25519_key)
    ed25519_public: $(cat work/early_ssh_host_ed25519_key.pub)
EOF
