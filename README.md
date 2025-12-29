# Todo List Application

Um gerenciador simples de tarefas (todo list) com interface gráfica em Tkinter e persistência de dados em JSON.

## Características

- ✅ **Adicionar tarefas** - Use o campo de texto e pressione Enter para adicionar uma nova tarefa
- 📋 **Listar tarefas** - Visualize todas as tarefas em uma tabela com seus status
- ⭐ **Prioridades** - Defina níveis de prioridade para cada tarefa:
  - `low` (Baixa) - cinza
  - `medium` (Média) - amarelo
  - `high` (Alta) - vermelho
- 🔄 **Gerenciar status** - Cicle entre os status de uma tarefa:
  - `pending` (Pendente)
  - `in_progress` (Em andamento)
  - `done` (Feita)
- 🗑️ **Remover tarefas** - Delete tarefas clicando no "×" ou usando o botão Remover
- 💾 **Persistência** - Todas as tarefas são automaticamente salvas em `tasks.json`
- 📊 **Ordenação automática** - Tarefas são ordenadas por prioridade (Alta → Média → Baixa)
- 📈 **Dashboard de Estatísticas** - Painel em tempo real mostrando:
  - Total de tarefas
  - Tarefas pendentes
  - Tarefas em andamento
  - Tarefas concluídas
  - Porcentagem de conclusão
- 🔍 **Busca e Filtros** - Encontre tarefas rapidamente com:
  - Campo de busca por texto (procura no título)
  - Filtro por status (Todos, Pendentes, Em andamento, Concluídas)
  - Filtro por prioridade (Todas, Alta, Média, Baixa)
  - Mostra quantas tarefas correspondem aos filtros

## Como usar

### Instalação de dependências

```bash
pip install -r requirements.txt
```

### Executar a aplicação

```bash
python todo_app.py
```

## Estrutura de dados

As tarefas são salvas em `tasks.json` com o seguinte formato:

```json
[
  {
    "id": 1,
    "task": "Descrição da tarefa",
    "status": "pending",
    "priority": "high",
    "done": false
  },
  {
    "id": 2,
    "task": "Outra tarefa",
    "status": "done",
    "priority": "medium",
    "done": true
  }
]
```

### Campos explicados:
- **id**: Identificador único e estável da tarefa
- **task**: Texto descritivo da tarefa
- **status**: Um de `pending`, `in_progress` ou `done`
- **priority**: Um de `low`, `medium` ou `high`
- **done**: Sincronizado com `status` (true se status == 'done')

## Design Visual

A aplicação utiliza:
- **Fonte unificada**: Segoe UI em todo o aplicativo
- **Pesos de fonte**:
  - Normal: 10pt para conteúdo regular
  - Bold: 10pt para labels
  - Bold Large: 11pt para títulos e destaque
- **Tema escuro**: Paleta visual elegante com contraste adequado
- **Cores semânticas**: Cada status e prioridade possui cores características para facilitar a identificação visual rápida

### Campos

- `id` (int): Identificador único e estável da tarefa
- `task` (str): Texto descritivo da tarefa
- `status` (str): Status atual (`pending`, `in_progress`, `done`)
- `done` (bool): Indicador de conclusão (sincronizado com `status`)

## Interface

A aplicação possui uma interface simples com:

- Campo de entrada de texto para adicionar novas tarefas
- Tabela mostrando todas as tarefas com suas informações
- Botões para gerenciar o status e remover tarefas
- Duplo clique em uma tarefa para alterar seu status

## Requisitos

- Python 3.7+
- Tkinter (incluído na maioria das instalações Python)

## Notas

- O arquivo `tasks.json` é criado automaticamente ao lado do script
- Os dados são salvos automaticamente após cada alteração
- A aplicação é leve e pode ser facilmente executada em qualquer sistema com Python
