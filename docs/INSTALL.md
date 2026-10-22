# Установка библиотеки KMD на компьютер

## Через локального Claude Code (рекомендуется)
Открыть Claude Code на компьютере с AutoCAD 2026 и вставить задание целиком:

```text
Установи библиотеку блоков KMD:

1. Если папки C:\KMD_Blocks нет — выполни:
   git clone -b claude/gracious-pasteur-op4bhj https://github.com/karasikss/karasikss.git C:\KMD_Blocks
   Если есть — обнови: git -C C:\KMD_Blocks pull
   Если git попросит вход в GitHub — дождись, пока я войду в открывшемся окне.

2. Скопируй папку C:\KMD_Blocks\skill\kmd-blocks в %USERPROFILE%\.claude\skills\kmd-blocks
   (заменить, если уже есть).

3. Найди конфигурацию MCP-сервера autocad-2026. Где искать:
   %APPDATA%\Claude\claude_desktop_config.json, %USERPROFILE%\.claude.json, .mcp.json проекта.
   В его env.ALLOWED_PATHS допиши C:\KMD_Blocks ЧЕРЕЗ ЗАПЯТУЮ к уже существующим путям
   (сервер делит список по запятой). Больше ничего в конфиге не меняй.
   Перед сохранением покажи мне diff и дождись подтверждения. Сделай резервную копию файла.

4. В CLAUDE.md моего рабочего проекта добавь строку:
   Библиотека блоков KMD: C:/KMD_Blocks (инструкция — skill kmd-blocks).

5. Отчитайся по каждому пункту и напомни, что клиент MCP нужно перезапустить.
```

После перезапуска — проверка по [MCP_PILOT.md](MCP_PILOT.md).

## Вручную (PowerShell)
```powershell
git clone -b claude/gracious-pasteur-op4bhj https://github.com/karasikss/karasikss.git C:\KMD_Blocks
Copy-Item C:\KMD_Blocks\skill\kmd-blocks "$env:USERPROFILE\.claude\skills\kmd-blocks" -Recurse -Force
```
Затем в конфиге MCP `autocad-2026` дописать `C:\KMD_Blocks` в `ALLOWED_PATHS` через запятую
и перезапустить клиент.

## Обновление
`git -C C:\KMD_Blocks pull` и повторить шаг 2 (копирование skill).
