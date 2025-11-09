## Loomi Desafio

API simples em FastAPI com integração opcional a PostgreSQL. Inclui dockerização, `docker-compose` (com profile de desenvolvimento para banco local), pipeline de deploy para EC2 e exemplo de infraestrutura com Terraform.

### Stack
- **API**: FastAPI + Uvicorn
- **ORM/DB**: SQLAlchemy (conexão direta), PostgreSQL opcional
- **Container**: Docker
- **Orquestração local**: docker-compose
- **Infra exemplo**: Terraform (AWS EC2 + SG + Key Pair)
- **CI/CD**: GitHub Actions (deploy via SSH para EC2)

## Endpoints
- **GET /**: informações básicas do serviço.
- **GET /health**: healthcheck da aplicação. Use `?db=true` para checar o banco.
- **GET /do-you-have-it**: retorna uma mensagem aleatória do dicionário interno.
- **GET /do-you-have-it-db**: retorna uma string aleatória da tabela `strings` no Postgres (coluna `content`).

## Requisitos
- Python 3.11+ (para rodar local)
- Docker e docker-compose (para rodar em containers)
- Terraform 1.6+ (se usar a infra de exemplo)

## Variáveis de Ambiente
No diretório `app/`, copie `env.example` para `.env` e ajuste conforme necessário:

```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=app
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

Observações:
- A aplicação monta `DATABASE_URL` automaticamente quando todas as variáveis acima existem.
- Em produção, use variáveis de ambiente/Secrets (não suba `.env` para o Git).

## Como Rodar
### 1) Local (sem Docker)
No diretório `app/`:
```
pip install -r requirements.txt
uvicorn main:app --reload
```
Acesse `http://localhost:8000` e `http://localhost:8000/docs`.

### 2) Docker
No diretório `app/`:
```
docker build -t loomi-desafio-app .
docker run --rm -p 8000:8000 --env-file .env loomi-desafio-app
```

### 3) docker-compose
No diretório `app/`:
```
docker-compose up -d --build
```
Por padrão, apenas o serviço da aplicação sobe. Para subir um Postgres local (profile `dev`):
```
docker-compose --profile dev up -d db
```
Isso cria um banco local acessível em `localhost:5432`.

## Banco de Dados
- O endpoint `/do-you-have-it-db` espera uma tabela `strings` com a coluna `content` (texto).
- Exemplo SQL:
```
CREATE TABLE IF NOT EXISTS strings (id SERIAL PRIMARY KEY, content TEXT NOT NULL);
INSERT INTO strings (content) VALUES ('You have it!'), ('You do not have it...'), ('You have a lot of it! Congratulations!');
```

## Healthcheck
- `GET /health` => `{"status": "ok"}`
- `GET /health?db=true` => também testa conexão com o banco (SELECT 1).

## CI/CD (GitHub Actions)
Workflow em `.github/workflows/deploy.yml`. A cada push na branch `main`, o job:
1. Conecta via SSH na sua instância EC2
2. Cria/atualiza o arquivo `.env` na pasta `~/loomi-desafio/app`
3. Atualiza o código (`git fetch/reset`)
4. Roda `docker-compose down && docker-compose up -d --build`
5. Reinicia o Nginx (se configurado na máquina)

### Secrets esperados
- `EC2_HOST`: IP/DNS público da EC2
- `EC2_USER`: usuário (ex: ubuntu, ec2-user, etc.)
- `EC2_SSH_KEY`: chave privada (PEM) da instância
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_HOST`, `POSTGRES_PORT`: credenciais/host do Postgres de produção

## Infra (Terraform)
Arquivos em `infra/`. Para provisionar:
```
cd infra
terraform init
terraform apply
```
Outputs:
- `public_ip`: IP público da EC2
- `ssh_private_key_pem`: chave privada gerada (sensível)

Importante:
- Este é um exemplo básico (sem VPC custom, sem RDS, sem hardening). Ajuste para sua realidade de segurança e rede.

## Observações de Segurança e Boas Práticas
- Imagem Docker roda como usuário não-root.
- `.env` e arquivos sensíveis não devem ser commitados.
- Para produção, prefira um banco gerenciado (ex: RDS) e segredos via gerenciadores (ex: SSM, Secrets Manager).
