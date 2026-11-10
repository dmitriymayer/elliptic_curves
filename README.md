# Elliptic curves, chapter 0

Визуализация задач семинара «Эллиптические кривые: от древности до наших дней»:
интерактивные чертежи, решения на Python и исторические комментарии со ссылками на источники.

Сайт: `https://<имя-пользователя>.github.io/<имя-репозитория>/`

## Что где лежит

| Путь | Что это |
| --- | --- |
| `index.html`, `problem-1-*.html` | готовые страницы сайта |
| `assets/` | скрипт страниц (React), стили и шрифты KaTeX |
| `problems/*/solution.py` | решения задач на Python (только стандартная библиотека) |
| `src/*.dc.html` | исходники страниц в формате Claude Design |
| `tools/` | сборка страниц из `src/` |

Решения запускаются так:

```
python3 problems/1.4-tunnell/solution.py
```

## Пересборка страниц

Нужны Python 3 и, если меняется сам рантайм, Node.js с пакетами `react`, `react-dom`, `esbuild`, `katex`.

```
REPO_URL=https://github.com/<user>/<repo> python3 tools/build.py
```
