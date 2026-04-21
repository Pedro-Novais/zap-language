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