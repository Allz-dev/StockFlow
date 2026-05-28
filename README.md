# StockFlow ERP - Sistema de Gerenciamento de Estoque

## Sobre o Projeto
Este é um mini ERP desenvolvido como projeto acadêmico para a disciplina de Programação. O objetivo é oferecer uma ferramenta simples, porém visualmente moderna, para que qualquer pequena loja possa gerenciar seus produtos e movimentações de entrada/saída.

## Tecnologias Utilizadas
- **Python 3.10+**
- **CustomTkinter**: Para uma interface com design moderno e suporte a Dark Mode.
- **SQLite**: Banco de dados local e leve, que não precisa de instalação externa.
- **ttk.Treeview**: Para exibição organizada de dados em tabelas.

## Funcionalidades
- **Login Seguro**: Acesso restrito (padrão: admin / 123).
- **Dashboard**: Visualização rápida do total de produtos, valor do estoque e alertas críticos.
- **Cadastro de Produtos**: Gerenciamento completo (nome, categoria, preço, quantidade).
- **Controle de Movimentação**: Registro de entradas e saídas com atualização automática do saldo.
- **Relatórios**: Resumo gerencial de estoque baixo e valores totais.

## Como Executar
1. Certifique-se de ter o Python instalado.
2. Instale a biblioteca necessária:
   ```bash
   pip install customtkinter
