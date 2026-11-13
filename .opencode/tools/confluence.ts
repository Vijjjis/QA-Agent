import { tool } from "@opencode-ai/plugin"

// ==========================================
// REGEX: Поиск и маскирование PII
// ==========================================

function maskPII(text: string) {

    let masked = text

    const detected: string[] = []

    // Email
    const emailRegex =
        /[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}/g

    // Телефон
    const phoneRegex =
        /(?:\+?\d[\d\s()-]{8,}\d)/g

    // Пароль
    const passwordRegex =
        /\b(password|пароль)\s*[:=]\s*[^\s<]+/gi

    // API Key / Token
    const tokenRegex =
        /\b(api[_-]?key|token)\s*[:=]\s*[^\s<]+/gi

    // ==========================================
    // Проверка паролей
    // ==========================================

    masked = masked.replace(passwordRegex, () => {
        detected.push("PASSWORD")
        return "[PASSWORD_MASKED]"
    })

    // ==========================================
    // Проверка API-ключей
    // ==========================================

    masked = masked.replace(tokenRegex, () => {
        detected.push("TOKEN")
        return "[TOKEN_MASKED]"
    })

    // ==========================================
    // Проверка Email
    // ==========================================

    masked = masked.replace(emailRegex, () => {
        detected.push("EMAIL")
        return "[EMAIL_MASKED]"
    })

    // ==========================================
    // Проверка телефонов
    // ==========================================

    masked = masked.replace(phoneRegex, () => {
        detected.push("PHONE")
        return "[PHONE_MASKED]"
    })

    return {
        piiFound: detected.length > 0,
        detectedPII: [...new Set(detected)],
        maskedText: masked
    }
}


// ==========================================
// CONFLUENCE TOOL
// ==========================================

export default tool({

    description:
        "Получить требования из Confluence по pageId " +
        "с автоматической Regex-проверкой и маскированием PII",

    args: {
        pageId: tool.schema.string()
    },

    async execute(args) {

        // ==========================================
        // 1. Переменные окружения
        // ==========================================

        const baseUrl = process.env.CONFLUENCE_URL
        const email = process.env.CONFLUENCE_EMAIL
        const token = process.env.CONFLUENCE_API_TOKEN

        if (!baseUrl || !email || !token) {
            throw new Error(
                "Не заданы переменные окружения Confluence"
            )
        }

        // ==========================================
        // 2. Авторизация
        // ==========================================

        const auth = Buffer.from(
            `${email}:${token}`
        ).toString("base64")

        // ==========================================
        // 3. Получение страницы Confluence
        // ==========================================

        const response = await fetch(
            `${baseUrl}/wiki/api/v2/pages/${args.pageId}?body-format=storage`,
            {
                method: "GET",
                headers: {
                    Authorization: `Basic ${auth}`,
                    Accept: "application/json"
                }
            }
        )

        if (!response.ok) {
            throw new Error(
                `Confluence API error: ${response.status} ${response.statusText}`
            )
        }

        // ==========================================
        // 4. Получение JSON
        // ==========================================

        const data = await response.json()

        // ==========================================
        // 5. Извлечение требований
        // ==========================================

        const requirements =
            data.body?.storage?.value

        if (typeof requirements !== "string") {
            throw new Error(
                "Не удалось получить содержимое страницы Confluence"
            )
        }

        // ==========================================
        // 6. Regex-проверка PII
        // ==========================================

        const piiResult = maskPII(requirements)

        // ==========================================
        // 7. Формирование результата
        // ==========================================

        const result = {
            pageId: args.pageId,

            title: data.title,

            piiCheck: {
                piiFound: piiResult.piiFound,
                detectedPII: piiResult.detectedPII
            },

            requirements: piiResult.maskedText
        }

        // ==========================================
        // 8. Возврат очищенных требований агенту
        // ==========================================

        return JSON.stringify(result, null, 2)
    }
})