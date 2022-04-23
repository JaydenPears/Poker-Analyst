import sys
import os
import time
from PIL import ImageColor, Image
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QPixmap, QFont, QIcon
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel
from PyQt5.QtWidgets import (QApplication, QDialog, QLabel, QLineEdit, QMainWindow,
                             QPushButton, QMenuBar,
                             QAction, QWidget, qApp,
                             QFileDialog, QColorDialog,
                             QMessageBox, QTableView)
from solution_for_cards import (Table, DIGNITIES_FOR_TABLE, DIGNITIES,
                                CATEGORIES, SYMBOLS, CheckCombinations, Database)


SIZE_MW = [1500, 800]
SIZE_SW = [750, 400]
SIZE_TW = [600, 400]
SIZE_FW = [1000, 450]
SIZE_FFW = [975, 400]

if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.designations_filename = 'main_designations.csv'
        self.colors_filename = 'main_colors.csv'
        self.chances_filename = 'chances.csv'

        self.font = QFont('Trebuchet MS', 10)
        self.font.setBold(True)

        self.lines_edit = []
        self.buttons = []
        self.buttons_for_chance = []
        self.labels_images_glossary = []
        self.lines_edit_chances = []
        self.labels_images_chances = []
        self.cards = []
        self.choices_buttons = []
        self.cards_at_player = {1: None, 2: None, 3: None, 4: None, 5: None, 6: None, 7: None}

        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, *SIZE_MW)
        self.setFixedSize(*SIZE_MW)
        self.setWindowTitle('Покерный аналитик')
        self.setWindowIcon(QIcon('icons/game_icon.jpg'))

        self.get_stats = QAction('&Общая статистика', self)
        self.get_stats.triggered.connect(self.get_stats_table)

        self.change_table = QAction('&Изменение таблицы', self)
        self.change_table.triggered.connect(self.do_change_table)

        self.change_category_color = QAction('&Изменение цвета категорий', self)
        self.change_category_color.triggered.connect(self.change_colors)

        self.close_app = QAction('&Закрыть приложение', self)
        self.close_app.triggered.connect(qApp.quit)

        self.menuBar = QMenuBar(self)
        self.setMenuBar(self.menuBar)

        self.fileMenu = self.menuBar.addMenu('&Настройки')
        self.fileMenu.addAction(self.get_stats)
        self.fileMenu.addAction(self.change_table)
        self.fileMenu.addAction(self.change_category_color)
        self.fileMenu.addAction(self.close_app)

        self.our_designations,\
        self.our_colors = Table(DIGNITIES).open_table(
                                                      self.designations_filename,
                                                      self.colors_filename
                                                     )

        self.our_colors_for_chances = Table(DIGNITIES).open_chances_colors(self.chances_filename)

        self.do_table(840, 30)
        self.do_glossary(620, 30)
        self.create_choice_on_preflop(50, 20)
        self.create_choice_on_next_stage(30, 400)
        self.create_table_for_chances(840, 450)
        self.create_gloassary_for_chances(620, 450)

    def get_stats_table(self):
        self.stats_table = ShowStatistics()
        self.stats_table.show()

    def create_gloassary_for_chances(self, x, y):
        self.keys = list(self.our_colors_for_chances.keys())
        self.label_book = QLabel('Глоссарий цветов для шансов\nна кругах раздачи.', self)
        self.label_book.setGeometry(x, y - 10, 200, 35)
        self.label_book.setFont(self.font)
        for line in range(1, 8):
            self.text = self.keys[line].split('-')
            self.label = QLineEdit(f'{self.text[0]}% - {self.text[1]}%', self)
            self.label.setGeometry(x + 110, y + 30 * line, 100, 30)
            self.label.setEnabled(False)
            self.label.setFont(self.font)
            self.lines_edit_chances.append(self.label)
            self.color = self.our_colors_for_chances[self.keys[line]]

            try:
                r, g, b = ImageColor.getcolor(self.color, 'RGB')
            except ValueError:
                r, g, b = (230, 230, 230)

            self.im = Image.new('RGB', (100, 30), (r, g, b))
            self.im.save(f'{line}chance.png')
            self.pixmap = QPixmap(f'{line}chance.png')
            self.label_image_chance = QLabel(self)
            self.label_image_chance.setGeometry(x, y + 30 * line, 100, 30)
            self.label_image_chance.setPixmap(self.pixmap)
            self.labels_images_chances.append(self.label_image)
            os.remove(f'{line}chance.png')

    def paint_table_for_chances(self):
        self.keys_for_colors = list(self.our_colors_for_chances.keys())[1::]
        for i in range(13):
            for j in range(13):
                text = DIGNITIES_FOR_TABLE[i][j]
                button = self.buttons_for_chance[i][j]
                button.setStyleSheet(f'')
                try:
                    number = self.chances[text]
                    for key_color in self.keys_for_colors:
                        key_line = [int(x) for x in key_color.split('-')]
                        min_line, max_line = key_line[0], key_line[1]
                        if number >= min_line and number <= max_line:
                            color_for_button = self.our_colors_for_chances[key_color]
                except KeyError:
                    color_for_button = '#e6e6e6'
                button.setStyleSheet(f'QPushButton {{background-color:\
                                                      {color_for_button}; color: black;}}')

    def create_table_for_chances(self, x, y):
        for i in range(13):
            self.array_for_button = []
            for j in range(13):
                self.text = DIGNITIES_FOR_TABLE[i][j]
                self.btn = QPushButton(f'{self.text}', self)
                self.btn.setGeometry(x + j * 50, y + i * 25, 50, 25)
                self.btn.setFont(self.font)
                self.color_for_button = '#e6e6e6'
                self.btn.setStyleSheet(f'QPushButton {{background-color:\
                                                      {self.color_for_button}; color: black;}}')
                self.array_for_button.append(self.btn)
            self.buttons_for_chance.append(self.array_for_button.copy())

    def create_choice_on_next_stage(self, x, y):
        for i in range(5):
            self.button_for_choice = QPushButton(self)
            self.button_for_choice.setGeometry(x + i * 110, y, 100, 140)
            self.button_for_choice.setEnabled(False)
            self.button_for_choice.clicked.connect(self.choice_card)
            self.choices_buttons.append(self.button_for_choice)

        self.button_clear = QPushButton('Фолд', self)
        self.button_clear.setGeometry(x, y + 150, 100, 30)
        self.button_clear.setFont(self.font)
        self.button_clear.clicked.connect(self.clear_choice_cards_on_desk)

        self.button_next_card = QPushButton('Рейз', self)
        self.button_next_card.setGeometry(x + 110, y + 150, 100, 30)
        self.button_next_card.setFont(self.font)
        self.button_next_card.clicked.connect(self.get_new_card)

        self.label_get_chance_on_next_stage = QLabel(self)
        self.label_get_chance_on_next_stage.setText(f'Шанс на флопе: неизвестно')
        self.label_get_chance_on_next_stage.setFont(self.font)
        self.label_get_chance_on_next_stage.setGeometry(x, y - 40, 250, 50)

    def clear_choice_cards_on_desk(self):
        self.label_get_chance_on_next_stage.setText(f'Шанс на флопе: неизвестно')
        for i in range(2, 7):
            self.cards_at_player[i + 1] = None
            self.button_for_choice = self.choices_buttons[i]
            self.button_for_choice.setEnabled(False)
            self.button_for_choice.setIcon(QIcon())
        for i in range(13):
            for j in range(13):
                button = self.buttons_for_chance[i][j]
                color_for_button = '#e6e6e6'
                button.setStyleSheet(f'QPushButton {{background-color:\
                                                    {color_for_button}; color: black;}}')
        for i in range(2):
            self.choices_buttons[i].setIcon(QIcon())
            self.cards_at_player[i + 1] = None
        self.label_get_chance_on_preflop.setText('Шанс на префлопе: неизвестно')
        self.count_cards_at_user = 0

    def create_choice_on_preflop(self, x, y):
        self.label_help = QLabel(self)
        self.label_help.setText('По нажатию на одну из двух кнопок ниже появляется\n'
                                'возможность выбрать карту на префлопе в новом окне.')
        self.label_help.setFont(self.font)
        self.label_help.setGeometry(x - 20, y, 400, 50)

        for i in range(2):
            self.button_for_choice = QPushButton(self)
            self.button_for_choice.setGeometry(x - 20 + i * 110, y + 50, 100, 140)
            self.button_for_choice.clicked.connect(self.choice_card)
            self.choices_buttons.append(self.button_for_choice)

        self.label_get_chance_on_preflop = QLabel(self)
        self.label_get_chance_on_preflop.setText(f'Шанс на префлопе: неизвестно')
        self.label_get_chance_on_preflop.setFont(self.font)
        self.label_get_chance_on_preflop.setGeometry(x - 20, y + 180, 350, 50)

    def choice_card(self):
        self.fw = MapSelection()
        self.fw.exec()
        self.result = self.fw.result
        self.count_cards_at_user = 0

        if self.result is not None:
            try:
                for card in self.cards_at_player:
                    if self.result == self.cards_at_player[card]:
                        self.error_choice_card()
                        raise FileNotFoundError
                self.index = self.choices_buttons.index(self.sender())
                self.change_icon(self.sender(), self.result)
                self.cards_at_player[self.index + 1] = self.result

                for i in self.cards_at_player:
                    if self.cards_at_player[i] is not None:
                        self.count_cards_at_user += 1
                if self.count_cards_at_user - 2 == 3:
                    time.sleep(0.5)
                    self.first_card = self.define_a_map(self.cards_at_player[1].split('.')[0])
                    self.second_card = self.define_a_map(self.cards_at_player[2].split('.')[0])
                    array_cards = []

                    for i in range(3, 6):
                        array_cards.append(self.define_a_map(self.cards_at_player[i].split('.')[0]))
                    self.chance = CheckCombinations().chance_on_flop(self.first_card,\
                                                        self.second_card, array_cards)
                    self.our_cards = []

                    for i in range(1, 3):
                        card = self.define_a_map(self.cards_at_player[i].split('.')[0])
                        card[1] = SYMBOLS[card[1]]
                        card = ' '.join(card)
                        self.our_cards.append(card)

                    self.cards_on_desk = []

                    for i in range(3, 6):
                        card = self.define_a_map(self.cards_at_player[i].split('.')[0])
                        card[1] = SYMBOLS[card[1]]
                        card = ' '.join(card)
                        self.cards_on_desk.append(card)

                    self.chances = self.change_dict_of_chances(self.chance)
                    self.total_chance = self.calculate_the_total_chance(self.chances)
                    Database().add_our_cards(self.our_cards)
                    Database().add_cards_on_desk(self.cards_on_desk)
                    Database().add_execute_for_main_table(self.total_chance)
                    self.label_get_chance_on_next_stage.setText(f'Шансы на флопе: ' +
                                                                f'{self.total_chance}%')
                elif self.count_cards_at_user - 2 == 4:
                    time.sleep(0.5)
                    self.first_card = self.define_a_map(self.cards_at_player[1].split('.')[0])
                    self.second_card = self.define_a_map(self.cards_at_player[2].split('.')[0])
                    array_cards = []

                    for i in range(3, 7):
                        array_cards.append(self.define_a_map(self.cards_at_player[i].split('.')[0]))
                    self.chance = CheckCombinations().chance_on_turn(self.first_card,\
                        self.second_card, array_cards)
                    self.our_cards = []

                    for i in range(1, 3):
                        card = self.define_a_map(self.cards_at_player[i].split('.')[0])
                        card[1] = SYMBOLS[card[1]]
                        card = ' '.join(card)
                        self.our_cards.append(card)

                    self.cards_on_desk = []

                    for i in range(3, 7):
                        card = self.define_a_map(self.cards_at_player[i].split('.')[0])
                        card[1] = SYMBOLS[card[1]]
                        card = ' '.join(card)
                        self.cards_on_desk.append(card)

                    self.chances = self.change_dict_of_chances(self.chance)
                    self.total_chance = self.calculate_the_total_chance(self.chances)
                    Database().add_our_cards(self.our_cards)
                    Database().update_cards_on_desk_on_turn(self.cards_on_desk)
                    Database().update_main_table_on_turn(self.total_chance, self.cards_on_desk)
                    self.label_get_chance_on_next_stage.setText(f'Шансы на тёрне: ' +
                                                                f'{self.total_chance}%')
                elif self.count_cards_at_user - 2 == 5:
                    time.sleep(0.5)
                    self.first_card = self.define_a_map(self.cards_at_player[1].split('.')[0])
                    self.second_card = self.define_a_map(self.cards_at_player[2].split('.')[0])
                    array_cards = []

                    for i in range(3, 8):
                        array_cards.append(self.define_a_map(self.cards_at_player[i].split('.')[0]))
                    self.chance = CheckCombinations().chance_on_river(self.first_card,\
                        self.second_card, array_cards)
                    self.our_cards = []

                    for i in range(1, 3):
                        card = self.define_a_map(self.cards_at_player[i].split('.')[0])
                        card[1] = SYMBOLS[card[1]]
                        card = ' '.join(card)
                        self.our_cards.append(card)

                    self.cards_on_desk = []

                    for i in range(3, 8):
                        card = self.define_a_map(self.cards_at_player[i].split('.')[0])
                        card[1] = SYMBOLS[card[1]]
                        card = ' '.join(card)
                        self.cards_on_desk.append(card)

                    self.chances = self.change_dict_of_chances(self.chance)
                    self.total_chance = self.calculate_the_total_chance(self.chances)
                    Database().add_our_cards(self.our_cards)
                    Database().update_cards_on_desk_on_river(self.cards_on_desk)
                    Database().update_main_table_on_river(self.total_chance, self.cards_on_desk)
                    self.label_get_chance_on_next_stage.setText(f'Шансы на ривере: ' +
                                                                f'{self.total_chance}%')
                elif self.count_cards_at_user - 2 == 0:
                    self.check_preflop()
                if self.count_cards_at_user - 2 >= 3:
                    self.paint_table_for_chances()
            except FileNotFoundError:
                pass

    def get_new_card(self):
        try:
            if self.count_cards_at_user >= 5:
                count = 0
                for i in range(1, self.count_cards_at_user + 1):
                    if self.cards_at_player[i] is not None:
                        count += 1
                if count == self.count_cards_at_user:
                    try:
                        button = self.choices_buttons[count]
                        button.setEnabled(True)
                    except IndexError:
                        pass
            elif self.count_cards_at_user == 2:
                for i in range(2, 5):
                    button = self.choices_buttons[i]
                    button.setEnabled(True)
        except AttributeError:
            pass

    def calculate_the_total_chance(self, dictionary):
        total_chance = 0
        count_elements = 0
        for key in dictionary:
            total_chance += dictionary[key]
            count_elements += 1
        total_chance = round(total_chance / count_elements, 2)
        return total_chance

    def change_dict_of_chances(self, dictionary):
        for key in dictionary:
            array = dictionary[key]
            dictionary[key] = round(array[0] / array[1] * 100, 2)
        return dictionary

    def check_preflop(self):
        if self.cards_at_player[1] is not None and self.cards_at_player[2] is not None:
            self.first_card = self.define_a_map(self.cards_at_player[1].split('.')[0])
            self.second_card = self.define_a_map(self.cards_at_player[2].split('.')[0])

            self.chance = CheckCombinations().\
            check_preflop(self.first_card, self.second_card)
            self.first_card = ' '.join([self.first_card[0], SYMBOLS[self.first_card[1]]])
            self.second_card = ' '.join([self.second_card[0], SYMBOLS[self.second_card[1]]])
            self.our_cards = [self.first_card, self.second_card]
            Database().add_our_cards(self.our_cards)
            Database().add_cards_on_desk('-')
            Database().add_execute_for_main_table(self.chance)
            if self.chance != '<50':
                self.label_get_chance_on_preflop.setText(f'Шанс на префлопе: {self.chance}%')
            else:
                self.label_get_chance_on_preflop.setText(f'Ваш шанс против случайной руки <50%. Только фолд!')

    def change_icon(self, button, icon_name):
        button.setIcon(QIcon(f'Колода карт/{icon_name}'))
        button.setIconSize(QtCore.QSize(100, 200))

    def error_choice_card(self):
        QMessageBox.critical(self, "Ошибка выбора карты",
                                   "Данная карта уже была выбрана.", QMessageBox.Ok)

    def define_a_map(self, text):
        if len(text) == 2:
            first_index = int(text[0])
            second_index = int(text[1])
        else:
            first_index = int(text[0:2])
            second_index = int(text[2])
        dignities = DIGNITIES[::-1]
        dignity = dignities[first_index]
        return [dignity, second_index]

    def do_table(self, x, y):
        for i in range(13):
            for j in range(13):
                self.btn = QPushButton(f'{DIGNITIES_FOR_TABLE[i][j]}', self)
                self.btn.setGeometry(x + j * 50, y + i * 25, 50, 25)
                self.btn.setFont(self.font)
                try:
                    self.color_for_button = self.our_colors[self.our_designations[self.btn.text()]]
                    self.btn.setStyleSheet(f'QPushButton {{background-color:\
                                                          {self.color_for_button}; color: black;}}')
                except KeyError:
                    self.color_for_button = self.our_colors['Other']
                    self.btn.setStyleSheet(f'QPushButton {{background-color:\
                                                          {self.color_for_button}; color: black;}}')
                self.buttons.append(self.btn)

        self.download_table = QPushButton('Загрузить таблицу', self)
        self.download_table.setGeometry(x, y + 330, 150, 30)
        self.download_table.setFont(self.font)
        self.download_table.clicked.connect(self.download_designations)

        self.download_table = QPushButton('Загрузить цвета категорий', self)
        self.download_table.setGeometry(x + 155, y + 330, 200, 30)
        self.download_table.setFont(self.font)
        self.download_table.clicked.connect(self.download_colors_category)

        self.download_table = QPushButton('По умолчанию', self)
        self.download_table.setGeometry(x + (155 + 205), y + 330, 150, 30)
        self.download_table.setFont(self.font)
        self.download_table.clicked.connect(self.by_default)

    def do_glossary(self, x, y):
        self.keys = list(self.our_colors.keys())
        self.label_book = QLabel('Глоссарий цветов для категорий.', self)
        self.label_book.setGeometry(x, y - 10, 210, 30)
        self.label_book.setFont(self.font)
        for line in range(1, 8):
            self.label = QLineEdit(f'{self.keys[line]}', self)
            self.label.setGeometry(x + 110, y + 30 * line, 100, 30)
            self.label.setEnabled(False)
            self.label.setFont(self.font)
            self.lines_edit.append(self.label)
            self.color = self.our_colors[self.keys[line]]

            try:
                r, g, b = ImageColor.getcolor(self.color, 'RGB')
            except ValueError:
                r, g, b = (230, 230, 230)

            self.im = Image.new('RGB', (100, 30), (r, g, b))
            self.im.save(f'{line}for_glossary.png')
            self.pixmap = QPixmap(f'{line}for_glossary.png')
            self.label_image = QLabel(self)
            self.label_image.setGeometry(x, y + 30 * line, 100, 30)
            self.label_image.setPixmap(self.pixmap)
            self.labels_images_glossary.append(self.label_image)
            os.remove(f'{line}for_glossary.png')

    def change_glossary(self):
        self.keys = list(self.our_colors.keys())
        for line in range(7):
            self.color = self.our_colors[self.keys[line + 1]]

            try:
                r, g, b = ImageColor.getcolor(self.color, 'RGB')
            except ValueError:
                r, g, b = (230, 230, 230)

            self.im = Image.new('RGB', (100, 30), (r, g, b))
            self.im.save(f'{line}.jpg')
            self.pixmap = QPixmap(f'{line}.jpg')
            self.labels_images_glossary[line].setPixmap(self.pixmap)
            os.remove(f'{line}.jpg')

    def download_designations(self):
        self.designations_filename = QFileDialog.getOpenFileName(self, 'Выбрать таблицу', '',
                                                          'Таблица (*.csv)\
                                                          ;;Все файлы (*)')[0]
        try:
            if '.csv' not in self.designations_filename:
                QMessageBox.critical(self, "Ошибка загрузки категорий",
                                     "Данный файл не содержит категорий карт.", QMessageBox.Ok)
                raise FileNotFoundError
            elif self.designations_filename[len(self.designations_filename) - 4::] != '.csv':
                QMessageBox.critical(self, "Ошибка загрузки категорий",
                                     "Данный файл не содержит категорий карт.", QMessageBox.Ok)
                raise FileNotFoundError
            self.our_designations = Table(DIGNITIES).open_table(
                                                    self.designations_filename,
                                                    self.colors_filename
                                                    )[0]
            if self.our_designations is None:
                QMessageBox.critical(self, "Ошибка загрузки категорий",
                                     "Данный файл не содержит категорий карт.", QMessageBox.Ok)
                raise FileNotFoundError
            try:
                self.checker = self.our_designations['cards'] == 'category'
                if self.checker is not True:
                    raise KeyError
                self.change_color_on_buttons()
            except KeyError:
                QMessageBox.critical(self, "Ошибка загрузки категорий",
                                     "Данный файл не содержит категорий карт.", QMessageBox.Ok)
        except FileNotFoundError:
            pass

    def download_colors_category(self):
        self.colors_filename = QFileDialog.getOpenFileName(self, 'Выбрать цвета категорий', '',
                                                           'Таблица (*.csv)\
                                                           ;;Все файлы (*)')[0]
        try:
            if '.csv' not in self.colors_filename:
                QMessageBox.critical(self, "Ошибка загрузки цветов категорий",
                                     "Данный файл не содержит цветов категорий.", QMessageBox.Ok)
                raise FileNotFoundError
            elif self.colors_filename[len(self.colors_filename) - 4::] != '.csv':
                QMessageBox.critical(self, "Ошибка загрузки цветов категорий",
                                     "Данный файл не содержит цветов категорий.", QMessageBox.Ok)
                raise FileNotFoundError
            self.our_colors = Table(DIGNITIES).open_table(
                                                          self.designations_filename,
                                                          self.colors_filename
                                                         )[1]
            if self.our_colors is None:
                QMessageBox.critical(self, "Ошибка загрузки цветов категорий",
                                     "Данный файл не содержит цветов категорий.", QMessageBox.Ok)
                raise FileNotFoundError
            try:
                self.checker = self.our_colors['category'] == 'color'
                if self.checker is not True or len(self.our_colors.keys()) != 8:
                    raise KeyError
                self.change_color_on_buttons()
                self.change_glossary()
            except KeyError:
                QMessageBox.critical(self, "Ошибка загрузки цветов категорий",
                                     "Данный файл не содержит цветов категорий.", QMessageBox.Ok)
        except FileNotFoundError:
            pass

    def by_default(self):
        self.our_designations,\
        self.our_colors = Table(DIGNITIES).open_table(
                                                      'main_designations.csv',
                                                      'main_colors.csv'
                                                     )
        self.colors_filename = 'main_colors.csv'
        self.designations_filename = 'main_designations.csv'
        self.change_color_on_buttons()
        self.change_glossary()

    def do_change_table(self):
        self.sw = ChangeCategoryCards(self.colors_filename)
        self.sw.show()

    def change_colors(self):
        self.tw = ChangeColorForCategory()
        self.tw.show()

    def change_color_on_buttons(self):
        for button in self.buttons:
            try:
                self.color_for_button = self.our_colors[self.our_designations[button.text()]]
                button.setStyleSheet(f'QPushButton {{background-color:\
                                                      {self.color_for_button}; color: black;}}')
            except KeyError:
                try:
                    self.color_for_button = self.our_colors['Other']
                except KeyError:
                    self.color_for_button = '#e6e6e6'
                button.setStyleSheet(f'QPushButton {{background-color:\
                                                    {self.color_for_button}; color: black;}}')


