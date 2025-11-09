/**
 * Онлайн меню ресторана - Главный модуль
 * @version 2.0
 * @author Sanjar Maxmudov
 */

(function() {
    'use strict';

    // Ожидаем полной загрузки DOM
    document.addEventListener('DOMContentLoaded', function () {
        const app = {
            // Конфигурация
            config: {
                currentPage: 1,
                categoryId: null,
                cacheTTL: 5 * 60 * 1000, // 5 минут
                itemsPerPage: 15,
                animationDelay: 100,
                messageDisplayTime: 600,
                messageHideDelay: 100
            },

            /**
             * Инициализация приложения
             */
            init() {
                this.bindEvents();
                this.loadCartCount();
                this.setupHistoryManagement();
                console.log('✅ Приложение инициализировано');
            },

            /**
             * Настройка управления историей браузера
             */
            setupHistoryManagement() {
                // Добавляем начальное состояние
                if (!window.history.state) {
                    window.history.replaceState({page: 'categories'}, '', window.location.href);
                }

                // Обработчик кнопки "Назад" браузера
                window.addEventListener('popstate', (event) => {
                    if (event.state && event.state.page === 'categories') {
                        this.returnToCategories();
                    } else if (event.state && event.state.page === 'dishes') {
                        // Перезагружаем блюда если были на странице блюд
                        if (this.config.categoryId) {
                            this.loadDishes(this.config.categoryId, this.config.currentPage);
                        }
                    } else {
                        // Если состояния нет, возвращаемся к категориям
                        this.returnToCategories();
                    }
                });
            },

            /**
             * Возврат к списку категорий
             */
            returnToCategories() {
                // Очищаем контейнеры
                $('#dishes').empty();
                $('#pagination').empty();

                // Показываем категории
                $('.categories, #restaurant-logo').fadeIn(300);

                // Сбрасываем состояние
                this.config.categoryId = null;
                $('.menu-title h2').text('Меню');
            },

            /**
             * Навешивание обработчиков событий
             */
            bindEvents() {
                $(document).on('click', '.category-btn', this.onCategoryClick.bind(this));
                $(document).on('click', '.add-to-cart-btn', this.onAddToCartClick.bind(this));
                $(document).on('click', '.dish-image', this.onDishImageClick.bind(this));
                $(document).on('click', '.prev-page', this.onPrevPageClick.bind(this));
                $(document).on('click', '.next-page', this.onNextPageClick.bind(this));
                $(document).on('click', '.menu-title', this.onMenuTitleClick.bind(this));
            },

            /**
             * Загрузка количества товаров в корзине при старте
             */
            loadCartCount() {
                $.ajax({
                    url: getCartUrl,
                    method: 'GET',
                    success: (response) => {
                        this.updateCartCount(response.total_quantity || 0);
                    },
                    error: (xhr, status, error) => {
                        console.error('Ошибка при загрузке корзины:', error);
                    }
                });
            },

            /**
             * Обработчик клика по категории
             */
            onCategoryClick(e) {
                const $button = $(e.currentTarget);
                this.config.categoryId = $button.data('id');
                this.config.currentPage = 1;

                // Добавляем состояние в историю браузера
                window.history.pushState({
                    page: 'dishes',
                    categoryId: this.config.categoryId
                }, '', `#category-${this.config.categoryId}`);

                // Анимация скрытия категорий
                $('.categories, #restaurant-logo').fadeOut(300, () => {
                    this.loadDishes(this.config.categoryId, this.config.currentPage);
                });
            },

            /**
             * Обработчик клика по кнопке "Добавить в корзину"
             */
            onAddToCartClick(e) {
                e.preventDefault();
                e.stopPropagation();

                const $btn = $(e.currentTarget);
                const dishId = $btn.data('dish-id');

                if (!dishId) {
                    this.showMessage('Ошибка: не указан ID блюда', 'error');
                    return;
                }

                // Отключаем кнопку на время запроса
                $btn.prop('disabled', true).addClass('loading');

                const addToCartUrlFinal = addToCartUrl.replace("0", dishId);

                $.ajax({
                    url: addToCartUrlFinal,
                    method: 'GET',
                    timeout: 10000,
                    success: (response) => {
                        if (response.success) {
                            this.showMessage(response.message, 'success');
                            this.updateCartCount(response.total_quantity);
                            this.highlightCart();

                            // Визуальная обратная связь
                            $btn.addClass('added');
                            setTimeout(() => $btn.removeClass('added'), 2000);
                        } else {
                            this.showMessage(response.message || 'Ошибка добавления', 'error');
                        }
                    },
                    error: (xhr) => {
                        let errorMessage = 'Ошибка при добавлении в корзину';

                        if (xhr.status === 404) {
                            errorMessage = 'Блюдо не найдено';
                        } else if (xhr.status === 0) {
                            errorMessage = 'Нет соединения с сервером';
                        } else if (xhr.responseJSON && xhr.responseJSON.error) {
                            errorMessage = xhr.responseJSON.error;
                        }

                        this.showMessage(errorMessage, 'error');
                        console.error('Ошибка добавления в корзину:', xhr);
                    },
                    complete: () => {
                        $btn.prop('disabled', false).removeClass('loading');
                    }
                });
            },

            /**
             * Обработчик клика по изображению блюда (открытие модалки)
             */
            onDishImageClick(e) {
                const imageUrl = $(e.currentTarget).attr('src');
                $('#modalDishImage').attr('src', imageUrl);
                $('#dishModal').modal('show');
            },

            /**
             * Обработчик клика "Предыдущая страница"
             */
            onPrevPageClick(e) {
                e.preventDefault();
                if (this.config.currentPage > 1) {
                    this.config.currentPage--;
                    this.loadDishes(this.config.categoryId, this.config.currentPage);
                }
            },

            /**
             * Обработчик клика "Следующая страница"
             */
            onNextPageClick(e) {
                e.preventDefault();
                this.config.currentPage++;
                this.loadDishes(this.config.categoryId, this.config.currentPage);
            },

            /**
             * Обработчик клика по заголовку меню (возврат к категориям)
             */
            onMenuTitleClick(e) {
                e.preventDefault();
                // Используем history.back() для возврата к категориям
                window.history.back();
            },

            /**
             * Загрузка блюд для категории с кешированием
             */
            loadDishes(categoryId, page = 1) {
                const cacheKey = `dishes_${categoryId}_${page}`;
                const cachedData = this.getCachedData(cacheKey);

                if (cachedData) {
                    this.renderDishes(cachedData);
                    return;
                }

                // Показываем индикатор загрузки
                this.showLoadingIndicator();

                $.ajax({
                    url: loadDishesUrl.replace("0", categoryId) + `?page=${page}`,
                    method: 'GET',
                    timeout: 15000,
                    success: (response) => {
                        if (response && response.dishes) {
                            this.setCachedData(cacheKey, response);
                            this.renderDishes(response);
                        } else {
                            this.showMessage('Нет данных для отображения', 'warning');
                        }
                    },
                    error: (xhr) => {
                        this.hideLoadingIndicator();

                        let errorMessage = 'Ошибка при загрузке блюд';

                        if (xhr.status === 404) {
                            errorMessage = 'Категория не найдена';
                        } else if (xhr.status === 0) {
                            errorMessage = 'Нет соединения с сервером';
                        } else if (xhr.responseJSON && xhr.responseJSON.error) {
                            errorMessage = xhr.responseJSON.error;
                        }

                        this.showMessage(errorMessage, 'error');
                        console.error('Ошибка загрузки данных:', xhr);
                    },
                    complete: () => {
                        this.hideLoadingIndicator();
                    }
                });
            },

            /**
             * Рендеринг блюд и пагинации
             */
            renderDishes(response) {
                if (!response || !response.dishes || response.dishes.length === 0) {
                    $('#dishes').html('<p class="text-center">Блюда в данной категории отсутствуют</p>');
                    return;
                }

                // Формируем HTML для блюд
                const dishesHtml = response.dishes.map(dish => `
                    <div class="col">
                        <div class="card h-80 dish-card p-2 mb-2" data-dish-id="${dish.id}">
                            <div class="dish-image-container">
                                <img src="${dish.image_url || '/static/images/no-image.png'}"
                                     alt="${this.escapeHtml(dish.name)}"
                                     class="dish-image"
                                     loading="lazy"
                                     onerror="this.src='/static/images/no-image.png'">
                            </div>
                            <div class="dish-info">
                                <h5 class="dish-title">${this.escapeHtml(dish.name)}</h5>
                                <p class="dish-description">${this.escapeHtml(dish.description || '')}</p>
                                <div class="d-flex justify-content-between align-items-center">
                                    <span class="dish-price">${dish.price} Sum</span>
                                    <button class="btn add-to-cart-btn"
                                            data-dish-id="${dish.id}"
                                            title="Добавить блюдо"
                                            aria-label="Добавить ${this.escapeHtml(dish.name)} в корзину">
                                        <i class="fas fa-shopping-cart fa-lg"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                `).join('');

                $('#dishes').html(dishesHtml);

                // Рендерим пагинацию
                this.renderPagination(response);

                // Анимация появления блюд
                this.animateDishes(response.dishes);

                // Обновляем заголовок
                $('.menu-title h2').text('Назад');
            },

            /**
             * Рендеринг пагинации
             */
            renderPagination(response) {
                const paginationHtml = `
                    <nav class="mt-3">
                        <ul class="pagination justify-content-center">
                            <li class="page-item ${!response.has_previous ? 'disabled' : ''}">
                                <a class="page-link prev-page" href="#" aria-label="Предыдущая">&laquo;</a>
                            </li>
                            <li class="page-item disabled">
                                <span class="page-link">Страница ${response.current_page} из ${response.total_pages}</span>
                            </li>
                            <li class="page-item ${!response.has_next ? 'disabled' : ''}">
                                <a class="page-link next-page" href="#" aria-label="Следующая">&raquo;</a>
                            </li>
                        </ul>
                    </nav>
                `;

                $('#pagination').html(paginationHtml);
            },

            /**
             * Анимация появления блюд
             */
            animateDishes(dishes) {
                dishes.forEach((dish, index) => {
                    setTimeout(() => {
                        $(`.dish-card[data-dish-id="${dish.id}"]`).addClass('visible');
                    }, index * this.config.animationDelay);
                });
            },

            /**
             * Показать сообщение пользователю
             */
            showMessage(message, type = 'success') {
                const $container = $('#message-container');
                const $text = $('#message-text');

                // Применяем стили в зависимости от типа
                $container.removeClass('success error warning');
                $container.addClass(type);

                $text.text(message);
                $container.fadeIn(this.config.messageHideDelay)
                    .delay(this.config.messageDisplayTime)
                    .fadeOut(this.config.messageHideDelay);
            },

            /**
             * Обновление счетчика корзины
             */
            updateCartCount(count) {
                $('#cart-count').text(count);

                if (count > 0) {
                    $('#cart-count').show();
                } else {
                    $('#cart-count').hide();
                }
            },

            /**
             * Подсветка корзины (анимация)
             */
            highlightCart() {
                const $cartIcon = $('.shopping-cart-lg');
                const $cartCount = $('#cart-count');

                // Анимация "тряски" корзины
                $cartIcon.addClass('shake');
                setTimeout(() => $cartIcon.removeClass('shake'), 600);

                // Анимация "прыжка" счетчика
                $cartCount.addClass('bounce');
                setTimeout(() => $cartCount.removeClass('bounce'), 600);
            },

            /**
             * Показать индикатор загрузки
             */
            showLoadingIndicator() {
                $('#dishes').html('<div class="text-center p-5"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Загрузка...</span></div></div>');
            },

            /**
             * Скрыть индикатор загрузки
             */
            hideLoadingIndicator() {
                // Индикатор будет заменен контентом или сообщением об ошибке
            },

            /**
             * Получить данные из кеша
             */
            getCachedData(key) {
                try {
                    const cachedItem = localStorage.getItem(key);
                    if (!cachedItem) return null;

                    const { timestamp, data } = JSON.parse(cachedItem);

                    if (Date.now() - timestamp < this.config.cacheTTL) {
                        return data;
                    } else {
                        localStorage.removeItem(key);
                        return null;
                    }
                } catch (error) {
                    console.error('Ошибка чтения кеша:', error);
                    return null;
                }
            },

            /**
             * Сохранить данные в кеш
             */
            setCachedData(key, data) {
                try {
                    const cacheItem = {
                        timestamp: Date.now(),
                        data: data
                    };
                    localStorage.setItem(key, JSON.stringify(cacheItem));
                } catch (error) {
                    console.error('Ошибка сохранения в кеш:', error);
                }
            },

            /**
             * Экранирование HTML для безопасности
             */
            escapeHtml(text) {
                if (!text) return '';

                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            }
        };

        // Запуск приложения
        app.init();
    });
})();