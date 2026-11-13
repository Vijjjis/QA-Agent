# QA-Agent System

Система позволяет выполнить анализ требований, создать задачи в Jira и тест-кейсы в Qase.

## Состав системы

### 1. Agents

- **QA-orchestrator** — Оркестратор всех агентов
- **requirement-review** — Агент для анализа требований
- **task-designer** — Агент для создания задач в Jira
- **test-designer** — Агент для создания тест-кейсов в Qase

### 2. Skills

- **requirement-review** — Skill для анализа требований агента `requirement-review`
- **task-design** — Skill для создания задач в Jira агента `task-designer`
- **test-design** — Skill для создания тест-кейсов в Qase агента `test-designer`

### 3. Tools

- **Confluence** — инструмент для доступа к Confluence
В инструменте Confluence также содержится PII-детектор для чувствительных данных
- **MCP Jira** — MCP-сервер для доступа к Jira
- **MCP Qase** — MCP-сервер для доступа к Qase

MCP заданы в корне проекта в конфигурации `opencode.json`.

### 4. Artifacts

- **requirement-review** — хранит артефакты работы агента `requirement-review`
- **task-designer** — хранит артефакты работы агента `task-designer`
- **test-designer** — хранит артефакты работы агента `test-designer`
- **orchestrator** - хранит артефакты работы агента `QA-orchestrator`

### 5. Evals

Блок для Eval-тестирования.
- **eval_runner.py** и **evaluator.py** - файлы для запуска Eval-тестирования
- **eval_results.json** - результаты Eval-тестирования
- **golden_dataset.json** - эталонный набор Eval-тестов

## Инструкция по запуску

Перед использованием системы необходимо иметь установленный OpenCode.

### Запуск системы

## Запуск AI-агента

1. Задать через терминал локальные переменные `CONFLUENCE_URL`, `CONFLUENCE_EMAIL`, `CONFLUENCE_API_TOKEN` для доступа к Confluence.
2. Задать через терминал локальную переменную QASE_API_TOKEN для доступа к Qase.
2. Выполнить команду `opencode mcp auth jira` и выполнить аутентификацию в Jira.
4. Выполнить команду `opencode`.
5. В открывшемся окне задать необходимый User Prompt, содержащий информацию о Confluence документе с требованиями (ссылка, номер), Jira-проекте (как минимум код проекта), Qase-проекте (как минимум код проекта).

## Запуск Eval-тестирования

Команда python evals/eval_runner.py
