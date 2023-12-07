from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Получаем файл из формы
        xml_file = request.files['xml_file']
        
        # Читаем содержимое XML-файла
        xml_content = xml_file.read().decode('utf-8')

        # Используем регулярные выражения для поиска строк с CVE
        cve_list = re.findall(r"CVE-[0-9]+-[0-9]+", xml_content)
        cve_list = sorted(set(cve_list))

        result = []

        # Перебираем найденные CVE
        for cve_id in cve_list:
            # Формируем URL для запроса на NVD
            url = f"https://nvd.nist.gov/vuln/detail/{cve_id}"

            # Выполняем запрос и проверяем наличие Exploit
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            exploit_badge = soup.find('span', class_='badge', string='Exploit')

            if exploit_badge:
                result.append({
                    'cve_id': cve_id,
                    'url': url,
                    'poc': True
                })
            else:
                result.append({
                    'cve_id': cve_id,
                    'url': url,
                    'poc': False
                })

        return render_template('result.html', result=result)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
