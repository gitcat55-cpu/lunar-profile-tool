#!/usr/bin/env python3
import customtkinter as ctk
import json
import os
import uuid
import threading
import time
from pathlib import Path

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

APP_NAME = "Flaxon Account Manager"
APP_VERSION = "1.0.0"

LUNAR_PATHS = [
    Path.home() / ".var" / "app" / "com.lunarclient.LunarClient" / ".lunarclient" / "settings" / "game",
    Path.home() / ".lunarclient" / "settings" / "game",
]

BG_DARK     = "#0d0d0f"
BG_CARD     = "#141418"
BG_INPUT    = "#1a1a20"
ACCENT      = "#4f8ef7"
ACCENT_DARK = "#3a6fd4"
TEXT_WHITE  = "#e8eaf0"
TEXT_GRAY   = "#6b7280"
TEXT_MUTED  = "#4b5263"
SUCCESS     = "#22c55e"
ERROR_RED   = "#ef4444"
BORDER      = "#252530"


def get_lunar_path() -> Path | None:
    for p in LUNAR_PATHS:
        if p.exists():
            return p
    return LUNAR_PATHS[0]


def load_accounts() -> dict:
    path = get_lunar_path() / "accounts.json"
    if path.exists():
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"activeAccountLocalId": "", "accounts": {}}


def save_accounts(data: dict):
    path = get_lunar_path()
    path.mkdir(parents=True, exist_ok=True)
    with open(path / "accounts.json", "w") as f:
        json.dump(data, f, indent=2)


def build_account_entry(username: str, uid: str) -> dict:
    return {
        "accessToken": uid,
        "accessTokenExpiresAt": "2050-07-02T10:56:30.717167800Z",
        "eligibleForMigration": False,
        "hasMultipleProfiles": False,
        "legacy": True,
        "persistent": True,
        "userProperites": [],
        "localId": uid,
        "minecraftProfile": {"id": uid, "name": username},
        "remoteId": uid,
        "type": "Xbox",
        "username": username,
    }


class ToastNotification(ctk.CTkToplevel):
    def __init__(self, master, message: str, success: bool = True):
        super().__init__(master)
        self.overrideredirect(True)
        self.attributes("-topmost", True)

        color = SUCCESS if success else ERROR_RED
        self.configure(fg_color=BG_CARD)

        frame = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=10,
                             border_width=1, border_color=color)
        frame.pack(fill="both", expand=True, padx=2, pady=2)

        dot = ctk.CTkLabel(frame, text="●", font=("Segoe UI", 10),
                           text_color=color)
        dot.pack(side="left", padx=(12, 4), pady=12)

        lbl = ctk.CTkLabel(frame, text=message, font=("Segoe UI", 12),
                           text_color=TEXT_WHITE)
        lbl.pack(side="left", padx=(0, 16), pady=12)

        self.update_idletasks()
        w, h = 320, 48
        mx = master.winfo_rootx() + master.winfo_width() // 2 - w // 2
        my = master.winfo_rooty() + master.winfo_height() - h - 24
        self.geometry(f"{w}x{h}+{mx}+{my}")

        threading.Thread(target=self._auto_close, daemon=True).start()

    def _auto_close(self):
        time.sleep(2.5)
        try:
            self.destroy()
        except Exception:
            pass


