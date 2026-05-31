% rebase('layout.tpl', title='Об авторах', year=year)

<link rel="stylesheet" type="text/css" href="/static/content/menu.css" />
<link rel="stylesheet" type="text/css" href="/static/content/about.css" /> 

<main class="about-system-wrapper">
    <div class="page-header">
        <h1>Об авторах</h1>
        <small>разработчики системы моделирования</small>
        <p class="lead">Команда программистов и исследователей, создавших комплекс визуализации графовых алгоритмов.</p>
    </div>

    <div class="card-panel about-project-card">
        <h2>О системе</h2>
        <p>Наша информационная система создана для наглядного интерактивного изучения базовых и комплексных алгоритмов теории графов. Она позволяет не просто производить сухие математические расчеты, но и визуализировать пошаговое выполнение процессов — от волнового заражения сети до оптимизации сложных коммерческих маршрутов.</p>
    </div>

    <div class="team-grid">
        
        <section class="about-card">
            <div class="about-card-header">
                <div class="avatar-placeholder">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 17.9391 4 19V21" stroke="#0284c7" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        <circle cx="12" cy="7" r="4" stroke="#0284c7" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
                <div>
                    <h3>Гуляев Андрей</h3>
                    <span class="role-badge badge-blue">Team Lead / Backend</span>
                </div>
            </div>
            <div class="about-card-body">
                <p>Проектировал общую архитектуру серверной части веб-приложения, управлял интеграцией модулей и обеспечивал стабильность системы.</p>
                <ul class="contribution-list">
                    <li>Разработка логики маршрутизации и интеграция шаблонов Bottle/Jinja2.</li>
                    <li>Оптимизация производительности серверной части симулятора.</li>
                    <li>Проектирование API для динамического обмена данными графов.</li>
                </ul>
            </div>
            <div class="about-card-footer">
                <div class="social-links-wrapper">
                    <a href="https://t.me/souldarkers" target="_blank" class="btn-social btn-tg">
                        <img src="/static/content/image/telegram.svg" alt="TG" class="social-icon"> Telegram
                    </a>
                    <a href="https://github.com/Lynndsa" target="_blank" class="btn-social btn-gh">
                        <img src="/static/content/image/github.svg" alt="GH" class="social-icon"> GitHub
                    </a>
                </div>
            </div>
        </section>

        <section class="about-card">
            <div class="about-card-header">
                <div class="avatar-placeholder">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 17.9391 4 19V21" stroke="#0891b2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        <circle cx="12" cy="7" r="4" stroke="#0891b2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
                <div>
                    <h3>Романова Лада</h3>
                    <span class="role-badge badge-cyan">Algorithm Engineer</span>
                </div>
            </div>
            <div class="about-card-body">
                <p>Отвечала за математическую точность, реализацию и оптимизацию графовых алгоритмов (BFS, DFS, Дейкстра, TSP).</p>
                <ul class="contribution-list">
                    <li>Реализация комбинированного метода Дейкстры + Brute Force для TSP.</li>
                    <li>Модификация алгоритма BFS под вероятностное заражение сети.</li>
                    <li>Валидация матриц смежности и парсинг импортируемых файлов <code>.txt</code>.</li>
                </ul>
            </div>
            <div class="about-card-footer">
                <div class="social-links-wrapper">
                    <a href="https://t.me/ladushsha" target="_blank" class="btn-social btn-tg">
                        <img src="/static/content/image/telegram.svg" alt="TG" class="social-icon"> Telegram
                    </a>
                    <a href="https://github.com/romanovalada" target="_blank" class="btn-social btn-gh">
                        <img src="/static/content/image/github.svg" alt="GH" class="social-icon"> GitHub
                    </a>
                </div>
            </div>
        </section>

        <section class="about-card">
            <div class="about-card-header">
                <div class="avatar-placeholder">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 17.9391 4 19V21" stroke="#14b8a6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        <circle cx="12" cy="7" r="4" stroke="#0891b2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
                <div>
                    <h3>Пономарёва Анастасия</h3>
                    <span class="role-badge badge-teal">Frontend / UI UX</span>
                </div>
            </div>
            <div class="about-card-body">
                <p>Занималась созданием адаптивного интерфейса системы, версткой компонентов и интерактивной генерацией SVG-схем графов.</p>
                <ul class="contribution-list">
                    <li>Разработка дизайн-системы, CSS-переменных и кастомных анимаций.</li>
                    <li>Динамический рендеринг рёбер и вершин графа в браузере.</li>
                    <li>Обеспечение кроссбраузерности и адаптивности для мобильных устройств.</li>
                </ul>
            </div>
            <div class="about-card-footer">
                <div class="social-links-wrapper">
                    <a href="https://t.me/anasiasiaaa" target="_blank" class="btn-social btn-tg">
                        <img src="/static/content/image/telegram.svg" alt="TG" class="social-icon"> Telegram
                    </a>
                    <a href="https://github.com/anasiasiaaa" target="_blank" class="btn-social btn-gh">
                        <img src="/static/content/image/github.svg" alt="GH" class="social-icon"> GitHub
                    </a>
                </div>
            </div>
        </section>

    </div>
</main>

<style>
:root {
    --blue-50: #f0f9ff;
    --blue-100: #e0f2fe;
    --blue-200: #bae6fd;
    --blue-400: #38bdf8;
    --blue-500: #0ea5e9;
    --blue-600: #0284c7;
    --blue-700: #0369a1;
    --cyan-500: #06b6d4;
    --cyan-600: #0891b2;
    --teal-500: #14b8a6;
    --text-main: #0f172a;
    --text-muted: #64748b;
    --radius: 16px;
    --shadow-sm: 0 2px 8px rgba(14, 165, 233, 0.08);
    --shadow-lg: 0 12px 24px rgba(14, 165, 233, 0.15);
    
    /* Брендовые соцсети */
    --color-tg: #24A1DE;
    --color-tg-hover: #1d82b3;
    --color-gh: #24292e;
    --color-gh-hover: #171a1d;
}

