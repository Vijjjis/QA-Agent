```mermaid
graph TD
    Start([1. User Prompt]) -->|Передача данных| Orchestrator[Orchestrator Agent]
    Orchestrator -->|Передача требований| Reviewer[Requirement Reviewer Agent]
    
    Reviewer -->|Confluence Tool + PII-детектор| Mask[Сокрытие персональных данных]
    Mask --> ReviewerAction[Анализ требований]
    ReviewerAction -->|Формирование артефакта| RevArtifact[Requirement Reviewer Artifact]
    
    RevArtifact --> CheckGate{Requirement Reviewer Gate == PASS?}
    
    CheckGate -->|Нет (FAIL)| FailBranch[Шаг 4.2: Остановка воркфлоу]
    FailBranch -->|Task, Jira, Test, Qase Gates = N/A| SetFail[Final Gate = FAIL]
    SetFail --> OrchFailArt[Формирование Orchestrator Agent Artifact с причинами остановки]
    OrchFailArt --> End([Конец воркфлоу])
    
    CheckGate -->|Да (PASS)| Parallel[Шаг 4.1 & 5: Параллельный запуск]
        Parallel --> TestAgent[Test Designer Agent]
        Parallel --> TaskAgent[Task Designer Agent]
        
        TestAgent -->|Skills & Tools| QaseSys[(Система Qase)]
        QaseSys --> TestArt[Test Model Artifact + Quality Gates]
        
        TaskAgent -->|Skills & Tools| JiraSys[(Система Jira)]
        JiraSys --> TaskArt[Jira Tasks Artifact + Quality Gates]
    
    TestArt --> FinalCheck[Шаг 6: Orchestrator Agent проверка статусов]
    TaskArt --> FinalCheck
    
    FinalCheck --> Evaluate{Все Gate = PASS?}
    Evaluate -->|Да| Success[Final Gate = SUCCESS]
    Evaluate -->|Нет| FailFinal[Final Gate = FAIL / Статусы с ошибками]
    
    Success --> FinalArt[Формирование агрегированного Orchestrator Agent Artifact]
    FailFinal --> FinalArt
    FinalArt --> End