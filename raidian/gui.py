"""Keyboard-operable, responsive Tkinter desktop workbench.

Native Treeview/Entry widgets make filenames and actions easy to inspect for
humans, accessibility tools and computer-use agents alike.
"""
from __future__ import annotations

import ctypes
import json
import os
from pathlib import Path
import queue
import sys
import threading
import tkinter as tk
from tkinter import filedialog, font as tkfont, messagebox, simpledialog, ttk
from typing import Callable

from . import __version__
from .core import GitError, Repository

BURGUNDY = "#551128"
RED = "#A72146"
RED_HOVER = "#C42B54"
BLUSH = "#FCECEF"
PAPER = "#FFFFFF"
CANVAS = "#F8F5F5"
TEXT = "#302329"
MUTED = "#776B70"
BORDER = "#E9DCDF"


def resource_path(relative: str) -> Path:
    """Locate optional assets in source checkout and PyInstaller onefile bundles."""
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
    return base / relative


def typography(root: tk.Tk) -> str:
    # Private process-only registration; external fonts are never installed systemwide.
    if os.name == "nt":
        for file in resource_path("assets/fonts").glob("*.ttf"):
            try:
                ctypes.windll.gdi32.AddFontResourceExW(str(file), 0x10, 0)
            except (AttributeError, OSError):
                pass
    candidates = ("Wanted Sans", "Pretendard", "맑은 고딕", "Malgun Gothic",
                  "Noto Sans CJK KR", "Apple SD Gothic Neo", "DejaVu Sans", "Arial")
    available = set(tkfont.families(root))
    return next((family for family in candidates if family in available), "TkDefaultFont")


