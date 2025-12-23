import logging
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
import os
from dotenv import load_dotenv
from typing import Optional

# Carrega variáveis de ambiente, se existir o arquivo .env
load_dotenv()

# --- Configurações ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DATABASE_FILE = "loja_bot.db"

# Configuração de logging básico
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# --- Funções do Banco de Dados ---
def initialize_database():
    """Cria a tabela de produtos no banco de dados se ela não existir."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        preco REAL NOT NULL,
        descricao TEXT,
        imagem TEXT
    )
    """)
    conn.commit()
    conn.close()
    logger.info("Banco de dados verificado/criado.")

def populate_initial_data():
    """Insere dados iniciais na tabela de produtos se ela estiver vazia."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        initial_products = [
            ("Camiseta Tech", 59.90, "Camiseta de algodão com estampa de tecnologia.", "https://placehold.co/600x400/007bff/white?text=Camiseta"),
            ("Caneca Dev", 35.00, "Caneca de cerâmica para seu café ou chá.", "https://placehold.co/600x400/28a745/white?text=Caneca"),
            ("Boné Hacker", 45.00, "Boné estiloso para todas as ocasiões.", "https://placehold.co/600x400/ffc107/black?text=Boné"),
            ("Caderno Coder", 69.90, "Caderno para suas anotações e diagramas.", "https://placehold.co/600x400/dc3545/white?text=Caderno"),
        ]
        cursor.executemany("INSERT INTO products (nome, preco, descricao, imagem) VALUES (?, ?, ?, ?)", initial_products)
        conn.commit()
        logger.info(f"{len(initial_products)} produtos iniciais adicionados.")
    conn.close()

def fetch_all_products() -> list:
    """Retorna todos os produtos do banco de dados."""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, preco, descricao, imagem FROM products")
    products = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return products

def fetch_product_by_id(product_id: int) -> Optional[dict]:
    """Retorna um produto específico pelo ID."""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, preco, descricao, imagem FROM products WHERE id = ?", (product_id,))
    product_data = cursor.fetchone()
    conn.close()
    return dict(product_data) if product_data else None

# --- Lógica do Carrinho ---
def get_cart(context: ContextTypes.DEFAULT_TYPE) -> dict:
    """Retorna o carrinho do usuário, criando um se não existir."""
    context.user_data.setdefault('cart', {})
    return context.user_data['cart']

# --- Comandos do Bot ---
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para o comando /start."""
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("🛍️ Ver Produtos", callback_data="show_products")],
        [InlineKeyboardButton("🛒 Meu Carrinho", callback_data="show_cart")],
        [InlineKeyboardButton("💝 Fazer Doação", callback_data="show_donation")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_html(
        rf"Olá {user.mention_html()}! Bem-vindo(a) à Loja Virtual. Use os botões ou comandos.",
        reply_markup=reply_markup,
    )

async def products_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para o comando /produtos e callback 'show_products'."""
    products = fetch_all_products()
    if not products:
        message_text = "Nenhum produto disponível no momento."
        reply_markup = None
    else:
        message_text = "🛍️ **Nossos Produtos:**\n\n"
        buttons = []
        for product in products:
            message_text += f"🆔 `{product['id']}`: **{product['nome']}** - R$ {product['preco']:.2f}\n"
            buttons.append(
                InlineKeyboardButton(f"{product['nome']} (R$ {product['preco']:.2f})", callback_data=f"view_product_{product['id']}")
            )
        
        keyboard = [buttons[i:i + 2] for i in range(0, len(buttons), 2)] # Botões em 2 colunas
        keyboard.append([InlineKeyboardButton("🛒 Ver Carrinho", callback_data="show_cart")])
        reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        try:
            await update.callback_query.message.edit_text(message_text, parse_mode="Markdown", reply_markup=reply_markup)
            await update.callback_query.answer()
        except Exception as e:
            logger.warning(f"Erro ao editar mensagem de produtos: {e}")
            try:
                await update.callback_query.answer()
            except:
                pass
    else:
        await update.message.reply_text(message_text, parse_mode="Markdown", reply_markup=reply_markup)

async def add_to_cart_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para o comando /adicionar."""
    try:
        product_id = int(context.args[0])
    except (IndexError, ValueError):
        await update.message.reply_text("Uso: `/adicionar <ID_DO_PRODUTO>` (ex: `/adicionar 1`)")
        return

    product_data = fetch_product_by_id(product_id)
    if not product_data:
        await update.message.reply_text(f"Produto com ID {product_id} não encontrado.")
        return

    cart = get_cart(context)
    cart[product_id] = cart.get(product_id, 0) + 1
    
    await update.message.reply_text(f"✅ '{product_data['nome']}' adicionado ao carrinho.")

async def remove_from_cart_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para o comando /remover."""
    try:
        product_id = int(context.args[0])
    except (IndexError, ValueError):
        await update.message.reply_text("Uso: `/remover <ID_DO_PRODUTO>` (ex: `/remover 1`)")
        return

    cart = get_cart(context)
    product_data = fetch_product_by_id(product_id)

    if not product_data:
        await update.message.reply_text(f"Produto com ID {product_id} não existe na loja.")
        return
    
    if product_id not in cart or cart[product_id] == 0:
        await update.message.reply_text(f"'{product_data['nome']}' não está no seu carrinho.")
        return

    cart[product_id] -= 1
    if cart[product_id] == 0:
        del cart[product_id]
        await update.message.reply_text(f"🗑️ '{product_data['nome']}' removido completamente do carrinho.")
    else:
        await update.message.reply_text(f"➖ Uma unidade de '{product_data['nome']}' removida. Restantes: {cart[product_id]}.")

async def cart_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para o comando /carrinho e callback 'show_cart'."""
    cart = get_cart(context)
    if not cart:
        message_text = "Seu carrinho está vazio. 🛒"
        keyboard = [[InlineKeyboardButton("🛍️ Ver Produtos", callback_data="show_products")]]
    else:
        message_text = "🛒 **Seu Carrinho:**\n\n"
        total_price = 0
        item_buttons = []
        for product_id, quantity in cart.items():
            product_data = fetch_product_by_id(product_id)
            if product_data:
                subtotal = product_data["preco"] * quantity
                total_price += subtotal
                message_text += f"🔹 {product_data['nome']} (x{quantity}) - R$ {subtotal:.2f}\n"
                item_buttons.append(InlineKeyboardButton(f"➖ Remover 1 {product_data['nome']}", callback_data=f"remove_one_{product_id}"))
            else: # Caso o produto tenha sido removido do DB mas ainda esteja no carrinho de alguém
                message_text += f"🔹 Produto ID {product_id} (indisponível) (x{quantity})\n"
        
        message_text += f"\n💰 **Total: R$ {total_price:.2f}**"
        
        keyboard = [[btn] for btn in item_buttons] # Cada botão de remoção em uma linha
        keyboard.append([InlineKeyboardButton("🛍️ Continuar Comprando", callback_data="show_products")])
        if cart:
             keyboard.append([InlineKeyboardButton("✅ Finalizar Compra", callback_data="checkout_cart")])
        keyboard.append([InlineKeyboardButton("💝 Fazer Doação", callback_data="show_donation")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.callback_query:
        try:
            await update.callback_query.message.edit_text(message_text, parse_mode="Markdown", reply_markup=reply_markup)
            await update.callback_query.answer()
        except Exception as e:
            logger.warning(f"Erro ao editar mensagem do carrinho: {e}")
            try:
                await update.callback_query.answer()
            except:
                pass
    else:
        await update.message.reply_text(message_text, parse_mode="Markdown", reply_markup=reply_markup)

async def checkout_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para o comando /finalizar e callback 'checkout_cart'."""
    cart = get_cart(context)
    if not cart:
        message_text = "Seu carrinho está vazio para finalizar."
        keyboard = [[InlineKeyboardButton("🛍️ Ver Produtos", callback_data="show_products")]]
    else:
        total_price = 0
        order_summary = "📄 **Resumo do Pedido:**\n"
        for product_id, quantity in cart.items():
            product_data = fetch_product_by_id(product_id)
            if product_data:
                subtotal = product_data["preco"] * quantity
                total_price += subtotal
                order_summary += f"  - {product_data['nome']} (x{quantity}) - R$ {subtotal:.2f}\n"
        order_summary += f"\n💸 **Total a Pagar: R$ {total_price:.2f}**\n\n"

        message_text = (
            f"{order_summary}"
            "Obrigado por comprar! 🎉\n"
            "(Simulação de pedido concluído. Nenhum pagamento real processado.)\n"
            "Seu carrinho foi esvaziado."
        )
        context.user_data['cart'] = {} # Limpa o carrinho
        keyboard = [[InlineKeyboardButton("🛍️ Comprar Novamente", callback_data="show_products")]]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.callback_query:
        try:
            await update.callback_query.message.edit_text(message_text, parse_mode="Markdown", reply_markup=reply_markup)
            await update.callback_query.answer(text="Pedido finalizado!")
        except Exception as e:
            logger.warning(f"Erro ao finalizar compra: {e}")
            try:
                await update.callback_query.answer(text="Pedido finalizado!")
            except:
                pass
    else:
        await update.message.reply_text(message_text, parse_mode="Markdown", reply_markup=reply_markup)

async def view_product_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para o comando /ver e callback 'view_product_ID'."""
    product_id = -1
    if update.callback_query: # Veio de um botão
        try:
            product_id = int(update.callback_query.data.split("_")[-1])
        except (IndexError, ValueError):
            try:
                await update.callback_query.answer("ID de produto inválido no callback.", show_alert=True)
            except:
                pass
            return
    elif context.args: # Veio de um comando /ver ID
        try:
            product_id = int(context.args[0])
        except (IndexError, ValueError):
            await update.message.reply_text("Uso: `/ver <ID_DO_PRODUTO>` (ex: `/ver 1`)")
            return
    else: # Comando /ver sem ID
        await update.message.reply_text("Uso: `/ver <ID_DO_PRODUTO>` (ex: `/ver 1`)")
        return

    product_data = fetch_product_by_id(product_id)
    if not product_data:
        if update.callback_query:
            try:
                await update.callback_query.answer("Produto não encontrado.", show_alert=True)
            except:
                pass
        else:
            await update.message.reply_text(f"Produto com ID {product_id} não encontrado.")
        return

    message_text = (
        f"🖼️ **{product_data['nome']}**\n\n"
        f"{product_data['descricao']}\n\n"
        f"💰 **Preço:** R$ {product_data['preco']:.2f}\n"
        f"🆔: `{product_data['id']}`"
    )
    keyboard = [
        [InlineKeyboardButton(f"➕ Adicionar ao Carrinho", callback_data=f"add_one_{product_id}")],
        [InlineKeyboardButton("🛍️ Voltar aos Produtos", callback_data="show_products")],
        [InlineKeyboardButton("🛒 Ver Carrinho", callback_data="show_cart")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    target_message = update.callback_query.message if update.callback_query else update.message

    try:
        if product_data.get("imagem"):
            if update.callback_query and target_message.photo: # Edita se já tem foto
                 await target_message.edit_caption(caption=message_text, parse_mode="Markdown", reply_markup=reply_markup)
            else: # Envia nova foto (ou substitui texto por foto)
                if update.callback_query: await target_message.delete() # Remove msg anterior se era callback
                await target_message.reply_photo(
                    photo=product_data["imagem"],
                    caption=message_text,
                    parse_mode="Markdown",
                    reply_markup=reply_markup
                )
        else: # Sem imagem, apenas texto
            if update.callback_query:
                await target_message.edit_text(text=message_text, parse_mode="Markdown", reply_markup=reply_markup)
            else:
                await target_message.reply_text(text=message_text, parse_mode="Markdown", reply_markup=reply_markup)
    except Exception as e:
        logger.warning(f"Erro ao exibir produto {product_id}: {e}")
        # Fallback para mensagem de texto simples em caso de erro
        try:
            await target_message.reply_text(text=message_text, parse_mode="Markdown", reply_markup=reply_markup)
        except:
            pass
    
    if update.callback_query:
        try:
            await update.callback_query.answer()
        except:
            pass


async def donation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para o comando /doar e callback 'show_donation'."""
    message_text = "💝 **Obrigado por considerar uma doação!**\n\nEscolha um valor ou digite um valor personalizado:\n"
    
    keyboard = [
        [InlineKeyboardButton("R$ 5,00", callback_data="donate_500")],
        [InlineKeyboardButton("R$ 10,00", callback_data="donate_1000")],
        [InlineKeyboardButton("R$ 25,00", callback_data="donate_2500")],
        [InlineKeyboardButton("R$ 50,00", callback_data="donate_5000")],
        [InlineKeyboardButton("💰 Outro valor", callback_data="donate_custom")],
        [InlineKeyboardButton("🔙 Voltar", callback_data="show_products")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        try:
            await update.callback_query.message.edit_text(message_text, parse_mode="Markdown", reply_markup=reply_markup)
            await update.callback_query.answer()
        except Exception as e:
            logger.warning(f"Erro ao editar mensagem de doação: {e}")
            try:
                await update.callback_query.answer()
            except:
                pass
    else:
        await update.message.reply_text(message_text, parse_mode="Markdown", reply_markup=reply_markup)


async def process_donation(update: Update, context: ContextTypes.DEFAULT_TYPE, amount_cents: int) -> None:
    """Processa a doação e exibe resumo."""
    amount_reais = amount_cents / 100
    message_text = (
        f"💖 **Obrigado pela generosa doação!**\n\n"
        f"Valor doado: **R$ {amount_reais:.2f}**\n\n"
        f"(Simulação de pagamento concluído. Nenhum pagamento real processado.)\n\n"
        f"Sua doação ajuda muito! 🙏"
    )
    
    keyboard = [
        [InlineKeyboardButton("💝 Fazer outra doação", callback_data="show_donation")],
        [InlineKeyboardButton("🛍️ Ver Produtos", callback_data="show_products")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        try:
            await update.callback_query.message.edit_text(message_text, parse_mode="Markdown", reply_markup=reply_markup)
            await update.callback_query.answer(text="Doação processada! Obrigado! 💖")
        except Exception as e:
            logger.warning(f"Erro ao processar doação: {e}")
            try:
                await update.callback_query.answer(text="Doação processada! Obrigado! 💖")
            except:
                pass
    else:
        await update.message.reply_text(message_text, parse_mode="Markdown", reply_markup=reply_markup)


async def text_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para mensagens de texto (doação personalizada)."""
    if context.user_data.get('waiting_for_donation'):
        try:
            # Tenta converter para float
            amount_str = update.message.text.replace(',', '.').strip()
            amount_reais = float(amount_str)
            
            if amount_reais <= 0:
                await update.message.reply_text("❌ Por favor, digite um valor maior que 0. (ex: 25 para R$ 25,00)")
                return
            
            amount_cents = int(amount_reais * 100)
            context.user_data['waiting_for_donation'] = False
            await process_donation(update, context, amount_cents)
        except ValueError:
            await update.message.reply_text("❌ Valor inválido! Digite apenas números. (ex: 25 para R$ 25,00)")


# --- Callbacks para Botões Inline ---
async def inline_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Processa todos os callbacks de botões inline."""
    query = update.callback_query
    data = query.data
    logger.info(f"Callback recebido: {data}")

    try:
        if data == "show_products":
            await products_handler(update, context)
        elif data == "show_cart":
            await cart_handler(update, context)
        elif data.startswith("view_product_"):
            await view_product_handler(update, context) # Reutiliza o handler
        elif data.startswith("add_one_"):
            try:
                product_id = int(data.split("_")[-1])
            except (IndexError, ValueError):
                try:
                    await query.answer("ID de produto inválido.", show_alert=True)
                except:
                    pass
                return
            
            product_data = fetch_product_by_id(product_id)
            if not product_data:
                try:
                    await query.answer("Produto não mais disponível.", show_alert=True)
                except:
                    pass
                return

            cart = get_cart(context)
            cart[product_id] = cart.get(product_id, 0) + 1
            try:
                await query.answer(text=f"✅ '{product_data['nome']}' adicionado!")
            except:
                pass

        elif data.startswith("remove_one_"):
            try:
                product_id = int(data.split("_")[-1])
            except (IndexError, ValueError):
                try:
                    await query.answer("ID de produto inválido.", show_alert=True)
                except:
                    pass
                return

            cart = get_cart(context)
            product_data = fetch_product_by_id(product_id)

            if not product_data: # Produto não existe mais no DB
                if product_id in cart: del cart[product_id]
                try:
                    await query.answer("Produto não encontrado. Removido do carrinho se estava lá.", show_alert=True)
                except:
                    pass
                await cart_handler(update, context) # Atualiza a view do carrinho
                return

            if product_id in cart and cart[product_id] > 0:
                cart[product_id] -= 1
                if cart[product_id] == 0:
                    del cart[product_id]
                    try:
                        await query.answer(text=f"🗑️ '{product_data['nome']}' removido completamente.")
                    except:
                        pass
                else:
                    try:
                        await query.answer(text=f"➖ Uma unidade de '{product_data['nome']}' removida.")
                    except:
                        pass
                await cart_handler(update, context) # Atualiza a mensagem do carrinho
            else:
                try:
                    await query.answer(text=f"'{product_data['nome']}' não está no carrinho.", show_alert=True)
                except:
                    pass
                await cart_handler(update, context) # Atualiza para mostrar que sumiu (ou não estava)

        elif data == "checkout_cart":
            await checkout_handler(update, context)
        elif data == "show_donation":
            await donation_handler(update, context)
        elif data.startswith("donate_"):
            try:
                if data == "donate_custom":
                    try:
                        await query.answer()
                    except:
                        pass
                    await update.callback_query.message.reply_text(
                        "💰 **Digite o valor desejado:**\n\nEx: 25 (para R$ 25,00)\nEx: 50.50 (para R$ 50,50)",
                        parse_mode="Markdown"
                    )
                    context.user_data['waiting_for_donation'] = True
                else:
                    amount_cents = int(data.split("_")[-1])
                    await process_donation(update, context, amount_cents)
            except (IndexError, ValueError):
                try:
                    await query.answer("Erro ao processar doação.", show_alert=True)
                except:
                    pass
        else:
            try:
                await query.answer(text="Ação não implementada.")
            except:
                pass
    except Exception as e:
        logger.error(f"Erro geral no handler de botões: {e}")
        try:
            await query.answer(text="Erro ao processar ação. Tente novamente.", show_alert=True)
        except:
            pass

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para o comando /help."""
    help_text = (
        "🤖 **Comandos:**\n"
        "/start - Iniciar conversa\n"
        "/produtos - Listar produtos\n"
        "/ver `<ID>` - Ver detalhes de um produto\n"
        "/adicionar `<ID>` - Adicionar produto ao carrinho\n"
        "/remover `<ID>` - Remover produto do carrinho\n"
        "/carrinho - Ver seu carrinho\n"
        "/finalizar - Finalizar compra (simulação)\n"
        "/doar - Fazer uma doação\n"
        "/help - Mostrar esta ajuda"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

def main() -> None:
    """Função principal para iniciar o bot."""
    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "SEU_TOKEN_AQUI_INVALIDO":
        logger.critical("ERRO: Token do Telegram não configurado.")
        return

    initialize_database()
    populate_initial_data()

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("produtos", products_handler))
    application.add_handler(CommandHandler("adicionar", add_to_cart_handler))
    application.add_handler(CommandHandler("remover", remove_from_cart_handler))
    application.add_handler(CommandHandler("carrinho", cart_handler))
    application.add_handler(CommandHandler("finalizar", checkout_handler))
    application.add_handler(CommandHandler("doar", donation_handler))
    application.add_handler(CommandHandler("help", help_handler))
    application.add_handler(CommandHandler("ver", view_product_handler)) # Comando direto /ver ID

    application.add_handler(CallbackQueryHandler(inline_button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message_handler))

    logger.info("Bot iniciando polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
