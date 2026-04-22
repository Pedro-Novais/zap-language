# AGENTS.md - Convenções do Projeto Zap Language

Este arquivo documenta as convenções e padrões adotados no projeto Zap Language para garantir consistência no código e colaboração eficaz.

## Convenções de Código

### Chamadas de Funções
- **Nomeação de Parâmetros**: Sempre nomeie explicitamente cada parâmetro passado em chamadas de função, mesmo quando a posição seria suficiente.
- **Quebra de Linhas**: Para funções com mais de um parâmetro, quebre a linha para cada parâmetro, alinhando-os para melhor legibilidade.

#### Exemplo Correto:
```python
service.send_email(
    to="user@example.com",
    subject="Welcome",
    body="Hello World",
)
```

#### Exemplo Incorreto:
```python
service.send_email("user@example.com", "Welcome", "Hello World")
```

Essa convenção melhora a clareza e reduz erros em refatorações ou mudanças na assinatura da função.

## Informações para Agentes

Este projeto é uma plataforma de aprendizado de idiomas via WhatsApp usando IA. Segue Clean Architecture com camadas core (domínio) e external (infraestrutura).

### Estrutura Principal
- **Core**: Lógica de negócio pura, sem dependências externas.
  - `interactor/`: Casos de uso (ex: ForgotPasswordInteractor).
  - `interface/`: Abstrações (ex: SendEmailService).
  - `model/`: Modelos de dados.
  - `shared/`: Erros, auth, etc.

- **External**: Implementações concretas.
  - `controllers/`: Lidam com HTTP, chamam interactors.
  - `routes/`: Definem endpoints Flask.
  - `repositories/`: Acesso a DB (SQLAlchemy).
  - `services/`: Integrações externas (WhatsApp, Email, etc.).
  - `container/`: DI e instâncias.

### Padrões
- Controllers usam interactors para lógica.
- Interactors recebem repositories/services via DI.
- Rotas seguem convenções de nomeação explícita de parâmetros.
- Exceções herdam de ApplicationError com status codes.
- Logs com loguru.
- Validação de requests com validate_request.

### Serviços Recentes
- SendEmailService: Envio de emails via SMTP com exceções específicas.
- ForgotPasswordInteractor: Processa reset de senha, verifica usuário e envia email.

Para novas features: Criar interface em core/interface/, implementação em external/services/, interactor em core/interactor/, controller method, e rota.

## Convenção sobre Comentários no Código

- **Proibição de comentários livres**: Comentários no código não são permitidos, exceto comentários que iniciem com `TODO`. Comentários de explicação, anotações ou pragmas devem ser evitados; use o código legível e documentação externa (README/AGENTS.md) quando necessário.