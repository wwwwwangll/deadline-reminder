import os
import pandas as pd
import smtplib
from flask import Flask, render_template, request, redirect, url_for
from email.mime.text import MIMEText
from email.header import Header

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

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

# 首页上传逻辑
@app.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.xlsx'):
            filename = os.path.splitext(file.filename)[0]
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename + '.csv')
            df = pd.read_excel(file)
            df.to_csv(filepath, index=False)
            return redirect(url_for('list_files'))
    return render_template('index.html')

# 文件展示页面（保留这一段，已修复重复定义）
@app.route('/files')
def list_files():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    files = [f for f in files if f.endswith('.csv')]
    return render_template('files.html', files=files)

# 自动检测页面
@app.route('/check')
def check_expired():
    today = pd.to_datetime('today').normalize()
    notify_threshold = today + pd.Timedelta(days=10)
    summary = []

    for fname in os.listdir(UPLOAD_FOLDER):
        if not fname.endswith('.csv'):
            continue
        path = os.path.join(UPLOAD_FOLDER, fname)
        try:
            df = pd.read_csv(path)
            for col in df.columns:
                try:
                    dates = pd.to_datetime(df[col], errors='coerce')
                    expired = df[dates < notify_threshold]
                    expired = expired[dates.notna()]
                    if not expired.empty:
                        summary.append((fname, col, expired))
                        content = f"文件 {fname} 的列 {col} 中有以下即将到期数据：\n" + expired.to_string(index=False)
                        send_email(f"{fname} 到期提醒", content)
                except:
                    continue
        except:
            continue
    return f"扫描完成，共提醒 {len(summary)} 项。"
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
from markupsafe import Markup
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
# 启动应用
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
