# -*- coding: utf-8 -*-
"""

Python 3 + tkinter. Внешние библиотеки не требуются.
"""

from __future__ import annotations

import json
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk


# -------------------- НАСТРОЙКИ --------------------

APP_TITLE = "FairyGuard — система доступа"
AUTHOR = "Жбанова София Романовна"
GROUP = "ИДБ-23-11"

MAXNAME = 20
MAXPASS = 10
ARITHMETIC_SIGNS = "+-*/%"


DATA_FILE = Path(__file__).resolve().with_name("accounts.json")

# Если рядом остался файл от предыдущей версии программы,
# программа один раз перенесет данные из него в accounts.json.
OLD_DATA_FILE = Path(__file__).resolve().with_name("security.db")


# -------------------- FAIRY / PINK ПАЛИТРА --------------------

PINK_BG = "#fff2f8"
PINK_PANEL = "#ffe3f0"
PINK_ACCENT = "#e84f8a"
PINK_ACCENT_DARK = "#c73c70"
PINK_TEXT = "#5b2942"
PINK_LIGHT = "#fff9fc"
PINK_BORDER = "#f1a8c5"

LILAC = "#eadcff"
LILAC_DARK = "#7a4d9b"
FAIRY_GLOW = "#fff4c7"
MINT = "#dcf7ee"


# -------------------- ДАННЫЕ ПОЛЬЗОВАТЕЛЕЙ --------------------

def default_admin() -> dict:
    """ADMIN, который автоматически создается при первом запуске."""
    return {
        "username": "ADMIN",
        "password": "",
        "blocked": False,
        "restricted": True,
    }


def save_accounts(accounts: list[dict]) -> None:
    """Сохраняет учетные записи и пароли в accounts.json."""
    temp_file = DATA_FILE.with_suffix(".tmp")
    with temp_file.open("w", encoding="utf-8") as file:
        json.dump(accounts, file, ensure_ascii=False, indent=2)
    temp_file.replace(DATA_FILE)


def _validate_accounts(data) -> list[dict]:
    if not isinstance(data, list):
        raise ValueError("Файл accounts.json должен содержать список учетных записей.")

    required = {"username", "password", "blocked", "restricted"}
    for account in data:
        if not isinstance(account, dict) or not required.issubset(account):
            raise ValueError("В accounts.json обнаружена некорректная учетная запись.")
    return data


def load_accounts() -> list[dict]:
    """
    Загружает данные из accounts.json.
    При первом запуске автоматически создает ADMIN с пустым паролем.

    Для удобства перехода с предыдущей версии поддерживается перенос
    JSON-данных из security.db в accounts.json.
    """
    if DATA_FILE.exists():
        with DATA_FILE.open("r", encoding="utf-8") as file:
            return _validate_accounts(json.load(file))

    if OLD_DATA_FILE.exists():
        try:
            with OLD_DATA_FILE.open("r", encoding="utf-8") as file:
                accounts = _validate_accounts(json.load(file))
            save_accounts(accounts)
            return accounts
        except (OSError, json.JSONDecodeError, ValueError):
            # Если старый файл не является JSON, просто начинаем с чистой базы.
            pass

    accounts = [default_admin()]
    save_accounts(accounts)
    return accounts


def find_account(accounts: list[dict], username: str) -> dict | None:
    for account in accounts:
        if account["username"] == username:
            return account
    return None


def check_variant_7(password: str) -> bool:
    """Требование варианта №7: цифра + знак арифметической операции."""
    has_digit = any(char.isdigit() for char in password)
    has_arithmetic_sign = any(char in ARITHMETIC_SIGNS for char in password)
    return has_digit and has_arithmetic_sign


# -------------------- ОБЩИЕ ЭЛЕМЕНТЫ ДИЗАЙНА --------------------

