from flask import Flask,render_template,redirect
from fetchall import query_with_fetchall
from insertData import insert_book
from updateData import update_book
from deleteData import delete_book

app = Flask(__name__)

@app.route('/')
def index():
  datas = query_with_fetchall()
  return render_template('list.html',datas=datas)

@app.route('/insert/<title>/<isbn>')
def insert(title,isbn):
  insert_book(title, isbn)
  return redirect('/')

@app.route('/update/<int:id>/<title>')
def update(id,title):
  affected_rows = update_book(id, title)
  print(f'Number of affected rows: {affected_rows}')
  return redirect('/')

@app.route('/delete/<int:id>')
def delete(id):
  affected_rows = delete_book(id)
  print(f'Number of affected rows: {affected_rows}')
  return redirect('/')

if  __name__ == '__main__':  
    app.run(debug=True)

