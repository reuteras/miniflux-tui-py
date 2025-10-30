#!/usr/bin/env bash
set -euo pipefail

if ! command -v uv >/dev/null 2>&1; then
    UV_VERSION="0.9.6"
    ARCH="$(uname -m)"
    case "${ARCH}" in
        x86_64)
            UV_ARCHIVE="uv-x86_64-unknown-linux-gnu"
            ;;
        aarch64)
            UV_ARCHIVE="uv-aarch64-unknown-linux-gnu"
            ;;
        *)
            echo "Unsupported architecture for uv installer: ${ARCH}" >&2
            exit 1
            ;;
    esac

    UV_BASE_URL="https://github.com/astral-sh/uv/releases/download/${UV_VERSION}"
    TMP_DIR="$(mktemp -d)"
    trap 'rm -rf "${TMP_DIR}"' EXIT

    ARCHIVE_PATH="${TMP_DIR}/${UV_ARCHIVE}.tar.gz"
    SHA_PATH="${ARCHIVE_PATH}.sha256"

    curl -LsSf "${UV_BASE_URL}/${UV_ARCHIVE}.tar.gz" -o "${ARCHIVE_PATH}"
    curl -LsSf "${UV_BASE_URL}/${UV_ARCHIVE}.tar.gz.sha256" -o "${SHA_PATH}"

    (cd "${TMP_DIR}" && sha256sum --check --status "${UV_ARCHIVE}.tar.gz.sha256")

    tar -xzf "${ARCHIVE_PATH}" -C "${TMP_DIR}"
    install -d "${HOME}/.local/bin"
    install -m 755 "${TMP_DIR}/${UV_ARCHIVE}/uv" "${HOME}/.local/bin/uv"
    install -m 755 "${TMP_DIR}/${UV_ARCHIVE}/uvx" "${HOME}/.local/bin/uvx"
    export PATH="$HOME/.local/bin:$PATH"
fi

uv sync --locked --all-groups
