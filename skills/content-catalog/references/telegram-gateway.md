# Telegram Gateway for Catalog Bot

Your capture bot (`@<your_bot_username>`) receives links from your phone and
Hermes auto-processes them into the content catalog.

## Setup

1. **Bot creation**: Via @BotFather on Telegram, `/newbot` → name: `<YourBotName>`,
   username: `<your_bot_username>`
2. **Token**: `<BOT_ID>:<SECRET>` (from @BotFather) → set in `~/.hermes/.env` as `TELEGRAM_BOT_TOKEN`
3. **Gateway**: Started via `hermes gateway run` (background process)
4. **User approval**: Your first message to the bot generates a pairing code
   (`<PAIRING_CODE>`) → approve it via `hermes pairing approve telegram <code>`
5. **Allowed users**: Set `TELEGRAM_ALLOWED_USERS=<your_telegram_user_id>` in `.env`
6. **Channel prompt**: Configured in config.yaml via:
   ```
   hermes config set telegram.channel_prompts '{"<your_telegram_user_id>": "..."}'
   ```

## Channel prompt content

The prompt instructs the gateway agent to:
- Detect source type (YouTube, Instagram, etc.)
- Fetch transcript/description
- For Instagram: download + transcribe audio
- Save to catalog using `$CATALOG_ROOT/scripts/transcript.py`
- Reply with NC-XXXX ID

## Gateway lifecycle commands

```bash
hermes gateway status          # Is it running?
hermes gateway run             # Start (foreground)
hermes gateway restart         # Restart (after config/.env changes)
hermes gateway install         # Install as user service (for persistence)
hermes gateway stop            # Stop
```

## Checking bot activity

```bash
# Check gateway logs for Telegram messages
grep -i "telegram\|text\|link\|instagram\|youtube" ~/.hermes/logs/gateway.log | tail -10

# Check API for pending updates
curl -s "https://api.telegram.org/bot$(grep '^TELEGRAM_BOT_TOKEN' ~/.hermes/.env | cut -d= -f2)/getUpdates"
```

## Pitfalls

- **Gateway must be restarted** after .env or config.yaml changes
  (`hermes gateway restart`)
- **First user message generates a pairing code** - must be approved via
  `hermes pairing approve telegram <code>` before the bot responds
- **Gateway sessions don't load skills automatically** - the channel prompt
  must tell the agent to use the catalog script directly (it works because
  the prompt references absolute paths)
- **Gateway dies on terminal close** - the background process is tied to the
  shell session. For persistent operation, install as a service:
  `hermes gateway install` (user) or `sudo hermes gateway install --system`
- **The channel prompt is a system prompt, not a skill load** - the gateway
  agent won't have the `content-catalog` skill loaded unless pre-configured
