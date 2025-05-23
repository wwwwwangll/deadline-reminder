import os
import pandas as pd
import smtplib
from flask import Flask, render_template, request
from email.mime.text import MIMEText
from email.header import Header

# 初始化 Flask
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 创建上传目录
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

# 首页上传页面
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.xlsx'):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            df = pd.read_excel(filepath)
            columns = df.columns.tolist()
            return render_template('select_column.html', columns=columns, filename=file.filename)
    return render_template('index.html')

# 表格选择后处理页面
@app.route('/result', methods=['POST'])
def result():
    column_name = request.form['column']
    filename = request.form['filename']
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    df = pd.read_excel(filepath)

    today = pd.to_datetime('today').normalize()
    try:
        df[column_name] = pd.to_datetime(df[column_name])
        expired_rows = df[df[column_name] < today]
    except Exception as e:
        return f"日期列解析错误：{e}"

    if not expired_rows.empty:
        content = "有以下到期数据：\n" + expired_rows.to_string(index=False)
        send_email("到期数据提醒", content)

    return render_template('result.html', tables=[expired_rows.to_html(classes='data', index=False)], titles=expired_rows.columns.values)

# 启动应用
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