def fairy_title(parent, text: str, bg: str = PINK_PANEL, size: int = 18):
    """Заголовок с легким fairy-декором без внешних картинок."""
    wrapper = tk.Frame(parent, bg=bg)
    wrapper.pack(fill="x")

    tk.Label(
        wrapper,
        text="♡  ✦  ✧",
        bg=bg,
        fg=LILAC_DARK,
        font=("Segoe UI Symbol", max(11, size - 4)),
    ).pack(side="left", padx=(10, 4))

    tk.Label(
        wrapper,
        text=text,
        bg=bg,
        fg=PINK_TEXT,
        font=("Segoe UI", size, "bold"),
    ).pack(side="left", expand=True)

    tk.Label(
        wrapper,
        text="✧  ✦  ♡",
        bg=bg,
        fg=LILAC_DARK,
        font=("Segoe UI Symbol", max(11, size - 4)),
    ).pack(side="right", padx=(4, 10))

    return wrapper


def fairy_button(parent, text: str, command, *, width: int = 15):
    return tk.Button(
        parent,
        text=f"♡  {text}",
        width=width,
        command=command,
        bg=PINK_ACCENT,
        fg="white",
        activebackground=PINK_ACCENT_DARK,
        activeforeground="white",
        relief="flat",
        cursor="hand2",
        font=("Segoe UI", 10, "bold"),
        padx=6,
        pady=6,
    )


def light_button(parent, text: str, command, *, width: int = 13):
    return tk.Button(
        parent,
        text=text,
        width=width,
        command=command,
        bg=PINK_LIGHT,
        fg=PINK_TEXT,
        activebackground=LILAC,
        activeforeground=PINK_TEXT,
        relief="solid",
        bd=1,
        cursor="hand2",
        font=("Segoe UI", 10),
        padx=4,
        pady=5,
    )


# -------------------- БАЗОВОЕ МОДАЛЬНОЕ ОКНО --------------------

