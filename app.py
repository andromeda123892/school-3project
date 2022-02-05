from flask import Flask, render_template, url_for, request, flash, redirect, session
import psycopg2
import datetime
from datetime import date
from config import host, user, password, db_name

app = Flask(__name__)
app.config['SECRET_KEY'] = '5ad30edaf0cbc613384f451979c18d6573058515a2ab'#Секретный ключ для формировании засекреченной сессии
"""Файл app.py, главный файл веб-приложения"""
#Главная страница
@app.route('/')
def index():
    return render_template("index.html")


# Каталог товаров и услуг
@app.route('/catalog')
def catalog():
    if not 'logged_in' in session: #Проверка наличии сесси, для того, чтобы отобразить привествие пользователя, если он авторизован
        sess = 0
    else:
        sess = session['logged_in']
    try:
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=db_name
        )
        with connection.cursor() as cursor:
            cursor.execute(
                f"""SELECT *
                    FROM "book"
                """
            )
            items = cursor.fetchall()
    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL", _ex)
    finally:
        if connection:
            connection.close() #закрытие подключения
            print("[INFO] PostgreSQL connection closed")
    return render_template("catalog.html", items=items, sess=sess)

# Панель для добавления товара в каталог главным работникам
@app.route('/panel/add_item', methods=['GET', 'POST'])
def add_item():
    if 'employee' in session:
        try:
            connection = psycopg2.connect(
                host=host,
                user=user,
                password=password,
                database=db_name
            )
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""SELECT login, password
                       FROM "Librarian"
                       WHERE login = '{session['employee'][0]}' AND password = '{session['employee'][1]}'
                           """
                )
                try:
                    result = cursor.fetchall()

                    if admin_list.count(result[0][0]):
                        typeofsession = 'item_admin'
                except:
                    pass
        except Exception as _ex:
            print("[INFO] Error while working with PostgreSQL", _ex)
        finally:
            if connection:
                connection.close()
                print("[INFO] PostgreSQL connection closed")

        if request.method == "POST":

            try:
                connection = psycopg2.connect(
                    host=host,
                    user=user,
                    password=password,
                    database=db_name
                )
                with connection.cursor() as cursor:
                    cursor.execute(
                        f"""SELECT login, password
                            FROM "Librarian"
                            WHERE "login" = '{session['employee'][0]}' AND password = '{session['employee'][1]}'
                    """
                    )
                    try:
                        result = cursor.fetchall()

                    except:
                        pass

                    if result:
                        cursor.execute(
                            f"""INSERT INTO "book" (name, id, author, href) VALUES ('{str(request.form['item_name'])}',DEFAULT, '{str(request.form['author'])}', '{str(request.form['href'])}');
                    """
                        )#Добавление нового предмета, указание цены и названия.
                    connection.commit()#Подтверждение транзакции
            except Exception as _ex:
                print("[INFO] Error while working with PostgreSQL", _ex)
            finally:
                if connection:
                    connection.close()
                    print("[INFO] PostgreSQL connection closed")
        return render_template("add_order.html", tip='item_admin')
    else:
        return ('404')


#Функция для изменения данных об пользователе
@app.route('/change', methods=['GET', 'POST'])
def change():
    if request.method == 'POST':
        if 'logged_in' in session:
            print('Чувак зареган')
            try:
                connection = psycopg2.connect(
                    host=host,
                    user=user,
                    password=password,
                    database=db_name
                )
                with connection.cursor() as cursor:
                    cursor.execute(
                        f"""SELECT login, password
                                            FROM "Client"
                                            WHERE login = '{str(session['logged_in'][0])}'
                    """
                    )
                    result = cursor.fetchall()
                    if not result:
                        error = 'Invalid username'
                    else:
                        if result[0][1] == session['logged_in'][1]:
                            print(request.form['login'])
                            print(request.form['fio'])
                            print(request.form['telephone'])
                            print(request.form['password'])
                            cursor.execute(
                                f"""UPDATE "Client"
                                    SET "fio" = '{str(request.form['fio'])}', "login" = '{str(request.form['login'])}', "password" = '{str(request.form['password'])}', "telephone" = {int(request.form['telephone'])}
                                    WHERE "login" = '{session['logged_in'][0]}';
                                                """
                            )#Получаются запросы для изменения данных
                            connection.commit()
                            return redirect(url_for("login"))
                        else:
                            error = 'Invalid password'
            except Exception as _ex:
                print("[INFO] Error while working with PostgreSQL", _ex)
            finally:
                if connection:
                    connection.close()
                    print("[INFO] PostgreSQL connection closed")
        return ('Не авторизован')
    else:
        return ('404')


#Личный кабинет пользователя
@app.route('/inside', methods=['GET', 'POST'])
def inside():
    if 'logged_in' in session:
        print('Чувак зареган12')
        try:
            connection = psycopg2.connect(
                host=host,
                user=user,
                password=password,
                database=db_name
            )
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""SELECT *
                        FROM "Book_Client" NATURAL JOIN "book"
                        WHERE "Book_Client"."id" = "book"."id" AND "login" = '{session['logged_in'][0]}'
"""
                )
                result = cursor.fetchall()
                print(result)
                print('jopa?1')
                return render_template("cabinet.html", tip='cabinet', books= result)
        except Exception as _ex:
            # return redirect(url_for("logout"))#Служит для избежания лишних ошибок
            print("[INFO] Error while working with PostgreSQL", _ex)
        finally:
            if connection:
                connection.close()
                print("[INFO] PostgreSQL connection closed")
    else:
        return ('Вы не авторизированы')


