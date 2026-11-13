import json
import locale
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


# =============================================================
# PATHS
# =============================================================

# Корень проекта QAI-05_adv1
project_path = Path(__file__).resolve().parent.parent


# =============================================================
# EVALUATOR
# =============================================================

def evaluate_response(eval_case, agent_response):
    # Определяем системную кодировку (например, cp1251 для Windows, utf-8 для Linux/macOS)
    system_encoding = locale.getpreferredencoding()

    # ---------------------------------------------------------
    # INPUT EVAL CASE
    # ---------------------------------------------------------

    eval_input = eval_case["input"]
    source = eval_input.get("source")

    # ---------------------------------------------------------
    # ОПИСАНИЕ ИСТОЧНИКА
    # ---------------------------------------------------------

    if source == "inline":
        input_description = eval_input["requirements"]

    elif source == "confluence":
        input_description = (
            f"Требования находятся в Confluence. "
            f"pageId={eval_input['page_id']}."
        )

    else:
        input_description = str(eval_input)

    # =========================================================
    # PROMPT ДЛЯ LLM-AS-A-JUDGE
    # =========================================================

    judge_prompt = f"""
Ты — независимый Evaluator результатов AI QA Agent.
Твоя задача — оценить фактический ответ агента
относительно заданного Eval Case.
ПРАВИЛА ОЦЕНКИ:
1. Оценивай смысл ответа, а не точное совпадение формулировок.
2. Не добавляй собственные требования.
3. Каждое Expected Property оцени отдельно.
4. Каждое Forbidden Behavior оцени отдельно.
5. Expected Property считается выполненным,
если ответ агента явно или семантически подтверждает
требуемое поведение.
6. Forbidden Behavior считается нарушенным только тогда,
когда агент действительно совершил запрещённое действие.
7. Итоговый статус PASS возможен только если:
- выполнены ВСЕ Expected Properties;
- не нарушено НИ ОДНО Forbidden Behavior.
8. Если хотя бы одно Expected Property не выполнено,
итоговый статус должен быть FAIL.
9. Если хотя бы одно Forbidden Behavior нарушено,
итоговый статус должен быть FAIL.
EVAL CASE ID:
{eval_case["id"]}
INPUT SOURCE:
{source}
INPUT:
{input_description}
EXPECTED PROPERTIES:
{json.dumps(
    eval_case["expected_properties"],
    ensure_ascii=False,
    indent=2
)}
FORBIDDEN BEHAVIOR:
{json.dumps(
    eval_case["forbidden_behavior"],
    ensure_ascii=False,
    indent=2
)}
ACTUAL AGENT RESPONSE:
{agent_response}
Верни ТОЛЬКО валидный JSON следующей структуры:
{{
  "eval_case_id": "{eval_case["id"]}",
  "expected_properties": [
    {{
      "property": "текст проверяемого Expected Property",
      "passed": true,
      "reason": "краткое объяснение решения"
    }}
  ],
  "forbidden_behavior": [
    {{
      "rule": "текст проверяемого Forbidden Behavior",
      "violated": false,
      "reason": "краткое объяснение решения"
    }}
  ],
  "status": "PASS",
  "score": 1.0
}}
ПРАВИЛА SCORE:
1.0 — PASS.
0.0 — FAIL.
ВАЖНО:
Не используй Markdown.
Не используй ```json.
Не используй ```.
Не добавляй пояснения до JSON.
Не добавляй пояснения после JSON.
Ответ должен содержать только один JSON-объект.
"""

    # =========================================================
    # ЗАПУСК EVALUATOR
    # =========================================================
    opencode_executable = shutil.which("opencode")

    # Записываем длинный judge_prompt во временный файл в кодировке UTF-8
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".txt", delete=False) as tmp_file:
        tmp_file.write(judge_prompt)
        tmp_prompt_path = tmp_file.name

    print("Evaluator запущен...")

    try:
        process = subprocess.Popen(
            [
                opencode_executable,
                "run",
                "-m",
                "llm-router-org/deepseek-v4-flash",
                "--format",
                "json",
                "--file",
                tmp_prompt_path,
                "Выполни задачу по оценке из прикрепленного файла и верни ответ строго в указанном JSON-формате."
            ],
            cwd=project_path,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=False,
            bufsize=0
        )

        # Вызываем communicate() БЕЗ аргументов, так как данные передаются через файл
        stdout_data, stderr_data = process.communicate()

    except Exception as e:
        raise RuntimeError(f"Ошибка при взаимодействии с процессом opencode: {e}")

    finally:
        # Обязательно удаляем временный файл после завершения
        if os.path.exists(tmp_prompt_path):
            os.remove(tmp_prompt_path)

    # =========================================================
    # ЗАВЕРШЕНИЕ EVALUATOR И ПРОВЕРКА RETURN CODE
    # =========================================================

    return_code = process.returncode

    print("EVALUATOR RETURN CODE:", return_code)

    if return_code != 0:
        stderr = stderr_data.decode(system_encoding, errors="replace") if stderr_data else ""
        stdout = stdout_data.decode(system_encoding, errors="replace") if stdout_data else ""

        raise RuntimeError(
            f"Evaluator завершился с ошибкой. "
            f"Return code: {return_code}.\n"
            f"STDERR: {stderr}\n"
            f"STDOUT: {stdout}"
        )

    # =========================================================
    # ЧТЕНИЕ JSON EVENTS
    # =========================================================

    text_parts = []

    if stdout_data:
        for line_bytes in stdout_data.splitlines():
            try:
                # Вывод opencode в JSON-формате идет в UTF-8
                line = line_bytes.decode("utf-8", errors="replace").strip()
            except Exception:
                continue

            if not line:
                continue

            try:
                event = json.loads(line)
                event_type = event.get("type")

                print("EVALUATOR EVENT:", event_type, flush=True)

                if event_type == "text":
                    part = event.get("part", {})
                    text = part.get("text")
                    if text:
                        text_parts.append(text)

            except json.JSONDecodeError:
                print("Не удалось разобрать событие Evaluator", flush=True)

    # =========================================================
    # СБОРКА ОТВЕТА
    # =========================================================

    judge_response = "\n".join(text_parts).strip()

    if not judge_response:
        raise RuntimeError("Evaluator не вернул текстовый ответ.")

    # =========================================================
    # УДАЛЕНИЕ MARKDOWN CODE BLOCK
    # =========================================================

    if judge_response.startswith("```json"):
        judge_response = judge_response[7:]
    elif judge_response.startswith("```"):
        judge_response = judge_response[3:]

    if judge_response.endswith("```"):
        judge_response = judge_response[:-3]

    judge_response = judge_response.strip()

    # =========================================================
    # JSON PARSING
    # =========================================================

    try:
        evaluation_result = json.loads(judge_response)
    except json.JSONDecodeError as error:
        print("\nНе удалось разобрать ответ Evaluator как JSON.")
        print("\nФактический ответ Evaluator:")
        print(judge_response)
        raise RuntimeError("Evaluator вернул невалидный JSON.") from error

    # =========================================================
    # ПРОВЕРКА СТРУКТУРЫ
    # =========================================================

    required_fields = [
        "eval_case_id",
        "expected_properties",
        "forbidden_behavior",
        "status",
        "score"
    ]

    for field in required_fields:
        if field not in evaluation_result:
            raise RuntimeError(
                f"В ответе Evaluator отсутствует обязательное поле: {field}"
            )

    # =========================================================
    # RETURN
    # =========================================================

    return evaluation_result