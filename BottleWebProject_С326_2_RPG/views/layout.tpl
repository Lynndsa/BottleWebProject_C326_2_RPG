<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    
    <link rel="stylesheet" type="text/css" href="/static/content/bootstrap.min.css" />
    <link rel="stylesheet" type="text/css" href="/static/content/menu.css" />
    <link rel="stylesheet" type="text/css" href="/static/content/site.css" />
    <link rel="stylesheet" type="text/css" href="/static/content/main.css" />
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    
    <script src="/static/scripts/modernizr-2.6.2.js"></script>
</head>

<body>
    <nav class="navbar navbar-custom navbar-static-top">
        <div class="container navbar-container">
            
            <div class="navbar-header">
                <button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".navbar-collapse">
                    <span class="icon-bar"></span>
                    <span class="icon-bar"></span>
                    <span class="icon-bar"></span>
                </button>
                
                <a href="/" class="navbar-brand">
                    <svg class="brand-svg-icon" width="42" height="42" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <circle cx="12" cy="4" r="3" fill="#0ea5e9" stroke="#0284c7" stroke-width="2"/>
                        <circle cx="4" cy="18" r="3" fill="#0ea5e9" stroke="#0284c7" stroke-width="2"/>
                        <circle cx="20" cy="18" r="3" fill="#0ea5e9" stroke="#0284c7" stroke-width="2"/>
                        <line x1="10.8" y1="6.8" x2="5.2" y2="15.2" stroke="#0ea5e9" stroke-width="2.5" stroke-linecap="round"/>
                        <line x1="13.2" y1="6.8" x2="18.8" y2="15.2" stroke="#0ea5e9" stroke-width="2.5" stroke-linecap="round"/>
                        <line x1="7" y1="18" x2="17" y2="18" stroke="#0ea5e9" stroke-width="2.5" stroke-linecap="round"/>
                    </svg>
                    <span>Система моделирования</span>
                </a>
            </div>

            <div class="navbar-collapse collapse">
                <ul class="nav navbar-nav navbar-right-custom">
                    <li><a href="/">Главная</a></li>
                    <li><a href="/bfs">Модуль BFS</a></li>
                    <li><a href="/dfs">Модуль DFS</a></li>
                    <li><a href="/tsp">Модуль TSP</a></li>
                    <li><a href="/about">Об авторах</a></li>
                </ul>
            </div>

        </div>
    </nav>

    <div class="container body-content">
        {{!base}}
        
        <hr class="footer-divider" />
        <footer class="main-footer">
            <p>&copy; {{ year }} - Информационная система графового моделирования.</p>
        </footer>
    </div>

    <script src="/static/scripts/jquery-1.10.2.js"></script>
    <script src="/static/scripts/bootstrap.js"></script>
    <script src="/static/scripts/respond.js"></script>
</body>
</html>