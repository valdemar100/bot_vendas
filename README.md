# 🤖 Bot de Vendas para Telegram

Este é um projeto de um bot para Telegram desenvolvido em Python, projetado para simular as funcionalidades básicas de uma loja virtual, como visualização de produtos, adição ao carrinho e finalização de compra (simulada).

## ✨ Funcionalidades

* **Listagem de Produtos**: Exibe os produtos disponíveis com nome, preço e ID.
* **Detalhes do Produto**: Mostra informações detalhadas de um produto específico, incluindo descrição e imagem (se disponível).
* **Carrinho de Compras**:
    * Adicionar produtos ao carrinho.
    * Remover produtos do carrinho.
    * Visualizar os itens no carrinho e o total.
* **Finalização de Compra (Simulada)**: Permite ao usuário "finalizar" o pedido, que limpa o carrinho e exibe um resumo. Nenhum processamento de pagamento real é implementado.
* **Interface Interativa**: Utiliza botões inline para facilitar a navegação e interação do usuário.
* **Persistência de Dados**: Armazena os dados dos produtos em um banco de dados SQLite.

## 🛠️ Tecnologias Utilizadas

* **Python 3.x**
* **python-telegram-bot**: Biblioteca para interagir com a API do Telegram.
* **SQLite3**: Banco de dados leve e baseado em arquivo para armazenar informações dos produtos.
* **python-dotenv** (opcional): Para gerenciar variáveis de ambiente (como o token do bot).

## 📋 Pré-requisitos

* Python 3.7 ou superior instalado.
* Conta no Telegram.
* Um token de bot do Telegram (obtido através do @BotFather).

## ⚙️ Configuração e Instalação

1.  **Clone o Repositório (ou baixe os arquivos):**
    ```bash
    git clone [https://github.com/valdemar100/bot_vendas.git](https://github.com/valdemar100/bot_vendas.git)
    cd bot_vendas 
    ```

2.  **Crie e Ative um Ambiente Virtual (Recomendado):**
    ```bash
    python -m venv venv
    # No Windows
    venv\Scripts\activate
    # No macOS/Linux
    source venv/bin/activate
    ```

3.  **Instale as Dependências:**
    Crie um arquivo `requirements.txt` com o seguinte conteúdo:
    ```txt
    python-telegram-bot
    python-dotenv
    ```
    E então instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure o Token do Bot:**
    * **Opção 1 (Recomendado - Arquivo `.env`):**
        Crie um arquivo chamado `.env` na raiz do projeto e adicione a seguinte linha, substituindo pelo seu token real:
        ```
        TELEGRAM_BOT_TOKEN="SEU_TOKEN_AQUI"
        ```
    * **Opção 2 (Diretamente no Código - Menos Seguro):**
        Abra o arquivo principal do bot (ex: `vendas.py` ou `main.py`) e substitua o valor da variável `TELEGRAM_BOT_TOKEN` pelo seu token.

## ▶️ Como Executar o Bot

1.  Certifique-se de que seu ambiente virtual está ativado e as dependências estão instaladas.
2.  Navegue até a pasta raiz do projeto no seu terminal.
3.  Execute o script principal do bot:
    ```bash
    python nome_do_seu_arquivo_principal.py
    ```
    (Por exemplo: `python vendas.py`)

4.  O bot deverá iniciar e exibir uma mensagem no console indicando que está rodando.
5.  Abra o Telegram, procure pelo username do seu bot e comece a interagir!

## 🚀 Uso (Comandos do Bot)

Após iniciar uma conversa com o bot no Telegram, você pode usar os seguintes comandos:

* `/start` - Inicia a conversa e exibe o menu principal.
* `/produtos` - Lista todos os produtos disponíveis na loja.
* `/ver <ID_DO_PRODUTO>` - Mostra detalhes de um produto específico (ex: `/ver 1`).
* `/adicionar <ID_DO_PRODUTO>` - Adiciona o produto especificado ao seu carrinho.
* `/remover <ID_DO_PRODUTO>` - Remove uma unidade do produto especificado do seu carrinho.
* `/carrinho` - Exibe os itens atualmente no seu carrinho e o valor total.
* `/finalizar` - Simula a finalização do seu pedido (limpa o carrinho).
* `/help` - Mostra uma mensagem de ajuda com os comandos disponíveis.

O bot também utiliza botões inline para uma navegação mais intuitiva pelas funcionalidades.

## 🔮 Próximos Passos (Possíveis Melhorias)

* [ ] Implementar persistência do carrinho de compras (atualmente em memória da sessão do usuário).
* [ ] Adicionar categorias de produtos.
* [ ] Funcionalidade de busca de produtos.
* [ ] Painel administrativo simples para gerenciar produtos no banco de dados.
* [ ] Suporte a diferentes idiomas.
* [ ] Integração com um sistema de pagamento real (Stripe, Mercado Pago, etc.) - **Apenas para fins de estudo e com as devidas precauções.**

## 🤝 Contribuições

Contribuições são bem-vindas! Se você tiver sugestões, correções de bugs ou novas funcionalidades, sinta-se à vontade para abrir uma *Issue* ou enviar um *Pull Request*.

## 📄 Licença

Este projeto é distribuído sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.
..

---
