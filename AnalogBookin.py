import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import psycopg2
from psycopg2.errors import TransactionRollbackError


class UserManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Главное окно")

        self.conn = psycopg2.connect(
            host="127.0.0.1",
            database="MDaMDS",
            user="postgres",
            password="12345678"
        )
        # Кнопки
        self.btn_register = ttk.Button(root, text="Зарегистрироваться", command=self.open_registration_form)
        self.btn_register.pack(pady=10)

        self.btn_authenticate = ttk.Button(root, text="Авторизоваться", command=self.open_authentication_form)
        self.btn_authenticate.pack(pady=10)

        self.btn_exit = ttk.Button(root, text="Закрыть приложение", command=root.destroy)
        self.btn_exit.pack(pady=10)

    def open_registration_form(self):
        registration_window = tk.Toplevel(self.root)
        registration_window.title("Форма регистрации")
        registration_form = RegistrationForm(registration_window)

    def open_authentication_form(self):
        authentication_window = tk.Toplevel(self.root)
        authentication_window.title("Форма аутентификации")
        authentication_form = AuthenticationForm(authentication_window)


class RegistrationForm:
    def __init__(self, root):
        self.root = root
        self.root.title("Форма регистрации")
        self.conn = psycopg2.connect(
            host="127.0.0.1",
            database="MDaMDS",
            user="postgres",
            password="12345678"
        )

        self.label_username = ttk.Label(root, text="Имя пользователя:")
        self.entry_username = ttk.Entry(root)

        self.label_password = ttk.Label(root, text="Пароль:")
        self.entry_password = ttk.Entry(root, show="*")

        self.label_first_name = ttk.Label(root, text="Имя:")
        self.entry_first_name = ttk.Entry(root)

        self.label_last_name = ttk.Label(root, text="Фамилия:")
        self.entry_last_name = ttk.Entry(root)

        self.btn_register = ttk.Button(root, text="Зарегистрироваться", command=self.register_user)

        # Размещение элементов на форме
        self.label_username.grid(row=0, column=0, padx=10, pady=5, sticky=tk.E)
        self.entry_username.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)

        self.label_password.grid(row=1, column=0, padx=10, pady=5, sticky=tk.E)
        self.entry_password.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)

        self.label_first_name.grid(row=2, column=0, padx=10, pady=5, sticky=tk.E)
        self.entry_first_name.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)

        self.label_last_name.grid(row=3, column=0, padx=10, pady=5, sticky=tk.E)
        self.entry_last_name.grid(row=3, column=1, padx=10, pady=5, sticky=tk.W)

        self.btn_register.grid(row=4, columnspan=2, pady=10)

    def register_user(self):
        # Получите значения из элементов интерфейса
        user_login = self.entry_username.get()
        user_password = self.entry_password.get()
        user_first_name = self.entry_first_name.get()
        user_last_name = self.entry_last_name.get()

        # Проверка наличия данных
        if any(not data.strip() for data in [user_login, user_password, user_first_name, user_last_name]):
            messagebox.showerror("Error", "All fields must be filled")
            return

        try:
            # Открываем транзакцию
            with self.conn:
                with self.conn.cursor() as cursor:
                    # Проверяем наличие пользователя в базе данных
                    cursor.execute("SELECT 1 FROM Users WHERE user_login = %s", (user_login,))
                    existing_user = cursor.fetchone()

                    if existing_user:
                        messagebox.showerror("Error", "User with this login already exists")
                        return

                    # Вызываем процедуру регистрации
                    cursor.execute("CALL register_user(%s, %s, %s, %s, %s)",
                                   (user_login, user_password, user_first_name, user_last_name, 2))

            # Показываем сообщение об успешном выполнении
            messagebox.showinfo("Success", "Operation completed successfully!")
            UserMainWindow(self.root, self.conn, 2)


        except TransactionRollbackError as e:
            # В случае ошибки откатываем транзакцию
            print("Error", f"An error occurred: {e}")

        finally:
            self.root.destroy()


def get_table_columns(table_name, conn):
    try:
        cursor = conn.cursor()
        query = f"""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = '{table_name}';
        """
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        cursor.close()

