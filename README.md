# Flaxon Account Manager

A **Linux desktop GUI tool** for managing offline profile names inside
Lunar Client's local `accounts.json` file.  
Built with Python 3 and CustomTkinter, styled after Lunar Client's dark UI.

> **Educational / hobbyist project.**  
> This tool only edits a local JSON file on your own machine. It does **not**
> authenticate with Microsoft, Mojang, or any online service. Accounts created
> this way are **offline-only** and **cannot be used on online-mode servers**
> (which require a valid paid Minecraft account).

---

## What It Does

Lunar Client stores your account information in a local file:

```
~/.var/app/com.lunarclient.LunarClient/.lunarclient/settings/game/accounts.json
# or, for native installs:
~/.lunarclient/settings/game/accounts.json
```

Flaxon Account Manager gives you a polished GUI to:

- **Add** an offline profile with a custom username
- **Edit** the username of any existing profile
- **Remove** profiles you no longer want
- See which profile is currently **active** in Lunar Client

No internet connection is required. No credentials are sent anywhere.

---

## Requirements

| Requirement | Notes |
|---|---|
| Linux (x86_64) | Ubuntu 20.04+ / Debian 11+ / Fedora 36+ tested |
| Lunar Client | Installed via Flatpak (`com.lunarclient.LunarClient`) or natively |
| Python 3.10+ | Only needed if running from source |

---

## Installation

### Option A – Pre-built binary (recommended)

1. Go to the [**Releases**](../../releases/latest) page.
2. Download `flaxon-account-linux.zip`.
3. Extract and run:

```bash
unzip flaxon-account-linux.zip
chmod +x flaxon-account
./flaxon-account
```

### Option B – Run from source

```bash
git clone https://github.com/YOUR_USERNAME/flaxon-account.git
cd flaxon-account
pip install -r requirements.txt
python src/main.py
```

### Option C – Build yourself

```bash
bash build.sh
# Binary will be at dist/flaxon-account
```

---

## Usage

1. **Open Lunar Client at least once** so it creates its settings folder.
2. **Close Lunar Client completely** before making changes.
3. Launch Flaxon Account Manager.
4. Type a username (3–16 characters, letters/numbers/underscores only).
5. Press **Add**.
6. Open Lunar Client – your profile will appear in the account list.

### Editing a username

Click the **✏** (pencil) button on any account card to rename it.

### Removing an account

Click the **✕** button on any account card to delete it.

---

## Known Limitations

| Issue | Explanation |
|---|---|
| "Invalid session" notification | Lunar Client periodically checks your session token. This is a warning only – you can still use the client offline. Disabling Lunar Client notifications removes the popup. |
| Cannot join online-mode servers | By design. Online servers verify your account with Mojang/Microsoft. This tool does not bypass that check. |
| Skin may not load | Skins are served by Mojang's API based on your UUID. Offline UUIDs won't match any skin. |
| Flatpak path only | If you use a non-Flatpak Lunar Client install, the tool automatically falls back to `~/.lunarclient/settings/game`. |

---

## Legal & Ethical Notes

- This project is **not affiliated with** Mojang Studios, Microsoft, or
  Moonsworth LLC (Lunar Client).
- It does not distribute, modify, or reverse-engineer any proprietary software.
- It only reads and writes a JSON configuration file that you own on your own
  machine, in the same way any text editor would.
- Minecraft's [EULA](https://www.minecraft.net/en-us/eula) and
  [Usage Guidelines](https://www.minecraft.net/en-us/usage-guidelines) apply
  to your use of the game. This tool does not help circumvent paid access to
  online servers.
- Licensed under the **MIT License** – see [`LICENSE`](LICENSE).

---

## Project Structure

```
flaxon-account/
├── src/
│   └── main.py          # Main application (CustomTkinter GUI)
├── requirements.txt     # Python dependencies
├── build.sh             # Local build script (PyInstaller)
├── build-linux.yml      # GitHub Actions CI/CD workflow
└── README.md
```

---

## License

MIT © Flaxon — free to use, modify, and redistribute with attribution.