class PinkDialog(tk.Toplevel):
    def __init__(self, parent: tk.Misc, title: str, width: int, height: int):
        super().__init__(parent)
        self.result = None
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        self.configure(bg=PINK_BG)
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.cancel)

    def center(self) -> None:
        self.update_idletasks()
        parent = self.master
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        width = self.winfo_width()
        height = self.winfo_height()

        x = max(0, px + (pw - width) // 2)
        y = max(0, py + (ph - height) // 2)
        self.geometry(f"+{x}+{y}")

    def cancel(self) -> None:
        self.result = None
        self.destroy()

    def show(self):
        self.center()
        self.wait_window()
        return self.result


# -------------------- ВХОД --------------------

class LoginDialog(PinkDialog):
    def __init__(self, parent):
        super().__init__(parent, "Вход в систему", 455, 325)

        card = tk.Frame(
            self,
            bg=PINK_PANEL,
            bd=1,
            relief="solid",
            highlightthickness=1,
            highlightbackground=PINK_BORDER,
        )
        card.pack(fill="both", expand=True, padx=22, pady=22)

        fairy_title(card, "Вход в систему", PINK_PANEL, 18).pack(pady=(18, 12))

        form = tk.Frame(card, bg=PINK_PANEL)
        form.pack(fill="x", padx=34)

        tk.Label(
            form, text="Имя пользователя",
            bg=PINK_PANEL, fg=PINK_TEXT, font=("Segoe UI", 10, "bold")
        ).pack(anchor="w")

        self.username = tk.Entry(
            form,
            font=("Segoe UI", 11),
            bd=1,
            relief="solid",
            highlightthickness=1,
            highlightbackground=PINK_BORDER,
            highlightcolor=PINK_ACCENT,
        )
        self.username.pack(fill="x", pady=(4, 13))

        tk.Label(
            form, text="Пароль",
            bg=PINK_PANEL, fg=PINK_TEXT, font=("Segoe UI", 10, "bold")
        ).pack(anchor="w")

        # Требование ЛР: вводимый пароль всегда скрывается '*'.
        self.password = tk.Entry(
            form,
            show="*",
            font=("Segoe UI", 11),
            bd=1,
            relief="solid",
            highlightthickness=1,
            highlightbackground=PINK_BORDER,
            highlightcolor=PINK_ACCENT,
        )
        self.password.pack(fill="x", pady=(4, 18))

        buttons = tk.Frame(card, bg=PINK_PANEL)
        buttons.pack()

        fairy_button(buttons, "Войти", self.ok, width=13).pack(side="left", padx=6)
        light_button(buttons, "Отмена", self.cancel, width=13).pack(side="left", padx=6)

        tk.Label(
            card,
            text="✧ Безопасность ✧",
            bg=PINK_PANEL,
            fg=LILAC_DARK,
            font=("Segoe UI", 8, "italic"),
        ).pack(pady=(12, 0))

        self.bind("<Return>", lambda _event: self.ok())
        self.bind("<Escape>", lambda _event: self.cancel())
        self.after(100, self.username.focus_set)

    def ok(self):
        username = self.username.get().strip()

        if not username:
            messagebox.showwarning("Вход", "Введите имя пользователя.", parent=self)
            self.username.focus_set()
            return

        self.result = (username, self.password.get())
        self.destroy()


# -------------------- УСТАНОВКА / СМЕНА ПАРОЛЯ --------------------

class PasswordDialog(PinkDialog):
    EXIT_PROGRAM = "__EXIT_PROGRAM__"

    def __init__(self, parent, account: dict, first_time: bool = False):
        title = "Установка пароля" if first_time else "Смена пароля"
        height = 365 if first_time else 420
        super().__init__(parent, title, 490, height)

        self.account = account
        self.first_time = first_time

        card = tk.Frame(
            self,
            bg=PINK_PANEL,
            bd=1,
            relief="solid",
            highlightthickness=1,
            highlightbackground=PINK_BORDER,
        )
        card.pack(fill="both", expand=True, padx=22, pady=22)

        fairy_title(card, title, PINK_PANEL, 18).pack(pady=(16, 8))

        if account["restricted"]:
            hint = "Для этой учетной записи пароль должен содержать цифру и знак + - * / %."
        else:
            hint = "Ограничение на состав пароля для этой учетной записи отключено."

        tk.Label(
            card,
            text=hint,
            wraplength=390,
            justify="center",
            bg=FAIRY_GLOW,
            fg=PINK_TEXT,
            font=("Segoe UI", 9),
            padx=10,
            pady=7,
        ).pack(padx=28, pady=(0, 10), fill="x")

        form = tk.Frame(card, bg=PINK_PANEL)
        form.pack(fill="x", padx=34)

        self.old_password = None

        if not first_time:
            tk.Label(
                form, text="Старый пароль",
                bg=PINK_PANEL, fg=PINK_TEXT, font=("Segoe UI", 10, "bold")
            ).pack(anchor="w")
            self.old_password = tk.Entry(form, show="*", font=("Segoe UI", 11))
            self.old_password.pack(fill="x", pady=(4, 10))

        tk.Label(
            form, text="Новый пароль",
            bg=PINK_PANEL, fg=PINK_TEXT, font=("Segoe UI", 10, "bold")
        ).pack(anchor="w")
        self.new_password = tk.Entry(form, show="*", font=("Segoe UI", 11))
        self.new_password.pack(fill="x", pady=(4, 10))

        tk.Label(
            form, text="Подтверждение",
            bg=PINK_PANEL, fg=PINK_TEXT, font=("Segoe UI", 10, "bold")
        ).pack(anchor="w")
        self.confirm_password = tk.Entry(form, show="*", font=("Segoe UI", 11))
        self.confirm_password.pack(fill="x", pady=(4, 16))

        buttons = tk.Frame(card, bg=PINK_PANEL)
        buttons.pack()

        fairy_button(buttons, "Сохранить", self.ok, width=14).pack(side="left", padx=6)

        cancel_text = "Завершить работу" if first_time else "Отмена"
        cancel_width = 17 if first_time else 13
        light_button(buttons, cancel_text, self.cancel, width=cancel_width).pack(
            side="left", padx=6
        )

        self.bind("<Return>", lambda _event: self.ok())
        self.bind("<Escape>", lambda _event: self.cancel())

        focus_widget = self.new_password if first_time else self.old_password
        self.after(100, focus_widget.focus_set)

    def cancel(self) -> None:
        # При первом обязательном вводе пароля отказ означает завершение программы.
        self.result = self.EXIT_PROGRAM if self.first_time else None
        self.destroy()

    def ok(self):
        if not self.first_time:
            if self.old_password.get() != self.account["password"]:
                messagebox.showerror(
                    "Смена пароля",
                    "Неверно введен старый пароль.",
                    parent=self,
                )
                self.old_password.focus_set()
                return

        new_password = self.new_password.get()
        confirmation = self.confirm_password.get()

        if not new_password:
            messagebox.showwarning(
                "Пароль",
                "Пароль не должен быть пустым.",
                parent=self,
            )
            self.new_password.focus_set()
            return

        if len(new_password) > MAXPASS:
            messagebox.showwarning(
                "Пароль",
                f"Длина пароля не должна превышать {MAXPASS} символов.",
                parent=self,
            )
            self.new_password.focus_set()
            return

        if new_password != confirmation:
            messagebox.showerror(
                "Пароль",
                "Пароли должны совпадать!",
                parent=self,
            )
            self.new_password.focus_set()
            self.new_password.selection_range(0, tk.END)
            return

        if self.account["restricted"] and not check_variant_7(new_password):
            messagebox.showerror(
                "Пароль не подходит",
                "Пароль не соответствует установленному ограничению.\n\n"
                "Нужны одновременно:\n"
                "• хотя бы одна цифра;\n"
                "• хотя бы один знак +  -  *  /  %.\n\n"
                "Введите другой пароль или воспользуйтесь кнопкой отмены.",
                parent=self,
            )
            self.new_password.focus_set()
            return

        self.result = new_password
        self.destroy()


# -------------------- ДОБАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯ --------------------

class NewUserDialog(PinkDialog):
    def __init__(self, parent, accounts: list[dict]):
        super().__init__(parent, "Добавление пользователя", 465, 285)
        self.accounts = accounts

        card = tk.Frame(
            self,
            bg=PINK_PANEL,
            bd=1,
            relief="solid",
            highlightthickness=1,
            highlightbackground=PINK_BORDER,
        )
        card.pack(fill="both", expand=True, padx=22, pady=22)

        fairy_title(card, "Новый пользователь", PINK_PANEL, 17).pack(pady=(18, 16))

        tk.Label(
            card,
            text="Имя нового пользователя",
            bg=PINK_PANEL,
            fg=PINK_TEXT,
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", padx=36)

        self.username = tk.Entry(card, font=("Segoe UI", 11))
        self.username.pack(fill="x", padx=36, pady=(5, 18))

        tk.Label(
            card,
            text="Пароль будет пустым до первого входа пользователя.",
            bg=MINT,
            fg=PINK_TEXT,
            font=("Segoe UI", 9),
            padx=8,
            pady=6,
        ).pack(padx=36, fill="x", pady=(0, 14))

        buttons = tk.Frame(card, bg=PINK_PANEL)
        buttons.pack()

        fairy_button(buttons, "Добавить", self.ok, width=14).pack(side="left", padx=6)
        light_button(buttons, "Отмена", self.cancel, width=13).pack(side="left", padx=6)

        self.bind("<Return>", lambda _event: self.ok())
        self.bind("<Escape>", lambda _event: self.cancel())
        self.after(100, self.username.focus_set)

    def ok(self):
        username = self.username.get().strip()

        if not username:
            messagebox.showwarning(
                "Добавление пользователя",
                "Введите имя пользователя.",
                parent=self,
            )
            self.username.focus_set()
            return

        if len(username) > MAXNAME:
            messagebox.showwarning(
                "Добавление пользователя",
                f"Имя не должно превышать {MAXNAME} символов.",
                parent=self,
            )
            return

        if find_account(self.accounts, username) is not None:
            messagebox.showerror(
                "Добавление пользователя",
                f"Пользователь {username}\nуже зарегистрирован!",
                parent=self,
            )
            self.username.focus_set()
            self.username.selection_range(0, tk.END)
            return

        self.result = username
        self.destroy()


# -------------------- ВСЕ ПОЛЬЗОВАТЕЛИ --------------------

class UsersWindow(tk.Toplevel):
    def __init__(self, parent, accounts: list[dict], on_save):
        super().__init__(parent)

        self.accounts = accounts
        self.on_save = on_save

        self.title("Учетные записи пользователей")
        self.geometry("790x485")
        self.minsize(730, 445)
        self.configure(bg=PINK_BG)
        self.transient(parent)
        self.grab_set()

        top = tk.Frame(self, bg=LILAC, height=76)
        top.pack(fill="x")
        top.pack_propagate(False)

        tk.Label(
            top,
            text="♡  ✦  Учетные записи пользователей  ✦  ♡",
            bg=LILAC,
            fg=PINK_TEXT,
            font=("Segoe UI", 18, "bold"),
        ).pack(pady=(13, 2))

        tk.Label(
            top,
            text="Выберите пользователя и измените его параметры ниже",
            bg=LILAC,
            fg=LILAC_DARK,
            font=("Segoe UI", 9),
        ).pack()

        table_frame = tk.Frame(self, bg=PINK_BG)
        table_frame.pack(fill="both", expand=True, padx=22, pady=(14, 0))

        self.tree = ttk.Treeview(
            table_frame,
            columns=("username", "blocked", "restricted"),
            show="headings",
            selectmode="browse",
            height=7,
        )
        self.tree.heading("username", text="Имя пользователя")
        self.tree.heading("blocked", text="Блокировка")
        self.tree.heading("restricted", text="Ограничение пароля")

        self.tree.column("username", width=285, anchor="center")
        self.tree.column("blocked", width=175, anchor="center")
        self.tree.column("restricted", width=245, anchor="center")

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview,
        )
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        editor = tk.LabelFrame(
            self,
            text=" ✧ Параметры выбранной учетной записи ✧ ",
            bg=PINK_PANEL,
            fg=PINK_TEXT,
            bd=1,
            relief="solid",
            font=("Segoe UI", 10, "bold"),
        )
        editor.pack(fill="x", padx=22, pady=(10, 14))

        editor.columnconfigure(1, weight=1)
        editor.columnconfigure(3, weight=1)

        self.selected_label = tk.Label(
            editor,
            text="Пользователь не выбран",
            bg=PINK_PANEL,
            fg=PINK_TEXT,
            font=("Segoe UI", 11, "bold"),
        )
        self.selected_label.grid(
            row=0,
            column=0,
            columnspan=5,
            sticky="w",
            padx=16,
            pady=(10, 6),
        )

        tk.Label(
            editor,
            text="Блокировка:",
            bg=PINK_PANEL,
            fg=PINK_TEXT,
            font=("Segoe UI", 10),
        ).grid(row=1, column=0, sticky="w", padx=(16, 7), pady=6)

        self.blocked_value = tk.StringVar(value="Нет")
        self.blocked_combo = ttk.Combobox(
            editor,
            textvariable=self.blocked_value,
            values=("Нет", "Да"),
            state="readonly",
            width=12,
        )
        self.blocked_combo.grid(
            row=1,
            column=1,
            sticky="w",
            padx=(0, 18),
            pady=6,
        )

        tk.Label(
            editor,
            text="Ограничение пароля:",
            bg=PINK_PANEL,
            fg=PINK_TEXT,
            font=("Segoe UI", 10),
        ).grid(row=1, column=2, sticky="w", padx=(0, 7), pady=6)

        self.restricted_value = tk.StringVar(value="Включено")
        self.restricted_combo = ttk.Combobox(
            editor,
            textvariable=self.restricted_value,
            values=("Включено", "Отключено"),
            state="readonly",
            width=15,
        )
        self.restricted_combo.grid(
            row=1,
            column=3,
            sticky="w",
            padx=(0, 10),
            pady=6,
        )

        self.save_button = fairy_button(
            editor,
            "Сохранить",
            self.save_selected,
            width=14,
        )
        self.save_button.config(state="disabled")
        self.save_button.grid(
            row=1,
            column=4,
            sticky="e",
            padx=(4, 16),
            pady=6,
        )

        tk.Label(
            editor,
            text="При включенном ограничении: цифра + один из знаков + - * / %.",
            bg=PINK_PANEL,
            fg=PINK_TEXT,
            font=("Segoe UI", 9),
        ).grid(
            row=2,
            column=0,
            columnspan=4,
            sticky="w",
            padx=16,
            pady=(3, 10),
        )

        light_button(editor, "Закрыть", self.destroy, width=12).grid(
            row=2,
            column=4,
            sticky="e",
            padx=(4, 16),
            pady=(3, 10),
        )

        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.bind("<Control-s>", lambda _event: self.save_selected())

        self.refresh(select_index=0 if self.accounts else None)

    def refresh(self, select_index: int | None = None):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for index, account in enumerate(self.accounts):
            self.tree.insert(
                "",
                "end",
                iid=str(index),
                values=(
                    account["username"],
                    "Да" if account["blocked"] else "Нет",
                    "Включено" if account["restricted"] else "Отключено",
                ),
            )

        if select_index is not None and 0 <= select_index < len(self.accounts):
            item_id = str(select_index)
            self.tree.selection_set(item_id)
            self.tree.focus(item_id)
            self.tree.see(item_id)
            self.on_select()
        else:
            self.selected_label.config(text="Пользователь не выбран")
            self.save_button.config(state="disabled")

    def on_select(self, _event=None):
        selected = self.tree.selection()
        if not selected:
            self.save_button.config(state="disabled")
            return

        index = int(selected[0])
        account = self.accounts[index]

        self.selected_label.config(text=f"♡ Пользователь: {account['username']}")
        self.blocked_value.set("Да" if account["blocked"] else "Нет")
        self.restricted_value.set(
            "Включено" if account["restricted"] else "Отключено"
        )
        self.save_button.config(state="normal")

    def save_selected(self):
        selected = self.tree.selection()

        if not selected:
            messagebox.showwarning(
                "Учетные записи",
                "Сначала выберите пользователя в таблице.",
                parent=self,
            )
            return

        index = int(selected[0])
        account = self.accounts[index]

        account["blocked"] = self.blocked_value.get() == "Да"
        account["restricted"] = self.restricted_value.get() == "Включено"

        self.on_save()
        self.refresh(select_index=index)

        messagebox.showinfo(
            "Учетные записи",
            f"Параметры пользователя {account['username']} сохранены.",
            parent=self,
        )


# -------------------- ГЛАВНОЕ ОКНО --------------------

class SecurityApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("820x520")
        self.root.minsize(760, 480)
        self.root.configure(bg=PINK_BG)

        try:
            self.accounts = load_accounts()
        except Exception as error:
            messagebox.showerror(
                "Ошибка",
                f"Не удалось открыть файл учетных записей:\n{error}",
                parent=self.root,
            )
            self.root.destroy()
            return

        self.current_user: dict | None = None
        self.failed_password_attempts = 0

        self.setup_styles()
        self.create_menu()
        self.create_main_ui()
        self.update_access()

        # Сразу после запуска запрашиваются имя и пароль.
        self.root.after(250, self.login)

    def setup_styles(self):
        style = ttk.Style()

        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Treeview",
            background=PINK_LIGHT,
            fieldbackground=PINK_LIGHT,
            foreground=PINK_TEXT,
            rowheight=30,
            borderwidth=0,
            font=("Segoe UI", 10),
        )
        style.configure(
            "Treeview.Heading",
            background=LILAC,
            foreground=PINK_TEXT,
            font=("Segoe UI", 10, "bold"),
            relief="flat",
        )
        style.map(
            "Treeview",
            background=[("selected", PINK_ACCENT)],
            foreground=[("selected", "white")],
        )

        style.configure(
            "TCombobox",
            fieldbackground=PINK_LIGHT,
            background=PINK_LIGHT,
            foreground=PINK_TEXT,
            padding=3,
        )

    def create_menu(self):
        menubar = tk.Menu(self.root)

        self.users_menu = tk.Menu(menubar, tearoff=0)
        self.users_menu.add_command(
            label="Смена пароля",
            command=self.change_password,
            state="disabled",
        )
        self.users_menu.add_command(
            label="Новый пользователь",
            command=self.add_user,
            state="disabled",
        )
        self.users_menu.add_command(
            label="Все пользователи",
            command=self.show_users,
            state="disabled",
        )
        self.users_menu.add_separator()
        self.users_menu.add_command(
            label="Выход",
            command=self.root.destroy,
        )
        menubar.add_cascade(label="Пользователи", menu=self.users_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(
            label="О программе",
            command=self.about,
        )
        menubar.add_cascade(label="Справка", menu=help_menu)

        self.root.config(menu=menubar)

    def create_main_ui(self):
        header = tk.Frame(self.root, bg=PINK_ACCENT, height=112)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="♡  FairyGuard  ♡",
            bg=PINK_ACCENT,
            fg="white",
            font=("Segoe UI", 25, "bold"),
        ).pack(pady=(13, 0))

        tk.Label(
            header,
            text="✦ система разграничения доступа ✦",
            bg=PINK_ACCENT,
            fg="#fff5fa",
            font=("Segoe UI", 10),
        ).pack()

        tk.Label(
            header,
            text="✧   ♡   ✦   ♡   ✧",
            bg=PINK_ACCENT,
            fg="#ffe2ee",
            font=("Segoe UI Symbol", 11),
        ).pack(pady=(3, 0))

        center = tk.Frame(self.root, bg=PINK_BG)
        center.pack(fill="both", expand=True)

        # Декоративные "искорки" по краям.
        tk.Label(
            center, text="✦\n♡\n✧",
            bg=PINK_BG, fg="#d6b4ef", font=("Segoe UI Symbol", 20)
        ).place(relx=0.08, rely=0.22)

        tk.Label(
            center, text="✧\n♡\n✦",
            bg=PINK_BG, fg="#f0a6c5", font=("Segoe UI Symbol", 20)
        ).place(relx=0.89, rely=0.54)

        card = tk.Frame(
            center,
            bg=PINK_PANEL,
            bd=1,
            relief="solid",
            highlightthickness=1,
            highlightbackground=PINK_BORDER,
        )
        card.place(
            relx=0.5,
            rely=0.46,
            anchor="center",
            width=565,
            height=255,
        )

        fairy_title(card, "Добро пожаловать", PINK_PANEL, 19).pack(
            pady=(26, 10)
        )

        tk.Label(
            card,
            text=(
                "Добро пожаловать!"
            ),
            bg=PINK_PANEL,
            fg=PINK_TEXT,
            justify="center",
            font=("Segoe UI", 11),
        ).pack(pady=(0, 18))

        self.login_button = fairy_button(
            card,
            "Вход в систему",
            self.login,
            width=19,
        )
        self.login_button.pack()

        self.logged_label = tk.Label(
            card,
            text="",
            bg=PINK_PANEL,
            fg=PINK_TEXT,
            justify="center",
            font=("Segoe UI", 11, "bold"),
        )

        tk.Label(
            card,
            text="♡ ✧ ♡",
            bg=PINK_PANEL,
            fg=LILAC_DARK,
            font=("Segoe UI Symbol", 13),
        ).pack(side="bottom", pady=12)

        self.status = tk.Label(
            self.root,
            text="✧ Пользователь не вошел в систему",
            anchor="w",
            bg=PINK_LIGHT,
            fg=PINK_TEXT,
            padx=12,
            font=("Segoe UI", 9),
        )
        self.status.pack(fill="x", side="bottom", ipady=5)

    def save(self):
        save_accounts(self.accounts)

    def update_access(self):
        logged_in = self.current_user is not None
        is_admin = logged_in and self.current_user["username"] == "ADMIN"

        # Обычному пользователю доступны только смена пароля и выход.
        self.users_menu.entryconfig(
            "Смена пароля",
            state="normal" if logged_in else "disabled",
        )
        self.users_menu.entryconfig(
            "Новый пользователь",
            state="normal" if is_admin else "disabled",
        )
        self.users_menu.entryconfig(
            "Все пользователи",
            state="normal" if is_admin else "disabled",
        )

        if not logged_in:
            if not self.login_button.winfo_manager():
                self.login_button.pack()
            self.logged_label.pack_forget()
            self.status.config(text="✧ Пользователь не вошел в систему")
            return

        self.login_button.pack_forget()

        role = "Администратор" if is_admin else "Обычный пользователь"
        restriction = (
            "включено"
            if self.current_user["restricted"]
            else "отключено"
        )

        self.logged_label.config(
            text=(
                f"♡ {self.current_user['username']} ♡\n"
                f"{role}\n"
                f"Ограничение пароля: {restriction}"
            )
        )
        self.logged_label.pack(pady=16)

        self.status.config(
            text=f"✦ Текущий пользователь: {self.current_user['username']} • {role}"
        )

    def login(self):
        if self.current_user is not None:
            return

        # Повторный ввод имени/пароля выполняется в цикле.
        while self.current_user is None:
            result = LoginDialog(self.root).show()

            # Отмена оставляет пользователя на главном экране:
            # он может повторить вход или выбрать "Выход".
            if result is None:
                return

            username, entered_password = result
            account = find_account(self.accounts, username)

            if account is None:
                messagebox.showerror(
                    "Вход",
                    "Вы не зарегистрированы!\n"
                    "Проверьте имя и попробуйте снова.",
                    parent=self.root,
                )
                continue

            # Новый пользователь / первый запуск ADMIN:
            # пустой пароль означает обязательную первичную установку.
            if account["password"] == "":
                new_password = PasswordDialog(
                    self.root,
                    account=account,
                    first_time=True,
                ).show()

                if new_password == PasswordDialog.EXIT_PROGRAM:
                    self.root.destroy()
                    return

                # На всякий случай: окно может быть уничтожено извне.
                if new_password is None:
                    return

                account["password"] = new_password
                self.save()

            elif entered_password != account["password"]:
                self.failed_password_attempts += 1
                remaining = 3 - self.failed_password_attempts

                if self.failed_password_attempts >= 3:
                    messagebox.showerror(
                        "Вход",
                        "Три раза введен неверный пароль.\n"
                        "Работа программы будет завершена.",
                        parent=self.root,
                    )
                    self.root.destroy()
                    return

                messagebox.showerror(
                    "Вход",
                    f"Неверный пароль!\nОсталось попыток: {remaining}",
                    parent=self.root,
                )
                continue

            if account["blocked"]:
                messagebox.showerror(
                    "Вход",
                    "Эта учетная запись заблокирована администратором.",
                    parent=self.root,
                )
                continue

            self.current_user = account
            self.update_access()

            messagebox.showinfo(
                "Вход",
                f"Добро пожаловать, {account['username']}! ♡",
                parent=self.root,
            )
            return

    def change_password(self):
        if self.current_user is None:
            return

        new_password = PasswordDialog(
            self.root,
            account=self.current_user,
            first_time=False,
        ).show()

        if new_password is None:
            return

        self.current_user["password"] = new_password
        self.save()

        messagebox.showinfo(
            "Смена пароля",
            "Пароль успешно изменен. ✦",
            parent=self.root,
        )

    def add_user(self):
        # Самостоятельной регистрации нет: пользователя создает ADMIN.
        if self.current_user is None or self.current_user["username"] != "ADMIN":
            return

        username = NewUserDialog(
            self.root,
            self.accounts,
        ).show()

        if username is None:
            return

        # Новый пользователь: уникальное имя, пустой пароль,
        # блокировка выключена, ограничение включено.
        self.accounts.append(
            {
                "username": username,
                "password": "",
                "blocked": False,
                "restricted": True,
            }
        )
        self.save()

        messagebox.showinfo(
            "Добавление пользователя",
            f"Пользователь {username} добавлен. ♡\n"
            "Пароль будет установлен при первом входе.",
            parent=self.root,
        )

    def show_users(self):
        if self.current_user is None or self.current_user["username"] != "ADMIN":
            return

        UsersWindow(
            self.root,
            self.accounts,
            self.save,
        )

    def about(self):
        # Здесь специально оставлены сведения о лабораторной и варианте.
        messagebox.showinfo(
            "О программе",
            "Лабораторная работа №1\n"
            "Разработка программы разграничения полномочий пользователей\n"
            "на основе парольной аутентификации\n\n"
            f"Автор: {AUTHOR}\n"
            f"Группа: {GROUP}\n\n"
            "Индивидуальный вариант №7:\n"
            "пароль должен содержать цифры и знаки арифметических операций.\n"
            "Используемые знаки: +  -  *  /  %\n\n"
            "Данные учетных записей и пароли сохраняются в accounts.json.",
            parent=self.root,
        )


def main():
    root = tk.Tk()
    SecurityApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
