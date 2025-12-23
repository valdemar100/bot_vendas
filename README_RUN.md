Instruções rápidas para rodar o bot (Windows PowerShell):

1) Instalar Python 3.10+ e criar ambiente virtual

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

2) Instalar dependências

```powershell
pip install -r requirements.txt
```

3) Criar `.env` com o token do Telegram

Crie um arquivo `.env` na mesma pasta com o conteúdo:

```
TELEGRAM_BOT_TOKEN=SEU_TOKEN_AQUI
```

4) Executar

```powershell
python .\vendas.py
```

Se aparecer "Python was not found", instale o Python e ative a opção "Add Python to PATH" na instalação.