class Pill(tk.Canvas):
    """A large-action pill with mouse, Enter/Space and visible focus feedback."""
    def __init__(self, master: tk.Misc, text: str, command: Callable[[], None],
                 color: str = RED, foreground: str = PAPER, width: int = 126):
        super().__init__(master, height=38, width=width, bg=master.cget("background"),
                         highlightthickness=2, highlightbackground=master.cget("background"),
                         highlightcolor=RED, takefocus=1, cursor="hand2", bd=0)
        self._text, self._command = text, command
        self._color, self._foreground = color, foreground
        self.bind("<Configure>", lambda _event: self._paint())
        self.bind("<Button-1>", lambda _event: self._command())
        self.bind("<Return>", lambda _event: self._command())
        self.bind("<space>", lambda _event: self._command())
        self.bind("<Enter>", lambda _event: self._paint(hover=True))
        self.bind("<Leave>", lambda _event: self._paint())
        self.bind("<FocusIn>", lambda _event: self.configure(highlightbackground=RED))
        self.bind("<FocusOut>", lambda _event: self.configure(highlightbackground=master.cget("background")))

    def _paint(self, hover: bool = False) -> None:
        w, h = max(4, self.winfo_width()), max(4, self.winfo_height())
        self.delete("all")
        r = min(18, h // 2 - 2)
        points = [r, 2, w-r, 2, w-2, 2, w-2, r, w-2, h-r, w-2, h-2,
                  w-r, h-2, r, h-2, 2, h-2, 2, h-r, 2, r, 2, 2]
        self.create_polygon(points, smooth=True, splinesteps=24,
                            fill=RED_HOVER if hover and self._color == RED else self._color,
                            outline="")
        self.create_text(w / 2, h / 2, text=self._text, fill=self._foreground,
                         font=(getattr(self, "font_family", "Arial"), 10, "bold"))


class Workbench:
    def __init__(self, root: tk.Tk, initial_repo: str = "."):
        self.root = root
        self.root.title(f"Raidian · 레이디안 {__version__}")
        self.root.geometry("1100x760")
        self.root.minsize(650, 610)
        self.root.configure(bg=CANVAS)
        self.font = typography(root)
        self.repo: Repository | None = None
        self.events: queue.Queue[tuple[bool, str, str]] = queue.Queue()
        self.busy = False
        self.compact: bool | None = None
        self.repo_text = tk.StringVar(value="저장소를 선택하세요")
        self.branch_text = tk.StringVar(value="브랜치: —")
        self.message = tk.StringVar()
        self.status_text = tk.StringVar(value="준비되었습니다 · F5 새로고침 · Ctrl+Enter 커밋")
        self._style()
        self._build()
        self._keys()
        self.root.after(100, self._poll)
        try:
            self.set_repo(initial_repo)
        except GitError:
            self.status_text.set("폴더 열기로 기존 Git 저장소를 선택하거나 새 저장소를 시작하세요.")

    def _style(self) -> None:
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("App.TFrame", background=CANVAS)
        style.configure("Card.TFrame", background=PAPER)
        style.configure("Title.TLabel", background=PAPER, foreground=TEXT,
                        font=(self.font, 13, "bold"))
        style.configure("Sub.TLabel", background=PAPER, foreground=MUTED,
                        font=(self.font, 10))
        style.configure("Base.TLabel", background=CANVAS, foreground=TEXT,
                        font=(self.font, 10))
        style.configure("TButton", padding=(14, 9), font=(self.font, 10),
                        foreground=TEXT, background=BLUSH, borderwidth=0)
        style.map("TButton", background=[("active", "#F2D8DE"), ("disabled", "#EEE5E8")])
        style.configure("TEntry", padding=7, fieldbackground=PAPER, foreground=TEXT)
        style.configure("Treeview", font=(self.font, 10), rowheight=32,
                        background=PAPER, fieldbackground=PAPER, foreground=TEXT,
                        borderwidth=0)
        style.configure("Treeview.Heading", font=(self.font, 10, "bold"),
                        background=BLUSH, foreground=BURGUNDY, padding=9, borderwidth=0)
        style.map("Treeview", background=[("selected", BLUSH)], foreground=[("selected", BURGUNDY)])

    def _pill(self, parent: tk.Misc, text: str, command: Callable[[], None],
              color: str = RED, fg: str = PAPER, width: int = 125) -> Pill:
        pill = Pill(parent, text, command, color, fg, width)
        pill.font_family = self.font
        return pill

    def _build(self) -> None:
        header = tk.Frame(self.root, bg=BURGUNDY, padx=22, pady=17)
        header.pack(fill="x")
        logo = tk.Canvas(header, width=45, height=45, bg=BURGUNDY, bd=0, highlightthickness=0)
        logo.pack(side="left", padx=(0, 13))
        # Ruby mascot uses only native Canvas primitives: no image dependency.
        logo.create_rectangle(2, 2, 44, 44, fill=BLUSH, outline="")
        logo.create_line(17, 11, 17, 32, 30, 37, fill=RED, width=3.5, capstyle=tk.ROUND, smooth=True)
        logo.create_line(17, 23, 26, 18, 30, 10, fill=RED, width=3.5, capstyle=tk.ROUND, smooth=True)
        for x, y in ((17, 11), (30, 10), (30, 37)):
            logo.create_oval(x - 4, y - 4, x + 4, y + 4, fill=RED_HOVER, outline=PAPER)
        logo.create_oval(20, 22, 23, 25, fill=BURGUNDY, outline="")
        logo.create_oval(27, 22, 30, 25, fill=BURGUNDY, outline="")
        logo.create_arc(22, 24, 29, 30, start=180, extent=170, style=tk.ARC, outline=BURGUNDY, width=1.5)
        title = tk.Frame(header, bg=BURGUNDY)
        title.pack(side="left")
        tk.Label(title, text="Raidian", fg=PAPER, bg=BURGUNDY,
                 font=(self.font, 21, "bold")).pack(anchor="w")
        tk.Label(title, text="작은 Git 작업실 · 명료하게, 안전하게, 함께", fg="#F7C8D4",
                 bg=BURGUNDY, font=(self.font, 10)).pack(anchor="w")
        tk.Label(header, text="GIT  /  GH  /  AGENTS", fg="#F5BCC9", bg=BURGUNDY,
                 font=(self.font, 9, "bold")).pack(side="right")

        body = ttk.Frame(self.root, style="App.TFrame", padding=(18, 15))
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=1)
        body.rowconfigure(3, weight=1)
        row = ttk.Frame(body, style="App.TFrame")
        row.grid(row=0, column=0, sticky="ew", pady=(0, 11))
        row.columnconfigure(0, weight=1)
        ttk.Entry(row, textvariable=self.repo_text, state="readonly").grid(row=0, column=0, sticky="ew", padx=(0, 9))
        ttk.Button(row, text="폴더 열기", command=self.open_repo).grid(row=0, column=1, padx=3)
        ttk.Button(row, text="새 저장소", command=self.init_repo).grid(row=0, column=2, padx=3)
        ttk.Button(row, text="새로고침", command=self.refresh).grid(row=0, column=3, padx=3)

        actions = tk.Frame(body, bg=CANVAS)
        actions.grid(row=1, column=0, sticky="ew", pady=(0, 11))
        self.actions = actions
        self.action_buttons = [
            self._pill(actions, "↑ 푸시", self.push, width=96),
            self._pill(actions, "↓ 가져오기", self.fetch, color=BLUSH, fg=BURGUNDY, width=126),
            ttk.Button(actions, text="브랜치 만들기", command=self.branch_create),
            ttk.Button(actions, text="브랜치 전환", command=self.branch_switch),
            ttk.Button(actions, text="병합 · no-ff", command=self.merge),
            ttk.Button(actions, text="원격", command=self.remote_dialog),
            ttk.Button(actions, text="GH / PR", command=self.github_dialog),
        ]

        info = tk.Frame(body, bg=BLUSH, padx=13, pady=10)
        info.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        tk.Label(info, textvariable=self.branch_text, fg=BURGUNDY, bg=BLUSH,
                 font=(self.font, 11, "bold")).pack(anchor="w")
        tk.Label(info, text="커밋 = 변경 저장  •  푸시 = 원격 전송  •  병합 = 이력 보존(no-ff)",
                 fg=MUTED, bg=BLUSH, font=(self.font, 9)).pack(anchor="w")

        self.panels = ttk.Frame(body, style="App.TFrame")
        self.panels.grid(row=3, column=0, sticky="nsew")
        self.panels.rowconfigure(0, weight=1)
        self.panels.columnconfigure(0, weight=1)
        self.panels.columnconfigure(1, weight=1)
        self.files_card, self.files_tree = self._tree_card(
            self.panels, "변경 파일", "작업 중인 파일을 한눈에 확인합니다.",
            (("state", "상태", 65), ("path", "파일", 360)))
        self.log_card, self.log_tree = self._tree_card(
            self.panels, "커밋 이력", "선택한 커밋을 복사하거나 안전하게 되돌립니다.",
            (("sha", "커밋", 90), ("date", "날짜", 90), ("message", "메시지", 260)))
        self.log_tree.bind("<<TreeviewSelect>>", lambda _: self._selection_hint())
        self.files_card.grid(row=0, column=0, sticky="nsew", padx=(0, 7))
        self.log_card.grid(row=0, column=1, sticky="nsew", padx=(7, 0))

        history_controls = ttk.Frame(body, style="App.TFrame")
        history_controls.grid(row=4, column=0, sticky="ew", pady=(11, 7))
        ttk.Button(history_controls, text="선택 커밋 복사 (cherry-pick)", command=self.copy_commit).pack(side="left", padx=(0, 8))
        ttk.Button(history_controls, text="선택 커밋 되돌리기 (revert)", command=self.revert).pack(side="left")
        ttk.Button(history_controls, text="AI 사용 안내", command=self.agent_info).pack(side="right")

        commit = tk.Frame(body, bg=PAPER, padx=13, pady=11)
        commit.grid(row=5, column=0, sticky="ew", pady=(0, 8))
        commit.columnconfigure(0, weight=1)
        tk.Label(commit, text="커밋 메시지", bg=PAPER, fg=BURGUNDY,
                 font=(self.font, 10, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 5))
        tk.Label(commit, text="비워두면 변경 종류를 파악해 자동 생성", bg=PAPER, fg=MUTED,
                 font=(self.font, 9)).grid(row=0, column=1, columnspan=2, sticky="e", pady=(0, 5))
        ttk.Entry(commit, textvariable=self.message).grid(row=1, column=0, sticky="ew", padx=(0, 10))
        self._pill(commit, "커밋", self.commit, width=90).grid(row=1, column=1, padx=(0, 6))
        self._pill(commit, "커밋 + 푸시", lambda: self.commit(push=True), width=135).grid(row=1, column=2)

        footer = tk.Frame(self.root, bg=CANVAS, padx=18, pady=5)
        footer.pack(fill="x", side="bottom")
        tk.Label(footer, textvariable=self.status_text, bg=CANVAS, fg=MUTED,
                 font=(self.font, 9), anchor="w").pack(fill="x")
        self.root.bind("<Configure>", self._resize, add="+")

    def _tree_card(self, parent: tk.Misc, title: str, subtitle: str,
                   columns: tuple[tuple[str, str, int], ...]) -> tuple[tk.Frame, ttk.Treeview]:
        card = tk.Frame(parent, bg=PAPER, padx=13, pady=12, highlightbackground=BORDER,
                        highlightthickness=1)
        tk.Label(card, text=title, bg=PAPER, fg=TEXT,
                 font=(self.font, 13, "bold")).pack(anchor="w")
        tk.Label(card, text=subtitle, bg=PAPER, fg=MUTED,
                 font=(self.font, 9)).pack(anchor="w", pady=(1, 9))
        inner = tk.Frame(card, bg=PAPER)
        inner.pack(fill="both", expand=True)
        keys = [col[0] for col in columns]
        table = ttk.Treeview(inner, columns=keys, show="headings", selectmode="browse", height=10)
        for key, label, width in columns:
            table.heading(key, text=label)
            table.column(key, width=width, minwidth=60, stretch=key in ("path", "message"))
        table.pack(side="left", fill="both", expand=True)
        scroll = ttk.Scrollbar(inner, orient="vertical", command=table.yview)
        table.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        return card, table

    def _resize(self, event: tk.Event) -> None:
        if event.widget is not self.root:
            return
        compact = self.root.winfo_width() < 860
        if compact == self.compact:
            return
        self.compact = compact
        for button in self.action_buttons:
            button.grid_forget()
        columns = 4 if compact else 7
        for col in range(7):
            self.actions.columnconfigure(col, weight=1 if col < columns else 0)
        for index, button in enumerate(self.action_buttons):
            button.grid(row=index // columns, column=index % columns, sticky="ew", padx=3, pady=3)
        self.files_card.grid_forget()
        self.log_card.grid_forget()
        self.panels.rowconfigure(1, weight=1 if compact else 0)
        self.panels.columnconfigure(1, weight=0 if compact else 1)
        if compact:
            self.files_card.grid(row=0, column=0, columnspan=2, sticky="nsew", pady=(0, 6))
            self.log_card.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(6, 0))
        else:
            self.files_card.grid(row=0, column=0, sticky="nsew", padx=(0, 7))
            self.log_card.grid(row=0, column=1, sticky="nsew", padx=(7, 0))

    def _keys(self) -> None:
        mapping = {"<Control-o>": self.open_repo, "<Control-Return>": self.commit,
                   "<Control-Shift-Return>": lambda: self.commit(push=True),
                   "<F5>": self.refresh, "<Alt-r>": self.refresh,
                   "<Alt-b>": self.branch_create, "<Alt-p>": self.push}
        for key, action in mapping.items():
            self.root.bind(key, lambda _event, cb=action: cb())

    def set_repo(self, path: str) -> None:
        if self.busy:
            raise GitError("진행 중인 Git 작업이 끝난 뒤 저장소를 변경할 수 있습니다.")
        self.repo = Repository(path)
        self.repo_text.set(str(self.repo.path))
        self.refresh()

    def open_repo(self) -> None:
        if self.busy:
            self.status_text.set("Git 작업 진행 중 · 완료 후 저장소를 열어주세요.")
            return
        selected = filedialog.askdirectory(title="Git 저장소 폴더 선택")
        if selected:
            try:
                self.set_repo(selected)
            except GitError as error:
                messagebox.showerror("저장소를 열 수 없습니다", str(error), parent=self.root)

    def init_repo(self) -> None:
        if self.busy:
            self.status_text.set("Git 작업 진행 중 · 완료 후 새 저장소를 시작하세요.")
            return
        selected = filedialog.askdirectory(title="새 Git 저장소 폴더 선택")
        if selected and messagebox.askyesno("저장소 시작", f"이 폴더에 Git을 시작할까요?\n{selected}", parent=self.root):
            try:
                self.set_repo(str(Repository.init(selected).path))
            except GitError as error:
                messagebox.showerror("오류", str(error), parent=self.root)

    def refresh(self) -> None:
        if self.repo is None:
            return
        try:
            snapshot = self.repo.snapshot()
        except GitError as error:
            self.status_text.set(f"오류: {error}")
            return
        self.branch_text.set(f"● {snapshot['branch']}  ·  변경 파일 {len(snapshot['files'])}개")
        for table in (self.files_tree, self.log_tree):
            children = table.get_children()
            if children:
                table.delete(*children)
        for file in snapshot["files"]:
            label = file["state"]
            self.files_tree.insert("", "end", values=(label, file["path"]))
        for commit in snapshot["history"]:
            self.log_tree.insert("", "end", iid=commit["sha"],
                                 values=(commit["sha"][:8], commit["date"], commit["message"]))
        self.status_text.set("최신 상태 · 항목 선택 시 작업 힌트를 볼 수 있습니다. · AI: raidian --json agent-guide")

    def _selection_hint(self) -> None:
        if self.log_tree.selection():
            self.status_text.set("커밋 선택됨 · 복사 = cherry-pick (새 이력 추가) · 되돌리기 = revert (기존 이력 보존)")

    def _job(self, title: str, operation: Callable[[], str]) -> None:
        if self.busy:
            self.status_text.set("이미 진행 중인 작업이 있습니다.")
            return
        if self.repo is None:
            messagebox.showinfo("저장소 필요", "먼저 Git 저장소를 열어주세요.", parent=self.root)
            return
        self.busy = True
        self.status_text.set(f"{title} 진행 중…")
        def worker() -> None:
            try:
                result = operation()
                self.events.put((True, title, str(result)))
            except (GitError, OSError, ValueError) as error:
                self.events.put((False, title, str(error)))
        threading.Thread(target=worker, daemon=True, name="raidian-git").start()

    def _poll(self) -> None:
        try:
            while True:
                success, title, detail = self.events.get_nowait()
                self.busy = False
                if success:
                    if title.startswith("커밋"):
                        self.message.set("")
                    self.status_text.set(f"✓ {title} 완료 · {detail[:150]}")
                    self.refresh()
                    self.status_text.set(f"✓ {title} 완료 · {detail[:150]}")
                else:
                    self.status_text.set(f"{title} 실패 · {detail[:170]}")
                    messagebox.showerror(f"{title} 실패", detail, parent=self.root)
        except queue.Empty:
            pass
        self.root.after(100, self._poll)

    def commit(self, push: bool = False) -> None:
        if self.repo is None:
            return
        text = self.message.get()
        repo = self.repo
        def work() -> str:
            result = repo.commit(text)
            if push:
                result += "\n" + repo.push()
            return result
        self._job("커밋 + 푸시" if push else "커밋", work)

    def push(self) -> None:
        if self.repo:
            self._job("푸시", self.repo.push)

    def fetch(self) -> None:
        if self.repo:
            self._job("원격 가져오기", self.repo.fetch)

    def branch_create(self) -> None:
        if not self.repo:
            return
        feature = simpledialog.askstring("기능 영역", "브랜치 영역 (예: feature / fix)", parent=self.root)
        if not feature:
            return
        detail = simpledialog.askstring("작업 이름", "작업 이름 (예: korean-encoding)", parent=self.root)
        if detail:
            source = self.repo.branch()
            self._job("하위 작업 브랜치", lambda: self.repo.nested_branch(feature, detail, source))

    def branch_switch(self) -> None:
        if not self.repo:
            return
        try:
            available = self.repo.branches()
        except GitError as error:
            messagebox.showerror("브랜치", str(error), parent=self.root)
            return
        name = simpledialog.askstring("브랜치 전환", "전환할 브랜치 이름:\n" + "\n".join(available[:14]), parent=self.root)
        if name:
            self._job("브랜치 전환", lambda: self.repo.switch(name))

    def merge(self) -> None:
        if not self.repo:
            return
        source = simpledialog.askstring("병합 · --no-ff", "현재 브랜치에 합칠 브랜치 이름:", parent=self.root)
        if source and messagebox.askyesno("병합 확인", f"'{source}'를 '{self.repo.branch()}'에 병합할까요?\n항상 --no-ff를 사용합니다.", parent=self.root):
            self._job("no-ff 병합", lambda: self.repo.merge(source))

    def _selected_sha(self) -> str | None:
        selected = self.log_tree.selection()
        if not selected:
            messagebox.showinfo("이력 선택", "먼저 오른쪽 커밋 이력에서 항목을 선택하세요.", parent=self.root)
            return None
        return selected[0]

    def copy_commit(self) -> None:
        sha = self._selected_sha()
        if sha and self.repo and messagebox.askyesno("커밋 복사", f"{sha[:10]} 변경분을 현재 브랜치에 새 커밋으로 적용할까요?", parent=self.root):
            self._job("커밋 복사", lambda: self.repo.cherry_pick(sha))

    def revert(self) -> None:
        sha = self._selected_sha()
        if sha and self.repo and messagebox.askyesno("안전한 되돌리기", f"{sha[:10]}의 변경을 취소하는 새 커밋을 만들까요?\n기존 이력은 지우지 않습니다.", parent=self.root):
            self._job("커밋 되돌리기", lambda: self.repo.revert(sha))

    def remote_dialog(self) -> None:
        if not self.repo:
            return
        remotes = self.repo.remotes()
        summary = "\n".join(f"{item['name']}  →  {item['url']}" for item in remotes if item["kind"] == "fetch") or "등록된 원격이 없습니다."
        name = simpledialog.askstring("원격 저장소", f"현재 원격:\n{summary}\n\n추가할 원격 이름 (취소하면 조회만):", parent=self.root)
        if name:
            url = simpledialog.askstring("원격 주소", f"'{name}'의 HTTPS/SSH URL:", parent=self.root)
            if url:
                self._job("원격 추가", lambda: self.repo.remote_add(name, url))

    def github_dialog(self) -> None:
        if self.repo:
            def work() -> str:
                prs = self.repo.github_prs()
                return "PR 없음" if not prs else " | ".join(f"#{pr['number']} {pr['title']}" for pr in prs)
            self._job("GitHub PR 조회", work)

    def agent_info(self) -> None:
        from .cli import agent_guide
        guide = agent_guide()
        messagebox.showinfo("Raidian · AI 에이전트", "GUI는 화면과 키보드로 조작할 수 있습니다.\n"
                            "CLI: raidian --repo 경로 --json status\n"
                            "MCP: raidian-mcp --repo 경로\n\n"
                            "읽기 전용이 기본값이며, MCP 쓰기는 --allow-write 필요.\n"
                            f"병합 기본값: {guide['defaults']['merge']}", parent=self.root)


def main(initial_repo: str = ".") -> None:
    root = tk.Tk()
    Workbench(root, initial_repo)
    root.mainloop()


if __name__ == "__main__":
    main()
