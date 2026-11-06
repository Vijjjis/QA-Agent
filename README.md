Описание QA-Agent System
Система позволяет выполнить анализ требований, создать задачи в Jira и тест-кейсы в Qase.
Состав системы.
1. Agents:
   - QA-orchestrator - Оркестратор всех агентов
   - requirement-review - Агент для анализа требований
   - task-designer - Агент для создания задач в Jira
   - test-designer - Агент для создания тест-кейсов в Qase
2. Skills:
   - requirement-review - skill для анализа требований агента requirement-review
   - task-design - skill для создания задач в Jira агента task-designer
   - test-design - skill для создания тест-кейсов в Qase агента test-designer
3. Tools:
   - confluence - инструмент для доступа к Confluence
   - mcp jira - MCP-сервер для доступа к Jira
   - mcp qase - MCP-сервер для доступа к Qase
mcp заданы в корне проекта в конфигурации opencode.json
4. Artifacts:
   - requirement-review - хранит артефакты работы агента requirement-review
   - task-designer - хранит артефакты работы агента task-designer
   - test-designer - хранит артефакты работы агента test-designer
Инструкция по запуску.
Перед использованием системы необходимо иметь установленный OpenCode.
Запуск системы:
   - задать через терминал локальные переменные CONFLUENCE_URL, CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN для доступа к Confluence
   - выполнить команду opencode mcp auth jira и выполнить аутентификацию в Jira
   - выполнить команду opencode mcp auth qase и выполнить аутентификацию в Qase
   - выполнить команду opencode
   - В открывшемся окне задать необходимый User Prompt