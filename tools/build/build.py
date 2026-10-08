#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build.py — собирает самодостаточный HTML-доклад из Markdown-исходника.
Стиль наследует industrial-b2b-web-design-research.html: бумага, акцент #B54A24,
прогресс-бар, липкая навигация, боковая рейка, секции с номерами глав."""
import re, html, sys
import markdown

SRC = '/home/claude/report/doklad-joomla-news.md'
OUT = '/mnt/user-data/outputs/joomla-6-news-platform-research.html'

src = open(SRC, encoding='utf-8').read()
meta = dict(re.findall(r'<!--\s*(\w+):\s*(.*?)\s*-->', src))
src = re.sub(r'<!--\s*\w+:.*?-->\n?', '', src)

md = markdown.Markdown(extensions=['tables', 'attr_list', 'md_in_html'])
body = md.convert(src)

# цитирование источников: [12] -> ссылка на запись
body = re.sub(r'(?<![\w"=/-])\[(\d{1,3})\](?!\()', lambda m: f'<a class="cite" href="#src-{m.group(1)}">{m.group(1)}</a>', body)

# разбивка на секции по h2
parts = re.split(r'(?=<h2 )', body)
head_html = parts[0]
sections = parts[1:]
apparatus = {'glossariy', 'reestry', 'ukazatel', 'istochniki'}
short = {
    'rezyume': 'резюме', 'chto-takoe': 'что такое', 'relizy': 'релизы', 'fundament': 'фундамент',
    'rynok': 'рынок', 'kontur': 'контур', 'konveyer': 'конвейер', 'taksonomiya': 'таксономия',
    'adminka': 'админка', 'nagruzka': 'нагрузка', 'vidimost': 'видимость', 'portaly': 'порталы',
    'ekosistema': 'экосистема', 'shablony': 'шаблоны', 'riski': 'риски', 'rekomendatsii': 'рекомендации',
    'glossariy': 'глоссарий', 'reestry': 'реестры', 'ukazatel': 'указатель', 'istochniki': 'источники'}
nav, rail, out_sections = [], [], []
n = 0
for sec in sections:
    m = re.match(r'<h2 id="([^"]+)">(.*?)</h2>', sec, re.S)
    sid, title = m.group(1), m.group(2)
    rest = sec[m.end():]
    if sid in apparatus:
        eyebrow = 'служебный аппарат'
        num = ''
    else:
        n += 1
        num = f'{n:02d}'
        eyebrow = f'глава {num}'
    nav.append(f'<a href="#{sid}">{short.get(sid, title)}</a>')
    if num:
        rail.append(f'<a href="#{sid}" title="{html.escape(title)}">{num}</a>')
    cls = 'section apparatus' if sid in apparatus else 'section'
    out_sections.append(
        f'<section id="{sid}" class="{cls}"><div class="wrap">'
        f'<div class="section-head"><p class="eyebrow">{eyebrow}</p><h2>{title}</h2></div>'
        f'<div class="prose">{rest}</div></div></section>')

title = meta.get('title', 'Доклад')
subtitle = meta.get('subtitle', '')
date = meta.get('date', '')

CSS = r"""
:root{--paper:#F3F4EF;--paper-raised:#FBFBF8;--ink:#171A1C;--ink-soft:#565D60;--ink-faint:#8B9190;--line:#DBDDD2;--line-strong:#C7CABC;--accent:#B54A24;--accent-ink:#7C3216;--steel:#33505E;--steel-soft:#DEE6E7;--serif:'Newsreader',Georgia,serif;--sans:'Manrope',system-ui,sans-serif;--mono:'JetBrains Mono',ui-monospace,monospace;--container:1120px;}
*,*::before,*::after{box-sizing:border-box}
html{background:var(--paper);scroll-behavior:smooth}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);font-size:16px;line-height:1.6;-webkit-font-smoothing:antialiased}
section[id]{scroll-margin-top:84px}
a{color:inherit}
.wrap{max-width:var(--container);margin:0 auto;padding:0 40px}
@media (max-width:720px){.wrap{padding:0 22px}}
.progress-track{position:fixed;top:0;left:0;width:100%;height:2px;background:var(--line);z-index:200}
.progress-fill{height:100%;width:0%;background:var(--accent)}
.topnav{position:sticky;top:2px;z-index:190;background:rgba(243,244,239,.92);backdrop-filter:blur(6px);border-bottom:1px solid var(--line)}
.topnav-inner{max-width:var(--container);margin:0 auto;padding:0 40px;display:flex;align-items:center;gap:28px;height:56px}
@media (max-width:720px){.topnav-inner{padding:0 22px;gap:18px}}
.topnav-mark{font-family:var(--mono);font-size:12px;letter-spacing:.03em;color:var(--ink);white-space:nowrap;text-decoration:none;font-weight:500}
.topnav-links{display:flex;gap:2px;overflow-x:auto;scrollbar-width:none}
.topnav-links::-webkit-scrollbar{display:none}
.topnav-links a{font-family:var(--mono);font-size:12px;white-space:nowrap;color:var(--ink-soft);text-decoration:none;padding:8px 10px;border-radius:2px;transition:color .15s,background-color .15s}
.topnav-links a:hover{color:var(--ink);background:var(--steel-soft)}
.topnav-links a.active{color:var(--accent-ink);font-weight:600}
.side-rail{position:fixed;right:22px;top:50%;transform:translateY(-50%);z-index:150;display:flex;flex-direction:column;gap:10px}
.side-rail a{font-family:var(--mono);font-size:10px;color:var(--ink-faint);text-decoration:none;width:24px;height:24px;display:flex;align-items:center;justify-content:center;border:1px solid transparent;border-radius:50%;transition:all .2s}
.side-rail a:hover{border-color:var(--line-strong);color:var(--ink)}
.side-rail a.active{color:var(--paper);background:var(--accent);border-color:var(--accent)}
@media (max-width:1240px){.side-rail{display:none}}
.hero-report{position:relative;overflow:hidden;padding:110px 0 80px}
.hero-report::before{content:"";position:absolute;inset:0;pointer-events:none;background-image:linear-gradient(rgba(23,26,28,.055) 1px,transparent 1px),linear-gradient(90deg,rgba(23,26,28,.055) 1px,transparent 1px);background-size:56px 56px;-webkit-mask-image:linear-gradient(to bottom,black,transparent 82%);mask-image:linear-gradient(to bottom,black,transparent 82%)}
.hero-inner{position:relative}
.eyebrow{font-family:var(--mono);font-size:12px;letter-spacing:.06em;color:var(--steel);margin:0 0 20px}
.hero-report h1{font-family:var(--serif);font-weight:500;font-size:clamp(2.4rem,5.6vw,4.4rem);line-height:1.04;letter-spacing:-.01em;margin:0 0 26px;max-width:16ch}
.hero-lead{font-size:19px;max-width:680px;margin:0 0 18px;line-height:1.6}
.hero-sub{font-size:15px;color:var(--ink-soft);max-width:640px;margin:0 0 36px}
.method-box{border:1px solid var(--line-strong);background:var(--paper-raised);padding:22px 26px;max-width:780px;border-radius:2px}
.method-box .eyebrow{margin-bottom:10px}
.method-box p{margin:0;font-size:14px;color:var(--ink-soft);line-height:1.65}
.section{padding:72px 0;border-top:1px solid var(--line)}
.section.apparatus{background:var(--paper-raised)}
.section-head{max-width:760px;margin-bottom:34px}
.section-head .eyebrow{margin-bottom:14px}
.section-head h2{font-family:var(--serif);font-weight:500;font-size:clamp(1.7rem,3.2vw,2.3rem);letter-spacing:-.01em;margin:0;line-height:1.15}
.prose{max-width:780px}
.prose p{margin:0 0 1.1em;font-size:16.5px;line-height:1.7}
.prose h3{font-family:var(--serif);font-weight:500;font-size:1.45rem;margin:2.2em 0 .7em;line-height:1.2}
.prose ol,.prose ul{padding-left:1.3em;margin:0 0 1.2em}
.prose li{margin:.35em 0;line-height:1.6}
.prose code{font-family:var(--mono);font-size:.86em;background:var(--steel-soft);padding:1px 5px;border-radius:2px}
.prose strong{font-weight:700}
.prose table{border-collapse:collapse;width:100%;max-width:100%;margin:1.4em 0 1.8em;font-size:14.5px;display:block;overflow-x:auto}
.prose th,.prose td{text-align:left;vertical-align:top;padding:9px 12px;border-bottom:1px solid var(--line)}
.prose th{font-family:var(--mono);font-size:11.5px;letter-spacing:.04em;color:var(--steel);font-weight:600;border-bottom:1px solid var(--line-strong)}
.prose tr:hover td{background:rgba(222,230,231,.35)}
a.cite{font-family:var(--mono);font-size:.72em;color:var(--accent-ink);text-decoration:none;vertical-align:super;line-height:0;padding:0 1px}
a.cite:hover{text-decoration:underline}
figure.diagram{margin:2em -10px 2.2em;padding:18px 10px 10px;border:1px solid var(--line);background:var(--paper-raised);border-radius:2px;max-width:none}
figure.diagram svg{width:100%;height:auto;display:block}
figure.diagram figcaption{font-size:13px;color:var(--ink-soft);margin:10px 10px 0;line-height:1.55}
.prose{max-width:none}
.prose > p,.prose > ol,.prose > ul,.prose > h3,.prose > dl{max-width:780px}
dl.glossary dt{font-weight:700;margin-top:1.1em}
dl.glossary dd{margin:.3em 0 0;color:var(--ink);font-size:15.5px;line-height:1.65}
ol.sources{font-size:14px;line-height:1.55;padding-left:2.2em;max-width:900px}
ol.sources li{margin:.45em 0;overflow-wrap:anywhere}
ol.sources li:target{background:var(--steel-soft);outline:2px solid var(--steel-soft)}
.closing{padding:60px 0 56px;border-top:1px solid var(--line)}
.closing-box{max-width:820px;padding:28px 32px;border:1px solid var(--line-strong);background:var(--paper-raised);border-radius:2px}
.closing-box p{margin:0 0 .6em;font-size:15px;line-height:1.7}
.closing-box p:last-child{margin:0;color:var(--ink-soft);font-size:13.5px}
@media print{.progress-track,.topnav,.side-rail{display:none}.section{padding:28px 0;page-break-inside:avoid}}
"""

JS = r"""
(function(){
  var fill=document.getElementById('progressFill');
  function up(){var h=document.documentElement;var s=h.scrollHeight-h.clientHeight;fill.style.width=(s>0?(h.scrollTop/s)*100:0)+'%';}
  document.addEventListener('scroll',up,{passive:true});up();
  var secs=[].slice.call(document.querySelectorAll('section[id]'));
  var links=[].slice.call(document.querySelectorAll('.topnav-links a, .side-rail a'));
  function setActive(id){links.forEach(function(a){a.classList.toggle('active',a.getAttribute('href')==='#'+id);});}
  if('IntersectionObserver' in window){
    var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){setActive(e.target.id);}});},{rootMargin:'-40% 0px -55% 0px',threshold:0});
    secs.forEach(function(s){io.observe(s);});
  }
})();
"""

doc = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)} — {html.escape(subtitle)}</title>
<meta name="description" content="Исследование-доклад: Joomla 6 как платформа для высоконагруженного новостного сайта — релизы, редакционный контур, конвейер новости, таксономия, нагрузка, видимость, живые порталы, русская и казахстанская экосистема.">
<meta name="author" content="Бейбит Саханов">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Manrope:wght@400;500;600;700&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<div class="progress-track"><div class="progress-fill" id="progressFill"></div></div>
<nav class="topnav" aria-label="Оглавление"><div class="topnav-inner">
<a class="topnav-mark" href="#top">joomla 6 · новостная редакция</a>
<div class="topnav-links">{''.join(nav)}</div>
</div></nav>
<aside class="side-rail" aria-hidden="true">{''.join(rail)}</aside>
<header class="hero-report" id="top"><div class="wrap hero-inner">
<p class="eyebrow">исследование-доклад · {html.escape(date)}</p>
<h1>{html.escape(title)}</h1>
<p class="hero-lead">{html.escape(subtitle).capitalize()}: что система даёт редакции в ядре, как выстроить конвейер новости и дерево смыслов, где она держит нагрузку и где требует инженерной работы.</p>
<p class="hero-sub">Автор — Бейбит Саханов, Астана. Все цифры и даты сверены по первоисточникам 8 октября 2026 года; расхождения и белые пятна вынесены в реестры, а не спрятаны в тексте.</p>
<div class="method-box"><p class="eyebrow">метод</p><p>Факты взяты с официальных страниц проекта Joomla, из руководства пользователя и разработчика, исходного кода ядра, карточек W3Techs и репозиториев расширений. Каждое утверждение несёт номер источника; список источников построен по первому упоминанию. Текст прошёл языковой прогон по четырём проходам и вычитку Редколлегией; типографика поставлена детерминированным типографом.</p></div>
</div></header>
<main>
{''.join(out_sections)}
</main>
<footer class="closing"><div class="wrap"><div class="closing-box">
<p>Доклад подготовлен как основание для выбора платформы новостного сайта. Рекомендации главы шестнадцатой самодостаточны; главы о конвейере и таксономии годятся как техническое задание на настройку.</p>
<p>Редакция 1.0 · 8 октября 2026 · Бейбит Саханов · материалы для внутреннего использования заказчика</p>
</div></div></footer>
<script>{JS}</script>
</body>
</html>
"""
open(OUT, 'w', encoding='utf-8').write(doc)
print('written', OUT, len(doc), 'chars;', n, 'глав;', len(nav), 'пунктов меню')