# Авторизация клиента
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        try:
            connection = psycopg2.connect(
                host=host,
                user=user,
                password=password,
                database=db_name
            )
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""SELECT login, password
                        FROM "Client"
                        WHERE login = '{str(request.form['username'])}'
"""
                )
                result = cursor.fetchall()
                if not result:
                    error = 'Invalid username'
                else:
                    if str(request.form['password']) == result[0][1]:
                        # session.init_app(app)
                        print('success')
                        session['logged_in'] = [str(request.form['username']), str(request.form['password'])]
                        print(session['logged_in'])
                        flash('You were logged in')
                        return redirect("/")
                    else:
                        error = 'Invalid password'
        except Exception as _ex:
            print("[INFO] Error while working with PostgreSQL", _ex)
        finally:
            if connection:
                connection.close()
                print("[INFO] PostgreSQL connection closed")
    return render_template('login.html', error=error, tip='login')


#Адрес для авторизации работников
@app.route('/employee', methods=['GET', 'POST'])
def employee():
    error = None
    if request.method == 'POST':
        try:
            connection = psycopg2.connect(
                host=host,
                user=user,
                password=password,
                database=db_name
            )
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""SELECT login, password
                        FROM "Librarian"
                        WHERE login = '{str(request.form['username'])}'
"""
                )#Запрос на получения логина пароля из БД
                result = cursor.fetchall()
                if not result:
                    error = 'Invalid username'
                else:#Проверка на соответствие
                    if str(request.form['password']) == result[0][1]:
                        # session.init_app(app)
                        session['employee'] = [str(request.form['username']), str(request.form['password'])]
                        flash('Вы вошли как работник')#Всплывающее окошко
                        return redirect(url_for(""))
                    else:
                        error = 'Invalid password'
        except Exception as _ex:
            print("[INFO] Error while working with PostgreSQL", _ex)
        finally:
            if connection:
                connection.close()
                print("[INFO] PostgreSQL connection closed")
    return render_template('employee.html', error=error, tip='login')


# Панель работника
@app.route('/panel', methods=['GET', 'POST'])
def panel():
    if 'employee' in session:
        try:
            connection = psycopg2.connect(
                host=host,
                user=user,
                password=password,
                database=db_name
            )
            with connection.cursor() as cursor:
                print('srabotalo')
        except Exception as _ex:
            print("[INFO] Error while working with PostgreSQL", _ex)
        finally:
            if connection:
                connection.close()
                print("[INFO] PostgreSQL connection closed")
        return render_template("employee.html", tip='panel')#Передача в employee.html
    else:
        return ('404')


# Регистрация клиента
@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        print('connection')
        try:
            connection = psycopg2.connect(
                host=host,
                user=user,
                password=password,
                database=db_name
            )
            with connection.cursor() as cursor:
                if request.form['fio'] and request.form['login'] and request.form['password']:
                    cursor.execute(
                        f"""INSERT INTO "Client" VALUES ('{str(request.form['fio'])}', '{str(request.form['login'])}', '{str(request.form['password'])}', NULL);
                        """#Добавление в БД данных о зарегестрировавшемся пользователе
                    )
                    connection.commit()
        except Exception as _ex:
            print("[INFO] Error while working with PostgreSQL", _ex)
        finally:
            if connection:
                connection.close()
                print("[INFO] PostgreSQL connection closed")
    return render_template('login.html', error=error, tip='register')


