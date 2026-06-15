import flet as ft
import flet.canvas as cv

def main(page: ft.Page):
    page.title = "Пульт Заміру Стель"
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20

    current_x = 160
    current_y = 120
    
    lines = []
    sides_data = []
    
    sides_container = ft.Column(spacing=5)
    wall_len_input = ft.TextField(label="Довжина нової стіни (м)", value="3.0", width=180, keyboard_type=ft.KeyboardType.NUMBER)
    result_text = ft.Text("Додайте першу стіну за допомогою стрілок", size=14, color=ft.Colors.GREY_700)
    
    canvas_shapes = []
    canvas = cv.Canvas(expand=True, shapes=canvas_shapes)

    def redraw_canvas():
        canvas_shapes.clear()
        if not lines:
            canvas_shapes.append(cv.Text(40, 110, "Використовуйте пульт нижче"))
            page.update()
            return
            
        path_elements = [cv.Path.MoveTo(lines[0][0], lines[0][1])]
        for line in lines:
            path_elements.append(cv.Path.LineTo(line[2], line[3]))
            
        canvas_shapes.append(
            cv.Path(path_elements, paint=ft.Paint(stroke_width=3, color=ft.Colors.BLUE_600, style=ft.PaintingStyle.STROKE))
        )
        
        for i, line in enumerate(lines):
            mid_x = (line[0] + line[2]) / 2
            mid_y = (line[1] + line[3]) / 2
            letter = chr(65 + i)
            canvas_shapes.append(cv.Text(mid_x + 5, mid_y - 5, f"{letter}:{sides_data[i]['val']}м"))
        page.update()

    def add_wall(direction):
        nonlocal current_x, current_y
        try:
            val = float(wall_len_input.value)
        except:
            return
            
        pixel_len = val * 30
        next_x, next_y = current_x, current_y
        if direction == "UP": next_y -= pixel_len
        elif direction == "DOWN": next_y += pixel_len
        elif direction == "LEFT": next_x -= pixel_len
        elif direction == "RIGHT": next_x += pixel_len
        
        lines.append((current_x, current_y, next_x, next_y))
        letter = chr(65 + len(sides_data))
        sides_data.append({"name": letter, "val": val})
        current_x, current_y = next_x, next_y
        
        rebuild_sides_list()
        redraw_canvas()
        calculate_metrics()

    def rebuild_sides_list():
        sides_container.controls.clear()
        for s in sides_data:
            sides_container.controls.append(
                ft.Row([
                    ft.Text(f"Сторона {s['name']}:", width=80, weight=ft.FontWeight.BOLD),
                    ft.Text(f"{s['val']} м", size=14)
                ], alignment=ft.MainAxisAlignment.CENTER)
            )
        page.update()

    def calculate_metrics():
        perimeter = sum(s["val"] for s in sides_data)
        if len(sides_data) == 4:
            area = sides_data[0]["val"] * sides_data[1]["val"]
            result_text.value = f"Площа: {area:.2f} м² | Периметр: {perimeter:.2f} м"
        else:
            result_text.value = f"Периметр: {perimeter:.2f} м | Додайте 4 стіни для розрахунку площі."
        page.update()

    def clear_all(e):
        nonlocal current_x, current_y
        current_x, current_y = 160, 120
        lines.clear()
        sides_data.clear()
        rebuild_sides_list()
        redraw_canvas()
        result_text.value = "Поле очищено."
        page.update()

    redraw_canvas()

    page.add(
        ft.AppBar(title=ft.Text("Пульт Заміру Стель"), bgcolor=ft.Colors.BLUE_600, color=ft.Colors.WHITE),
        ft.Column([
            ft.Text("Ескіз стелі:", size=14, weight=ft.FontWeight.W_500),
            ft.Container(content=canvas, width=320, height=240, bgcolor=ft.Colors.GREY_50, border_radius=8),
            ft.Container(height=5),
            result_text,
            ft.Container(height=5),
            wall_len_input,
            ft.Text("Оберіть напрямок стіни:", size=12, color=ft.Colors.GREY_600),
            ft.Column([
                ft.Row([ft.IconButton(ft.Icons.ARROW_UPWARD, on_click=lambda e: add_wall("UP"), icon_size=30, icon_color=ft.Colors.BLUE)], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([
                    ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: add_wall("LEFT"), icon_size=30, icon_color=ft.Colors.BLUE),
                    ft.Container(width=40),
                    ft.IconButton(ft.Icons.ARROW_FORWARD, on_click=lambda e: add_wall("RIGHT"), icon_size=30, icon_color=ft.Colors.BLUE),
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([ft.IconButton(ft.Icons.ARROW_DOWNWARD, on_click=lambda e: add_wall("DOWN"), icon_size=30, icon_color=ft.Colors.BLUE)], alignment=ft.MainAxisAlignment.CENTER),
            ], spacing=0),
            ft.ElevatedButton("Очистити все", on_click=clear_all, icon=ft.Icons.REFRESH, color=ft.Colors.RED)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )
ft.app(target=main)
