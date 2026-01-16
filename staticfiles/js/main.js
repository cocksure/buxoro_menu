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
                // Закрываем все модальные окна
                this.closeModal();
                this.closeEditModal();

                // Очищаем контейнеры
                $('#dishes').empty();
                $('#pagination').empty();

                // Показываем категории и скрываем поиск и кнопку "Назад"
                $('.categories, #restaurant-logo').fadeIn(300);
                $('.search-container-header').fadeOut(200);
                $('.menu-title').fadeOut(200, function() {
                    $(this).addClass('d-none');
                });
                $('#dish-search').val('');
                $('#clear-search').hide();

                // Сбрасываем состояние
                this.config.categoryId = null;
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
                $(document).on('click', '.edit-dish-btn', this.onEditDishClick.bind(this));

                // Обработчики для поиска
                $('#dish-search').on('input', this.debounce(this.onSearchInput.bind(this), 300));
                $('#clear-search').on('click', this.onClearSearch.bind(this));
            },

            /**
             * Debounce функция для оптимизации поиска
             */
            debounce(func, wait) {
                let timeout;
                return function executedFunction(...args) {
                    const later = () => {
                        clearTimeout(timeout);
                        func(...args);
                    };
                    clearTimeout(timeout);
                    timeout = setTimeout(later, wait);
                };
            },

            /**
             * Обработчик ввода в поисковую строку
             */
            onSearchInput(e) {
                const searchTerm = $(e.target).val().toLowerCase().trim();

                if (searchTerm.length > 0) {
                    $('#clear-search').fadeIn(200);
                    this.filterDishes(searchTerm);
                } else {
                    $('#clear-search').fadeOut(200);
                    this.showAllDishes();
                }
            },

            /**
             * Очистка поискового запроса
             */
            onClearSearch() {
                $('#dish-search').val('').focus();
                $('#clear-search').fadeOut(200);
                this.showAllDishes();
            },

            /**
             * Фильтрация блюд по поисковому запросу
             */
            filterDishes(searchTerm) {
                let visibleCount = 0;

                $('.dish-card').each(function() {
                    const dishName = $(this).find('.dish-title').text().toLowerCase();
                    const dishDesc = $(this).find('.dish-description').text().toLowerCase();

                    if (dishName.includes(searchTerm) || dishDesc.includes(searchTerm)) {
                        $(this).parent().fadeIn(300);
                        visibleCount++;
                    } else {
                        $(this).parent().fadeOut(300);
                    }
                });

                // Показываем сообщение если ничего не найдено
                if (visibleCount === 0 && $('.dish-card').length > 0) {
                    if ($('#no-results').length === 0) {
                        $('#dishes').append(`
                            <div id="no-results" class="col-12 text-center p-5">
                                <i class="fas fa-search fa-3x text-muted mb-3"></i>
                                <h4>Ничего не найдено</h4>
                                <p class="text-muted">Попробуйте изменить поисковый запрос</p>
                            </div>
                        `);
                    }
                } else {
                    $('#no-results').remove();
                }
            },

            /**
             * Показать все блюда
             */
            showAllDishes() {
                $('.dish-card').parent().fadeIn(300);
                $('#no-results').remove();
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

                // Открываем кастомное модальное окно
                this.openModal();
            },

            /**
             * Открыть модальное окно
             */
            openModal() {
                const $modal = $('#dishModal');
                $modal.fadeIn(300).addClass('active');

                // Блокируем прокрутку body
                $('body').css('overflow', 'hidden');

                // Обработчики закрытия
                $('.custom-modal-backdrop, .custom-modal-image, .custom-modal-close').off('click').on('click', (e) => {
                    this.closeModal();
                });

                // Закрытие по Esc
                $(document).off('keydown.modal').on('keydown.modal', (e) => {
                    if (e.key === 'Escape') {
                        this.closeModal();
                    }
                });
            },

            /**
             * Закрыть модальное окно
             */
            closeModal() {
                const $modal = $('#dishModal');
                $modal.removeClass('active').fadeOut(300);

                // Разблокируем прокрутку body
                $('body').css('overflow', '');

                // Удаляем обработчики
                $(document).off('keydown.modal');
            },

            /**
             * Обработчик клика по кнопке редактирования блюда
             */
            onEditDishClick(e) {
                e.preventDefault();
                e.stopPropagation();

                const $btn = $(e.currentTarget);
                const dishData = {
                    id: $btn.data('dish-id'),
                    name: $btn.data('dish-name'),
                    description: $btn.data('dish-description'),
                    price: $btn.data('dish-price'),
                    image: $btn.data('dish-image'),
                    is_available: $btn.data('dish-available')
                };

                this.openEditModal(dishData);
            },

            /**
             * Открыть модальное окно редактирования блюда
             */
            openEditModal(dishData) {
                // Заполняем форму данными
                $('#edit-dish-id').val(dishData.id);
                $('#edit-dish-name').val(dishData.name);
                $('#edit-dish-description').val(dishData.description);
                $('#edit-dish-price').val(dishData.price);
                $('#edit-dish-available').prop('checked', dishData.is_available);

                // Показываем превью изображения если есть
                if (dishData.image) {
                    $('#edit-dish-image-preview').attr('src', dishData.image).show();
                } else {
                    $('#edit-dish-image-preview').hide();
                }

                // Показываем модальное окно
                const $modal = $('#editDishModal');
                $modal.fadeIn(300).addClass('active');
                $('body').css('overflow', 'hidden');

                // Обработчики закрытия
                $('.edit-modal-backdrop, .edit-modal-close').off('click').on('click', () => {
                    this.closeEditModal();
                });

                // Закрытие по Esc
                $(document).off('keydown.editmodal').on('keydown.editmodal', (e) => {
                    if (e.key === 'Escape') {
                        this.closeEditModal();
                    }
                });

                // Обработчик отправки формы
                $('#edit-dish-form').off('submit').on('submit', (e) => {
                    e.preventDefault();
                    this.saveDishChanges();
                });
            },

            /**
             * Закрыть модальное окно редактирования
             */
            closeEditModal() {
                const $modal = $('#editDishModal');
                $modal.removeClass('active').fadeOut(300);
                $('body').css('overflow', '');
                $(document).off('keydown.editmodal');
            },

            /**
             * Сохранить изменения блюда
             */
            saveDishChanges() {
                const formData = new FormData($('#edit-dish-form')[0]);

                // Добавляем секретный ключ для авторизации
                formData.append('edit_key', editSecretKey);

                $.ajax({
                    url: '/update-dish/',
                    method: 'POST',
                    data: formData,
                    processData: false,
                    contentType: false,
                    success: (response) => {
                        if (response.success) {
                            this.showMessage(response.message || 'Блюдо успешно обновлено!', 'success');
                            this.closeEditModal();

                            // Очищаем кеш и перезагружаем блюда
                            localStorage.clear();
                            this.loadDishes(this.config.categoryId, this.config.currentPage);
                        } else {
                            this.showMessage(response.error || 'Ошибка при сохранении', 'error');
                        }
                    },
                    error: (xhr) => {
                        let errorMessage = 'Ошибка при сохранении изменений';

                        if (xhr.status === 403) {
                            errorMessage = 'Доступ запрещен';
                        } else if (xhr.responseJSON && xhr.responseJSON.error) {
                            errorMessage = xhr.responseJSON.error;
                        }

                        this.showMessage(errorMessage, 'error');
                        console.error('Ошибка:', xhr);
                    }
                });
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
                // Напрямую возвращаемся к главной странице
                this.returnToCategories();

                // Обновляем историю браузера
                window.history.pushState({page: 'categories'}, '', window.location.pathname + window.location.search);
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
                        <div class="card h-70 dish-card" data-dish-id="${dish.id}">
                            <div class="dish-image-container">
                                <img src="${dish.image_url || '/static/images/no-image.png'}"
                                     alt="${this.escapeHtml(dish.name)}"
                                     class="dish-image"
                                     loading="lazy"
                                     onerror="this.onerror=null; this.src='data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 width=%27400%27 height=%27300%27%3E%3Crect fill=%27%23f0f0f0%27 width=%27400%27 height=%27300%27/%3E%3Ctext fill=%27%23999%27 font-family=%27sans-serif%27 font-size=%2724%27 dy=%2710.5%27 font-weight=%27bold%27 x=%2750%25%27 y=%2750%25%27 text-anchor=%27middle%27%3E%D0%9D%D0%B5%D1%82 %D1%84%D0%BE%D1%82%D0%BE%3C/text%3E%3C/svg%3E';">
                            </div>
                            <div class="dish-info">
                                <h5 class="dish-title">${this.escapeHtml(dish.name)}</h5>
                                <p class="dish-description">${this.escapeHtml(dish.description || '')}</p>
                                <div class="d-flex justify-content-between align-items-center">
                                    <span class="dish-price">${dish.price} Sum</span>
                                    <div class="d-flex gap-2">
                                        ${isEditMode ? `
                                            <button class="btn edit-dish-btn"
                                                    data-dish-id="${dish.id}"
                                                    data-dish-name="${this.escapeHtml(dish.name)}"
                                                    data-dish-description="${this.escapeHtml(dish.description || '')}"
                                                    data-dish-price="${dish.price}"
                                                    data-dish-image="${dish.image_url || ''}"
                                                    data-dish-available="${dish.is_available}"
                                                    title="Редактировать блюдо"
                                                    aria-label="Редактировать ${this.escapeHtml(dish.name)}">
                                                <i class="fas fa-pen"></i>
                                            </button>
                                        ` : ''}
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
                    </div>
                `).join('');

                $('#dishes').html(dishesHtml);

                // Рендерим пагинацию
                this.renderPagination(response);

                // Анимация появления блюд
                this.animateDishes(response.dishes);

                // Показываем поиск и кнопку "Назад"
                $('.search-container-header').fadeIn(300);
                $('.menu-title').removeClass('d-none').fadeIn(300);
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
             * Показать индикатор загрузки (Skeleton)
             */
            showLoadingIndicator() {
                const skeletonCount = 6; // Количество skeleton карточек
                const skeletonHtml = Array(skeletonCount).fill(0).map(() => `
                    <div class="col">
                        <div class="skeleton-dish-card">
                            <div class="skeleton-image"></div>
                            <div class="skeleton-info">
                                <div class="skeleton skeleton-title"></div>
                                <div class="skeleton skeleton-description"></div>
                                <div class="skeleton skeleton-description" style="width: 80%;"></div>
                                <div class="skeleton skeleton-price"></div>
                            </div>
                        </div>
                    </div>
                `).join('');

                $('#dishes').html(skeletonHtml);
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