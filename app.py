from flask import Flask, render_template, request, redirect, url_for
import os
port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.header import Header

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 发送邮件函数
def send_email(subject, content):
    sender = 'liyewang3@163.com'
    receiver = 'liyewang3@163.com'
    smtp_server = 'smtp.163.com'
    smtp_port = 465
    smtp_password = 'EB2MXRVessA77twZ'  # 使用你的SMTP授权码

    message = MIMEText(content, 'plain', 'utf-8')
    message['From'] = Header("到期提醒机器人", 'utf-8')
    message['To'] = Header("接收者", 'utf-8')
    message['Subject'] = Header(subject, 'utf-8')

    try:
        smtp = smtplib.SMTP_SSL(smtp_server, smtp_port)
        smtp.login(sender, smtp_password)
        smtp.sendmail(sender, [receiver], message.as_string())
        smtp.quit()
        print("\u2705 邮件发送成功")
    except Exception as e:
        print("\u274c 邮件发送失败：", e)

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
        return f"\u65e5\u671f\u5217\u89e3\u6790\u9519\u8bef\uff1a{e}"

    if not expired_rows.empty:
        content = "\u6709\u4ee5\u4e0b\u5230\u671f\u6570\u636e\uff1a\n" + expired_rows.to_string(index=False)
        send_email("\u5230\u671f\u6570\u636e\u63d0\u9192", content)

    return render_template('result.html', tables=[expired_rows.to_html(classes='data', index=False)], titles=expired_rows.columns.values)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)  # 确保已指定端口
    import os
from flask import Flask

app = Flask(__name__)

# ...你的路由和逻辑...

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

