import pymysql, webbrowser
from flask import Flask, request, render_template
import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 상수로 사용할 경로들
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = Flask(__name__,
            template_folder=TEMPLATE_DIR,
            static_folder=STATIC_DIR,)

# 환경변수 읽기: app.config에 등록
app.config['ID'] = os.getenv('ID')
app.config['DB_HOST'] = os.getenv('DB_HOST')
app.config['DB_USER'] = os.getenv('DB_USER')
app.config['DB_PASSWORD'] = os.getenv('DB_PASSWORD')
app.config['DB_NAME'] = os.getenv('DB_NAME')

# 데이터베이스 연결
def get_db():
    return pymysql.connect(
        host=app.config['DB_HOST'],
        port=3306,
        user=app.config['DB_USER'],
        password=app.config['DB_PASSWORD'],
        database=app.config['DB_NAME'],
        charset="utf8"
    )

# 간단하게 데이터 가져오기
def find_data():
    conn = get_db()
    with conn.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute("select * from sample")
        data = cursor.fetchall()
    conn.close()
    return data

# ga_id는 모든 템플릿에서 공통으로 사용하니 모든 템플릿에서 사용할 수 있게 주입
@app.context_processor
def inject_config():
    return dict(ga_id=app.config['ID'])

# 첫 화면
@app.route('/', methods=['GET', 'POST'])
def index():
    email = ""
    result = find_data()
    if request.method == 'POST':
        email = request.form.get('email')

    # 전달할 데이터 수정하기 좋게 따로 관리
    context = {
        'email': email,
        'result': result,
        'site_name': "Flask app"
    }

    return render_template("index.html", **context)


if __name__ == '__main__':
    webbrowser.open_new_tab("http://127.0.0.1:5000")
    app.run()