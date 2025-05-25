from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Date, DateTime
from datetime import datetime
import os
import pandas as pd
import smtplib
from flask import Flask, render_template, request, redirect, url_for
from email.mime.text import MIMEText
from email.header import Header
from markupsafe import Markup

app = Flask(__name__)
postgresql://deadline_db_ikib_user:TjODVsAqZ9FFv8hZdQUVSW3F2JRSiblE@dpg-d0pik6emcj7s73e6k6eg-a/deadline_db_ikib
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
db = SQLAlchemy(app)

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# 数据库模型
class Record(db.Model):
    id = Column(Integer, primary_key=True)
    filename = Column(String(128))
    due_date = Column(Date)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

# 邮件发送函数
def send_email(subject, content):
    sender = 'liyewang3@163.com'
    receiver = 'liyewang3@163.com'
    smtp_server = 'smtp.163.com'
    smtp_port = 465
    smtp_password = 'EB2MXRVessA77twZ'

    message = MIMEText(content, 'plain', 'utf-8')
    message['From'] = Header("到期提醒机器人", 'utf-8')
    message['To'] = Header("接收者", 'utf-8')
    message['Subject'] = Header(subject, 'utf-8')

    try:
        smtp = smtplib.SMTP_SSL(smtp_server, smtp_port)
        smtp.login(sender, smtp_password)
        smtp.sendmail(sender, [receiver], message.as_string())
        smtp.quit()
        print("✅ 邮件发送成功")
    except Exception as e:
        print("❌ 邮件发送失败：", e)

@app.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.xlsx'):
            df = pd.read_excel(file)
            filename = file.filename
            for _, row in df.iterrows():
                try:
                    due_date = pd.to_datetime(row['到期日期'], errors='coerce')
                    if pd.notna(due_date):
                        record = Record(filename=filename, due_date=due_date)
                        db.session.add(record)
                except Exception as e:
                    print(f"skip: {e}")
            db.session.commit()
            return redirect(url_for('list_files'))
    return render_template('index.html')

@app.route('/files')
def list_files():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    files = [f for f in files if f.endswith('.csv')]
    return render_template('files.html', files=files)

@app.route('/check')
def check_expired():
    today = pd.to_datetime('today').normalize()
    notify_threshold = today + pd.Timedelta(days=10)
    records = Record.query.filter(Record.due_date < notify_threshold).all()
    if records:
        content = "\n".join([f"{r.filename} - {r.due_date}" for r in records])
        send_email("数据库到期提醒", content)
    return f"扫描完成，共提醒 {len(records)} 项。"

@app.route('/view/<filename>')
def view_file(filename):
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(path):
        return f"文件 {filename} 不存在"
    try:
        df = pd.read_csv(path)
        return render_template('view.html', filename=filename, table=df.to_html(index=False, classes='data'))
    except Exception as e:
        return f"读取文件失败：{e}"

@app.route('/edit/<filename>', methods=['GET', 'POST'])
def edit_file(filename):
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if request.method == 'POST':
        content = request.form['content']
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return redirect(url_for('list_files'))
    else:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        return render_template('edit.html', filename=filename, content=content)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
