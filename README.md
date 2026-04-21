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

5.  **Iniciar os serviços**:
    -   Certifique-se de que o **Redis** está rodando.
    -   Executar o Flask: `flask run` ou `python app.py`.
    -   Executar o worker do Celery: `celery -A worker.worker worker --loglevel=info`.

## Usage

O projeto opera principalmente como um Webhook. A interação ocorre enviando mensagens para o número configurado no WhatsApp.

-   **Endpoint Principal**: `/webhook` (POST), que recebe os JSONs da API do WhatsApp contendo o texto do usuário.
-   **Fluxo**: O servidor recebe a mensagem, valida o usuário via banco de dados, recupera o histórico, solicita a resposta à IA e devolve a mensagem formatada para o usuário final.
-   **Login com Google**: `/api/v1/auth/login` inicia o redirecionamento OAuth2 e `/api/v1/auth/callback` conclui a autenticação, persistindo o usuário e criando a sessão autenticada.
