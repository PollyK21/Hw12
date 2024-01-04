from collections import UserDict
from datetime import date, datetime
import csv


class Field:
    def __init__(self, value):
        self.value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        if self.is_valid_format(value):
            self.__value = value
            # return self.__value
        else:
            raise ValueError

    def __str__(self):
        return str(self.value)


class Name(Field):
    def is_valid_format(self, value):
        return True


class Phone(Field):
    def is_valid_format(self, value):
        if (len(value) == 10 and value.isdigit()):
            return True
        else:
            return False


class Birthday(Field):
    def is_valid_format(self, value):
        try:
            datetime.strptime(value, '%d.%m.%Y')
            return True
        except ValueError:
            return False


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        new_phone = Phone(phone)
        self.phones.append(new_phone)

    def set_birthday(self, birthday):
        if self.birthday is not None:
            raise ValueError("Birthday already set for this contact")
        else:
            self.birthday = Birthday(birthday)

    def remove_phone(self, phone):
        for ph in self.phones:
            if ph.value == phone:
                self.phones.remove(ph)

    def edit_phone(self, old_phone, new_phone):
        if any(p.value == old_phone for p in self.phones):
            self.remove_phone(old_phone)
            self.add_phone(new_phone)
        else:
            raise ValueError

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def days_to_birthday(self):
        if self.birthday is not None:
            today = date.today()
            birth_date = datetime.strptime(f"{self.birthday}", "%d.%m.%Y").date()
            new_b = birth_date.replace(year=today.year)
            if today > new_b:
                new_b = new_b.replace(year=today.year + 1)
            delta = new_b - today
            return delta
        else:
            return None

    def __str__(self):
        phones_str = "; ".join(str(phone) for phone in self.phones)
        return f"Contact name: {self.name}, phones: {phones_str}, birthday: {self.birthday}"


