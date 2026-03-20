from statemachine import State, StateMachine


class DocumentScanner(StateMachine):
    "Конечный автомат для сканирования документов с проверкой количества страниц."

    # Состояния
    готов_к_сканированию = State(initial=True)
    сканирование_в_процессе = State()
    сканирование_завершено = State()

    # Внутреннее свойство - счетчик страниц
    page_counter = 0

    # Переходы
    start_scan = готов_к_сканированию.to(сканирование_в_процессе)

    # Один и тот же метод `scan_page` вызывает разные переходы в зависимости от условий
    scan_page = сканирование_в_процессе.to(
        сканирование_в_процессе, cond="is_not_final_page"
    ) | сканирование_в_процессе.to(сканирование_завершено, cond="is_final_page")

    finish_scan = сканирование_завершено.to(готов_к_сканированию)

    # Методы-условия, возвращающие True/False
    def is_not_final_page(self):
        """
        Условие: счетчик страниц еще не достиг лимита.
        """
        # Допустим, мы хотим сканировать 3 страницы
        return self.page_counter < 3

    def is_final_page(self):
        """
        Условие: счетчик страниц достиг лимита.
        """
        return self.page_counter >= 3

    # Обработчики событий и состояний
    def on_enter_готов_к_сканированию(self):
        print("Сканер готов к работе.")
        self.page_counter = 0

    def on_enter_сканирование_в_процессе(self):
        print("Сканирование начато.")

    def on_scan_page(self):
        self.page_counter += 1
        print(f"Отсканирована страница #{self.page_counter}.")

    def on_enter_сканирование_завершено(self):
        print("Сканирование завершено. Все страницы отсканированы.")

    def on_finish_scan(self):
        print("Сканер сброшен и готов к новому сканированию.")


if __name__ == "__main__":
    scanner = DocumentScanner()

    print(f"Текущее состояние: {scanner.current_state.id}")

    # Начинаем сканирование
    print("\nНачинаем сканирование...")
    scanner.start_scan()
    print(f"Текущее состояние: {scanner.current_state.id}")

    # Сканируем страницы
    print("\nСканируем первую страницу...")
    scanner.scan_page()
    print(
        f"Текущее состояние: {scanner.current_state.id}, счетчик: {scanner.page_counter}"
    )

    print("\nСканируем вторую страницу...")
    scanner.scan_page()
    print(
        f"Текущее состояние: {scanner.current_state.id}, счетчик: {scanner.page_counter}"
    )

    # Сканируем последнюю страницу, которая вызывает переход в другое состояние
    print("\nСканируем третью (последнюю) страницу...")
    scanner.scan_page()
    print(
        f"Текущее состояние: {scanner.current_state.id}, счетчик: {scanner.page_counter}"
    )

    # Попытка сканировать еще раз, когда процесс завершен (ничего не произойдет)
    print("\nПопытка отсканировать еще одну страницу, когда сканирование завершено...")
    scanner.scan_page()
    print(f"Текущее состояние: {scanner.current_state.id}")

    # Завершаем и сбрасываем сканер
    print("\nЗавершаем сканирование...")
    scanner.finish_scan()
    print(f"Текущее состояние: {scanner.current_state.id}")
