import flet as ft
import flet.canvas as cv
import math

def main(page: ft.Page):
    page.title = "Замір Стель PRO (Тріангуляція)"
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 15

    # Початкова конфігурація: 4 кути (A, B, C, D)
    # Зберігаємо сторони як зв'язки між точками: A-B, B-C, C-D, D-A
    num_corners = 4
    sides_values = {"A-B": 4.0, "B-C": 3.0, "C-D": 4.0, "D-A": 3.0}
    diagonals_values = {"A-C": 5.0} # Діагональ для точного розрахунку 4-кутника

    sides_container = ft.Column(spacing=5)
    diags_container = ft.Column(spacing=5)
    result_text = ft.Text("Внесіть розміри для точного розрахунку", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800)
    
    canvas_shapes = []
    canvas = cv.Canvas(expand=True, shapes=canvas_shapes)

    def generate_inputs():
        # Створення полів для сторін (A-B, B-C...)
        sides_container.controls.clear()
        letters = [chr(65 + i) for i in range(num_corners)]
        
        for i in range(num_corners):
            p1 = letters[i]
            p2 = letters[(i + 1) % num_corners]
            pair = f"{p1}-{p2}"
            if pair not in sides_values:
                sides_values[pair] = 3.0 # Стандартне значення за замовчуванням
                
            def make_side_change(p=pair):
                return lambda e: update_value(sides_values, p, e.control.value)

            sides_container.controls.append(
                ft.Row([
                    ft.Text(f"Стіна {pair}: ", width=80, weight=ft.FontWeight.W_500),
                    ft.TextField(value=str(sides_values[pair]), width=90, dense=True, on_change=make_side_change(), keyboard_type=ft.KeyboardType.NUMBER)
                ], alignment=ft.MainAxisAlignment.CENTER)
            )

        # Створення полів для необхідних діагоналей (для тріангуляції)
        diags_container.controls.clear()
        # Для N кутів потрібно точно (N - 3) діагоналей з точки А
        for i in range(2, num_corners - 1):
            pair = f"A-{letters[i]}"
            if pair not in diagonals_values:
                diagonals_values[pair] = 5.0
                
            def make_diag_change(p=pair):
                return lambda e: update_value(diagonals_values, p, e.control.value)

            diags_container.controls.append(
                ft.Row([
                    ft.Text(f"Діагональ {pair}: ", width=110, color=ft.Colors.BLUE_700),
                    ft.TextField(value=str(diagonals_values[pair]), width=90, dense=True, on_change=make_diag_change(), keyboard_type=ft.KeyboardType.NUMBER)
                ], alignment=ft.MainAxisAlignment.CENTER)
            )
        page.update()

    def update_value(dataset, pair, val):
        try: dataset[pair] = float(val)
        except: pass

    def change_corners(delta):
        nonlocal num_corners
        new_corners = num_corners + delta
        if 3 <= new_corners <= 8: # Обмеження від 3 до 8 кутів
            num_corners = new_corners
            generate_inputs()
            calculate_all(None)

    def heron_area(a, b, c):
        # Формула Герона для розрахунку площі одного трикутника
        if a + b <= c or a + c <= b or b + c <= a:
            return 0 # Неіснуючий трикутник
        s = (a + b + c) / 2
        return math.sqrt(max(0, s * (s - a) * (s - b) * (s - c)))

    def calculate_all(e):
        try:
            letters = [chr(65 + i) for i in range(num_corners)]
            perimeter = sum(sides_values[f"{letters[i]}-{letters[(i+1)%num_corners]}"] for i in range(num_corners))
            
            total_area = 0.0
            
            # Тріангуляція: розбиваємо будь-який багатокутник на трикутники з вершини А
            for i in range(1, num_corners - 1):
                # Сторона 1 трикутника (ліва стіна або попередня діагональ)
                side1_name = f"A-{letters[i]}" if i > 1 else f"A-{letters[1]}"
                s1 = diagonals_values[side1_name] if i > 1 else sides_values[side1_name]
                
                # Сторона 2 трикутника (зовнішня стіна кімнати)
                side2_name = f"{letters[i]}-{letters[i+1]}"
                s2 = sides_values[side2_name]
                
                # Сторона 3 трикутника (наступна діагональ або права стіна)
                side3_name = f"A-{letters[i+1]}" if i < num_corners - 2 else f"{letters[num_corners-1]}-A"
                # Коригуємо назву для стіни, якщо вона записана навпаки як D-A
                if side3_name not in sides_values and i == num_corners - 2:
                    side3_name = f"A-{letters[num_corners-1]}" if f"A-{letters[num_corners-1]}" in sides_values else f"{letters[num_corners-1]}-A"
                
                s3 = diagonals_values[side3_name] if i < num_corners - 2 else sides_values[side3_name]
                
                # Додаємо площу поточного трикутника
                total_area += heron_area(s1, s2, s3)

            if total_area == 0:
                result_text.value = f"Периметр: {perimeter:.2f} м | Помилка: Перевірте діагоналі!"
            else:
                result_text.value = f"Площа: {total_area:.2f} м² | Периметр: {perimeter:.2f} м"
            
            # Малюємо точний пропорційний ескіз
            draw_sketch()
        except Exception as ex:
            result_text.value = "Помилка вводу даних!"
        page.update()

    def draw_sketch():
        canvas_shapes.clear()
        center_x, center_y = 160, 120
        radius = 75
        
        # Будуємо гарні кути для візуалізації
        pts = []
        for i in range(num_corners):
            angle = (2 * math.pi * i / num_corners) - math.pi / 2
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            pts.append((x, y))

        path_elements = [cv.Path.MoveTo(pts[0][0], pts[0][1])]
        for p in pts[1:]:
            path_elements.append(cv.Path.LineTo(p[0], p[1]))
        path_elements.append(cv.Path.Close())
        
        canvas_shapes.append(cv.Path(path_elements, paint=ft.Paint(stroke_width=3, color=ft.Colors.BLUE_600, style=ft.PaintingStyle.STROKE)))
        
        # Додаємо червоні точки-кути А, B, C...
        letters = [chr(65 + i) for i in range(num_corners)]
        for i, p in enumerate(pts):
            canvas_shapes.append(cv.Circle(p[0], p[1], 5, paint=ft.Paint(color=ft.Colors.RED_600)))
            
            angle = (2 * math.pi * i / num_corners) - math.pi / 2
            tx = center_x + (radius + 15) * math.cos(angle) - 5
            ty = center_y + (radius + 15) * math.sin(angle) - 5
            canvas_shapes.append(cv.Text(tx, ty, letters[i]))
        page.update()

    generate_inputs()
    calculate_all(None)

    page.add(
        ft.AppBar(title=ft.Text("Замірник Стель PRO"), bgcolor=ft.Colors.BLUE_600, color=ft.Colors.WHITE),
        ft.Column([
            ft.Text("Кількість кутів у кімнаті:", size=14, weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.ElevatedButton("Додати кут (+1)", on_click=lambda e: change_corners(1), icon=ft.Icons.ADD),
                ft.ElevatedButton("Прибрати кут (-1)", on_click=lambda e: change_corners(-1), icon=ft.Icons.REMOVE, bgcolor=ft.Colors.RED_50)
            ], alignment=ft.MainAxisAlignment.CENTER),
            
            ft.Container(height=10),
            ft.Text("Ескіз кімнати:", size=14, weight=ft.FontWeight.W_500),
            ft.Container(content=canvas, width=320, height=240, bgcolor=ft.Colors.GREY_50, border_radius=8),
            
            ft.Container(height=5),
            result_text,
            ft.Container(height=5),
            
            ft.FilledButton("Перерахувати та оновити", on_click=calculate_all, style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE)),
            
            ft.Container(height=10),
            ft.Text("Довжини стін (м):", size=14, weight=ft.FontWeight.BOLD),
            sides_container,
            
            ft.Container(height=10),
            ft.Text("Внутрішні діагоналі (м):", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
            diags_container,
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

ft.app(target=main)
