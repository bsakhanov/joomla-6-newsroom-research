# Joomla 6 для новостной редакции

**Исследование-доклад, интерактивный лонгрид и пошаговый разбор редакционного конвейера на чистой Joomla 6.1.4**

*Редакция 1.1 · 8 октября 2026 · автор — Бейбит Саханов, Астана*

[English version below](#joomla-6-for-the-newsroom)

---

## О чём это

Годится ли свободная система управления содержимым Joomla в её шестом поколении на роль платформы для новостного сайта с большим потоком материалов и большим трафиком? Исследование отвечает «да» и перечисляет условия. Три довода держат вывод: зрелость релизного цикла (мажор раз в два года, ветка 7.0-dev уже открыта), редакционный контур в ядре — роли, многостадийный процесс публикации, версии, график выхода, многоязычие, баннеры — и живые примеры: второй по посещаемости новостной сайт Хорватии и порталы из первой десятки тысяч сайтов мира работают на Joomla. Слабые места названы без умолчаний и получают инженерный ответ.

Особое внимание — русскому сообществу разработчиков, Казахстану (локализация, платёжные системы, запасной язык интерфейса) и редакционному конвейеру с четырьмя ролями: репортёр → редактор отдела → корректор → главред для материалов особой важности.

## Состав

| папка | что внутри |
|---|---|
| `doklad/` | исследование-доклад: самодостаточный HTML (16 глав, 4 схемы, 93 источника, реестры расхождений и белых пятен, глоссарий) и его Markdown-исходник |
| `longread/` | интерактивный лонгрид «Редакция в ядре»: симулятор ролей и конвейера, дерево меток, модель нагрузки, генератор разметки NewsArticle, созвездие экосистемы, весы рисков — один файл без внешних библиотек |
| `konveyer-v-skrinshotakh/` | пошаговый разбор конвейера на реальной Joomla 6.1.4 — 36 скриншотов админки и лицевой стороны глазами администратора и четырёх ролей, дочерние шаблоны, встроенный лонгрид |
| `redkollegiya/` | отчёт вычитки по методологии языкового прогона (Чуковский → Аграновский ∥ Слопотрон → Розенталь → Мильчин) |
| `tools/` | всё для воспроизведения: сборщик доклада, исходники лонгрида, скрипты моделирования редакции на штатных моделях Joomla, снимщик экранов на WebKitGTK |
| `dist/` | архив разбора со снимками и его однофайловая версия |

## Как смотреть

Все HTML-файлы самодостаточны — откройте в браузере. Если включены GitHub Pages: [доклад](https://bsakhanov.github.io/joomla-6-newsroom-research/doklad/joomla-6-news-platform-research.html) · [лонгрид](https://bsakhanov.github.io/joomla-6-newsroom-research/longread/joomla-6-longread-v1.1.html) · [конвейер в скриншотах](https://bsakhanov.github.io/joomla-6-newsroom-research/konveyer-v-skrinshotakh/).

## Метод

Факты взяты с официальных страниц проекта Joomla, из руководства пользователя и разработчика, исходного кода ядра (ветки 6.1-dev — 7.0-dev), карточек W3Techs и репозиториев расширений; все адреса открыты 8 октября 2026 года. Каждое утверждение несёт номер источника; список построен по первому упоминанию. Расхождения источников (Р) и белые пятна (М) вынесены в реестры, а не спрятаны в тексте. Текст прошёл четыре прохода языкового прогона и вычитку Редколлегией; типографика поставлена детерминированным типографом.

## Воспроизведение разбора со скриншотами

```
# Joomla 6.1.4 из пакета GitHub, PHP ≥ 8.3, MariaDB ≥ 10.6
php installation/joomla.php install -n --site-name=... --admin-username=admin ...
cp tools/joomla-demo/*.php cli/ && php cli/redakciya.php && php cli/redakciya_articles.php && php cli/redakciya_menu.php
# снимки: Xvfb + WebKitGTK (gir1.2-webkit2-4.1, python3-gi)
python3 tools/screenshots/plans.py && tools/screenshots/run_shots.sh admin reporter editor proof chief front
```

Скрипт `redakciya.php` собирает сценарий теми же моделями, которыми пользуется админка: группы, уровень доступа, пользователи, процесс со стадиями и переходами, права, категория-отдел, материалы в разных стадиях. Пароли демо-пользователей — в скрипте, менять перед любым использованием вне песочницы.

## Версии

- **1.1** — 8 октября 2026: поправки по Schema.org (готовые NewsArticle с автозаполнением в каталоге, в ядре — ручной Article и плагин Custom), ветки 6.3-dev и 7.0-dev с плановой датой 12 октября 2027, глава о дочерних шаблонах, приложение «Конвейер в скриншотах», реестр Р-05.
- **1.0** — 8 октября 2026: первая редакция доклада и лонгрида.

## Лицензия

Тексты, схемы и снимки — [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.ru); скрипты в `tools/` — MIT. Торговые марки Joomla® принадлежат Open Source Matters, Inc.

---

# Joomla 6 for the Newsroom

**A research report, an interactive long-read, and a step-by-step walkthrough of an editorial pipeline on a clean Joomla 6.1.4 install**

*Edition 1.1 · 8 October 2026 · by Beibit Sakhanov, Astana*

## What this is

Is the free content management system Joomla, in its sixth generation, fit to run a news site with a heavy flow of stories and heavy traffic? The report answers yes, with conditions spelled out. Three arguments carry the conclusion: a mature release cycle (a major every two years, with the 7.0-dev branch already open), an editorial core — roles, multi-stage publishing workflows, versions, scheduling, multilingual associations, banners — and living examples: Croatia's second most visited news site and portals in the world's top ten thousand run on Joomla. Weak points are named plainly and given an engineering answer.

Special attention goes to the Russian-speaking developer community, to Kazakhstan (localisation, payment systems, interface language fallback), and to a four-role newsroom pipeline: reporter → desk editor → proofreader → editor-in-chief for high-importance pieces.

## Contents

| folder | inside |
|---|---|
| `doklad/` | the research report: a self-contained HTML (16 chapters, 4 diagrams, 93 sources, registers of discrepancies and gaps, glossary) and its Markdown source |
| `longread/` | the interactive long-read "Newsroom in the core": role and pipeline simulator, tag tree, load model, NewsArticle markup generator, ecosystem constellation, risk scales — one file, no external libraries |
| `konveyer-v-skrinshotakh/` | the walkthrough on a real Joomla 6.1.4: 36 screenshots of the admin and the frontend as seen by the administrator and four roles, child templates, an embedded long-read |
| `redkollegiya/` | the proofreading report produced with the author's editorial methodology |
| `tools/` | everything needed to reproduce: report builder, long-read sources, scripts that model the newsroom with Joomla's own MVC models, a WebKitGTK screenshot runner |
| `dist/` | the walkthrough archive with images and its single-file version |

## How to view

Every HTML file is self-contained — open it in a browser. With GitHub Pages enabled: [report](https://bsakhanov.github.io/joomla-6-newsroom-research/doklad/joomla-6-news-platform-research.html) · [long-read](https://bsakhanov.github.io/joomla-6-newsroom-research/longread/joomla-6-longread-v1.1.html) · [walkthrough](https://bsakhanov.github.io/joomla-6-newsroom-research/konveyer-v-skrinshotakh/).

## Method

Facts come from the Joomla project's official pages, the user and developer manuals, the core source code (branches 6.1-dev to 7.0-dev), W3Techs site cards and extension repositories; every URL was opened on 8 October 2026. Each claim carries a source number; the list is ordered by first mention. Source discrepancies (Р) and gaps (М) live in registers rather than being hidden in prose. The texts are in Russian.

## Reproducing the walkthrough

See the commands above: install Joomla 6.1.4 from the GitHub package, run the `tools/joomla-demo` scripts to build the scenario with Joomla's own models, then run the WebKitGTK screenshot plans under Xvfb. Demo passwords live in the scripts — change them before any use outside a sandbox.

## License

Texts, diagrams and screenshots — [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); scripts in `tools/` — MIT. Joomla® trademarks belong to Open Source Matters, Inc.
