from flask import Flask, render_template, request, redirect, url_for
import os
import pandas as pd

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

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
        return f"日期列解析错误：{e}"

    return render_template('result.html', tables=[expired_rows.to_html(classes='data', index=False)], titles=expired_rows.columns.values)

if __name__ == '__main__':
    app.run(debug=True)
