// Ожидаем полной загрузки DOM перед выполнением скрипта
document.addEventListener('DOMContentLoaded', function () {
    const app = {
        currentPage: 1, // Текущая страница пагинации
        categoryId: null, // ID текущей категории блюд
        cacheTTL: 5 * 60 * 1000, // Время жизни кэша (5 минут)

        // Инициализация приложения
        init() {
            // Если больше не используете карусель, можно убрать initSwiper
            // this.initSwiper();
            this.bindEvents(); // Навешивание обработчиков событий
        },

        // Навешивание обработчиков событий
        bindEvents() {
            $(document).on('click', '.category-btn', this.onCategoryClick.bind(this)); // Клик по категории
            $(document).on('click', '.add-to-cart-btn', this.onAddToCartClick.bind(this)); // Клик по кнопке "Добавить в корзину"
            $(document).on('click', '.dish-image', this.onDishImageClick.bind(this)); // Клик по изображению блюда
            $(document).on('click', '.prev-page', this.onPrevPageClick.bind(this)); // Клик по кнопке "Предыдущая страница"
            $(document).on('click', '.next-page', this.onNextPageClick.bind(this)); // Клик по кнопке "Следующая страница"
            // Обработчик клика по заголовку меню для возврата к списку категорий
            $(document).on('click', '.menu-title', this.onMenuTitleClick.bind(this));
        },

        // Обработчик клика по категории
        onCategoryClick(e) {
            this.categoryId = $(e.currentTarget).data('id'); // Получаем ID категории
            this.currentPage = 1; // Сбрасываем текущую страницу на первую

            // Скрываем контейнер с категориями (укажите правильный селектор, например, если у вас <div class="categories">)
            $('.categories').fadeOut(300);
            // Если требуется, скрываем и логотип ресторана
            $('#restaurant-logo').fadeOut(300);

            // Загружаем блюда для выбранной категории
            this.loadDishes(this.categoryId, this.currentPage);
        },

        // Обработчик клика по кнопке "Добавить в корзину"
        onAddToCartClick(e) {
            const $btn = $(e.currentTarget);
            const dishId = $btn.data('dish-id'); // Получаем ID блюда
            const addToCartUrlFinal = addToCartUrl.replace("0", dishId); // Формируем URL для добавления в корзину

            $.ajax({
                url: addToCartUrlFinal,
                method: "GET",
                success: (response) => {
                    if (response.success) {
                        this.showMessage(response.message);
                        this.updateCartCount(response.total_quantity);
                        this.highlightCart();
                    } else {
                        console.error("Ошибка при добавлении в корзину:", response.message);
                    }
                },
                error: (xhr, status, error) => {
                    console.error("Ошибка при запросе добавления в корзину: " + error);
                }
            });
        },

        // Обработчик клика по изображению блюда
        onDishImageClick(e) {
            const imageUrl = $(e.currentTarget).attr('src'); // Получаем URL изображения
            $('#modalDishImage').attr('src', imageUrl);
            $('#dishModal').modal('show');
        },

        // Обработчик клика по кнопке "Предыдущая страница"
        onPrevPageClick(e) {
            e.preventDefault();
            if (this.currentPage > 1) {
                this.currentPage--;
                this.loadDishes(this.categoryId, this.currentPage);
            }
        },

        // Обработчик клика по кнопке "Следующая страница"
        onNextPageClick(e) {
            e.preventDefault();
            this.currentPage++;
            this.loadDishes(this.categoryId, this.currentPage);
        },

        // Обработчик клика по заголовку меню для возврата к списку категорий
        onMenuTitleClick(e) {
            const headerText = $(e.currentTarget).find('h2').text().trim();
            if (headerText === 'Назад') {
                // Очищаем контейнеры с блюдами и пагинацией
                $('#dishes').empty();
                $('#pagination').empty();
                // Показываем список категорий
                $('.categories').fadeIn(300);
                // При необходимости, возвращаем логотип ресторана
                $('#restaurant-logo').fadeIn(300);
                // Сбрасываем выбранную категорию
                this.categoryId = null;
                // Меняем текст заголовка обратно на "Меню"
                $(e.currentTarget).find('h2').text('Меню');
            }
        },

        // Загрузка блюд для указанной категории и страницы
        loadDishes(categoryId, page = 1) {
            const cacheKey = `dishes_${categoryId}_${page}`;
            const cachedData = localStorage.getItem(cacheKey);

            if (cachedData) {
                const {timestamp, data} = JSON.parse(cachedData);
                if (Date.now() - timestamp < this.cacheTTL) {
                    this.renderDishes(data);
                    return;
                } else {
                    localStorage.removeItem(cacheKey);
                }
            }

            $.ajax({
                url: loadDishesUrl.replace("0", categoryId) + `?page=${page}`,
                success: (response) => {
                    localStorage.setItem(cacheKey, JSON.stringify({timestamp: Date.now(), data: response}));
                    this.renderDishes(response);
                },
                error: (xhr, status, error) => {
                    console.error("Ошибка при запросе данных: " + error);
                    this.showMessage("Ошибка при загрузке данных. Пожалуйста, попробуйте позже.");
                }
            });
        },

        // Рендеринг блюд и пагинации
        renderDishes(response) {
            let dishesHtml = response.dishes.map(dish => `
        <div class="col">
            <div class="card h-100 dish-card p-2 mb-2" data-dish-id="${dish.id}">
                <div class="dish-image-container">
                    <img src="${dish.image_url}" alt="${dish.name}" class="dish-image" loading="lazy">
                </div>
                <div class="dish-info">
                    <h5 class="dish-title">${dish.name}</h5>
                    <p class="dish-description">${dish.description}</p>
                    <div class="d-flex justify-content-between align-items-center">
                        <span class="dish-price">${dish.price} Sum</span>
                        <button class="btn btn add-to-cart-btn" data-dish-id="${dish.id}" title="Добавить блюдо">
                            <i class="fas fa-shopping-cart fa-lg"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `).join('');

            $('#dishes').html(dishesHtml);

            const paginationHtml = `
        <nav class="mt-3">
            <ul class="pagination justify-content-center">
                <li class="page-item ${!response.has_previous ? 'disabled' : ''}">
                    <a class="page-link prev-page" href="#" aria-label="Previous">&laquo;</a>
                </li>
                <li class="page-item disabled">
                    <span class="page-link">Страница ${response.current_page} из ${response.total_pages}</span>
                </li>
                <li class="page-item ${!response.has_next ? 'disabled' : ''}">
                    <a class="page-link next-page" href="#" aria-label="Next">&raquo;</a>
                </li>
            </ul>
        </nav>`;
            $('#pagination').html(paginationHtml);

            // Анимация появления блюд
            response.dishes.forEach((dish, index) => {
                setTimeout(() => $(`.dish-card[data-dish-id="${dish.id}"]`).addClass('visible'), index * 100);
            });

            // Обновляем заголовок меню на "Назад"
            $('.menu-title h2').text('Назад');
        },

        // Показ сообщения пользователю
showMessage(message) {
    $('#message-text').text(message);
    $('#message-container').fadeIn(100).delay(600).fadeOut(100);
},

        // Обновление счетчика корзины
        updateCartCount(count) {
            $('#cart-count').text(count);
        },

        // Подсветка корзины
        highlightCart() {
            $('#cart-icon').addClass('highlight');
            setTimeout(() => $('#cart-icon').removeClass('highlight'), 1000);
        }
    };

    app.init();
});