def create_table_from_columns(root, table_columns):
    table_frame = ttk.Frame(root)
    table_frame.pack()

    for column_name, in table_columns:
        label = ttk.Label(table_frame, text=column_name, borderwidth=1, relief="solid", width=20)
        label.pack(side="left")

    return table_frame

def load_data(root, conn, table_name='actionlog'):
    try:
        with conn.cursor() as cursor:
            query = f"SELECT * FROM {table_name}"
            cursor.execute(query)
            results = cursor.fetchall()

            # Create Treeview widget
            treeview = ttk.Treeview(root)
            treeview["columns"] = [column_name for column_name, in get_table_columns(table_name, conn)]
            treeview.heading("#0", text="", anchor="w")
            treeview.column("#0", anchor="w", width=1)

            for column_name, in get_table_columns(table_name, conn):
                treeview.heading(column_name, text=column_name)
                treeview.column(column_name, anchor="w", width=100)

            treeview.pack()

            # Fill Treeview with data
            for row in results:
                treeview.insert("", "end", values=row)

    except Exception as e:
        print(f"Error: {e}")


class CreateOfferWindow:
    def __init__(self, root, conn):
        self.root = root
        self.conn = conn

        self.create_order_window = tk.Toplevel(root)
        self.create_order_window.title("Create Order")

        # Fetch data for dropdown list
        apartment_data = self.fetch_apartment_data()

        # Dropdown for apartment selection
        self.apartment_label = tk.Label(self.create_order_window, text="Apartment:")
        self.apartment_var = tk.StringVar()
        self.apartment_dropdown = ttk.Combobox(self.create_order_window, textvariable=self.apartment_var, values=apartment_data)
        self.apartment_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        self.apartment_dropdown.grid(row=0, column=1, padx=10, pady=10, sticky=tk.W)

        # Other entry fields for order details
        self.price_label = tk.Label(self.create_order_window, text="Price per Night:")
        self.price_entry = tk.Entry(self.create_order_window)
        self.price_label.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        self.price_entry.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)

        self.stay_days_label = tk.Label(self.create_order_window, text="Stay Days:")
        self.stay_days_entry = tk.Entry(self.create_order_window)
        self.stay_days_label.grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        self.stay_days_entry.grid(row=2, column=1, padx=10, pady=10, sticky=tk.W)

        self.country_label = tk.Label(self.create_order_window, text="Country:")
        self.country_entry = tk.Entry(self.create_order_window)
        self.country_label.grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)
        self.country_entry.grid(row=3, column=1, padx=10, pady=10, sticky=tk.W)

        self.address_label = tk.Label(self.create_order_window, text="Address:")
        self.address_entry = tk.Entry(self.create_order_window)
        self.address_label.grid(row=4, column=0, padx=10, pady=10, sticky=tk.W)
        self.address_entry.grid(row=4, column=1, padx=10, pady=10, sticky=tk.W)

        # Button to submit the order
        self.submit_button = tk.Button(self.create_order_window, text="Submit Order", command=self.submit_order)
        self.submit_button.grid(row=5, column=0, columnspan=2, pady=20)

    def fetch_apartment_data(self):
        try:
            with self.conn.cursor() as cursor:
                query = """
                SELECT
                    type_name,
                    num_of_floors,
                    num_of_rooms,
                    num_of_beds,
                    apartment_type
                FROM
                    apartments
                LEFT JOIN apartmenttypes ON apartments.apartment_type::int = apartmenttypes.id;
                """
                cursor.execute(query)
                apartment_data = cursor.fetchall()
                return [f"{data[0]} - {data[1]} floors, {data[2]} rooms, {data[3]} beds" for data in apartment_data]
        except Exception as e:
            print(f"Error fetching apartment data: {e}")
            return []

    def validate_numeric_input(self, value):
        try:
            float_value = float(value)
            if float_value < 0:
                return False
            return True
        except ValueError:
            return False

    def submit_order(self):
        try:
            selected_apartment = self.apartment_var.get()
            print(self.apartment_var.get())
            price_per_night = self.price_entry.get()
            stay_days = self.stay_days_entry.get()
            country = self.country_entry.get()
            address = self.address_entry.get()


            if not self.validate_numeric_input(price_per_night) or not self.validate_numeric_input(stay_days):
                tk.messagebox.showerror("Error", "Invalid numeric input for price per night or stay days")
                return

            if not selected_apartment or not country or not address:
                tk.messagebox.showerror("Error", "All fields must be filled")
                return

            with self.conn.cursor() as cursor:
                apartment_type = selected_apartment.split(" - ")[0]
                cursor.execute("SELECT id FROM apartmenttypes WHERE type_name = %s", (apartment_type,))
                apartment_id = cursor.fetchone()[0]

                insert_query = """
                INSERT INTO Offers (apartment_id, price_per_night, stay_days, country, address)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id_offer;
                """
                cursor.execute(insert_query, (apartment_id, price_per_night, stay_days, country, address))
                offer_id = cursor.fetchone()[0]

                self.conn.commit()

                tk.messagebox.showinfo("Success", f"Offer submitted successfully! Offer ID: {offer_id}")

                # Close the create_order_window
                self.create_order_window.destroy()

        except Exception as e:
            tk.messagebox.showerror("Error", f"An error occurred: {e}")

