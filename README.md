Создание изолированного серверного окружения и разработка с нуля веб-приложение с функцией загрузки и хранения изображений
вувывывыв
# Проект: Настройка виртуальной среды, PostgreSQL, Apache, PHP и Python

## Архитектура окружения

-   **Хост-машина:** macOS (ARM)
-   **Гостевая система:** Ubuntu (VirtualBox)
-   **Проброс портов:**
    -   `127.0.0.1:5433 → 10.0.3.15:5432` --- доступ к PostgreSQL
-   **pgAdmin** подключается к `localhost:5433`

## 1. Установка и настройка Ubuntu в VirtualBox

-   Создание VM, установка Ubuntu

-   Первичная настройка пользователя

-   Обновление системы:

    ``` bash
    sudo apt update && sudo apt upgrade -y
    ```

-   Исправление нестабильного SSH

-   Настройка сети (enp0s8/enp0s9) и DHCP:

    ``` yaml
    network:
      version: 2
      renderer: networkd
      ethernets:
        enp0s8:
          dhcp4: true
          optional: true
        enp0s9:
          dhcp4: true
          optional: true
    ```

-   Применение:

    ``` bash
    sudo netplan apply
    ```

-   Проброс SSH `2222 → 22`

-   Подключение:

    ``` bash
    ssh -p 2222 vladislav@127.0.0.1
    ```

## 2. Установка и настройка PostgreSQL

``` bash
sudo apt install postgresql postgresql-contrib
sudo systemctl status postgresql
```

### Пароль суперпользователя

``` bash
sudo -u postgres psql -c "ALTER USER postgres PASSWORD '123456';"
```

### Удалённые подключения

`postgresql.conf`:

    listen_addresses = '*'

`pg_hba.conf`:

    host  all  all  0.0.0.0/0   md5
    host  all  all  ::/0        md5

### Тестирование

``` sql
CREATE TABLE users (id VARCHAR(100));
SELECT * FROM users;
```

## 3. Установка Apache и PHP

``` bash
sudo apt install apache2 php libapache2-mod-php
```

Перенос PHP-файла:

``` bash
sudo cp /home/select1.php /var/www/html/
```

Запуск:

    http://localhost:8080/select1.php

## 4. Работа с изображениями в PostgreSQL + PHP

``` sql
CREATE TABLE images (
  id SERIAL PRIMARY KEY,
  image_url VARCHAR(500)
);
INSERT INTO images (image_url) VALUES ('/images/image_test.png');
```

Установка драйвера:

``` bash
sudo apt install php-pgsql
```

Запуск:

    http://localhost:8080/select1.php

## 5. Переход на Python

Установка:

``` bash
sudo apt install python3 python3-pip python3-venv python3-psycopg2
```

Виртуальное окружение:

``` bash
python3 -m venv myenv
source myenv/bin/activate
pip install psycopg2-binary
```

Запуск Python-сервера (порт 8000):

``` bash
sudo python3 select1.py
```

## 6. Загрузка изображений через веб-интерфейс

Функционал:
- загрузка изображения пользователем
- определение следующего ID в БД
- переименование файла `image<ID>.png`
- сохранение на диск
- запись пути в PostgreSQL

Структура проекта - разделение на 2 файла: - **backend_images.py** - **frontend_images.html**
