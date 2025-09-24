#!/bin/bash

# Function to decrypt data using the same algorithm as your Python code
decrypt_data() {
    local secret="$1"
    local salt="$2"
    local encrypted_data="$3"

    uv run python3 -c "from dev_observer.common.crypto import Encryptor; e=Encryptor('$secret'); print(e.decrypt('$encrypted_data', '$salt'))"
}

# Usage example:
# decrypt_data "your_secret" "your_salt" "encrypted_base64_data"