class AccountCard(ctk.CTkFrame):
    def __init__(self, master, uid: str, username: str,
                 is_active: bool, on_edit, on_delete, **kwargs):
        super().__init__(master, fg_color=BG_INPUT, corner_radius=8,
                         border_width=1,
                         border_color=ACCENT if is_active else BORDER,
                         **kwargs)
        self.uid = uid
        self.username = username

        left = ctk.CTkFrame(self, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True, padx=14, pady=12)

        avatar = ctk.CTkLabel(left, text=username[0].upper(),
                              width=36, height=36,
                              fg_color=ACCENT, corner_radius=6,
                              font=("Segoe UI", 14, "bold"),
                              text_color="white")
        avatar.pack(side="left", padx=(0, 10))

        info = ctk.CTkFrame(left, fg_color="transparent")
        info.pack(side="left", fill="y")

        name_row = ctk.CTkFrame(info, fg_color="transparent")
        name_row.pack(anchor="w")

        ctk.CTkLabel(name_row, text=username,
                     font=("Segoe UI", 13, "bold"),
                     text_color=TEXT_WHITE).pack(side="left")

        if is_active:
            ctk.CTkLabel(name_row, text=" ACTIVE",
                         font=("Segoe UI", 9, "bold"),
                         text_color=ACCENT).pack(side="left", padx=(6, 0))

        ctk.CTkLabel(info, text=f"UUID: {uid[:18]}…",
                     font=("Segoe UI", 10),
                     text_color=TEXT_MUTED).pack(anchor="w")

        right = ctk.CTkFrame(self, fg_color="transparent")
        right.pack(side="right", padx=10)

        ctk.CTkButton(right, text="✏", width=32, height=32,
                      font=("Segoe UI", 14),
                      fg_color=BG_CARD, hover_color=BORDER,
                      text_color=TEXT_GRAY, corner_radius=6,
                      command=lambda: on_edit(uid, username)).pack(side="left", padx=4)

        ctk.CTkButton(right, text="✕", width=32, height=32,
                      font=("Segoe UI", 14),
                      fg_color=BG_CARD, hover_color="#3a1a1a",
                      text_color=ERROR_RED, corner_radius=6,
                      command=lambda: on_delete(uid)).pack(side="left")


class EditDialog(ctk.CTkToplevel):
    def __init__(self, master, uid: str, current_name: str, on_save):
        super().__init__(master)
        self.title("Edit Username")
        self.geometry("380x200")
        self.resizable(False, False)
        self.configure(fg_color=BG_CARD)
        self.attributes("-topmost", True)
        self.grab_set()

        self.columnconfigure(0, weight=1)

        ctk.CTkLabel(self, text="Edit Username",
                     font=("Segoe UI", 15, "bold"),
                     text_color=TEXT_WHITE).grid(row=0, column=0, pady=(24, 4), padx=28, sticky="w")

        ctk.CTkLabel(self, text=f"UUID: {uid[:24]}…",
                     font=("Segoe UI", 10),
                     text_color=TEXT_MUTED).grid(row=1, column=0, padx=28, sticky="w")

        self.entry = ctk.CTkEntry(self, placeholder_text="New username",
                                  fg_color=BG_INPUT, border_color=BORDER,
                                  text_color=TEXT_WHITE, height=40,
                                  font=("Segoe UI", 13))
        self.entry.grid(row=2, column=0, padx=28, pady=12, sticky="ew")
        self.entry.insert(0, current_name)
        self.entry.select_range(0, "end")
        self.entry.focus()

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=3, column=0, padx=28, pady=(0, 20), sticky="e")

        ctk.CTkButton(btn_frame, text="Cancel", width=90, height=36,
                      fg_color=BG_INPUT, hover_color=BORDER,
                      text_color=TEXT_GRAY, corner_radius=8,
                      command=self.destroy).pack(side="left", padx=(0, 8))

        ctk.CTkButton(btn_frame, text="Save", width=90, height=36,
                      fg_color=ACCENT, hover_color=ACCENT_DARK,
                      text_color="white", corner_radius=8,
                      command=lambda: self._save(uid, on_save)).pack(side="left")

        self.entry.bind("<Return>", lambda _: self._save(uid, on_save))

    def _save(self, uid, callback):
        name = self.entry.get().strip()
        if 3 <= len(name) <= 16 and name.isalnum() or "_" in name:
            callback(uid, name)
            self.destroy()


class FlaxonApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("520x620")
        self.minsize(480, 560)
        self.configure(fg_color=BG_DARK)
        self.resizable(True, True)

        self._build_ui()
        self._refresh_accounts()

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        self._build_header()
        self._build_add_section()
        self._build_accounts_section()
        self._build_footer()

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color=BG_CARD,
                              corner_radius=0, height=64)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(1, weight=1)
        header.grid_propagate(False)

        logo_frame = ctk.CTkFrame(header, fg_color=ACCENT,
                                  corner_radius=6, width=36, height=36)
        logo_frame.grid(row=0, column=0, padx=18, pady=14)
        logo_frame.grid_propagate(False)
        ctk.CTkLabel(logo_frame, text="F", font=("Segoe UI", 16, "bold"),
                     text_color="white").place(relx=0.5, rely=0.5, anchor="center")

        title_col = ctk.CTkFrame(header, fg_color="transparent")
        title_col.grid(row=0, column=1, sticky="w")
        ctk.CTkLabel(title_col, text=APP_NAME,
                     font=("Segoe UI", 14, "bold"),
                     text_color=TEXT_WHITE).pack(anchor="w")
        ctk.CTkLabel(title_col, text="Lunar Client · Account Tool",
                     font=("Segoe UI", 10),
                     text_color=TEXT_MUTED).pack(anchor="w")

        ctk.CTkLabel(header, text=f"v{APP_VERSION}",
                     font=("Segoe UI", 10),
                     text_color=TEXT_MUTED).grid(row=0, column=2, padx=18)

    def _build_add_section(self):
        card = ctk.CTkFrame(self, fg_color=BG_CARD,
                            corner_radius=12, border_width=1,
                            border_color=BORDER)
        card.grid(row=1, column=0, padx=20, pady=(18, 0), sticky="ew")
        card.columnconfigure(0, weight=1)

        ctk.CTkLabel(card, text="Add Account",
                     font=("Segoe UI", 12, "bold"),
                     text_color=TEXT_WHITE).grid(row=0, column=0, columnspan=2,
                                                 padx=18, pady=(16, 4), sticky="w")
        ctk.CTkLabel(card, text="Enter a username (3–16 chars, letters/numbers/underscore)",
                     font=("Segoe UI", 10),
                     text_color=TEXT_MUTED).grid(row=1, column=0, columnspan=2,
                                                  padx=18, sticky="w")

        input_row = ctk.CTkFrame(card, fg_color="transparent")
        input_row.grid(row=2, column=0, columnspan=2,
                       padx=18, pady=(10, 16), sticky="ew")
        input_row.columnconfigure(0, weight=1)

        self.username_entry = ctk.CTkEntry(
            input_row,
            placeholder_text="Enter username…",
            fg_color=BG_INPUT,
            border_color=BORDER,
            text_color=TEXT_WHITE,
            placeholder_text_color=TEXT_MUTED,
            height=42,
            font=("Segoe UI", 13),
            corner_radius=8,
        )
        self.username_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.username_entry.bind("<Return>", lambda _: self._add_account())

        self.add_btn = ctk.CTkButton(
            input_row,
            text="Add",
            width=80,
            height=42,
            fg_color=ACCENT,
            hover_color=ACCENT_DARK,
            text_color="white",
            font=("Segoe UI", 13, "bold"),
            corner_radius=8,
            command=self._add_account,
        )
        self.add_btn.grid(row=0, column=1)

    def _build_accounts_section(self):
        section = ctk.CTkFrame(self, fg_color="transparent")
        section.grid(row=2, column=0, padx=20, pady=(18, 0), sticky="nsew")
        section.columnconfigure(0, weight=1)
        section.rowconfigure(1, weight=1)

        header_row = ctk.CTkFrame(section, fg_color="transparent")
        header_row.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header_row.columnconfigure(1, weight=1)

        ctk.CTkLabel(header_row, text="Accounts",
                     font=("Segoe UI", 12, "bold"),
                     text_color=TEXT_WHITE).grid(row=0, column=0, sticky="w")

        self.count_label = ctk.CTkLabel(header_row, text="0 accounts",
                                        font=("Segoe UI", 10),
                                        text_color=TEXT_MUTED)
        self.count_label.grid(row=0, column=2, sticky="e")

        self.scroll = ctk.CTkScrollableFrame(
            section,
            fg_color=BG_CARD,
            corner_radius=12,
            border_width=1,
            border_color=BORDER,
            scrollbar_button_color=BORDER,
            scrollbar_button_hover_color=ACCENT,
        )
        self.scroll.grid(row=1, column=0, sticky="nsew")
        self.scroll.columnconfigure(0, weight=1)

        self.empty_label = ctk.CTkLabel(
            self.scroll,
            text="No accounts yet.\nAdd one above to get started.",
            font=("Segoe UI", 12),
            text_color=TEXT_MUTED,
            justify="center",
        )

    def _build_footer(self):
        footer = ctk.CTkFrame(self, fg_color="transparent", height=40)
        footer.grid(row=3, column=0, sticky="ew", padx=20, pady=10)
        footer.columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(
            footer,
            text="",
            font=("Segoe UI", 10),
            text_color=TEXT_MUTED,
        )
        self.status_label.grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(footer,
                     text="For educational purposes only · Not affiliated with Mojang or Lunar Client",
                     font=("Segoe UI", 9),
                     text_color=TEXT_MUTED).grid(row=0, column=1, sticky="e")

    def _refresh_accounts(self):
        for widget in self.scroll.winfo_children():
            widget.destroy()

        data = load_accounts()
        accounts = data.get("accounts", {})
        active = data.get("activeAccountLocalId", "")

        if not accounts:
            self.empty_label = ctk.CTkLabel(
                self.scroll,
                text="No accounts yet.\nAdd one above to get started.",
                font=("Segoe UI", 12),
                text_color=TEXT_MUTED,
                justify="center",
            )
            self.empty_label.pack(pady=40)
        else:
            for i, (uid, info) in enumerate(accounts.items()):
                name = info.get("minecraftProfile", {}).get("name", uid)
                card = AccountCard(
                    self.scroll,
                    uid=uid,
                    username=name,
                    is_active=(uid == active),
                    on_edit=self._edit_account,
                    on_delete=self._delete_account,
                )
                card.grid(row=i, column=0, sticky="ew", pady=(0, 6), padx=6)

        n = len(accounts)
        self.count_label.configure(text=f"{n} account{'s' if n != 1 else ''}")
        path = get_lunar_path() / "accounts.json"
        self.status_label.configure(text=str(path))

    def _validate_username(self, name: str) -> str | None:
        name = name.strip()
        if len(name) < 3:
            return "Username must be at least 3 characters."
        if len(name) > 16:
            return "Username must be 16 characters or fewer."
        allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_")
        if not all(c in allowed for c in name):
            return "Only letters, numbers, and underscores allowed."
        return None

    def _add_account(self):
        username = self.username_entry.get().strip()
        err = self._validate_username(username)
        if err:
            ToastNotification(self, err, success=False)
            self.username_entry.configure(border_color=ERROR_RED)
            self.after(1500, lambda: self.username_entry.configure(border_color=BORDER))
            return

        data = load_accounts()
        existing_names = [
            v.get("minecraftProfile", {}).get("name", "").lower()
            for v in data["accounts"].values()
        ]
        if username.lower() in existing_names:
            ToastNotification(self, f'"{username}" already exists.', success=False)
            return

        uid = str(uuid.uuid4()).replace("-", "")
        data["accounts"][uid] = build_account_entry(username, uid)
        if not data["activeAccountLocalId"]:
            data["activeAccountLocalId"] = uid
        save_accounts(data)

        self.username_entry.delete(0, "end")
        self._refresh_accounts()
        ToastNotification(self, f'Account "{username}" added!')

    def _edit_account(self, uid: str, current_name: str):
        def on_save(u, new_name):
            data = load_accounts()
            if u in data["accounts"]:
                data["accounts"][u]["username"] = new_name
                data["accounts"][u]["minecraftProfile"]["name"] = new_name
            save_accounts(data)
            self._refresh_accounts()
            ToastNotification(self, f'Renamed to "{new_name}"')

        EditDialog(self, uid, current_name, on_save)

    def _delete_account(self, uid: str):
        data = load_accounts()
        name = data["accounts"].get(uid, {}).get("minecraftProfile", {}).get("name", uid)
        if uid in data["accounts"]:
            del data["accounts"][uid]
        if data["activeAccountLocalId"] == uid:
            remaining = list(data["accounts"].keys())
            data["activeAccountLocalId"] = remaining[0] if remaining else ""
        save_accounts(data)
        self._refresh_accounts()
        ToastNotification(self, f'Removed "{name}"', success=False)


if __name__ == "__main__":
    app = FlaxonApp()
    app.mainloop()
