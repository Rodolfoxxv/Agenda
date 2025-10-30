# Agenda

Aplicação Flask que mantém uma agenda simples utilizando DuckDB e também expõe
endpoints para receber webhooks JSON autenticados via JWT. Essa estrutura ajuda
a integrar formulários externos que disparam inspeções e enviam seus dados para
uma URL controlada por você.

## Configuração

1. **Dependências**

   ```bash
   poetry install
   ```

2. **Variáveis de ambiente opcionais**

   - `INTEGRATION_USERNAME`: usuário aceito pelo endpoint de autenticação
     (padrão: `integration`).
   - `INTEGRATION_PASSWORD`: senha do usuário (padrão: `integration123`).
   - `INTEGRATION_JWT_SECRET`: segredo utilizado para assinar o token JWT
     (padrão: `change-this-secret`).
   - `INTEGRATION_JWT_EXP_MINUTES`: minutos de validade do token (padrão: `30`).

3. **Banco de dados**

   Para criar (ou recriar) o banco `agenda.db` com as tabelas necessárias,
   execute:

   ```bash
   poetry run python create_agenda_db.py
   ```

## Executando o servidor

```bash
poetry run python main.py
```

Por padrão a aplicação sobe em `http://127.0.0.1:5000`.

## Fluxo de autenticação e recebimento de dados

1. **Obter o token JWT**

   Faça um `POST` em `/integration/auth` com usuário e senha em JSON:

   ```bash
   curl -X POST http://127.0.0.1:5000/integration/auth \
     -H "Content-Type: application/json" \
     -d '{"username": "integration", "password": "integration123"}'
   ```

   Resposta esperada:

   ```json
   {
     "access_token": "<token>",
     "token_type": "Bearer",
     "expires_in_minutes": 30
   }
   ```

2. **Receber os webhooks**

   Cadastre a URL `POST /integration/events` na plataforma que dispara as
   inspeções. A requisição deve incluir o header
   `Authorization: Bearer <token>` obtido no passo anterior e o JSON enviado
   será armazenado na tabela `integration_events`.

   Exemplo de teste manual:

   ```bash
   curl -X POST http://127.0.0.1:5000/integration/events \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"form_id": "123", "cliente": "ACME", "respostas": []}'
   ```

3. **Consultar eventos armazenados**

   Quando precisar revisar o que foi armazenado, execute:

   ```bash
   curl http://127.0.0.1:5000/integration/events -H "Authorization: Bearer <token>"
   ```

   A resposta lista todos os eventos salvos, incluindo o `payload` original e o
   horário de recebimento.
