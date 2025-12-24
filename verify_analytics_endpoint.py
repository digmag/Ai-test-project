#!/usr/bin/env python3
"""
Проверка добавления нового эндпоинта аналитики
"""
import sys
import os
import asyncio

# Импортируем наше приложение
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import main

def test_routes():
    """Проверка, что новый маршрут добавлен"""
    # Создаем приложение с отключенными настройками autoreload
    app = main.make_app()

    # Отключаем autoreload для предотвращения проблем с event loop
    app.settings['autoreload'] = False

    # Проверяем, что маршрут для аналитики добавлен
    routes = [rule.matcher.regex.pattern for rule in app.named_rules.values()]
    print("Доступные маршруты:")
    for route in routes:
        print(f"  {route}")

    # Проверяем, что маршрут /analytics присутствует
    analytics_route_exists = any("/analytics" in route for route in routes)
    print(f"\nМаршрут /analytics существует: {analytics_route_exists}")

    if analytics_route_exists:
        print("✓ Новый эндпоинт аналитики успешно добавлен")
        return True
    else:
        print("✗ Маршрут /analytics не найден")
        return False

if __name__ == "__main__":
    success = test_routes()
    if success:
        print("\nВсе проверки пройдены успешно!")
    else:
        print("\nПроизошла ошибка!")
        sys.exit(1)