class ChangeCategoryCards(QWidget):
    def __init__(self, colors_filename):
        super().__init__()

        self.table_filename = 'main_designations.csv'
        self.colors_filename = colors_filename

        self.buttons = []

        self.font = QFont('Trebuchet MS', 10)
        self.font.setBold(True)

        self.initUI()

    def initUI(self):
        self.setGeometry(200, 200, *SIZE_SW)
        self.setFixedSize(*SIZE_SW)
        self.setWindowTitle('Изменение таблицы')
        self.setWindowIcon(QIcon('icons/game_icon.jpg'))

        self.open_table = QAction('&Открыть таблицу', self)
        self.open_table.triggered.connect(self.open_designations)

        self.save_table = QAction('&Сохранить таблицу как', self)
        self.save_table.triggered.connect(self.file_save)

        self.table_default = QAction('&Использовать таблицу по умолчанию', self)
        self.table_default.triggered.connect(self.table_by_default)

        self.MenuBar = QMenuBar(self)
        self.menu = self.MenuBar.addMenu('&Настройки')

        self.menu.addAction(self.open_table)
        self.menu.addAction(self.table_default)
        self.menu.addAction(self.save_table)

        self.our_designations = {}
        self.our_colors = Table(DIGNITIES).open_table(
                                                      self.table_filename,
                                                      self.colors_filename
                                                     )[1]

    def open_designations(self):
        self.table_filename = QFileDialog.getOpenFileName(self, 'Выбрать таблицу', '',
                                                          'Таблица (*.csv)\
                                                          ;;Все файлы (*)')[0]
        try:
            if '.csv' not in self.table_filename:
                QMessageBox.critical(self, "Ошибка загрузки категорий",
                                     "Данный файл не содержит категорий карт.", QMessageBox.Ok)
                raise FileNotFoundError
            elif self.table_filename[len(self.table_filename)::] != '.csv':
                QMessageBox.critical(self, "Ошибка загрузки категорий",
                                     "Данный файл не содержит категорий карт.", QMessageBox.Ok)
                raise FileNotFoundError
            self.our_designations = Table(DIGNITIES).open_table(
                                                                self.table_filename,
                                                                self.colors_filename
                                                               )[0]
            if self.our_designations is None:
                QMessageBox.critical(self, "Ошибка загрузки категорий",
                                     "Данный файл не содержит категорий карт.", QMessageBox.Ok)
                raise FileNotFoundError
            try:
                self.checker = self.our_designations['cards'] == 'category'
                if self.checker is not True:
                    raise KeyError
                self.create_table(50, 30)
            except KeyError:
                QMessageBox.critical(self, "Ошибка загрузки категорий",
                                     "Данный файл не содержит категорий карт.", QMessageBox.Ok)
        except FileNotFoundError:
            pass

    def table_by_default(self):
        self.our_designations = Table(DIGNITIES).open_table(
                                                            'main_designations.csv',
                                                            'main_colors.csv'
                                                           )[0]
        self.create_table(50, 30)

    def file_save(self):
        self.filename_by_save = QFileDialog.getSaveFileName(self, 'Save File', '')[0]
        Table(DIGNITIES).save_designations(self.filename_by_save, self.our_designations)

    def create_table(self, x, y):
        self.label_help = QLabel('Нажатие на ячейку таблицы позволяет циклично'
                                 ' изменять цвет категории для выбранной карты.', self)
        self.label_help.setFont(self.font)
        self.label_help.setHidden(False)
        self.label_help.setGeometry(x, y + 320, 650, 50)

        for i in range(13):
            for j in range(13):
                self.btn = QPushButton(f'{DIGNITIES_FOR_TABLE[i][j]}', self)
                self.btn.setGeometry(x + j * 50, y + i * 25, 50, 25)
                self.btn.setHidden(False)
                self.btn.setFont(self.font)
                try:
                    self.color_for_button = self.our_colors[self.our_designations[self.btn.text()]]
                    self.btn.setStyleSheet(f'QPushButton {{background-color:\
                                                          {self.color_for_button}; color: black;}}')
                except KeyError:
                    self.color_for_button = self.our_colors['Other']
                    self.btn.setStyleSheet(f'QPushButton {{background-color:\
                                                          {self.color_for_button}; color: black;}}')
                self.btn.clicked.connect(self.change_color_for_button)
                self.buttons.append(self.btn)

    def change_color_for_button(self):
        self.our_button = self.sender()

        try:
            self.category = self.our_designations[self.our_button.text()]
        except KeyError:
            self.category = 'Other'

        if self.category == 'Other':
            self.category = CATEGORIES[0]
        else:
            self.index = CATEGORIES.index(self.category)
            self.category = CATEGORIES[self.index + 1]

        self.color_for_button = self.our_colors[self.category]
        self.our_button.setStyleSheet(f'QPushButton {{background-color:\
                                                          {self.color_for_button}; color: black;}}')

        if self.category != 'Other':
            self.our_designations[self.our_button.text()] = self.category
        else:
            del self.our_designations[self.our_button.text()]


