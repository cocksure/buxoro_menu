document.addEventListener('DOMContentLoaded', function () {
    $(document).ready(function () {
        let currentPage = 1;
        let categoryId = null;

        // Функция для загрузки блюд
        function loadDishes(categoryId, page = 1) {
            console.log("Loading dishes for category:", categoryId);
            $.ajax({
                url: loadDishesUrl.replace("0", categoryId) + `?page=${page}`,
                success: function (response) {
                    console.log("Dishes response:", response);  // Логируем данные
                    let dishes = response.dishes;
                    let dishesHtml = '';

                    if (dishes.length > 0) {
                        dishes.forEach(function (dish) {
                            if (dish.is_available) {
                                dishesHtml += `
                                    <div class="col">
                                        <div class="card h-100 dish-card p-2 mb-2">
                                            <div class="dish-image-container">
                                                <img src="${dish.image_url}" alt="${dish.name}" class="dish-image" style="cursor: pointer;" title="Нажмите, чтобы увеличить" loading="lazy">
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
                                    </div>`;
                            }
                        });
                    } else {
                        dishesHtml = '<p class="text-center">Нет доступных блюд в этой категории.</p>';
                    }

                    $('#dishes').html(dishesHtml);

                    // Обновляем пагинацию
                    let paginationHtml = `
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

                    // Обработчики событий для пагинации
                    $('.prev-page').click(function (e) {
                        e.preventDefault();
                        if (response.has_previous) loadDishes(categoryId, page - 1);
                    });

                    $('.next-page').click(function (e) {
                        e.preventDefault();
                        if (response.has_next) loadDishes(categoryId, page + 1);
                    });
                },
                error: function (xhr, status, error) {
                    console.error("Ошибка при запросе данных: " + error);
                }
            });
        }

        // Открытие модального окна при клике на изображение
        $(document).on('click', '.dish-image', function () {
            const imageUrl = $(this).attr('src'); // Получаем URL изображения
            $('#modalDishImage').attr('src', imageUrl); // Устанавливаем URL в модальное окно
            $('#dishModal').modal('show'); // Открываем модальное окно
        });

        // Загружаем блюда при выборе категории
        $('.category-btn').click(function () {
            categoryId = $(this).data('id');
            currentPage = 1; // Сбрасываем на первую страницу
            loadDishes(categoryId, currentPage);

            $('#restaurant-logo').fadeOut(300); // Скрываем логотип
        });

        // Обработчик клика по кнопке "Добавить в корзину"
        $(document).on('click', '.add-to-cart-btn', function () {
            var dishId = $(this).data('dish-id'); // Получаем ID блюда

            // Проверяем, что dishId передается правильно
            console.log("Dish ID: ", dishId);

            // Формируем финальный URL для запроса
            var addToCartUrlFinal = addToCartUrl.replace("0", dishId);
            console.log("Final URL: ", addToCartUrlFinal);

            // Отправляем AJAX-запрос на добавление в корзину
            $.ajax({
                url: addToCartUrlFinal,
                method: "GET",
                success: function (response) {
                    if (response.success) {
                        // Покажем сообщение о добавлении в корзину
                        showMessage(response.message);

                        // Обновляем количество товаров в корзине
                        $('#cart-count').text(response.total_quantity); // Обновляем счётчик в интерфейсе
                    } else {
                        console.error("Ошибка при добавлении в корзину:", response.message);
                    }
                },
                error: function (xhr, status, error) {
                    console.error("Ошибка при запросе добавления в корзину: " + error);
                }
            });
        });


        // Функция для отображения сообщения
        function showMessage(message) {
            $('#message-text').text(message);
            $('#message-container').fadeIn(300);

            // Скрыть сообщение через 3 секунды
            setTimeout(function () {
                $('#message-container').fadeOut(300);
            }, 1500);
        }
    });
});
