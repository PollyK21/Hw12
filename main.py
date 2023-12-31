from collections import UserDict
from datetime import date, datetime
import pickle


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
    def __init__(self, filename):
        super().__init__()
        self.filename = filename

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
        with open(self.filename, "wb") as fh:
            pickle.dump(self, fh)

    def read_from_file(self):
        with open(self.filename, "rb") as fh:
            decoded = pickle.load(fh)
            return decoded


# book = AddressBook("book1.bin")

# # Створення запису для John
# john_record = Record("John")
# john_record.add_phone("1234567890")
# try:
#     john_record.add_phone("9876543210l")
# except ValueError:
#     print("помилка")
# try:
#     john_record.set_birthday("20.3.1997")
# except ValueError:
#     print("помилка")


# # Додавання запису John до адресної книги
# book.add_record(john_record)

# Створення та додавання нового запису для Jane
# jane_record = Record("Jane")
# jane_record.add_phone("9876543210")
# book.add_record(jane_record)

# john = book.search("1")
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


# # Збереження на диск
# book.save_to_disk()

# # Відновлення з диска
# book.read_from_file()

# for name, record in book.data.items():
#     print(record)