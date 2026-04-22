# Zap-Language

Uma plataforma inteligente integrada ao WhatsApp que utiliza Inteligência Artificial para auxiliar usuários no aprendizado e na prática da língua inglesa de forma conversacional e automatizada.

## 🎯 Problema que Resolve

O projeto atende à necessidade de praticar idiomas de maneira acessível e constante, eliminando a barreira de agendamento de aulas tradicionais. Ele resolve a falta de um interlocutor disponível 24/7 para conversação, oferecendo correções e interações em tempo real diretamente em um aplicativo de mensagens amplamente utilizado.

## ✨ Principais Funcionalidades

-   **Interface via WhatsApp**: Integração direta para recebimento e envio de mensagens.
-   **Processamento de Linguagem Natural (LLM)**: Uso de IA para gerar respostas contextuais e educativas.
-   **Gerenciamento de Contexto**: Histórico de mensagens persistente para manter a continuidade das conversas.
-   **Autenticação de Usuários**: Sistema para identificar e gerenciar perfis individuais.
-   **Processamento Assíncrono**: Execução de tarefas em segundo plano para garantir que a interface do chat permaneça rápida.

## 🚀 Tecnologias Utilizadas

-   **Linguagem Principal**: Python.
-   **Framework Web**: Flask (utilizado para a construção da API e Webhooks).
-   **Banco de Dados**: SQLAlchemy (ORM) para persistência de dados e usuários.
-   **Task Queue**: Celery acompanhado de Redis para o processamento de mensagens e filas.
-   **Processamento de Dados**: Bibliotecas como lxml para manipulação de XML e integração com APIs externas.

## 🏗️ Arquitetura do Projeto

O projeto segue uma arquitetura limpa (Clean Architecture) dividida em camadas:

### Core (Domínio)
- **`core/interactor/`**: Contém os interactors (casos de uso) que orquestram a lógica de negócio.
- **`core/interface/`**: Define interfaces para serviços e repositórios (abstrações).
- **`core/model/`**: Modelos de dados do domínio.
- **`core/shared/`**: Utilitários compartilhados, como erros e autenticação.

### External (Infraestrutura)
- **`external/controllers/`**: Controllers que lidam com requisições HTTP e chamam os interactors.
- **`external/routes/`**: Definição das rotas Flask usando Blueprints.
- **`external/repositories/`**: Implementações concretas dos repositórios (banco de dados).
- **`external/services/`**: Implementações de serviços externos (WhatsApp, Email, etc.).
- **`external/container/`**: Injeção de dependências e configuração de instâncias.

### Outros Diretórios
- **`manager/`**: Gerenciadores de conversação e serviços auxiliares.
- **`utils/`**: Utilitários diversos, como validação de requests e middleware.
- **`migrations/`**: Scripts de migração do banco de dados (Alembic).
- **`test/`**: Testes unitários e de integração.

## ⚙️ Como Instalar e Rodar

1.  **Clonar o repositório**: Obtenha o código-fonte em sua máquina local.
    ```bash
    git clone <URL_DO_REPOSITORIO>
    cd application
    ```

2.  **Configurar o ambiente virtual**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # No Windows: venv\Scripts\activate
    ```

3.  **Instalar dependências**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configurar variáveis de ambiente**: Crie um arquivo `.env` na raiz do projeto e defina as chaves de API (WhatsApp/OpenAI) e strings de conexão do banco de dados.

    Variáveis adicionais para autenticação Google:
    - `GOOGLE_CLIENT_ID`
    - `GOOGLE_CLIENT_SECRET`
    - `SECRET_KEY`
    - `FRONTEND_URL` (opcional, usado no redirect após o callback OAuth)
    
    Variáveis adicionais para envio de e-mail com Resend:
    - `RESEND_API_KEY` : API key fornecida pelo Resend (obrigatório para envio de emails).
    - `RESEND_FROM_EMAIL` : Endereço de e-mail remetente usado nas mensagens enviadas.

5.  **Iniciar os serviços**:
    -   Certifique-se de que o **Redis** está rodando.
    -   Executar o Flask: `flask run` ou `python app.py`.
    -   Executar o worker do Celery: `celery -A worker.worker worker --loglevel=info`.

## Usage

O projeto opera principalmente como um Webhook. A interação ocorre enviando mensagens para o número configurado no WhatsApp.

-   **Endpoint Principal**: `/webhook` (POST), que recebe os JSONs da API do WhatsApp contendo o texto do usuário.
-   **Fluxo**: O servidor recebe a mensagem, valida o usuário via banco de dados, recupera o histórico, solicita a resposta à IA e devolve a mensagem formatada para o usuário final.
-   **Login com Google**: `/api/v1/auth/login` inicia o redirecionamento OAuth2 e `/api/v1/auth/callback` conclui a autenticação, persistindo o usuário e criando a sessão autenticada.

## Envio de E-mail (Resend)

Este projeto usa a implementação `ResendSendEmailService` (arquivo `external/services/resend_send_email_service.py`) para enviar e-mails via a API do Resend. Para habilitar o envio de e-mail:

- Configure `RESEND_API_KEY` e `RESEND_FROM_EMAIL` no `.env`/ambiente.
- A dependência `resend` já está declarada em `requirements.txt`.

Exemplo de uso (via container instanciado no projeto):

```python
from external.container import send_email_service

send_email_service.send_email(
    to="user@example.com",
    subject="Assunto de teste",
    body="<p>Corpo do e-mail em HTML</p>",
)
```

Por segurança, o controller/endpoint retorna mensagens genéricas em fluxos de recuperação de senha para não revelar se um e-mail existe no sistema.
