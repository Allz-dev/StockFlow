import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import sqlite3

# --- CONFIGURAÇÃO VISUAL ---
ctk.set_appearance_mode("dark")
azul_principal = "#3a7ebf"
hover_azul = "#559de6"
fundo_principal = "#1e1e1e"
sidebar_cor = "#252525"
cards_cor = "#2b2b2b"

# --- BANCO DE DADOS ---
def init_db():
    conn = sqlite3.connect('estoque.db')
    cursor = conn.cursor()
    # Tabela de Usuários
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        usuario TEXT UNIQUE,
                        senha TEXT)''')
    
    # Tabela de Produtos
    cursor.execute('''CREATE TABLE IF NOT EXISTS produtos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT,
                        categoria TEXT,
                        preco REAL,
                        quantidade INTEGER,
                        observacao TEXT)''')
    
    # Tabela de Movimentações
    cursor.execute('''CREATE TABLE IF NOT EXISTS movimentacoes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        produto_id INTEGER,
                        tipo TEXT,
                        quantidade INTEGER,
                        data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY(produto_id) REFERENCES produtos(id))''')
    
    # Criar usuário padrão se não existir
    try:
        cursor.execute("INSERT INTO usuarios (usuario, senha) VALUES (?, ?)", ('admin', '123'))
    except sqlite3.IntegrityError:
        pass
        
    conn.commit()
    conn.close()

# --- CLASSE PRINCIPAL DO APP ---
class StockFlowApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("StockFlow ERP - Gerenciamento de Estoque")
        self.geometry("1100x650")
        self.configure(fg_color=fundo_principal)

        init_db()
        self.tela_login()

    def limpar_tela(self):
        for widget in self.winfo_children():
            widget.destroy()

    # --- TELA DE LOGIN ---
    def tela_login(self):
        self.limpar_tela()
        
        frame_login = ctk.CTkFrame(self, width=350, height=450, fg_color=sidebar_cor)
        frame_login.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(frame_login, text="StockFlow", font=("Arial Bold", 28), text_color=azul_principal).pack(pady=(40, 5))
        ctk.CTkLabel(frame_login, text="Faça login para continuar", font=("Arial", 14), text_color="gray").pack(pady=(0, 30))

        self.ent_user = ctk.CTkEntry(frame_login, placeholder_text="Usuário", width=250, height=40)
        self.ent_user.pack(pady=10)

        self.ent_pass = ctk.CTkEntry(frame_login, placeholder_text="Senha", width=250, height=40, show="*")
        self.ent_pass.pack(pady=10)

        btn_login = ctk.CTkButton(frame_login, text="Entrar", width=250, height=40, 
                                  fg_color=azul_principal, hover_color=hover_azul, command=self.verificar_login)
        btn_login.pack(pady=30)

    def verificar_login(self):
        user = self.ent_user.get()
        pas = self.ent_pass.get()

        conn = sqlite3.connect('estoque.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE usuario = ? AND senha = ?", (user, pas))
        res = cursor.fetchone()
        conn.close()

        if res:
            self.montar_layout_principal()
        else:
            messagebox.showerror("Erro", "Usuário ou senha inválidos!")

    # --- LAYOUT PRINCIPAL (DASHBOARD + MENU) ---
    def montar_layout_principal(self):
        self.limpar_tela()

        # Menu Lateral
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color=sidebar_cor)
        self.sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(self.sidebar, text="STOCKFLOW", font=("Arial Bold", 20), text_color=azul_principal).pack(pady=30)

        btns = [
            ("Dashboard", self.show_dashboard),
            ("Produtos", self.show_produtos),
            ("Movimentações", self.show_movimentacoes),
            ("Relatórios", self.show_relatorios)
        ]

        for texto, comando in btns:
            btn = ctk.CTkButton(self.sidebar, text=texto, fg_color="transparent", text_color="white",
                                hover_color=cards_cor, anchor="w", height=45, command=comando)
            btn.pack(fill="x", padx=10, pady=5)

        # Conteúdo Direita
        self.container = ctk.CTkFrame(self, fg_color=fundo_principal)
        self.container.pack(side="right", expand=True, fill="both", padx=20, pady=20)

        self.show_dashboard()

    # --- ABA: DASHBOARD ---
    def show_dashboard(self):
        for w in self.container.winfo_children(): w.destroy()

        ctk.CTkLabel(self.container, text="Dashboard Geral", font=("Arial Bold", 24)).pack(anchor="w", pady=(0, 20))

        # Grid de cards
        frame_cards = ctk.CTkFrame(self.container, fg_color="transparent")
        frame_cards.pack(fill="x")

        # Lógica de dados
        conn = sqlite3.connect('estoque.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM produtos")
        total_p = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM produtos WHERE quantidade <= 5")
        baixo_e = cursor.fetchone()[0]

        cursor.execute("SELECT SUM(preco * quantidade) FROM produtos")
        valor_t = cursor.fetchone()[0] or 0
        conn.close()

        self.criar_card(frame_cards, "Total Produtos", str(total_p), 0)
        self.criar_card(frame_cards, "Estoque Baixo (<=5)", str(baixo_e), 1)
        self.criar_card(frame_cards, "Valor em Estoque", f"R$ {valor_t:.2f}", 2)

    def criar_card(self, master, titulo, valor, col):
        card = ctk.CTkFrame(master, width=250, height=120, fg_color=cards_cor)
        card.grid(row=0, column=col, padx=10, pady=10)
        card.grid_propagate(False)

        ctk.CTkLabel(card, text=titulo, font=("Arial", 14), text_color="gray").pack(pady=(15, 5))
        ctk.CTkLabel(card, text=valor, font=("Arial Bold", 22)).pack()

    # --- ABA: PRODUTOS ---
    def show_produtos(self):
        for w in self.container.winfo_children(): w.destroy()

        # Título e Formulário simples no topo
        header = ctk.CTkFrame(self.container, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(header, text="Gerenciamento de Produtos", font=("Arial Bold", 22)).pack(side="left")

        form = ctk.CTkFrame(self.container, fg_color=cards_cor)
        form.pack(fill="x", pady=10, padx=5)

        # Entradas
        self.ent_nome = ctk.CTkEntry(form, placeholder_text="nome", width=150)
        self.ent_nome.grid(row=0, column=0, padx=10, pady=15)
        self.ent_cat = ctk.CTkEntry(form, placeholder_text="categoria", width=120)
        self.ent_cat.grid(row=0, column=1, padx=10)
        self.ent_preco = ctk.CTkEntry(form, placeholder_text="preço (ex: 10,50)", width=100)
        self.ent_preco.grid(row=0, column=2, padx=10)
        self.ent_qtd = ctk.CTkEntry(form, placeholder_text="qtd", width=80)
        self.ent_qtd.grid(row=0, column=3, padx=10)
        self.ent_obs = ctk.CTkEntry(form, placeholder_text="obs", width=150)
        self.ent_obs.grid(row=0, column=4, padx=10)

        btn_add = ctk.CTkButton(form, text="Cadastrar", width=100, fg_color="green", command=self.cadastrar_produto)
        btn_add.grid(row=0, column=5, padx=10)

        # Tabela (Treeview)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=cards_cor, foreground="white", fieldbackground=cards_cor, borderwidth=0)
        style.map("Treeview", background=[('selected', azul_principal)])

        self.tree = ttk.Treeview(self.container, columns=("ID", "Nome", "Cat", "Preço", "Qtd", "Obs"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nome", text="Nome")
        self.tree.heading("Cat", text="Categoria")
        self.tree.heading("Preço", text="Preço")
        self.tree.heading("Qtd", text="Qtd")
        self.tree.heading("Obs", text="Observação")
        
        self.tree.column("ID", width=40)
        self.tree.column("Qtd", width=60)
        self.tree.pack(expand=True, fill="both", pady=10)

        # Botões de Ação
        btn_box = ctk.CTkFrame(self.container, fg_color="transparent")
        btn_box.pack(fill="x")
        ctk.CTkButton(btn_box, text="Remover Selecionado", fg_color="#c0392b", command=self.remover_produto).pack(side="left", padx=5)
        ctk.CTkButton(btn_box, text="Editar Selecionado", command=self.preparar_edicao).pack(side="left", padx=5)

        self.atualizar_tabela_produtos()

    def cadastrar_produto(self):
        nome = self.ent_nome.get().lower()
        cat = self.ent_cat.get().lower()
        preco = self.ent_preco.get().replace(',', '.')
        qtd = self.ent_qtd.get()
        obs = self.ent_obs.get().lower()

        if not (nome and cat and preco and qtd):
            messagebox.showwarning("Aviso", "Preencha todos os campos obrigatórios!")
            return

        try:
            conn = sqlite3.connect('estoque.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO produtos (nome, categoria, preco, quantidade, observacao) VALUES (?,?,?,?,?)",
                           (nome, cat, float(preco), int(qtd), obs))
            conn.commit()
            conn.close()
            self.atualizar_tabela_produtos()
            # Limpar campos
            self.ent_nome.delete(0, 'end'); self.ent_preco.delete(0, 'end'); self.ent_qtd.delete(0, 'end')
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao cadastrar: {e}")

    def atualizar_tabela_produtos(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        conn = sqlite3.connect('estoque.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM produtos")
        for row in cursor.fetchall():
            tag = "baixo" if row[4] <= 5 else ""
            self.tree.insert("", "end", values=row, tags=(tag,))
        conn.close()
        self.tree.tag_configure("baixo", foreground="#e74c3c")

    def remover_produto(self):
        selected = self.tree.selection()
        if not selected: return
        
        item_id = self.tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Confirmar", "Deseja excluir este produto?"):
            conn = sqlite3.connect('estoque.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM produtos WHERE id = ?", (item_id,))
            conn.commit()
            conn.close()
            self.atualizar_tabela_produtos()

    def preparar_edicao(self):
        selected = self.tree.selection()
        if not selected: return
        
        # Simplesmente carrega nos campos lá em cima para "facilitar"
        valores = self.tree.item(selected[0])['values']
        self.remover_produto() # Remove o antigo e o aluno clica em cadastrar o novo (técnica simples)
        self.ent_nome.insert(0, valores[1])
        self.ent_cat.insert(0, valores[2])
        self.ent_preco.insert(0, valores[3])
        self.ent_qtd.insert(0, valores[4])

    # --- ABA: MOVIMENTAÇÕES ---
    def show_movimentacoes(self):
        for w in self.container.winfo_children(): w.destroy()

        ctk.CTkLabel(self.container, text="Movimentação de Estoque", font=("Arial Bold", 22)).pack(anchor="w", pady=(0, 20))

        frame_mov = ctk.CTkFrame(self.container, fg_color=cards_cor)
        frame_mov.pack(fill="x", pady=10)

        # Buscar nomes de produtos para o menu
        conn = sqlite3.connect('estoque.db')
        cursor = conn.cursor()
        cursor.execute("SELECT nome FROM produtos")
        prods = [p[0] for p in cursor.fetchall()]
        conn.close()

        if not prods: prods = ["Cadastre um produto primeiro"]

        self.combo_prod = ctk.CTkComboBox(frame_mov, values=prods, width=200)
        self.combo_prod.grid(row=0, column=0, padx=20, pady=20)

        self.ent_qtd_mov = ctk.CTkEntry(frame_mov, placeholder_text="quantidade", width=100)
        self.ent_qtd_mov.grid(row=0, column=1, padx=10)

        ctk.CTkButton(frame_mov, text="Entrada (+)", fg_color="#27ae60", width=100, 
                      command=lambda: self.registrar_mov("entrada")).grid(row=0, column=2, padx=10)
        
        ctk.CTkButton(frame_mov, text="Saída (-)", fg_color="#c0392b", width=100, 
                      command=lambda: self.registrar_mov("saida")).grid(row=0, column=3, padx=10)

        # Histórico simples
        ctk.CTkLabel(self.container, text="Histórico Recente", font=("Arial Bold", 16)).pack(anchor="w", pady=(20, 5))
        self.tree_mov = ttk.Treeview(self.container, columns=("ID", "Produto", "Tipo", "Qtd", "Data"), show="headings")
        for col in ("ID", "Produto", "Tipo", "Qtd", "Data"): self.tree_mov.heading(col, text=col)
        self.tree_mov.pack(expand=True, fill="both")
        self.atualizar_tabela_mov()

    def registrar_mov(self, tipo):
        nome_prod = self.combo_prod.get()
        try:
            qtd_mov = int(self.ent_qtd_mov.get())
        except:
            messagebox.showerror("Erro", "Quantidade inválida")
            return

        conn = sqlite3.connect('estoque.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, quantidade FROM produtos WHERE nome = ?", (nome_prod,))
        res = cursor.fetchone()
        
        if res:
            p_id, p_qtd_atual = res
            nova_qtd = p_qtd_atual + qtd_mov if tipo == "entrada" else p_qtd_atual - qtd_mov

            if nova_qtd < 0:
                messagebox.showwarning("Aviso", "Estoque insuficiente para essa saída!")
                conn.close()
                return

            cursor.execute("UPDATE produtos SET quantidade = ? WHERE id = ?", (nova_qtd, p_id))
            cursor.execute("INSERT INTO movimentacoes (produto_id, tipo, quantidade) VALUES (?,?,?)", (p_id, tipo, qtd_mov))
            conn.commit()
        
        conn.close()
        self.atualizar_tabela_mov()
        self.ent_qtd_mov.delete(0, 'end')

    def atualizar_tabela_mov(self):
        for item in self.tree_mov.get_children(): self.tree_mov.delete(item)
        conn = sqlite3.connect('estoque.db')
        cursor = conn.cursor()
        cursor.execute('''SELECT m.id, p.nome, m.tipo, m.quantidade, m.data 
                          FROM movimentacoes m JOIN produtos p ON m.produto_id = p.id 
                          ORDER BY m.id DESC LIMIT 15''')
        for row in cursor.fetchall(): self.tree_mov.insert("", "end", values=row)
        conn.close()

    # --- ABA: RELATÓRIOS ---
    def show_relatorios(self):
        for w in self.container.winfo_children(): w.destroy()
        
        ctk.CTkLabel(self.container, text="Relatórios Gerenciais", font=("Arial Bold", 24)).pack(anchor="w", pady=(0, 20))
        
        frame_rel = ctk.CTkFrame(self.container, fg_color=cards_cor)
        frame_rel.pack(fill="both", expand=True, padx=10, pady=10)

        conn = sqlite3.connect('estoque.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM produtos")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT nome, quantidade FROM produtos WHERE quantidade <= 5")
        baixos = cursor.fetchall()
        
        cursor.execute("SELECT SUM(preco * quantidade) FROM produtos")
        valor_total = cursor.fetchone()[0] or 0
        conn.close()

        txt = f"""
        RESUMO DO SISTEMA
        ---------------------------------------
        Total de itens únicos: {total}
        Valor Total em Mercadoria: R$ {valor_total:.2f}
        
        PRODUTOS COM ESTOQUE CRÍTICO (5 ou menos):
        """
        for b in baixos:
            txt += f"\n- {b[0].upper()}: {b[1]} unidades"

        label_rel = ctk.CTkLabel(frame_rel, text=txt, font=("Courier New", 16), justify="left", anchor="nw")
        label_rel.pack(padx=20, pady=20, fill="both", expand=True)

# --- INICIALIZAÇÃO ---
if __name__ == "__main__":
    app = StockFlowApp()
    app.mainloop()