class UpdateUserRoleWindow:
    def __init__(self, root, conn):
        self.root = root
        self.conn = conn

        self.update_user_role_window = tk.Toplevel(root)
        self.update_user_role_window.title("Update User Role")

        # Label and Combobox for User Login
        self.user_login_label = tk.Label(self.update_user_role_window, text="User Login:")
        self.user_login_var = tk.StringVar()
        self.user_login_combobox = ttk.Combobox(self.update_user_role_window, textvariable=self.user_login_var)
        self.user_login_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        self.user_login_combobox.grid(row=0, column=1, padx=10, pady=10, sticky=tk.W)

        # Label and Combobox for User Role
        self.user_role_label = tk.Label(self.update_user_role_window, text="User Role:")
        self.user_role_var = tk.StringVar()
        self.user_role_combobox = ttk.Combobox(
            self.update_user_role_window,
            textvariable=self.user_role_var,
            values=["Admin", "Moderator", "User"]
        )
        self.user_role_label.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        self.user_role_combobox.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)

        # Button to update user role
        self.update_button = tk.Button(self.update_user_role_window, text="Update Role", command=self.update_role)
        self.update_button.grid(row=2, column=0, columnspan=2, pady=20)

        # Fetch user data for Combobox
        self.fetch_user_data()

    def fetch_user_data(self):
        try:
            with self.conn.cursor() as cursor:
                query = "SELECT id_user, user_login, role_id FROM users"
                cursor.execute(query)
                user_data = cursor.fetchall()

            # Update Combobox with user logins
            logins = [f"{login} ({role})" for _, login, role in user_data]
            self.user_login_combobox["values"] = logins

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while fetching user data: {e}")

    def update_role(self):
        try:
            selected_login = self.user_login_var.get()
            user_id = selected_login.split(" ")[0]  # Extract user ID from the selected login
            user_role = self.user_role_var.get()
            tmp = {"Admin":1, "User":2, "Moderator":4}
            user_role = tmp.get(user_role)


            with self.conn.cursor() as cursor:
                # Assuming you have a table named "users" with columns "id" and "role"
                update_query = "UPDATE users SET role_id = %s WHERE user_login = %s"
                cursor.execute(update_query, (user_role, user_id))

            self.conn.commit()
            messagebox.showinfo("Success", "User role updated successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
class AdminMainWindow:
    def __init__(self, root, conn, admin_id):
        self.root = root
        self.conn = conn
        self.admin_id = admin_id

        self.label_welcome = tk.Label(self.root, text=f"Welcome, Admin (Admin ID: {admin_id})")
        self.label_welcome.pack()

        self.treeview = ttk.Treeview(self.root)

        self.button_load_data = tk.Button(self.root, text="Load data", command=self.load_data_1)
        self.button_create_offer = tk.Button(self.root, text="Create Offer", command=self.create_offer)
        self.button_update_user = tk.Button(self.root, text="Update User", command=self.update_user_role)
        self.button_delete_user = tk.Button(self.root, text="Delete User", command=self.delete_user)
        self.button_add_review = tk.Button(self.root, text="Add Review", command=self.add_review)

        self.button_load_data.pack()
        self.button_create_offer.pack()
        self.button_update_user.pack()
        self.button_delete_user.pack()
        self.button_add_review.pack()

    def load_data_1(self, name ='actionlog'):
        load_data(self.root,self.conn,name)

    def create_offer(self):
        create_order_window = CreateOfferWindow(root, self.conn)

        # Ждем, пока окно заказа не будет закрыто
        root.wait_window(create_order_window.create_order_window)

        # После закрытия окна заказа выполняем load_data
        load_data(self.root, self.conn, 'offers')

    def update_user_role(self):
        update_user_role_window = UpdateUserRoleWindow(root, self.conn)

    def delete_user(self):
        # Реализация удаления пользователя
        pass

    def add_review(self):
        # Реализация добавления отзыва
        pass


class UserMainWindow:
    def __init__(self, root, conn, login):
        self.root = root
        self.conn = conn
        self.login = login

        # Добавьте элементы интерфейса для окна пользователя
        self.label_welcome = tk.Label(self.root, text=f"Welcome, User (User: {login})")
        self.label_welcome.grid(row=0, column=0, columnspan=2, pady=10)

        self.btn_view_offers = tk.Button(self.root, text="View Offers", command=self.view_offers)
        self.btn_view_offers.grid(row=1, column=0, pady=5)

        self.btn_view_reviews = tk.Button(self.root, text="View Reviews", command=self.view_reviews)
        self.btn_view_reviews.grid(row=1, column=1, pady=5)

        # Другие кнопки и элементы интерфейса

    def view_offers(self):
        # Логика для просмотра предложений
        pass

    def view_reviews(self):
        # Логика для просмотра отзывов
        pass


def open_main_window(user_id):
    root = tk.Tk()
    conn = psycopg2.connect(
        host="127.0.0.1",
        database="MDaMDS",
        user="postgres",
        password="12345678")

    with conn.cursor() as cursor:
        query = "SELECT role_id, user_login FROM Users WHERE id_user = %s;"
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()

    if result[0] == 1:  # Пример ID для администратора
        AdminMainWindow(root, conn, result[1])
    if result[0] == 2:  # Пример ID для пользователя
        UserMainWindow(root, conn, result[1])
    else:
        print("Unknown role")

    root.mainloop()


class AuthenticationForm:
    def __init__(self, root):
        self.root = root
        self.root.title("Форма аутентификации")
        self.conn = psycopg2.connect(
            host="127.0.0.1",
            database="MDaMDS",
            user="postgres",
            password="12345678"
        )

        # Элементы интерфейса для формы аутентификации
        self.label_username = ttk.Label(root, text="Имя пользователя:")
        self.entry_username = ttk.Entry(root)
        self.entry_username.insert(0,'Admin')


        self.label_password = ttk.Label(root, text="Пароль:")
        self.entry_password = ttk.Entry(root, show="*", )
        self.entry_password.insert(0,'Admin')


        self.btn_authenticate = ttk.Button(root, text="Войти", command=self.authenticate_user)

        # Размещение элементов на форме
        self.label_username.grid(row=0, column=0, padx=10, pady=5, sticky=tk.E)
        self.entry_username.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)

        self.label_password.grid(row=1, column=0, padx=10, pady=5, sticky=tk.E)
        self.entry_password.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)

        self.btn_authenticate.grid(row=2, columnspan=2, pady=10)

    def authenticate_user(self):
        username = self.entry_username.get()
        password = self.entry_password.get()

        try:
            # Открываем транзакцию
            self.conn.autocommit = False

            with self.conn.cursor() as cursor:
                # Вызываем процедуру аутентификации
                cursor.execute("SELECT authenticate_user(%s, %s)", (username, password))

                # Получаем результат
                result = cursor.fetchone()

                # Если результат True, то аутентификация прошла успешно
                if result and result[0]:
                    # cursor.execute("CALL log_authentication(%s, %s)", (result[0], "User authenticated successfully"))
                    # messagebox.showinfo("Authentication", "Authentication successful!")
                    self.root.destroy()
                    open_main_window(result[0])
                else:
                    messagebox.showerror("Authentication", "Authentication failed.")

            # Подтверждаем транзакцию
            self.conn.commit()


        except Exception as e:
            # В случае ошибки выводим сообщение и откатываем транзакцию
            print("Error", f"An error occurred: {e}")
            self.conn.rollback()

        finally:
            # Восстанавливаем режим автокоммита и закрываем соединение
            self.conn.autocommit = True
            self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = UserManagementApp(root)
    root.mainloop()
