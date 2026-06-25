import flet as ft
import flet.canvas as cv

def main(page: ft.Page):
    page.title = "Замір Стель - Побудова"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.ALWAYS  
    
    # -------------------------------------------------------------
    # СТАН ДОДАТКУ
    # -------------------------------------------------------------
    state_points = [
        ft.Offset(100, 100),  # Точка 1 (Завжди база)
        ft.Offset(300, 100),  # Точка 2
        ft.Offset(300, 300),  # Точка 3
        ft.Offset(100, 300),  # Точка 4
    ]
    
    camera = {
        "offset_x": 200.0,  
        "offset_y": 100.0,  
        "zoom": 1.0         
    }

    area_text = ft.Text(
        value="Площа: 0.00 м² | Периметр: 0.00 м", 
        size=16, 
        weight=ft.FontWeight.BOLD, 
        color=ft.Colors.BLUE_900
    )
    
    inputs_list = ft.Row(wrap=True, alignment=ft.MainAxisAlignment.CENTER, spacing=8)
    canvas = cv.Canvas(expand=True, shapes=[])

    # -------------------------------------------------------------
    # ЛОГІКА МАЛЮВАННЯ ТА РОЗРАХУНКІВ
    # -------------------------------------------------------------
    def render_canvas():
        canvas.shapes.clear()
        
        if len(state_points) < 2:
            page.update()
            return

        total_perimeter = 0.0
        n = len(state_points)

        for i in range(n):
            p1 = state_points[i]
            p2 = state_points[(i + 1) % n]
            
            x1 = p1.x * camera["zoom"] + camera["offset_x"]
            y1 = p1.y * camera["zoom"] + camera["offset_y"]
            x2 = p2.x * camera["zoom"] + camera["offset_x"]
            y2 = p2.y * camera["zoom"] + camera["offset_y"]
            
            # Малюємо стіну
            canvas.shapes.append(
                cv.Line(x1, y1, x2, y2, paint=ft.Paint(stroke_width=3, color=ft.Colors.BLUE_900))
            )
            
            # Довжина
            pixel_dist = (((p2.x - p1.x) ** 2) + ((p2.y - p1.y) ** 2)) ** 0.5
            meters = pixel_dist / 100.0
            total_perimeter += meters
            
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            if abs(p1.x - p2.x) < 1:  # Вертикальна стіна
                center_x += 25
            else:  # Горизонтальна стіна
                center_y -= 15
                
            canvas.shapes.append(
                cv.Text(
                    x=center_x, y=center_y, value=f"{meters:.2f} м",
                    style=ft.TextStyle(size=11, color=ft.Colors.BLUE_GREY_700, weight=ft.FontWeight.W_600),
                    alignment=ft.Alignment(0, 0)
                )
            )
            
            canvas.shapes.append(
                cv.Circle(x1, y1, radius=6, paint=ft.Paint(style=ft.PaintingStyle.FILL, color=ft.Colors.RED_500))
            )

        # Площа за Гауссом
        area_sum = 0.0
        for i in range(n):
            j = (i + 1) % n
            xi, yi = state_points[i].x / 100.0, state_points[i].y / 100.0
            xj, yj = state_points[j].x / 100.0, state_points[j].y / 100.0
            area_sum += xi * yj - xj * yi
            
        calculated_area = abs(area_sum) / 2.0
        area_text.value = f"Площа: {calculated_area:.2f} м² | Периметр: {total_perimeter:.2f} м"
        
        update_input_fields()
        page.update()

    # -------------------------------------------------------------
    # ДИНАМІЧНІ ПОЛЯ РОЗМІРІВ
    # -------------------------------------------------------------
    def update_input_fields():
        inputs_list.controls.clear()
        n = len(state_points)
        
        for i in range(n):
            p1 = state_points[i]
            p2 = state_points[(i + 1) % n]
            cur_len = (((p2.x - p1.x)**2) + ((p2.y - p1.y)**2))**0.5 / 100.0
            
            # Останню замикаючу стіну робимо доступною тільки для читання (щоб не ламати кути)
            is_locked = (i == n - 1)
            
            wall_field = ft.TextField(
                label=f"Стіна {i+1}" + (" (Авто)" if is_locked else ""),
                value=f"{cur_len:.2f}",
                width=100,
                height=38,
                text_size=11,
                data=i,
                disabled=is_locked, # Блокуємо замикаючу стіну
                suffix=ft.Text("м", size=10),
                keyboard_type=ft.KeyboardType.NUMBER,
                on_submit=on_wall_size_change
            )
            inputs_list.controls.append(wall_field)

    def on_wall_size_change(e):
        try:
            idx = e.control.data  
            new_meters = float(e.control.value)
            new_pixels = new_meters * 100.0
            
            p1 = state_points[idx]
            p2 = state_points[idx + 1] # Змінюємо тільки внутрішні стіни, не замикаючу
            
            if abs(p1.x - p2.x) < 1:  # ВЕРТИКАЛЬНА СТІНА
                direction = 1 if p2.y > p1.y else -1
                current_len = p2.y - p1.y
                dy = (new_pixels * direction) - current_len
                
                # Посуваємо всі точки після цієї
                for k in range(idx + 1, len(state_points)):
                    state_points[k] = ft.Offset(state_points[k].x, state_points[k].y + dy)
                    
            else:  # ГОРИЗОНТАЛЬНА СТІНА
                direction = 1 if p2.x > p1.x else -1
                current_len = p2.x - p1.x
                dx = (new_pixels * direction) - current_len
                
                # Посуваємо всі точки після цієї
                for k in range(idx + 1, len(state_points)):
                    state_points[k] = ft.Offset(state_points[k].x + dx, state_points[k].y)
                
            render_canvas()
        except (ValueError, IndexError):
            pass

    # -------------------------------------------------------------
    # КЕРУВАННЯ ПУЛЬТОМ
    # -------------------------------------------------------------
    def on_canvas_drag(e: ft.DragUpdateEvent):
        camera["offset_x"] += getattr(e, "delta_x", getattr(e, "dx", 0))
        camera["offset_y"] += getattr(e, "delta_y", getattr(e, "dy", 0))
        render_canvas()

    def add_corner(direction):
        if not state_points: return
        last_point = state_points[-1]
        step = 60  
        
        if direction == "up":    new_point = ft.Offset(last_point.x, last_point.y - step)
        elif direction == "down":  new_point = ft.Offset(last_point.x, last_point.y + step)
        elif direction == "left":  new_point = ft.Offset(last_point.x - step, last_point.y)
        elif direction == "right": new_point = ft.Offset(last_point.x + step, last_point.y)
            
        state_points.append(new_point)
        render_canvas()

    def remove_last_corner(e):
        if len(state_points) > 2:  
            state_points.pop()
            render_canvas()

    def clear_canvas(e):
        state_points.clear()
        state_points.extend([ft.Offset(100, 100), ft.Offset(300, 100), ft.Offset(300, 300), ft.Offset(100, 300)])
        render_canvas()

    # -------------------------------------------------------------
    # ІНТЕРФЕЙС LAYOUT
    # -------------------------------------------------------------
    gesture_detector = ft.GestureDetector(
        content=canvas,
        on_pan_update=on_canvas_drag,
    )

    drawing_zone = ft.Container(
        content=gesture_detector,
        height=420,
        border=ft.Border.all(1, ft.Colors.GREY_300),
        bgcolor=ft.Colors.GREY_50,
        clip_behavior=ft.ClipBehavior.NONE
    )

    compact_arrows = ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=5,
        controls=[
            ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_size=20, on_click=lambda _: add_corner("left")),
            ft.IconButton(icon=ft.Icons.ARROW_UPWARD, icon_size=20, on_click=lambda _: add_corner("up")),
            ft.IconButton(icon=ft.Icons.ARROW_DOWNWARD, icon_size=20, on_click=lambda _: add_corner("down")),
            ft.IconButton(icon=ft.Icons.ARROW_FORWARD, icon_size=20, on_click=lambda _: add_corner("right")),
        ]
    )

    controls_layout = ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=8,
        controls=[
            area_text,
            ft.Text("Розміри стін (введіть число та Enter):", size=11, color=ft.Colors.GREY_600),
            inputs_list,  
            ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=15,
                controls=[
                    compact_arrows, 
                    ft.TextButton("Скасувати кут", icon=ft.Icons.UNDO, icon_color=ft.Colors.ORANGE_800, on_click=remove_last_corner),
                    ft.TextButton("Очистити", icon=ft.Icons.DELETE, icon_color=ft.Colors.RED, on_click=clear_canvas),
                ]
            )
        ]
    )

    page.add(ft.Column(controls=[drawing_zone, controls_layout]))
    render_canvas()

ft.run(main)
