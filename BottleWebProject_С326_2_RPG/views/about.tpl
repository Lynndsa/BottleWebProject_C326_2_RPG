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