# Страничка товара
@app.route('/item/<int:id>', methods=['GET', 'POST'])
def item(id):
    try:
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=db_name
        )
        with connection.cursor() as cursor:
            cursor.execute(
                f"""SELECT *
                    FROM "book"
                    WHERE id = {id}
                    
               """
            )
            result = cursor.fetchall()#Данные об предмете по id

    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL", _ex)
    finally:
        if connection:
            connection.close()
            print("[INFO] PostgreSQL connection closed")
    if request.method == 'POST':#Если пользователь нажал на кнопку добавить
        if 'basket' not in session:  # Создаем сессию для корзины
            session['basket'] = []
        if 'basket' in session:
            try:
                session['basket'] += [{'tip': 'item',
                                       'id': id}]#Заполнение корзины товаром

            except:
                return "Очистите корзину"


    return render_template('shop.html', id=id, item=result, tip='item')


# Оплата, корзина
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'logged_in' in session and session['basket']:#Сперва происходит наличие сессий корзины и авторизации.
        if 'basket' in session:
            result2 = []
            items = session['basket']#Объявление в переменной всех предметов и услуг в корзине.
            try:
                connection = psycopg2.connect(
                    host=host,
                    user=user,
                    password=password,
                    database=db_name
                )
                with connection.cursor() as cursor:
                    cursor.execute(f"""
                                        SELECT href, id, author, name
                                        FROM "book"

""")
                    result2 = cursor.fetchall()
                    print(result2)
            except Exception as _ex:
                print("[INFO] Error while working with PostgreSQL", _ex)
            finally:
                if connection:
                    connection.close()
                    print("[INFO] PostgreSQL connection closed")
            if request.method == "POST":
                try:
                    connection = psycopg2.connect(
                        host=host,
                        user=user,
                        password=password,
                        database=db_name
                    )
                    with connection.cursor() as cursor:
                        cursor.execute(
                            f"""SELECT login, password
                                        FROM "Client"
                                        WHERE login = '{session['logged_in'][0]}' AND password = '{session['logged_in'][1]}'
                        """
                        )
                        try:
                            result = cursor.fetchall()
                        except:
                            pass
                        timedate = date.today()
                        timedate3 = datetime.date(timedate.year, timedate.month + 1, timedate.day)
                        print(timedate)
                        print(timedate3)
                        print(type(timedate))
                        if result: #Проверка на соответствие логина и пароля в БД, а так же проверка баланса, он должен быть больше sum
                            for i in session['basket']:
                                if i['tip'] == 'item':
                                    if 'id' in i:
                                        cursor.execute(
                                            f"""INSERT INTO "Book_Client" (id, "date_in" , date_out, login) VALUES ({i['id']}, '{timedate}', '{timedate3}', '{str(session['logged_in'][0])}');
                                        """
                                        )#Добавление в заказ предметов
                            connection.commit()
                            session['basket'] = [] #Очищение корзины
                        else:
                            return ('Недостаточно средств')
                except Exception as _ex:
                    print("[INFO] Error while working with PostgreSQL", _ex)
                finally:
                    if connection:
                        connection.close()
                        print("[INFO] PostgreSQL connection closed")
            return render_template('shop.html', tip='checkout', items=items, hrefs=result2)
    else:
        return ('Корзина пуста')

#Функция для очищения корзины
@app.route('/clean', methods=['GET', 'POST'])
def clean():
    session['basket'] = []
    return redirect(url_for('checkout'))


# Разлогиниться
@app.route('/logout')
def logout():
    # session.pop('logged_in', None)
    if 'logged_in' in session:
        session.pop('logged_in', None)#Удаление сессии клиента
    if 'employee' in session:
        session.pop('employee', None)#Удаление сессии работника
    if 'basket' in session:
        session.pop('employee', None)#очистка корзины
    flash('You were logged out')#Всплывающее окошко, что вышел
    return redirect(url_for('index'))


if __name__ == "__main__":#Режим отладки
    app.run(debug=True)