class ChangeColorForCategory(QWidget):
    def __init__(self):
        super().__init__()

        self.colors_filename = 'main_colors.csv'

        self.font = QFont('Trebuchet MS', 10)
        self.font.setBold(True)

        self.buttons = []
        self.labels = []

        self.initUI()

    def initUI(self):
        self.setGeometry(200, 200, *SIZE_TW)
        self.setFixedSize(*SIZE_TW)
        self.setWindowTitle('Изменение цвета категорий')
        self.setWindowIcon(QIcon('icons/game_icon.jpg'))

        self.open_table = QAction('&Открыть цвета категорий', self)
        self.open_table.triggered.connect(self.open_table_colors)

        self.save_table = QAction('&Сохранить цвета категорий как', self)
        self.save_table.triggered.connect(self.save_the_table)

        self.table_default = QAction('&Использовать цвета категорий по умолчанию', self)
        self.table_default.triggered.connect(self.by_default)

        self.MenuBar = QMenuBar(self)
        self.menu = self.MenuBar.addMenu('&Настройки')

        self.menu.addAction(self.open_table)
        self.menu.addAction(self.table_default)
        self.menu.addAction(self.save_table)

        self.our_colors = {}

    def save_the_table(self):
        self.filename_by_save = QFileDialog.getSaveFileName(self, 'Save File', '')[0]
        Table(DIGNITIES).save_colors_category(self.filename_by_save, self.our_colors)

    def by_default(self):
        self.buttons = []
        self.labels = []
        self.our_colors = Table(DIGNITIES).open_table(
                                                      'main_designations.csv',
                                                      'main_colors.csv'
                                                     )[1]
        self.create_table_of_colors(10, 20)

    def open_table_colors(self):
        self.buttons = []
        self.labels = []
        self.colors_filename = QFileDialog.getOpenFileName(self, 'Выбрать таблицу', '',
                                                          'Таблица (*.csv)\
                                                          ;;Все файлы (*)')[0]
        try:
            if '.csv' not in self.colors_filename:
                QMessageBox.critical(self, "Ошибка загрузки цветов категорий",
                                     "Данный файл не содержит цветов категорий.", QMessageBox.Ok)
                raise FileNotFoundError
            elif self.colors_filename[len(self.colors_filename)::] != '.csv':
                QMessageBox.critical(self, "Ошибка загрузки цветов категорий",
                                     "Данный файл не содержит цветов категорий.", QMessageBox.Ok)
                raise FileNotFoundError
            self.our_colors = Table(DIGNITIES).open_table(
                                                          'main_designations.csv',
                                                          self.colors_filename
                                                         )[1]
            if self.our_colors is None:
                QMessageBox.critical(self, "Ошибка загрузки цветов категорий",
                                     "Данный файл не содержит цветов категорий.", QMessageBox.Ok)
                raise FileNotFoundError
            try:
                self.checker = self.our_colors['category'] == 'color'
                if self.checker is not True or len(self.our_colors.keys()) != 8:
                    raise KeyError
                self.create_table_of_colors(10, 20)
            except KeyError:
                QMessageBox.critical(self, "Ошибка загрузки цветов категорий",
                                     "Данный файл не содержит цветов категорий.", QMessageBox.Ok)
        except FileNotFoundError:
            pass

    def create_table_of_colors(self, x, y):
        self.label_help = QLabel('Нажатие на кнопку "Изменить цвет" даёт вам возможность\n'
                                 'изменить цвет выбранной категории.', self)
        self.label_help.setHidden(False)
        self.label_help.setGeometry(x, y, 700, 50)
        self.label_help.setFont(self.font)

        self.keys_for_color = list(self.our_colors.keys())
        for i in range(7):
            self.label = QLineEdit(f'{self.keys_for_color[i + 1]}', self)
            self.label.setGeometry(x, y + 50 + 30 * i, 100, 30)
            self.label.setEnabled(False)
            self.label.setHidden(False)
            self.label.setFont(self.font)
            self.labels.append(self.label)

            self.color = self.our_colors[self.keys_for_color[i + 1]]

            try:
                r, g, b = ImageColor.getcolor(self.color, 'RGB')
            except ValueError:
                r, g, b = (230, 230, 230)

            self.im = Image.new('RGB', (100, 30), (r, g, b))
            self.im.save(f'{i}.jpg')
            self.pixmap = QPixmap(f'{i}.jpg')
            self.label_image = QLabel(self)
            self.label_image.setHidden(False)
            self.label_image.setGeometry(x + 110, y + 50 + 30 * i, 100, 30)
            self.label_image.setPixmap(self.pixmap)
            os.remove(f'{i}.jpg')

            self.btn = QPushButton('Изменить цвет', self)
            self.btn.setGeometry(x + 220, y + 50 + 30 * i, 110, 30)
            self.btn.setFont(self.font)
            self.btn.setHidden(False)
            self.btn.clicked.connect(self.change_color_for_button)
            self.buttons.append(self.btn)

    def rgb_to_hex(self, rgb):
        return '%02x%02x%02x' % rgb

    def change_color_for_button(self):
        self.color = QColorDialog.getColor()
        x, y = 10, 20
        if self.color.isValid():
            self.color = self.color.getRgb()
            self.index = self.buttons.index(self.sender())
            self.color_to_hex = '#' + self.rgb_to_hex(self.color[:3])
            self.our_colors[self.keys_for_color[self.index + 1]] = self.color_to_hex

            self.im = Image.new('RGB', (100, 30), (self.color))
            self.im.save(f'{self.index}.jpg')
            self.pixmap = QPixmap(f'{self.index}.jpg')
            self.label_image = QLabel(self)
            self.label_image.setHidden(False)
            self.label_image.setGeometry(x + 110, y + 50 + 30 * self.index, 100, 30)
            self.label_image.setPixmap(self.pixmap)
            os.remove(f'{self.index}.jpg')


