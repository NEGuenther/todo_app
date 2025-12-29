"""Aplicativo de lista de tarefas (Todo) com interface Tkinter.

Este módulo implementa um gerenciador simples de tarefas com persistência em JSON.

Recursos principais
- Adicionar tarefas via campo de texto (Enter adiciona).
- Listar tarefas em uma tabela (Treeview) com status:
    - `pending` (Pendente)
    - `in_progress` (Em andamento)
    - `done` (Feita)
- Alterar status por botões ou duplo clique (ciclo de status).
- Remover tarefa clicando no "×" (coluna de delete) ou via botão Remover.
- Persistir tudo em `tasks.json` ao lado do script.

Formato de persistência (`tasks.json`)
Uma lista de objetos com chaves:
- `id` (int): identificador estável do item.
- `task` (str): texto da tarefa.
- `status` (str): `pending` | `in_progress` | `done`.
- `done` (bool): compatibilidade/atalho; é sincronizado com `status`.
"""

import json
import tkinter as tk
import tkinter.font as tkfont
from pathlib import Path
from tkinter import messagebox, ttk
from typing import Any, Literal, TypedDict

# Persist tasks alongside the script
DATA_FILE = Path(__file__).with_name("tasks.json")


TaskStatus = Literal["pending", "in_progress", "done"]


class Task(TypedDict, total=False):
    """Representa uma tarefa persistida em `tasks.json`."""

    id: int
    task: str
    status: TaskStatus
    done: bool


def load_tasks() -> list[Task]:
    """Carrega tarefas do arquivo JSON.

    Retorna:
        Lista de tarefas. Se o arquivo não existir ou estiver inválido, retorna lista vazia.

    Observação:
        Se o JSON estiver corrompido, exibe um alerta e recria a base (retornando `[]`).
    """
    if DATA_FILE.exists():
        try:
            data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except json.JSONDecodeError:
            messagebox.showwarning("Aviso", "Arquivo de tarefas corrompido. Ele será recriado.")
    return []


def save_tasks(tasks: list[Task]) -> None:
    """Salva a lista de tarefas em JSON (UTF-8) no arquivo de persistência."""
    DATA_FILE.write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8")


