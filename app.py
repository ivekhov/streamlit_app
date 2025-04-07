import streamlit as st

# 🔐 Простейшее хранилище пользователей
USERS = {
    "admin": "admin123",
    "user1": "password1",
    "data_analyst": "securepass"
}

# 🧠 Проверка логина и пароля
def check_credentials(username, password):
    return USERS.get(username) == password

# 💾 Сессионное состояние (Streamlit 1.18+)
def login_session():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = ""

# 📥 Форма логина
def login_form():
    st.title("🔐 Авторизация")
    with st.form("login_form"):
        username = st.text_input("Логин")
        password = st.text_input("Пароль", type="password")
        submitted = st.form_submit_button("Войти")
        if submitted:
            if check_credentials(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Добро пожаловать, {username}!")
            else:
                st.error("Неверный логин или пароль")

# 📤 Главная страница после входа
def main_app():
    st.sidebar.write(f"👤 Вы вошли как: **{st.session_state.username}**")
    st.sidebar.button("Выйти", on_click=logout)

    st.title("📊 Основной интерфейс приложения")
    st.write("Здесь может быть дашборд, визуализация данных или аналитика.")

# 🚪 Выход
def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""

# 🚀 Запуск
def main():
    login_session()
    if st.session_state.logged_in:
        main_app()
    else:
        login_form()

if __name__ == "__main__":
    main()
