import streamlit as st
import bcrypt
import sqlite3

DB_NAME = "users.db"

# 📁 Инициализация базы с ролевой моделью
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash BLOB,
            role TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# 📝 Регистрация с выбором роли
def register_user(username, password, role="viewer"):
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", (username, hashed_pw, role))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# 🔍 Аутентификация и извлечение роли
def check_credentials(username, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT password_hash, role FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    if row and bcrypt.checkpw(password.encode('utf-8'), row[0]):
        return True, row[1]
    return False, None

def login_session():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""

def login_form():
    st.title("🔐 Вход")
    with st.form("login_form"):
        username = st.text_input("Логин")
        password = st.text_input("Пароль", type="password")
        submitted = st.form_submit_button("Войти")
        if submitted:
            valid, role = check_credentials(username, password)
            if valid:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = role
                st.success(f"Добро пожаловать, {username}! Ваша роль: {role}")
            else:
                st.error("Неверный логин или пароль")



# 🧭 Интерфейс по ролям
def main_app():
    st.sidebar.write(f"👤 Вы вошли как: **{st.session_state.username}** ({st.session_state.role})")
    st.sidebar.button("Выйти", on_click=logout)

    role = st.session_state.role

    if role == "admin":
        admin_dashboard()
    elif role == "analyst" or role == "viewer":
        password_change_form()  # Возможность смены пароля для пользователя
    else:
        st.error("Неизвестная роль. Обратитесь к администратору.")





# 👑 Админский интерфейс
def admin_dashboard():
    st.title("👑 Админ-панель")
    st.write("Управление пользователями и ролями")

    st.subheader("➕ Добавить нового пользователя")
    with st.form("admin_register_form"):
        new_username = st.text_input("Новый логин")
        new_password = st.text_input("Новый пароль", type="password")
        new_role = st.selectbox("Роль", ["viewer", "analyst", "admin"])
        submitted = st.form_submit_button("Создать пользователя")
        if submitted:
            if register_user(new_username, new_password, new_role):
                st.success("Пользователь успешно создан!")
            else:
                st.error("Такой логин уже существует.")

    st.divider()

    # Добавим форму для смены пароля
    password_change_form()

    show_all_users()


def update_user_role(username, new_role):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET role = ? WHERE username = ?", (new_role, username))
    conn.commit()
    conn.close()


def show_all_users():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT username, role FROM users")
    users = c.fetchall()
    conn.close()

    st.subheader("📋 Управление пользователями")

    roles = ["admin", "analyst", "viewer"]

    for user, role in users:
        cols = st.columns([3, 2, 2])
        with cols[0]:
            st.write(user)
        with cols[1]:
            new_role = st.selectbox(
                f"Роль для {user}", roles, index=roles.index(role), key=f"role_{user}",
                disabled=(user == st.session_state.username)
            )
        with cols[2]:
            if user != st.session_state.username:
                if st.button("Обновить", key=f"update_{user}"):
                    update_user_role(user, new_role)
                    st.success(f"Роль для {user} обновлена на {new_role}")
                    st.rerun()
            else:
                st.write("👤 (вы)")


# 📊 Интерфейс аналитика
def analyst_dashboard():
    st.title("📊 Аналитика")
    st.write("Здесь доступ к графикам, дашбордам и моделям.")

# 👁 Интерфейс для просмотра
def viewer_dashboard():
    st.title("📄 Просмотр отчётов")
    st.write("Ограниченный доступ: только к итоговым метрикам и PDF.")

def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""


def create_initial_admin():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Проверим, существует ли уже админ
    c.execute("SELECT * FROM users WHERE role = 'admin'")
    if not c.fetchone():
        username = "admin"
        password = "admin123"  # ⚠️ Измени перед деплоем!
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        c.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", (username, hashed_pw, "admin"))
        conn.commit()
        st.info(f"Создан пользователь `admin` с паролем `{password}`")
    conn.close()


def change_password(username, old_password, new_password):
    # Проверим старый пароль
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()

    if row and bcrypt.checkpw(old_password.encode('utf-8'), row[0]):
        # Старый пароль верный, обновляем на новый
        hashed_pw = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("UPDATE users SET password_hash = ? WHERE username = ?", (hashed_pw, username))
        conn.commit()
        conn.close()
        return True
    return False


def password_change_form():
    st.title("🔑 Смена пароля")

    # Различие между пользователем и администратором
    if st.session_state.role == "admin":
        username = st.text_input("Логин пользователя, чей пароль меняем (оставьте пустым для изменения собственного)", "")
    else:
        username = st.session_state.username

    old_password = st.text_input("Старый пароль", type="password")
    new_password = st.text_input("Новый пароль", type="password")
    confirm_password = st.text_input("Подтвердите новый пароль", type="password")

    if new_password != confirm_password:
        st.error("Пароли не совпадают!")

    elif st.button("Изменить пароль"):
        if username == "":
            st.error("Пожалуйста, укажите логин для смены пароля")
        elif change_password(username, old_password, new_password):
            st.success(f"Пароль для {username} успешно изменён.")
        else:
            st.error("Неверный старый пароль.")






def main():
    init_db()
    create_initial_admin()
    login_session()

    if not st.session_state.logged_in:
        st.title("🔐 Авторизация")
        login_form()
    else:
        main_app()


if __name__ == "__main__":
    main()


