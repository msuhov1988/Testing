ИНСТРУКЦИЯ ПО КЛОНИРОВАНИЮ И ЗАПУСКУ

Перейдите в директорию, где вы хотите разместить проект, и выполните команду:
git clone https://github.com/msuhov1988/Testing

После клонирования перейдите в директорию проекта и создайте виртуальное окружение:
python -m venv venv

Активируйте окружение:
windows: venv\Scripts\activate
linux:   source venv/bin/activate  

Убедитесь, что вы находитесь в корневой директории проекта, и выполните следующую команду:
pip install -r requirements.txt

Файл для запуска: launch.py
Находясь в корневой директории, выполните: python launch.py
