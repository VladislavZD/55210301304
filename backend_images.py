from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse as urlparse
from urllib.parse import parse_qs
import psycopg2 
import os
import cgi

class ImageHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/images/'):
            self.serve_image()
        else: # Отдает HTML пользователю
            html = self.generate_html()
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
    
    def do_POST(self):
        content_type = self.headers.get('Content-Type', '')# обработка POST-запросов загрузок файлов и переключения кнопки
        if 'multipart/form-data' in content_type:
            self.handle_file_upload()
        else:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            parsed_data = parse_qs(post_data)
            show_images_current = parsed_data.get('show_images', ['0'])[0]
            next_show_value = '0' if show_images_current == '1' else '1'
    
            html = self.generate_html(show_images_current == '1', next_show_value)
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
    
    def handle_file_upload(self): #обратобка загрузки файлов 
        try:
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST',
                        'CONTENT_TYPE': self.headers['Content-Type']}
            )
            
            file_item = form['image_file']
            
            if file_item.file and file_item.filename:
                images_folder = '/home/vladislav/images'
                if not os.path.exists(images_folder):
                    os.makedirs(images_folder)
                
                # получаем расширение файла
                original_filename = file_item.filename
                file_extension = os.path.splitext(original_filename)[1].lower()
                
                next_id = self.get_next_image_id() #получение id из бд
                
                if next_id is not None: 
                    #формируем новое имя файла
                    new_filename = f"image{next_id}{file_extension}"
                    file_path = os.path.join(images_folder, new_filename)
                    image_url = f'/images/{new_filename}'
                    
                    #сохраняем файл
                    with open(file_path, 'wb') as f:
                        f.write(file_item.file.read())
                    
                    #сохраняем в бд
                    self.save_image_to_db(image_url)
                    
                    self.send_response(303)
                    self.send_header('Location', '/')
                    self.end_headers()
                else:
                    self.send_error(500, "Failed to get next ID from database")
            else:
                self.send_error(400, "No file uploaded")
                
        except Exception as e:
            self.send_error(500, f"Upload error: {str(e)}")
    
    def get_next_image_id(self):
        """Получает следующий ID для картинки"""
        try:
            conn = psycopg2.connect(
                host='localhost',
                dbname='postgres', 
                user='postgres',
                password='123456'
            )
            cur = conn.cursor()
            
            cur.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM images") #получаем максимальный ID и прибавляем 1
            next_id = cur.fetchone()[0]
            
            cur.close()
            conn.close()
            print(f"Next image ID: {next_id}")
            return next_id
            
        except Exception as e:
            print(f"Database error in get_next_image_id: {e}")
            return None
    
    def save_image_to_db(self, image_url):
        try:  #Сохранение информации о картинке в бд
            conn = psycopg2.connect(
                host='localhost',
                dbname='postgres', 
                user='postgres',
                password='123456'
            )
            cur = conn.cursor()
            
            cur.execute(
                "INSERT INTO images (image_url) VALUES (%s)",
                (image_url,)
            )
            
            conn.commit()
            cur.close()
            conn.close()
            print(f"Image saved to DB: {image_url}")
            
        except Exception as e:
            print(f"Database error in save_image_to_db: {e}")
    
    def serve_image(self):
        # рбработка статических изображений 
        try:
            image_url = self.path
            image_path = '/home/vladislav' + image_url
            
            if not os.path.exists(image_path):
                self.send_error(404, f"File not found: {image_path}")
                return
            
            if self.path.endswith('.png'):
                mime_type = 'image/png'
            elif self.path.endswith('.jpg') or self.path.endswith('.jpeg'):
                mime_type = 'image/jpeg'
            elif self.path.endswith('.gif'):
                mime_type = 'image/gif'
            elif self.path.endswith('.webp'):
                mime_type = 'image/webp'
            else:
                mime_type = 'application/octet-stream'
            
            with open(image_path, 'rb') as file:
                file_content = file.read()
            
            self.send_response(200)
            self.send_header('Content-type', mime_type)
            self.send_header('Content-length', len(file_content))
            self.end_headers()
            self.wfile.write(file_content)
            
        except Exception as e:
            self.send_error(500, f"Server error: {str(e)}")
    
    def generate_html(self, show_images=False, next_show_value='1'): #генерируется html страницу из файла фронтенда
        with open('frontend-images.html', 'r', encoding='utf-8') as f:
            html_template = f.read()
        
        images_html = ""
        if show_images:
            images_html = self.get_images_from_db()
        
        # плейсхолдеры
        html = html_template.replace('{{next_show_value}}', next_show_value)
        html = html.replace('{{button_text}}', 'Скрыть картинки' if show_images else 'Показать картинки')
        html = html.replace('{{images_html}}', images_html)
        
        return html
    
    def get_images_from_db(self): #Получение картинки из бд и формирование html-код для отображение веб страницы
        try:
            conn = psycopg2.connect(
                host='localhost',
                dbname='postgres', 
                user='postgres',
                password='123456'
            )
            cur = conn.cursor()          
            cur.execute("SELECT * FROM images ORDER BY id")  
            rows = cur.fetchall()         
            
            images_html = ""
            for row in rows:
                filename = os.path.basename(row[1])
                images_html += f'''
    <div class="image-card">
        <img src="{row[1]}" alt="{filename}">
        <div><strong>ID:</strong> {row[0]}</div>
        <div><strong>Название:</strong> {filename}</div>
        <div><strong>Путь:</strong> {row[1]}</div>
    </div>'''
            
            cur.close()
            conn.close()
            return images_html
            
        except Exception as e:
            return f"<p style='color: red; margin: 20px;'>Ошибка загрузки из базы данных: {e}</p>"

def run_server():
    images_folder = '/home/vladislav/images'
    if not os.path.exists(images_folder):
        os.makedirs(images_folder)
        print(f"Создана папка для картинок: {images_folder}")
    
    #Наличие файла фронтенд
    if not os.path.exists('frontend-images.html'):
        print("ОШИБКА: Файл frontend-images.html не найден!")
        print("Создайте файл frontend-images.html в той же папке что и backend.py")
        return
    
    server = HTTPServer(('0.0.0.0', 8000), ImageHandler)
    print('Рабочая ссылка: http://localhost:8000')
    server.serve_forever()

if __name__ == '__main__':
    run_server()
