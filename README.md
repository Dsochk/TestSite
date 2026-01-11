# TestSite

## Требования

- ОС: Debian 12.11.0 (bookworm)
- CPU: 2 vCPU
- RAM: 2–4 GB
- Диск: 20–40 GB
- Сеть VM: NAT + Host‑Only (рекомендуется)

## Настройка сети VM

### Вариант 1: Host‑Only (рекомендуется)

**VirtualBox/VMware:**
- Адаптер 1: NAT
- Адаптер 2: Host‑Only

**На Debian VM (если нужен статический IP):**
```bash
sudo nano /etc/network/interfaces
```
Добавьте:
```
auto enp0s8
iface enp0s8 inet static
    address 192.168.56.100
    netmask 255.255.255.0
```
Примените:
```bash
sudo systemctl restart networking
```

### Вариант 2: Bridged

```bash
sudo dhclient
```

## Установка

### Вариант A: копирование в /opt/lab
```bash
sudo mkdir -p /opt/lab
sudo cp -r /path/to/project/* /opt/lab/
cd /opt/lab
sudo bash scripts/setup.sh
```

### Вариант B: передача по scp
```bash
scp -rp ./project_folder VMuser@VM_IP:/home/VMuser/lab
sudo mkdir -p /opt/lab
sudo cp -r /home/VMuser/lab/* /opt/lab/
cd /opt/lab
sudo bash scripts/setup.sh
```

Установка занимает ~5–10 минут. Скрипт:
- ставит пакеты
- настраивает Django/PHP/React
- применяет миграции
- создаёт SUID‑бинарник
- создаёт флаг `/root/flag.txt`
- запускает сервисы

## Запуск сервисов

```bash
cd /opt/lab
bash scripts/start_services.sh
```

## Доступ к приложению

Узнать IP:
```bash
hostname -I
```

Открыть в браузере:
- Главная: `http://VM_IP/`
- Django LMS: `http://VM_IP/portal/`
- PHP Support: `http://VM_IP/support/`
- Django Admin: `http://VM_IP/admin/`
- React RSC Demo: `http://VM_IP/api/rsc/demo`

## Учётные данные

Сгенерированы при установке:
```
/root/lab_credentials.txt
```

## Режим сложности

Лаборатория работает в режиме `hard`:
```bash
sudo bash scripts/set_difficulty.sh hard
sudo systemctl restart lms-django lms-react nginx php8.2-fpm
```

## Обновление курсов

Если изменяли `scripts/init_data.py`:
```bash
cd /opt/lab/django-lms
source venv/bin/activate
export PYTHONPATH="/opt/lab/django-lms:$PYTHONPATH"
python /opt/lab/scripts/init_data.py
deactivate
```

## Исправление маршрутов Nginx (если 404 на static/support)

```bash
sudo cp /opt/lab/nginx/lms.conf /etc/nginx/sites-available/lms
sudo nginx -t
sudo systemctl reload nginx
```

Или:
```bash
cd /opt/lab
bash scripts/fix_nginx_routes.sh
```

## Полезные команды

```bash
sudo systemctl status lms-django lms-react nginx php8.2-fpm
sudo journalctl -u lms-django -n 50
sudo journalctl -u lms-react -n 50
sudo tail -f /var/log/nginx/error.log
```

## Troubleshooting (частые проблемы)

### Django settings not configured
```bash
cd /opt/lab/django-lms
source venv/bin/activate
export PYTHONPATH="/opt/lab/django-lms:$PYTHONPATH"
python /opt/lab/scripts/init_data.py
deactivate
```

### ModuleNotFoundError: No module named 'courses'
```bash
cd /opt/lab/django-lms
source venv/bin/activate
export PYTHONPATH="/opt/lab/django-lms:$PYTHONPATH"
python /opt/lab/scripts/init_data.py
```

### Database locked
```bash
sudo systemctl stop lms-django
pkill -f gunicorn
pkill -f python.*manage.py
sleep 2
cd /opt/lab/django-lms
source venv/bin/activate
python /opt/lab/scripts/init_data.py
```

### Permission denied (Django)
```bash
sudo chown -R www-data:www-data /opt/lab/django-lms
sudo chmod -R 755 /opt/lab/django-lms
sudo chmod 666 /opt/lab/django-lms/db.sqlite3
```

### Migrations not applied
```bash
cd /opt/lab/django-lms
source venv/bin/activate
python manage.py makemigrations
python manage.py migrate
deactivate
```

### Static files не найдены
```bash
cd /opt/lab/django-lms
source venv/bin/activate
python manage.py collectstatic --noinput
deactivate
sudo chown -R www-data:www-data /opt/lab/django-lms/static
```

### Gunicorn не запускается (порт 8000 занят)
```bash
sudo lsof -ti:8000 | xargs sudo kill -9
sudo pkill -f gunicorn
sudo systemctl start lms-django
```

### React RSC не запускается
```bash
cd /opt/lab/react-components
npm install
sudo systemctl restart lms-react
```

### PHP database not found
```bash
cd /opt/lab/php-support
php init_db.php
sudo chown www-data:www-data support.db
sudo chmod 666 support.db
```

### 502 Bad Gateway
```bash
sudo systemctl start lms-django
sudo journalctl -u lms-django -n 50
```

### Страница не загружается
```bash
sudo systemctl status nginx
sudo nginx -t
sudo tail -f /var/log/nginx/error.log
```

### Не могу подключиться с хоста
```bash
sudo systemctl status nginx lms-django lms-react
sudo ss -tlnp | grep -E ':(80|8000|3000)'
hostname -I
```

### Firewall
```bash
sudo ufw status
sudo ufw allow 80/tcp
sudo ufw allow 8000/tcp
sudo ufw allow 3000/tcp
```

## Полный перезапуск

```bash
sudo systemctl stop lms-django lms-react nginx php8.2-fpm
sudo pkill -f gunicorn
sudo pkill -f "node.*server.js"
sleep 2
cd /opt/lab
bash scripts/start_services.sh
```

## Документация

См. также:
- `docs/README.md`
- `docs/TROUBLESHOOTING.md`
- `docs/SETUP_NETWORK.md`
- `FIX_ROUTES.md`
- `UPDATE_COURSES.md`