.about-system-wrapper {
    max-width: 100%;
    margin: 0 auto;
    padding: 4rem 0 6rem;
}

.page-header {
    border-bottom: 3px solid var(--blue-100) !important;
    padding-bottom: 2.5rem !important;
    margin: 2rem 0 4rem !important;
}
.page-header h1 {
    font-size: 3.5rem !important;
    font-weight: 700;
    color: var(--blue-600);
    margin: 0 0 0.75rem;
}
.page-header small {
    display: block;
    font-size: 2.0rem !important;
    font-weight: 400;
    color: var(--text-muted);
    margin-top: 0.5rem;
}
.page-header .lead {
    font-size: 1.8rem !important;
    color: var(--text-muted);
    margin: 1.25rem 0 0;
    max-width: 950px;
}

/* Общая карточка */
.card-panel.about-project-card {
    background: #fff;
    border: 2px solid var(--blue-100);
    border-radius: var(--radius);
    padding: 3rem;
    margin-bottom: 4rem;
    box-shadow: var(--shadow-sm);
}
.card-panel.about-project-card h2 {
    font-size: 2.3rem;
    color: var(--blue-600);
    margin-top: 0;
    margin-bottom: 1.5rem;
    font-weight: 700;
}
.card-panel.about-project-card p {
    font-size: 1.55rem;
    line-height: 1.7;
    color: #334155;
    margin: 0;
}

/* Сетка карточек */
.team-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(460px, 1fr));
    gap: 3.5rem;
    align-items: stretch;
}

/* Карточки авторов */
.about-card {
    background: #fff;
    border: 2px solid var(--blue-100);
    border-radius: var(--radius);
    box-shadow: var(--shadow-sm);
    transition: all 0.3s ease;
    display: flex;
    flex-direction: column;
    height: 100%;
    overflow: hidden;
}
.about-card:hover {
    transform: translateY(-8px);
    box-shadow: var(--shadow-lg);
    border-color: var(--blue-400);
}

.about-card-header {
    background: linear-gradient(135deg, var(--blue-50) 0%, var(--blue-100) 100%);
    border-bottom: 2px solid var(--blue-100);
    padding: 2.2rem 2.5rem;
    display: flex;
    align-items: center;
    gap: 20px;
}
.about-card-header h3 {
    font-size: 2.1rem;
    font-weight: 700;
    color: var(--text-main);
    margin: 0 0 0.5rem 0;
}

.avatar-placeholder {
    width: 64px;
    height: 64px;
    background: #fff;
    border: 2px solid var(--blue-200);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 10px rgba(14, 165, 233, 0.1);
    flex-shrink: 0;
}

.role-badge {
    display: inline-block;
    padding: 0.4em 1em;
    font-size: 1.1rem;
    font-weight: 700;
    border-radius: 8px;
    color: #fff;
}
.badge-blue { background: var(--blue-500); }
.badge-cyan { background: var(--cyan-500); }
.badge-teal { background: var(--teal-500); }

.about-card-body {
    padding: 2.5rem;
    flex: 1;
    display: flex;
    flex-direction: column;
}
.about-card-body p {
    margin: 0 0 2rem 0;
    color: var(--text-main);
    font-size: 1.5rem;
    line-height: 1.6;
}

.contribution-list {
    margin: 0;
    padding-left: 25px;
}
.contribution-list li {
    padding: 0.6rem 0;
    font-size: 1.4rem;
    color: #475569;
    position: relative;
    list-style-type: square;
}

/* Стилизация кнопок соцсетей в футере */
.about-card-footer {
    background: #fafafa;
    border-top: 2px solid var(--blue-100);
    padding: 2rem 2.5rem;
    margin-top: auto;
}

.social-links-wrapper {
    display: flex;
    gap: 12px;
}

.btn-social {
    flex: 1;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 1rem 1.5rem;
    font-size: 1.3rem;
    font-weight: 600;
    border-radius: 10px;
    color: #fff !important;
    text-decoration: none !important;
    transition: background-color 0.2s ease, transform 0.1s ease;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.btn-social:active {
    transform: scale(0.98);
}

.btn-tg {
    background-color: var(--color-tg);
}
.btn-tg:hover {
    background-color: var(--color-tg-hover);
}

.btn-gh {
    background-color: var(--color-gh);
}
.btn-gh:hover {
    background-color: var(--color-gh-hover);
}

/* Стили для картинок-иконок внутри кнопок */
.social-icon {
    width: 20px;
    height: 20px;
    display: inline-block;
    vertical-align: middle;
    /* Этот фильтр делает любую черную картинку абсолютно белой */
    filter: brightness(0) invert(1); 
}

/* Анимации */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.about-card {
    animation: fadeInUp 0.5s ease backwards;
}
.about-card:nth-child(1) { animation-delay: 0.1s; }
.about-card:nth-child(2) { animation-delay: 0.2s; }
.about-card:nth-child(3) { animation-delay: 0.3s; }

@media (max-width: 991px) {
    .team-grid {
        grid-template-columns: 1fr;
    }
    .about-system-wrapper {
        padding: 3rem 1.5rem 4rem;
    }
    .social-links-wrapper {
        flex-direction: column;
    }
}
</style>