class TodoApp(tk.Tk):
    """Janela principal do aplicativo de tarefas."""

    def __init__(self):
        """Inicializa janela, tema, carrega tarefas, constrói UI e renderiza lista."""
        super().__init__()
        self.title("Minhas Tarefas")
        self.geometry("760x640")
        self.resizable(False, False)

        self._apply_theme()

        self.tasks = load_tasks()
        self._next_id = max([t.get("id", 0) for t in self.tasks], default=0) + 1

        self._normalize_tasks()

        self._build_ui()
        self._refresh_list()

    def _normalize_tasks(self) -> None:
        """Normaliza tarefas antigas para o formato atual.

        Compatibilidade:
        - Se não houver `status`, deriva de `done` e garante ambos consistentes.
        - Persiste automaticamente se houver mudanças.
        """
        updated = False
        for task in self.tasks:
            status = task.get("status")
            if not status:
                status = "done" if task.get("done") else "pending"
                task["status"] = status
                task["done"] = status == "done"
                updated = True
        if updated:
            save_tasks(self.tasks)

    # Canvas-based rounded button for a softer look
    class RoundedButton(tk.Canvas):
        """Botão desenhado em Canvas com cantos arredondados.

        Esta classe é usada para ter um botão com aparência mais suave do que o `ttk.Button`.
        Ela desenha um retângulo arredondado (polígono com `smooth=True`) e um texto central.

        Eventos:
        - Hover: altera cor de fundo
        - Press: altera cor de fundo
        - Release: executa `command` se o mouse estiver sobre o widget
        """

        def __init__(self, parent, text, command, bg, fg, hover_bg, active_bg, radius=10, padx=14, pady=8, base_bg=None):
            """Cria o botão arredondado.

            Parâmetros:
                parent: Widget pai.
                text: Texto exibido.
                command: Função chamada ao clicar.
                bg/fg: Cores base do botão e do texto.
                hover_bg/active_bg: Cores no hover e no clique.
                radius: Raio aproximado do arredondamento.
                padx/pady: Espaçamento interno.
                base_bg: Cor de fundo do Canvas (se omitida, usa background da janela).
            """
            self.font = tkfont.Font(family="Segoe UI", size=10, weight="bold")
            text_width = self.font.measure(text)
            text_height = self.font.metrics("linespace")
            width = text_width + padx * 2
            height = text_height + pady * 2
            bg_canvas = base_bg if base_bg else parent.winfo_toplevel().cget("background")
            super().__init__(parent, width=width, height=height, highlightthickness=0, bd=0,
                             bg=bg_canvas)

            self.command = command
            self.normal_bg = bg
            self.hover_bg = hover_bg
            self.active_bg = active_bg
            self.fg = fg
            self.radius = radius

            self._rect = self._round_rect(2, 2, width - 2, height - 2, radius, fill=self.normal_bg, outline="")
            self._text = self.create_text(width / 2, height / 2, text=text, fill=self.fg, font=self.font)

            self.bind("<Enter>", self._on_enter)
            self.bind("<Leave>", self._on_leave)
            self.bind("<ButtonPress-1>", self._on_press)
            self.bind("<ButtonRelease-1>", self._on_release)

        def _round_rect(self, x1: int, y1: int, x2: int, y2: int, r: int, **kwargs: Any) -> int:
            """Desenha um retângulo arredondado retornando o id do polígono no Canvas."""
            points = [
                x1 + r, y1,
                x2 - r, y1,
                x2, y1,
                x2, y1 + r,
                x2, y2 - r,
                x2, y2,
                x2 - r, y2,
                x1 + r, y2,
                x1, y2,
                x1, y2 - r,
                x1, y1 + r,
                x1, y1,
            ]
            return self.create_polygon(points, smooth=True, splinesteps=20, **kwargs)

        def _set_bg(self, color: str) -> None:
            """Atualiza a cor de preenchimento do retângulo."""
            self.itemconfig(self._rect, fill=color)

        def _on_enter(self, _: tk.Event) -> None:
            self._set_bg(self.hover_bg)

        def _on_leave(self, _: tk.Event) -> None:
            self._set_bg(self.normal_bg)

        def _on_press(self, _: tk.Event) -> None:
            self._set_bg(self.active_bg)

        def _on_release(self, event: tk.Event) -> None:
            if self.command and self.winfo_containing(event.x_root, event.y_root) == self:
                self.command()
            self._set_bg(self.hover_bg)

    def _apply_theme(self) -> None:
        """Configura paleta e estilos ttk para um tema escuro."""
        # Dark gray palette
        self.configure(bg="#1a1a1a")  # dark gray background
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        fg = "#e5e5e5"              # light gray text
        fg_muted = "#9ca3af"        # medium gray
        surface = "#2a2a2a"         # dark gray surface
        card = "#3a3a3a"            # medium dark gray card
        accent = "#6b7280"          # gray accent
        accent_hover = "#4b5563"    # darker gray hover
        border = "#1f1f1f"          # very dark border
        cursor = "#d1d5db"          # light gray cursor - very visible

        self.colors = {
            "fg": fg,
            "fg_muted": fg_muted,
            "surface": surface,
            "card": card,
            "accent": accent,
            "accent_hover": accent_hover,
            "accent_active": "#374151",
            "border": border,
            "cursor": cursor,
            "danger": "#7f1d1d",
            "danger_hover": "#991b1b",
            "danger_active": "#b91c1c",
            "muted_hover": "#4a4a4a",
            "muted_active": "#525252",
            "status_pending_bg": "#fed7aa",   # light orange
            "status_pending_fg": "#92400e",
            "status_progress_bg": "#bfdbfe",  # light blue
            "status_progress_fg": "#1d4ed8",
            "status_done_bg": "#bbf7d0",      # light green
            "status_done_fg": "#6b7280",      # fogged text gray
        }

        # General styling
        self.style.configure("TFrame", background=surface)
        self.style.configure("TLabel", background=surface, foreground=fg, font=("Segoe UI", 10))
        self.style.configure("TEntry", fieldbackground=card, foreground=fg, bordercolor=border, 
                           insertcolor=cursor)
        self.style.configure("TButton", background=accent, foreground="white", font=("Segoe UI", 10, "bold"), padding=8)
        self.style.map("TButton",
                       background=[("active", accent_hover)],
                       relief=[("pressed", "sunken"), ("!pressed", "flat")])

        # Treeview styling
        self.style.configure("Treeview",
                             background=card,
                             fieldbackground=card,
                             foreground=fg,
                             bordercolor=border,
                             rowheight=28,
                             font=("Segoe UI", 10))
        self.style.configure("Treeview.Heading",
                             background=surface,
                             foreground=fg,
                             font=("Segoe UI", 10, "bold"))
        self.style.map("Treeview",
                       background=[("selected", accent)],
                       foreground=[("selected", "white")])
        self.style.layout("Treeview", [
            ("Treeview.treearea", {"sticky": "nswe"})
        ])

        # Tag styles for statuses
        self.style.configure("Treeview.Pending", background=self.colors["status_pending_bg"],
                             foreground=self.colors["status_pending_fg"])
        self.style.configure("Treeview.Progress", background=self.colors["status_progress_bg"],
                             foreground=self.colors["status_progress_fg"])
        self.style.configure("Treeview.Done", background=self.colors["status_done_bg"],
                             foreground=self.colors["status_done_fg"])

        # Scrollbar styling
        self.style.configure("Vertical.TScrollbar",
                             background=surface,
                             troughcolor=card,
                             arrowcolor=fg_muted,
                             bordercolor=border)
        self.style.map("Vertical.TScrollbar",
                       background=[("active", accent_hover)])

    def _build_ui(self) -> None:
        """Constrói todos os widgets da janela (entrada, preview, lista, ações)."""
        main = ttk.Frame(self, padding=16)
        main.pack(fill=tk.BOTH, expand=True)

        # Input + botão adicionar
        top = ttk.Frame(main)
        top.pack(fill=tk.X, pady=(0, 12))

        TodoButton = self.RoundedButton
        palette = self.colors
        
        ttk.Label(top, text="Nova tarefa:").pack(side=tk.LEFT)
        self.entry = ttk.Entry(top)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8)
        self.entry.bind("<Return>", lambda _: self.add_task())
        TodoButton(top, text="Adicionar", command=self.add_task, bg=palette["accent"], fg="white",
                   hover_bg=palette["accent_hover"], active_bg=palette["accent_active"],
                   base_bg=palette["surface"]).pack(side=tk.LEFT, padx=(6, 0))

        # Preview area to show texto completo da tarefa selecionada
        self.preview = tk.Text(main, height=4, wrap="word", bg=palette["card"], fg=palette["fg"],
                       insertbackground=palette["cursor"], relief="flat", padx=10, pady=8)
        self.preview.config(state="disabled")
        self.preview.pack(fill=tk.X, pady=(8, 12))

        # Lista de tarefas
        columns = ("task", "status", "delete")
        tree_frame = ttk.Frame(main)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=18)
        self.tree.heading("task", text="Tarefa")
        self.tree.heading("status", text="Status")
        self.tree.heading("delete", text="")
        self.tree.column("task", width=460, anchor=tk.W, stretch=True)
        self.tree.column("status", width=120, anchor=tk.CENTER, stretch=False)
        self.tree.column("delete", width=50, anchor=tk.CENTER, stretch=False)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.bind("<Double-1>", lambda _: self.toggle_selected())
        self.tree.bind("<<TreeviewSelect>>", self._update_preview)
        self.tree.bind("<Button-1>", self._on_tree_click)

        # Color tags for statuses
        self.tree.tag_configure("pending", background=palette["status_pending_bg"],
                                foreground=palette["status_pending_fg"])
        self.tree.tag_configure("in_progress", background=palette["status_progress_bg"],
                                foreground=palette["status_progress_fg"])
        self.tree.tag_configure("done", background=palette["status_done_bg"],
                                foreground=palette["status_done_fg"])

        scrollbar_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Barra de ações
        actions = ttk.Frame(main)
        actions.pack(fill=tk.X, pady=(12, 0))

        TodoButton(actions, text="Concluir", command=lambda: self.set_status("done"), bg=palette["accent"], fg="white",
               hover_bg=palette["accent_hover"], active_bg=palette["accent_active"],
               base_bg=palette["surface"]).pack(side=tk.LEFT)
        TodoButton(actions, text="Em andamento", command=lambda: self.set_status("in_progress"), bg=palette["card"], fg=palette["fg"],
               hover_bg=palette["muted_hover"], active_bg=palette["muted_active"],
               base_bg=palette["surface"]).pack(side=tk.LEFT, padx=8)
        TodoButton(actions, text="Reabrir", command=lambda: self.set_status("pending"), bg=palette["card"], fg=palette["fg"],
               hover_bg=palette["muted_hover"], active_bg=palette["muted_active"],
               base_bg=palette["surface"]).pack(side=tk.LEFT, padx=(0, 8))
        TodoButton(actions, text="Remover", command=self.remove_selected, bg=palette["danger"], fg="white",
                   hover_bg=palette["danger_hover"], active_bg=palette["danger_active"],
                   base_bg=palette["surface"]).pack(side=tk.LEFT)

    def _refresh_list(self) -> None:
        """Re-renderiza o Treeview com base em `self.tasks` e atualiza o preview."""
        self.tree.delete(*self.tree.get_children())
        for task in self.tasks:
            status_val = task.get("status", "pending")
            task["done"] = status_val == "done"

            display = task["task"].strip() or "(sem título)"
            if status_val == "pending":
                status_label = "Pendente"
                tags = ("pending",)
            elif status_val == "in_progress":
                status_label = "Em andamento"
                tags = ("in_progress",)
            else:
                status_label = "Feita"
                tags = ("done",)

            self.tree.insert("", tk.END, iid=str(task["id"]), values=(display, status_label, "×"), tags=tags)

        # Update preview text with current selection
        self._update_preview()

    def _on_tree_click(self, event: tk.Event) -> None:
        """Handler de clique no Treeview.

        Se clicar na coluna de delete ("×"), remove a tarefa imediatamente.
        """
        region = self.tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            if column == "#3":  # Coluna delete (task=#1, status=#2, delete=#3)
                item = self.tree.identify_row(event.y)
                if item:
                    task_id = int(item)
                    self.tasks = [t for t in self.tasks if t["id"] != task_id]
                    save_tasks(self.tasks)
                    self._refresh_list()

    def _selection_ids(self) -> list[int]:
        """Retorna os ids selecionados no Treeview como `int`."""
        return [int(item) for item in self.tree.selection()]

    def _update_preview(self, *_: Any) -> None:
        """Atualiza a área de preview com o texto completo da primeira tarefa selecionada."""
        selection = self._selection_ids()
        text = ""
        if selection:
            # show first selected task's text
            task_id = selection[0]
            for task in self.tasks:
                if task["id"] == task_id:
                    text = task.get("task", "").strip()
                    break
        self.preview.config(state="normal")
        self.preview.delete("1.0", tk.END)
        if text:
            self.preview.insert("1.0", text)
        self.preview.config(state="disabled")

    def add_task(self) -> None:
        """Cria uma nova tarefa com status `pending` usando o texto do campo de entrada."""
        text = self.entry.get().strip()
        if not text:
            messagebox.showinfo("Aviso", "Digite uma tarefa antes de adicionar.")
            return
        self.tasks.append({"id": self._next_id, "task": text, "done": False, "status": "pending"})
        self._next_id += 1
        save_tasks(self.tasks)
        self.entry.delete(0, tk.END)
        self._refresh_list()

    def set_status(self, status: TaskStatus) -> None:
        """Define o status para todas as tarefas selecionadas.

        Parâmetros:
            status: Um de `pending`, `in_progress`, `done`.
        """
        ids = self._selection_ids()
        if not ids:
            return
        valid = {"pending", "in_progress", "done"}
        if status not in valid:
            return
        for task in self.tasks:
            if task["id"] in ids:
                task["status"] = status
                task["done"] = status == "done"
        save_tasks(self.tasks)
        self._refresh_list()

    def toggle_selected(self) -> None:
        """Alterna o status da seleção em ciclo: pending → in_progress → done → pending."""
        ids = self._selection_ids()
        if not ids:
            return
        for task in self.tasks:
            if task["id"] in ids:
                current = task.get("status", "pending")
                if current == "pending":
                    task["status"] = "in_progress"
                elif current == "in_progress":
                    task["status"] = "done"
                else:
                    task["status"] = "pending"
                task["done"] = task["status"] == "done"
        save_tasks(self.tasks)
        self._refresh_list()

    def remove_selected(self) -> None:
        """Remove todas as tarefas selecionadas (com persistência imediata)."""
        ids = set(self._selection_ids())
        if not ids:
            return
        self.tasks = [t for t in self.tasks if t["id"] not in ids]
        save_tasks(self.tasks)
        self._refresh_list()


if __name__ == "__main__":
    app = TodoApp()
    app.mainloop()