class MapSelection(QDialog):
    def __init__(self):
        super().__init__()

        self.cards = []
        self.result = None

        self.initUI()

    def initUI(self):
        self.setGeometry(200, 200, *SIZE_FW)
        self.setFixedSize(*SIZE_FW)
        self.setWindowTitle('Выбор карты')
        self.setWindowIcon(QIcon('icons/game_icon.jpg'))

        self.create_table_of_cards(10, 10)

    def create_table_of_cards(self, x, y):
        for i in range(4):
            self.buttons = []
            for j in range(13):
                self.btn = QPushButton(self)
                self.btn.setGeometry(x + j * 75, y + i * 100, 75, 100)
                self.btn.setIcon(QIcon(f'Колода карт/{j}{i}.png'))
                self.btn.setIconSize(QtCore.QSize(75, 100))
                self.btn.clicked.connect(self.return_card)
                self.buttons.append(self.btn)
            self.cards.append(self.buttons)

    def return_card(self):
        for i in range(4):
            if self.sender() in self.cards[i]:
                self.result = f'{self.cards[i].index(self.sender())}{i}.png'
                self.close()


class ShowStatistics(QWidget):
    def __init__(self):
        super().__init__()

        self.cards = []
        self.result = None

        self.initUI()

    def initUI(self):
        self.setGeometry(200, 200, *SIZE_FFW)
        self.setFixedSize(*SIZE_FFW)
        self.setWindowTitle('Статистика')
        self.setWindowIcon(QIcon('icons/game_icon.jpg'))

        self.clear_table = QAction('&Очистить таблицу', self)
        self.clear_table.triggered.connect(self.clear_database)

        self.update_table = QAction('&Обновить', self)
        self.update_table.triggered.connect(self.update_view)

        self.MenuBar = QMenuBar(self)
        self.menu = self.MenuBar.addMenu('&Настройки')
        self.menu.addAction(self.update_table)
        self.menu.addAction(self.clear_table)

        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName('statistics_for_game.db')
        self.db.open()

        self.view_database()

    def view_database(self):
        self.view = QTableView(self)

        self.model = QSqlTableModel(self, self.db)
        self.model.setTable('games')
        self.model.select()

        self.view.setModel(self.model)
        self.view.setGeometry(10, 30, SIZE_FFW[0] - 20, SIZE_FFW[1] - 40)

        for i in range(0, 9):
            self.view.horizontalHeader().setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeToContents)

    def update_view(self):
        self.model.select()

    def clear_database(self):
        Database().clear_all_tables()
        self.update_view()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec())