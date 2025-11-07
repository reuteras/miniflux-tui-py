# GitHub Codespaces Setup

This guide explains how to use miniflux-tui-py in GitHub Codespaces with secure credential management and optional Tailscale support for private networks.

## Quick Start

### 1. Create Codespace Configuration

Run this command in your codespace terminal:

```bash
miniflux-tui --init-codespace
```

This creates a configuration file optimized for Codespaces that reads credentials from environment variables.

### 2. Set Up GitHub Secrets

Add your Miniflux credentials as Codespace secrets:

**Repository Secrets** (recommended for project-specific setup):
1. Go to your repository on GitHub
2. Navigate to **Settings** → **Secrets and variables** → **Codespaces**
3. Click **New repository secret**
4. Add these secrets:
   - `MINIFLUX_SERVER_URL`: Your Miniflux server URL (e.g., `https://miniflux.example.com`)
   - `MINIFLUX_API_KEY`: Your Miniflux API token

**User Secrets** (for personal use across all your codespaces):
1. Go to [GitHub Settings](https://github.com/settings/codespaces)
2. Scroll to **Codespaces secrets**
3. Add the same secrets as above

### 3. Start the Application

```bash
miniflux-tui
```

The application will automatically read your credentials from the environment variables set by GitHub Codespaces secrets.

## Configuration Details

The Codespaces configuration (`~/.config/miniflux-tui/config.toml`) is designed to work with environment variables:

```toml
# Server URL - automatically read from MINIFLUX_SERVER_URL environment variable
server_url = "https://PLACEHOLDER_SET_MINIFLUX_SERVER_URL_SECRET"

# Password command - reads MINIFLUX_API_KEY from environment
password = ["sh", "-c", "echo $MINIFLUX_API_KEY"]

# Start in grouped mode by default
[sorting]
default_group_by_feed = true
```

### How It Works

1. **Server URL**: The application checks for the `MINIFLUX_SERVER_URL` environment variable at runtime and uses it if present
2. **API Key**: The password command executes `echo $MINIFLUX_API_KEY`, which retrieves the token from the environment
3. **Grouped Mode**: Entries are grouped by feed by default, providing better organization in the codespace environment

## Using Tailscale for Private Server Access

If your Miniflux server is on a private network (not publicly accessible), you can use Tailscale to securely connect your codespace to your private network.

### Prerequisites

- A Tailscale account ([sign up free](https://login.tailscale.com/start))
- Your Miniflux server connected to your Tailscale network
- A Tailscale auth key

### Setup Steps

#### 1. Generate Tailscale Auth Key

1. Go to [Tailscale Admin Console → Settings → Keys](https://login.tailscale.com/admin/settings/keys)
2. Click **Generate auth key**
3. Configure the key:
   - **Reusable**: Enable (allows multiple codespace instances)
   - **Ephemeral**: Enable (automatically removes device when disconnected)
   - **Tags**: Optional (e.g., `tag:codespace`)
4. Copy the generated key (starts with `tskey-auth-...`)

#### 2. Add Auth Key as Codespace Secret

1. Go to your repository **Settings** → **Secrets and variables** → **Codespaces**
2. Add a new secret:
   - Name: `TAILSCALE_AUTHKEY`
   - Value: Your auth key from step 1

#### 3. Install and Connect Tailscale in Codespace

Run these commands in your codespace terminal:

```bash
# Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# Connect to your Tailscale network
sudo tailscale up --authkey=$TAILSCALE_AUTHKEY
```

#### 4. Verify Connection

Check your Tailscale status:

```bash
tailscale status
```

You should see your codespace listed and your other Tailscale devices.

#### 5. Update Server URL

Use your Miniflux server's Tailscale hostname in the `MINIFLUX_SERVER_URL` secret:

- Format: `http://[machine-name]` or `http://[tailscale-ip]:8080`
- Example: `http://miniflux-server` or `http://100.64.0.1:8080`

You can find your server's Tailscale name/IP in the [Tailscale Admin Console → Machines](https://login.tailscale.com/admin/machines).

#### 6. Allow Self-Signed Certificates (Optional)

If your Miniflux server uses a self-signed certificate over Tailscale:

```bash
# Edit the config file
nano ~/.config/miniflux-tui/config.toml

# Change this line:
allow_invalid_certs = true
```

### Automating Tailscale Setup

To avoid running Tailscale commands manually each time, you can add a setup script:

**Create `.devcontainer/devcontainer.json`:**

```json
{
  "name": "Miniflux TUI Development",
  "image": "mcr.microsoft.com/devcontainers/python:3.11",
  "postCreateCommand": "pip install miniflux-tui-py && miniflux-tui --init-codespace",
  "postStartCommand": ".devcontainer/setup-tailscale.sh"
}
```

**Create `.devcontainer/setup-tailscale.sh`:**

```bash
#!/bin/bash
# Install Tailscale if TAILSCALE_AUTHKEY is set
if [ -n "$TAILSCALE_AUTHKEY" ]; then
    echo "Setting up Tailscale..."
    curl -fsSL https://tailscale.com/install.sh | sh
    sudo tailscale up --authkey=$TAILSCALE_AUTHKEY --hostname=codespace-miniflux-tui
    echo "Tailscale connected!"
    tailscale status
fi
```

Make it executable:

```bash
chmod +x .devcontainer/setup-tailscale.sh
```

Now Tailscale will automatically connect when your codespace starts!

## Troubleshooting

### "Configuration contains placeholder for server_url"

**Problem**: The application can't find the `MINIFLUX_SERVER_URL` environment variable.

**Solution**:
1. Verify the secret is set in GitHub Settings → Codespaces
2. Restart your codespace (secrets are only loaded at codespace creation)
3. Or manually set it in the terminal: `export MINIFLUX_SERVER_URL="https://your-server.com"`

### "Password command returned empty output"

**Problem**: The `MINIFLUX_API_KEY` environment variable is not set or empty.

**Solution**:
1. Check the secret is set in GitHub Settings
2. Restart your codespace
3. Or manually set it: `export MINIFLUX_API_KEY="your-token-here"`

### Tailscale Connection Fails

**Problem**: `sudo tailscale up` fails with authentication error.

**Solution**:
1. Verify `TAILSCALE_AUTHKEY` secret is set correctly
2. Check that the auth key hasn't expired
3. Generate a new auth key and update the secret
4. Ensure the key is marked as **Reusable**

### Can't Access Miniflux Server via Tailscale

**Problem**: Connection times out or refused.

**Solution**:
1. Verify your Miniflux server is running and connected to Tailscale
2. Check the Tailscale IP/hostname is correct: `tailscale status`
3. Test connectivity: `curl http://[tailscale-ip]:8080/healthcheck`
4. Ensure firewall allows connections from Tailscale network

## Security Notes

- **Secrets are encrypted** at rest in GitHub and only exposed as environment variables in your codespace
- **Tailscale auth keys** should be ephemeral and reusable for codespace use
- **Never commit** secrets, API tokens, or auth keys to your repository
- **Use repository secrets** for project-specific credentials
- **Use user secrets** for personal credentials shared across all your codespaces

## Additional Resources

- [GitHub Codespaces Secrets Documentation](https://docs.github.com/en/codespaces/managing-codespaces-for-your-organization/managing-encrypted-secrets-for-your-repository-and-organization-for-github-codespaces)
- [Tailscale with GitHub Codespaces Guide](https://tailscale.com/kb/1160/github-codespaces)
- [Miniflux API Documentation](https://miniflux.app/docs/api.html)
- [miniflux-tui-py Configuration Guide](configuration.md)
