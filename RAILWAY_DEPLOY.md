# Bot de Vendas - Telegram

Bot de loja virtual para Telegram com suporte a produtos, carrinho e doações.

## Funcionalidades

✅ Listar produtos com preços  
✅ Ver detalhes de produtos  
✅ Adicionar/remover do carrinho  
✅ Finalizar compra (simulação)  
✅ Sistema de doações com valores personalizados  
✅ Banco de dados SQLite  

## Deploy no Railway

### Pré-requisitos
- Conta no [Railway.app](https://railway.app)
- Token do bot Telegram (de @BotFather)
- GitHub com o repositório clonado

### Passos para Deploy

1. **Acesse Railway.app** e faça login com GitHub

2. **Crie um novo projeto** → "Deploy from GitHub"

3. **Selecione o repositório** com o bot

4. **Adicione as variáveis de ambiente:**
   - Vá para a aba "Variables"
   - Adicione: `TELEGRAM_BOT_TOKEN=seu_token_aqui`

5. **Pronto!** O bot será deployado automaticamente

### Monitoramento

- Acesse os logs em Railway para verificar se está rodando
- O bot vai receber mensagens automaticamente do Telegram

## Arquivos incluídos

- `Procfile` - Configuração de como iniciar o bot no Railway
- `runtime.txt` - Versão do Python (3.11)
- `requirements.txt` - Dependências Python
- `.env.example` - Exemplo de configuração

## Desenvolvimento Local

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# Criar arquivo .env com TELEGRAM_BOT_TOKEN=seu_token
python vendas.py
```

## Troubleshooting

**Bot não responde:**
- Verifique o token no `.env` ou variáveis do Railway
- Confira os logs no dashboard do Railway

**Erro de banco de dados:**
- O SQLite funciona no Railway, mas os dados são perdidos em deploys
- Para persistência, use um banco de dados remoto (PostgreSQL)

## Estrutura

```
bot_vendas-main/
├── vendas.py          # Código principal do bot
├── requirements.txt   # Dependências
├── Procfile          # Configuração Railway
├── runtime.txt       # Versão Python
├── .env.example      # Exemplo .env
└── loja_bot.db       # Banco de dados (criado automaticamente)
```