class AddressBook(UserDict):
    def __init__(self, csv_file=None):
        super().__init__()
        self.csv_file = csv_file
        self.records = []
        if csv_file is not None:
            self.read_from_file()

    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def search(self, query):
        results = []
        for name, record in self.data.items():
            if query.lower() in name.lower():
                results.append(str(record))
                continue
            # Пошук за номерами телефону
            for phone in record.phones:
                if query.lower() in phone.value.lower():
                    results.append(str(record))
                    break
            # Пошук за днем народження
                if record.birthday is not None:
                    birthday_str = str(record.birthday)
                    if query.lower() in birthday_str.lower():
                        results.append(str(record))
        return "\n".join(res for res in results)

    def delete(self, name):
        if name in self.data:
            self.data.pop(name)

    def iterator(self, page_size):
        records = list(self.data.values())
        total_records = len(records)
        start = 0
        page_number = 1

        while start < total_records:
            page = records[start:start + page_size]
            yield f"Page {page_number}:\n" + "\n".join(str(record) for record in page)
            start += page_size
            page_number += 1

    def save_to_disk(self):
        with open(self.csv_file, 'w', newline='') as file:
            field = ["Name", "Phones", "Birthday"]
            writer = csv.DictWriter(file, fieldnames=field)
            writer.writeheader()
            # Записуємо дані
            for name, record in self.data.items():
                phones_str = ";".join(str(phone) for phone in record.phones)
                writer.writerow({
                    "Name": name,
                    "Phones": phones_str,
                    "Birthday": str(record.birthday) if record.birthday else "None"
                })

    def read_from_file(self):
        with open(self.csv_file, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                record = Record(row["Name"])
                phones = row["Phones"].split(";")
                for phone in phones:
                    record.add_phone(phone)
                if row["Birthday"] != "None":
                    record.set_birthday(row["Birthday"])
                self.add_record(record)


def input_error(func):
    def wrapper(*args):
        try:
            return func(*args)
        except KeyError:
            return "Contact not found."
        except IndexError:
            return "Contact"
        except TypeError:
            return "Invalid input. Please check your input."
    return wrapper


@input_error
def handle_hello():
    return "How can I help you?"


@input_error
def handle_add(name, phone):
    if name not in ADDRESS_BOOK.data.keys():
        record = Record(name)
        try:
            record.add_phone(phone)
            ADDRESS_BOOK.add_record(record)
            return f"Contact {name} added with phone number {phone}"
        except ValueError:
            return "Invalid phone"
    else:
        record = ADDRESS_BOOK.find(name)
        try:
            record.add_phone(phone)
            return f"Phone number {phone} added for contact {name}"
        except ValueError:
            return "Invalid phone"


@input_error
def handle_change(name, old_phone, new_phone):
    record = ADDRESS_BOOK.find(name)
    if record is not None:
        try:
            record.edit_phone(old_phone, new_phone)
            return f"Phone number for contact {name} changed to {new_phone}"
        except ValueError:
            return "Invalid phone"
    else:
        raise KeyError


@input_error
def handle_set_birthday(name, day):
    record = ADDRESS_BOOK.find(name)
    if record is not None:
        try:
            record.set_birthday(day)
            return f"Birthday for contact {name} is set to {day}"
        except ValueError:
            return "Please enter the date in DD.MM.YYYY format."
    else:
        raise KeyError


@input_error
def days_to_birthday(name):
    record = ADDRESS_BOOK.find(name)
    if record is not None:
        return record.days_to_birthday()
    else:
        raise KeyError


@input_error
def handle_delete(name):
    record = ADDRESS_BOOK.find(name)
    if record is not None:
        ADDRESS_BOOK.delete(name)
        return f"{name} deleted"
    else:
        raise KeyError


@input_error
def handle_phone(name):
    record = ADDRESS_BOOK.find(name)
    if record is not None:
        return record
    else:
        raise KeyError


@input_error
def handle_show_all():
    if len(ADDRESS_BOOK.data) == 0:
        raise KeyError
    else:
        all = []
        for record in ADDRESS_BOOK.data.values():
            all.append(str(record))
        return "\n".join(res for res in all)


@input_error
def handle_search(query):
    return ADDRESS_BOOK.search(query)


DEFAULT_FILE = "new_book.csv"


@input_error
def handle_open(csv_file=None):
    global ADDRESS_BOOK, DEFAULT_FILE
    if csv_file is None:
        # Якщо файл не вказаний, відкриваємо файл за замовченням
        csv_file = DEFAULT_FILE
    try:
        ADDRESS_BOOK = AddressBook(csv_file)
        DEFAULT_FILE = csv_file
        return f"Address book opened from {csv_file}"
    except FileNotFoundError:
        try:
            ADDRESS_BOOK = AddressBook(DEFAULT_FILE)
            return f"File not found. Address book opened from {DEFAULT_FILE}"
        except FileNotFoundError:
            ADDRESS_BOOK = AddressBook(None)
            return "Starting with an empty address book."


@input_error
def handle_save():
    global ADDRESS_BOOK
    if ADDRESS_BOOK.csv_file is None:
        # Якщо ADDRESS_BOOK створено без файлу, тобто AddressBook(None), то зберегти в новий файл
        ADDRESS_BOOK.csv_file = DEFAULT_FILE
        ADDRESS_BOOK.save_to_disk()
        return f"Address book saved to {DEFAULT_FILE}"
    else:
        # Якщо ADDRESS_BOOK має вказаний файл, то перезаписати його
        ADDRESS_BOOK.save_to_disk()
        return f"Address book saved to {ADDRESS_BOOK.csv_file}"


def show_help():
    help_message = """
        Доступні команди:
        hello: Вивести вітальне повідомлення.
        open [ім'я_файлу]: Відкрити адресну книгу з вказаного файлу або останнього відкритого файлу.
        save: Зберегти поточну адресну книгу.
        add [іʼмя] [телефон]: Додати новий контакт до адресної книги.
        change [іʼмя] [старий телефон] [новий телефон]: Змінити дані існуючого контакту.
        info [іʼмя]: Вивести інформацію про контакт.
        show all: Відобразити всі контакти в адресній книзі.
        set birthday [іʼмя] [дата]: Встановити день народження для контакту.
        days to birthday [іʼмя]: Розрахувати кількість днів до наступного дня народження для контакту.
        delete [іʼмя]: Видалити контакт з адресної книги.
        search [запит]: Пошук в адресній книзі за символами.
        """
    return help_message


COMMANDS = {
    "help": show_help,
    "hello": handle_hello,
    "open": handle_open,
    "save": handle_save,
    "add": handle_add,
    "change": handle_change,
    "info": handle_phone,
    "show all": handle_show_all,
    "set birthday": handle_set_birthday,
    "days to birthday": days_to_birthday,
    "delete": handle_delete,
    "search": handle_search
}


@input_error
def main():
    global ADDRESS_BOOK
    handle_open()
    while True:
        user_input = input("Enter a command: ").lower()
        if user_input in ["good bye", "close", "exit"]:
            print(handle_save())
            print("Good bye!")
            break
        for command in COMMANDS.keys():
            if user_input.startswith(command):
                args = user_input[len(command):].split()
                print(COMMANDS[command](*args))
                break
        else:
            print("Unknown command. Please try again.")


if __name__ == "__main__":
    main()

# csv_file = "book.csv"
# book = AddressBook(csv_file)

# # Створення запису для John
# john_record = Record("John")
# john_record.add_phone("1234567890")
# john_record.add_phone("0000000000")
# # # try:
# # #     john_record.add_phone("9876543210l")
# # # except ValueError:
# # #     print("помилка")
# try:
#     john_record.set_birthday("20.3.1997")
# except ValueError:
#     print("помилка")


# # # Додавання запису John до адресної книги
# book.add_record(john_record)

# # Створення та додавання нового запису для Jane
# jane_record = Record("Jane")
# jane_record.add_phone("9876543210")
# book.add_record(jane_record)

# john = book.search("j")
# print(john)

# print(book)

# Знаходження та редагування телефону для John
# john = book.find("John")
# print(john)
# john.edit_phone("1234567890", "1112223333")
    
# days = john.days_to_birthday()
# print(days)

# print(john_record)  # Виведення: Contact name: John, phones: 1112223333; 5555555555


# # # Пошук конкретного телефону у записі John
# found_phone = john_record.find_phone("1234567890")
# print(found_phone)
# #   # Виведення: 5555555555


# # Видалення запису Jane
# book.delete("Jane")


# for page in book.iterator(3):
#     print(page)


# Виведення всіх записів у книзі
# for name, record in book.data.items():
#     print(record)


# Збереження на диск
# book.save_to_disk()

# # Відновлення з диска
# book.read_from_file()

# for name, record in book.data.items():
#     print(record)

# Створення та додавання нового запису для Jane
# a = Record("a")
# a.add_phone("9322222222")
# book.add_record(a)
    
# # Створення та додавання нового запису для Jane
# b = Record("b")
# b.add_phone("7777777777")
# book.add_record(b)

# book.save_to_disk()

# book.read_from_file()

# for name, record in book.data.items():
#     print(record)


# john = book.find("John")
# john.edit_phone("0000000000", "4444444444")
# print(john)
