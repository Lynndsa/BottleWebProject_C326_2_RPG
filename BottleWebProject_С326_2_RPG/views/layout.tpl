<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} - GraphLabs</title>
    
    <link rel="stylesheet" type="text/css" href="/static/content/bootstrap.min.css" />
    <link rel="stylesheet" type="text/css" href="/static/content/menu.css" />
    <link rel="stylesheet" type="text/css" href="/static/content/site.css" />
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
                    <span class="brand-icon">☤</span> GraphLabs
                </a>
            </div>

            <div class="navbar-collapse collapse">
                <ul class="nav navbar-nav">
                    <li><a href="/">Главная</a></li>
                    <li><a href="/bfs">Модуль BFS (Вирус)</a></li>
                    <li><a href="/dfs">Модуль DFS (Блокчейн)</a></li>
                    <li><a href="/tsp">Модуль TSP (Экскурсии)</a></li>
                    <li><a href="/about">Об авторах</a></li>
                </ul>
            </div>

        </div>
    </nav>

    <div class="container body-content">
        {{base}}
        
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