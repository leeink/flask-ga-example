import pymysql, webbrowser
from flask import Flask, request, render_template, session
import os
from dotenv import load_dotenv
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import  mean_squared_error, r2_score

# 환경변수 로드
load_dotenv()

# 상수로 사용할 경로들
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = Flask(__name__,
            template_folder=TEMPLATE_DIR,
            static_folder=STATIC_DIR,)
app.secret_key = os.getenv('SECRET_KEY')

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
def find_seoul(gu: str | None = None):
    conn = get_db()
    with conn.cursor() as cursor:
        if gu:
            cursor.execute(f"select year, {gu} from pop_seoul")
        else:
            cursor.execute("select year, subtotal from pop_seoul")
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
    if request.method == 'POST':
        email = request.form.get('email')

    # 전달할 데이터 수정하기 좋게 따로 관리
    context = {
        'email': email,
        'site_name': "Flask app",
    }


    return render_template("index.html", **context)

# 구 별 인구수 추이
@app.route('/statistic', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        gu = request.form.get('filter')
    else:
        gu = 'subtotal'

    data = find_seoul(gu) if gu else []
    pred, acc, rmse = regression()

    context = {
        'data': data,
        'site_name': "Flask app",
        'selected_filter': gu,
        'pred': pred,
        'acc': acc,
        'rmse': rmse,
    }

    return render_template("statistic.html", **context)

# 분석 자체는 잘못된 것, 그냥 예시로 절차가 이렇다는 것만 인지
def regression():
    conn = get_db()
    with conn.cursor() as cursor:
        df = pd.read_sql("SELECT * FROM pop_seoul", conn)
        df = df.set_index('year').T
        df.columns = df.columns.astype(str)
    by_year = df.drop('subtotal')
    X = by_year.drop(columns=['2025'])
    Y = by_year['2025']

    X_train, X_test, y_train, y_test = train_test_split(
        X, Y, test_size=0.2, random_state=42
    )

    import numpy as np

    reg = LinearRegression()
    reg.fit(X_train, y_train)

    y_pred = reg.predict(X_test)
    acc = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    return y_pred, acc, rmse

if __name__ == '__main__':
    webbrowser.open_new_tab("http://127.0.0.1:5000")
    app.run()