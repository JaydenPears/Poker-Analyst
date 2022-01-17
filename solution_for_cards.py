import csv
import sqlite3


class Table:
    def __init__(self, array):
        self.array = array
        self.table = list()
        self.colors_for_chances = {}
        self.designations = {}
        self.colors = {}
        self.create()

    def create(self):
        for card_1 in self.array:
            cards = list()
            for card_2 in self.array:
                if card_1 == card_2:
                    cards.append(card_2[0] + card_1[0])
                elif self.array.index(card_1) > self.array.index(card_2):
                    cards.append(card_2[0] + card_1[0] + 'o')
                else:
                    cards.append(card_1[0] + card_2[0] + 's')
            self.table.append(cards.copy())
        return self.table.copy()

    def open_table(self, filename_designations, filename_colors_category):
        with open(filename_colors_category, encoding="utf8") as csvfile:
            reader = csv.reader(csvfile, delimiter=':', quotechar='"')
            for index, row in enumerate(reader):
                    self.colors[row[0]] = row[1]

        with open(filename_designations, encoding="utf8") as csvfile:
            reader = csv.reader(csvfile, delimiter=':', quotechar='"')
            for index, row in enumerate(reader):
                    self.designations[row[0]] = row[1]
        return self.designations, self.colors

    def open_chances_colors(self, filename_chances):
        with open(filename_chances, encoding="utf8") as csvfile:
            reader = csv.reader(csvfile, delimiter=':', quotechar='"')
            for index, row in enumerate(reader):
                    self.colors_for_chances[row[0]] = row[1]

        return self.colors_for_chances

    def save_designations(self, filename_designations, designations):
        if '.csv' not in filename_designations:
            filename_designations += '.csv'
        with open(filename_designations, 'w', newline='') as csvfile:
            writer = csv.writer(
                csvfile, delimiter=':', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for key in designations:
                writer.writerow([key, designations[key]])

    def save_colors_category(self, filename_colors, colors):
        if '.csv' not in filename_colors:
            filename_colors += '.csv'
        with open(filename_colors, 'w', newline='') as csvfile:
            writer = csv.writer(
                csvfile, delimiter=':', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for key in colors:
                writer.writerow([key, colors[key]])


COMBINATIONS = ['High Card', 'Pair', 'Two Pair', 'Three of a Kind', 'Straight', 
                'Flush', 'Full House', 'Four of a Kind', 
                'Straight Flush', 'Royal Flush']
DIGNITIES = ['Ace', 'King', 'Queen', 'Jack', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
SYMBOLS = ['Hearts', 'Spades', 'Diamonds', 'Clubs']
DIGNITIES_FOR_TABLE = Table(DIGNITIES).create()
CATEGORIES = ['EP', 'MP', 'HJ', 'CO', 'BU', 'SB', 'Other']
DIGNITIES_SHORT_TO_LONG = {'A': 'Ace', 'K': 'King', 'Q': 'Queen', 'J': 'Jack'}
CHANCE_IN_PREFLOP = {'AA': 85.4, 'KK': 82.6, 'QQ': 80.1, 'JJ': 77.7, 
                     'TT': 75.2, '99': 72.3, '88': 69.4, '77': 66.5,
                     '66': 63.6, '55': 60.7, '44': 57.4, '33': 54.2,
                     '22': 50.9, 'AKs': 67.0, 'AKo': 65.3, 'AQs': 66.3,
                     'AQo': 64.4, 'AJs': 65.4, 'AJo': 63.5, 'ATs': 64.6,
                     'ATo': 62.7, 'A9s': 62.8, 'A9o': 60.8, 'A8s': 61.9,
                     'A8o': 59.9, 'A7s': 61.0, 'A7o': 58.8, 'A6s': 59.9,
                     'A6o': 57.7, 'A5s': 59.9, 'A5o': 57.7, 'A4s': 59.0,
                     'A4o': 56.7, 'A3s': 58.2, 'A3o': 55.8, 'KQs': 63.4,
                     'KQo': 61.5, 'QJs': 62.6, 'QJo': 60.6, 'KTs': 61.8,
                     'KTo': 59.7, 'QJs': 60.3, 'QJo': 58.1, 'QTs': 59.4,
                     'QTo': 57.3, 'JTs': 57.5, 'JTo': 55.3, 'J9s': 55.7,
                     'J9o': 53.2, 'T9s': 54.0, 'T9o': 51.5, '98s': 50.8,
                     '98o': 48.1}

CARDS = []
for i in range(4):
    for j in range(13):
        CARDS.append(f'{DIGNITIES[j]} {SYMBOLS[i]}')


class CheckCombinations:
    def __init__(self):
        self.combinations = []
        self.cards = CARDS

    def check_preflop(self, first_card, second_card):
        self.first_card = first_card
        self.second_card = second_card
        if DIGNITIES.index(self.first_card[0]) > DIGNITIES.index(self.second_card[0]):
            self.first_card, self.second_card = second_card, first_card
        designation = self.first_card[0][0] + self.second_card[0][0]
        if self.first_card[0] != self.second_card[0]:
            if self.first_card[1] == self.second_card[1]:
                designation += 's'
            else:
                designation += 'o'
        try:
            return CHANCE_IN_PREFLOP[designation]
        except KeyError:
            return '<50'

    def chance_on_flop(self, first_card, second_card, array_of_cards):
        self.cards = CARDS.copy()
        first_card = ' '.join([first_card[0], SYMBOLS[int(first_card[1])]])
        second_card = ' '.join([second_card[0], SYMBOLS[int(second_card[1])]])
        for i in range(3):
            card = array_of_cards[i]
            card = ' '.join([card[0], SYMBOLS[card[1]]])
            array_of_cards[i] = card
        self.cards.remove(first_card)
        self.cards.remove(second_card)
        for card in array_of_cards:
            self.cards.remove(card)

        chances = {}

        for first_enemy_card in self.cards:
            for second_enemy_card in self.cards:
                for first_desk_card in self.cards:
                    for second_desk_card in self.cards:
                        checker = list({first_enemy_card, second_enemy_card, first_desk_card,
                                        second_desk_card})
                        if len(checker) != 4:
                            continue
                        our_cards = [first_card, second_card, first_desk_card, second_desk_card]
                        our_cards += array_of_cards
                        enemy_cards = [first_enemy_card, second_enemy_card]
                        enemy_cards += [first_desk_card, second_desk_card]
                        enemy_cards += array_of_cards
                        res = self.check_who_win(our_cards.copy(), enemy_cards.copy())
                        for_table_name = ''
                        cards_of_enemy = [first_enemy_card.split(), second_enemy_card.split()]
                        if DIGNITIES.index(cards_of_enemy[0][0]) > DIGNITIES.index(cards_of_enemy[1][0]):
                            cards_of_enemy[0] = second_enemy_card.split()
                            cards_of_enemy[1] = first_enemy_card.split()
                        if cards_of_enemy[0][0] == cards_of_enemy[1][0]:
                            for_table_name = cards_of_enemy[0][0][0] + cards_of_enemy[1][0][0]
                        elif cards_of_enemy[0][1] == cards_of_enemy[1][1]:
                            for_table_name = cards_of_enemy[0][0][0] + cards_of_enemy[1][0][0] + 's'
                        else:
                            for_table_name = cards_of_enemy[0][0][0] + cards_of_enemy[1][0][0] + 'o'
                        if for_table_name in chances:
                            chance_now = chances[for_table_name]
                            chance_now[0] += res
                            chance_now[1] += 1
                            chances[for_table_name] = chance_now.copy()
                        else:
                            chances[for_table_name] = [res, 1]
        return chances

    def chance_on_turn(self, first_card, second_card, array_of_cards):
        self.cards = CARDS.copy()
        first_card = ' '.join([first_card[0], SYMBOLS[int(first_card[1])]])
        second_card = ' '.join([second_card[0], SYMBOLS[int(second_card[1])]])
        for i in range(4):
            card = array_of_cards[i]
            card = ' '.join([card[0], SYMBOLS[card[1]]])
            array_of_cards[i] = card
        self.cards.remove(first_card)
        self.cards.remove(second_card)
        for card in array_of_cards:
            self.cards.remove(card)

        chances = {}

        for first_enemy_card in self.cards:
            for second_enemy_card in self.cards:
                for first_desk_card in self.cards:
                    checker = list({first_enemy_card, second_enemy_card, first_desk_card})
                    if len(checker) != 3:
                        continue
                    our_cards = [first_card, second_card, first_desk_card]
                    our_cards += array_of_cards
                    enemy_cards = [first_enemy_card, second_enemy_card]
                    enemy_cards += [first_desk_card] + array_of_cards
                    res = self.check_who_win(our_cards.copy(), enemy_cards.copy())
                    for_table_name = ''
                    cards_of_enemy = [first_enemy_card.split(), second_enemy_card.split()]
                    if DIGNITIES.index(cards_of_enemy[0][0]) > DIGNITIES.index(cards_of_enemy[1][0]):
                        cards_of_enemy[0] = second_enemy_card.split()
                        cards_of_enemy[1] = first_enemy_card.split()
                    if cards_of_enemy[0][0] == cards_of_enemy[1][0]:
                        for_table_name = cards_of_enemy[0][0][0] + cards_of_enemy[1][0][0]
                    elif cards_of_enemy[0][1] == cards_of_enemy[1][1]:
                        for_table_name = cards_of_enemy[0][0][0] + cards_of_enemy[1][0][0] + 's'
                    else:
                        for_table_name = cards_of_enemy[0][0][0] + cards_of_enemy[1][0][0] + 'o'
                    if for_table_name in chances:
                        chance_now = chances[for_table_name]
                        chance_now[0] += res
                        chance_now[1] += 1
                        chances[for_table_name] = chance_now.copy()
                    else:
                        chances[for_table_name] = [res, 1]
        return chances

    def chance_on_river(self, first_card, second_card, array_of_cards):
        self.cards = CARDS.copy()
        first_card = ' '.join([first_card[0], SYMBOLS[int(first_card[1])]])
        second_card = ' '.join([second_card[0], SYMBOLS[int(second_card[1])]])
        for i in range(5):
            card = array_of_cards[i]
            card = ' '.join([card[0], SYMBOLS[card[1]]])
            array_of_cards[i] = card
        self.cards.remove(first_card)
        self.cards.remove(second_card)
        for card in array_of_cards:
            self.cards.remove(card)

        chances = {}

        for first_enemy_card in self.cards:
            for second_enemy_card in self.cards:
                for first_desk_card in self.cards:
                    checker = list({first_enemy_card, second_enemy_card, first_desk_card})
                    if len(checker) != 3:
                        continue
                    our_cards = [first_card, second_card, first_desk_card]
                    our_cards += array_of_cards
                    enemy_cards = [first_enemy_card, second_enemy_card]
                    enemy_cards += [first_desk_card] + array_of_cards
                    res = self.check_who_win(our_cards.copy(), enemy_cards.copy())
                    for_table_name = ''
                    cards_of_enemy = [first_enemy_card.split(), second_enemy_card.split()]
                    if DIGNITIES.index(cards_of_enemy[0][0]) > DIGNITIES.index(cards_of_enemy[1][0]):
                        cards_of_enemy[0] = second_enemy_card.split()
                        cards_of_enemy[1] = first_enemy_card.split()
                    if cards_of_enemy[0][0] == cards_of_enemy[1][0]:
                        for_table_name = cards_of_enemy[0][0][0] + cards_of_enemy[1][0][0]
                    elif cards_of_enemy[0][1] == cards_of_enemy[1][1]:
                        for_table_name = cards_of_enemy[0][0][0] + cards_of_enemy[1][0][0] + 's'
                    else:
                        for_table_name = cards_of_enemy[0][0][0] + cards_of_enemy[1][0][0] + 'o'
                    if for_table_name in chances:
                        chance_now = chances[for_table_name]
                        chance_now[0] += res
                        chance_now[1] += 1
                        chances[for_table_name] = chance_now.copy()
                    else:
                        chances[for_table_name] = [res, 1]
        return chances

    def check_who_win(self, our_cards, enemy_cards):
        our_cards_for_check = []
        for card in our_cards:
            our_card = DIGNITIES[::-1].index(card.split()[0]) + 2
            our_cards_for_check.append([our_card, SYMBOLS.index(card.split()[1])])
        enemy_cards_for_check = []
        for card in enemy_cards:
            enemy_card = DIGNITIES[::-1].index(card.split()[0]) + 2
            enemy_cards_for_check.append([enemy_card, SYMBOLS.index(card.split()[1])])
        our_result = self.check_combination(our_cards_for_check)
        enemy_result = self.check_combination(enemy_cards_for_check)
        if COMBINATIONS.index(our_result) > COMBINATIONS.index(enemy_result):
            return 1
        elif COMBINATIONS.index(our_result) < COMBINATIONS.index(enemy_result):
            return 0
        else:
            our_result = self.check_equal_combinations(our_cards_for_check, enemy_cards_for_check)
            if our_result == 1:
                return 1
            else:
                return 0

    def check_equal_combinations(self, our_cards, enemy_cards):
        our_result = self.check_combination(our_cards)
        our_cards_dignity = [int(x[0]) for x in our_cards]
        enemy_cards_dignity = [int(x[0]) for x in enemy_cards]
        if our_result == 'High Card':
            return self.check_equal_high_card(our_cards_dignity, enemy_cards_dignity)
        elif our_result == 'Pair':
            return self.check_equal_pair(our_cards_dignity, enemy_cards_dignity)
        elif our_result == 'Two Pair':
            return self.check_equal_two_pair(our_cards_dignity, enemy_cards_dignity)
        elif our_result == 'Three of a Kind':
            return self.check_equal_three_of_a_kind(our_cards_dignity, enemy_cards_dignity)
        elif our_result == 'Straight':
            return self.check_equal_straight(our_cards_dignity, enemy_cards_dignity)
        elif our_result == 'Flush':
            return self.check_equal_flush(our_cards, enemy_cards)
        elif our_result == 'Full House':
            return self.check_equal_full_house(our_cards_dignity, enemy_cards_dignity)
        elif our_result == 'Four of a Kind':
            return self.check_equal_four_of_a_kind(our_cards_dignity, enemy_cards_dignity)
        else:
            return self.check_equal_straight_flush(our_cards, enemy_cards)

    def check_equal_straight_flush(self, our_cards, enemy_cards):
        our_flush_cards = []
        our_symbols = [x[1] for x in our_cards]
        for i in our_symbols:
            if our_symbols.count(i) >= 5:
                our_symbol = i
        our_all_cards = []
        for i in our_cards:
            if i[1] == our_symbol:
                our_flush_cards.append(i[0])
            else:
                our_all_cards.append(i[0])

        enemy_flush_cards = []
        enemy_symbols = [x[1] for x in enemy_cards]
        for i in enemy_symbols:
            if enemy_symbols.count(i) >= 5:
                enemy_symbol = i
        enemy_all_cards = []
        for i in enemy_cards:
            if i[1] == enemy_symbol:
                enemy_flush_cards.append(i[0])
            else:
                enemy_all_cards.append(i[0])

        return self.check_equal_straight(our_flush_cards, enemy_flush_cards)

    def check_equal_four_of_a_kind(self, our_cards_dignity, enemy_cards_dignity):
        our_array = []
        for i in our_cards_dignity:
            if our_cards_dignity.count(i) == 4 and i not in our_array:
                our_array.append(i)
        for i in our_array:
            for j in range(4):
                our_cards_dignity.remove(i)

        enemy_array = []
        for i in enemy_cards_dignity:
            if enemy_cards_dignity.count(i) == 4 and i not in enemy_array:
                enemy_array.append(i)
        for i in enemy_array:
            for j in range(4):
                enemy_cards_dignity.remove(i)
        while True:
            flag = True
            for i in our_array:
                if i in enemy_array:
                    enemy_array.remove(i)
                    flag = False
            if flag:
                break
        if len(our_array) == 0 or len(enemy_array) == 0:
            while True:
                flag = True
                for i in our_cards_dignity:
                    if i in enemy_cards_dignity:
                        enemy_cards_dignity.remove(i)
                        flag = False
                if flag:
                    break
            if len(our_cards_dignity) == 0 or len(enemy_cards_dignity) == 0:
                return 1
            elif max(our_cards_dignity) >= max(enemy_cards_dignity):
                return 1
            else:
                return 0
        elif max(our_array) == max(enemy_array):
            while True:
                flag = True
                for i in our_cards_dignity:
                    if i in enemy_cards_dignity:
                        enemy_cards_dignity.remove(i)
                        flag = False
                if flag:
                    break
            if len(our_cards_dignity) == 0:
                return 1
            elif max(our_cards_dignity) >= max(enemy_cards_dignity):
                return 1
            else:
                return 0
        elif max(our_array) > max(enemy_array):
            return 1
        else:
            return 0

    def check_equal_full_house(self, our_cards_dignity, enemy_cards_dignity):
        array_of_our_threes = []
        for i in our_cards_dignity:
            if our_cards_dignity.count(i) >= 3 and i not in array_of_our_threes:
                array_of_our_threes.append(i)
        max_our_trees = max(array_of_our_threes)
        array_of_our_pair = []
        for i in our_cards_dignity:
            if our_cards_dignity.count(i) >= 2 and i not in array_of_our_pair:
                array_of_our_pair.append(i)
        max_our_pair = max(array_of_our_pair)

        array_of_enemy_threes = []
        for i in enemy_cards_dignity:
            if enemy_cards_dignity.count(i) >= 3 and i not in array_of_enemy_threes:
                array_of_enemy_threes.append(i)
        max_enemy_trees = max(array_of_enemy_threes)
        array_of_enemy_pair = []
        for i in enemy_cards_dignity:
            if enemy_cards_dignity.count(i) >= 2 and i not in array_of_enemy_pair:
                array_of_enemy_pair.append(i)
        max_enemy_pair = max(array_of_enemy_pair)

        if max_our_trees > max_enemy_trees:
            return 1
        elif max_our_trees == max_enemy_trees:
            if max_our_pair >= max_enemy_pair:
                return 1
            else:
                return 0
        else:
            return 0

    def check_equal_flush(self, our_cards, enemy_cards):
        our_array = []
        our_symbols = [x[1] for x in our_cards]
        for i in our_symbols:
            if our_symbols.count(i) >= 5:
                our_symbol = i
        for i in our_cards:
            if i[1] == our_symbol:
                our_array.append(i[0])

        enemy_array = []
        enemy_symbols = [x[1] for x in enemy_cards]
        for i in enemy_symbols:
            if enemy_symbols.count(i) >= 5:
                enemy_symbol = i
        for i in enemy_cards:
            if i[1] == enemy_symbol:
                enemy_array.append(i[0])

        while True:
            flag = True
            for i in our_array:
                if i in enemy_array:
                    our_array.remove(i)
                    enemy_array.remove(i)
                    flag = False
                    break
            if flag:
                break
        if len(our_array) == 0 and len(enemy_array) == 0:
            return 1
        elif len(our_array) == 0 and len(enemy_array) != 0:
            return 0
        elif len(our_array) != 0 and len(enemy_array) == 0:
            return 1
        elif max(our_array) >= max(enemy_array):
            return 1
        else:
            return 0

    def check_equal_straight(self, our_cards_dignity, enemy_cards_dignity):
        our_maybe_straight = sorted(our_cards_dignity)
        if 13 in our_maybe_straight:
            our_maybe_straight.append(1)
            our_maybe_straight = sorted(our_maybe_straight)
        enemy_maybe_straight = sorted(enemy_cards_dignity)
        if 13 in enemy_maybe_straight:
            enemy_maybe_straight.append(1)
            enemy_maybe_straight = sorted(enemy_maybe_straight)

        for i in range(len(our_maybe_straight) - 5, -1, -1):
            our_straight = our_maybe_straight[i:i + 6]
            count = 0
            for j in range(5):
                if j - 1 >= 0:
                    if our_straight[j] - our_straight[j - 1] == 1:
                        count += 1
            if count == 4:
                break

        for i in range(len(enemy_maybe_straight) - 5, -1, -1):
            enemy_straight = enemy_maybe_straight[i:i + 6]
            count = 0
            for j in range(5):
                if j - 1 >= 0:
                    if enemy_straight[j] - enemy_straight[j - 1] == 1:
                        count += 1
            if count == 4:
                break

        if max(our_straight) >= max(enemy_straight):
            return 1
        else:
            return 0

    def check_equal_three_of_a_kind(self, our_cards_dignity, enemy_cards_dignity):
        array_our_set = []
        for i in our_cards_dignity:
            if our_cards_dignity.count(i) >= 3 and i not in array_our_set:
                array_our_set.append(i)
        max_our_set = max(array_our_set)

        array_enemy_set = []
        for i in enemy_cards_dignity:
            if enemy_cards_dignity.count(i) >= 3 and i not in array_enemy_set:
                array_enemy_set.append(i)
        max_enemy_set = max(array_enemy_set)

        while max_our_set in our_cards_dignity:
            our_cards_dignity.remove(max_our_set)

        while max_enemy_set in enemy_cards_dignity:
            enemy_cards_dignity.remove(max_enemy_set)

        if max_our_set > max_enemy_set:
            return 1
        elif max_our_set == max_enemy_set:
            our_kicker = max(our_cards_dignity)
            enemy_kicker = max(enemy_cards_dignity)
            if our_kicker >= enemy_kicker:
                return 1
            else:
                return 0
        else:
            return 0

    def check_equal_two_pair(self, our_cards_dignity, enemy_cards_dignity):
        array_our_pairs = []
        for i in our_cards_dignity:
            if our_cards_dignity.count(i) != 1 and i not in array_our_pairs:
                array_our_pairs.append(i)
        max_for_our_cards = max(array_our_pairs)
        array_our_pairs.remove(max_for_our_cards)
        second_max_for_our_cards = max(array_our_pairs)

        array_enemy_pairs = []
        for i in enemy_cards_dignity:
            if enemy_cards_dignity.count(i) != 1 and i not in array_enemy_pairs:
                array_enemy_pairs.append(i)
        max_for_enemy_cards = max(array_enemy_pairs)
        array_enemy_pairs.remove(max_for_enemy_cards)
        second_max_for_enemy_cards = max(array_enemy_pairs)

        our_cards_dignity.remove(max_for_our_cards)
        our_cards_dignity.remove(max_for_our_cards)
        our_cards_dignity.remove(second_max_for_our_cards)
        our_cards_dignity.remove(second_max_for_our_cards)

        enemy_cards_dignity.remove(max_for_enemy_cards)
        enemy_cards_dignity.remove(max_for_enemy_cards)
        enemy_cards_dignity.remove(second_max_for_enemy_cards)
        enemy_cards_dignity.remove(second_max_for_enemy_cards)

        if max_for_our_cards > max_for_enemy_cards:
            return 1
        elif max_for_our_cards == max_for_enemy_cards:
            if second_max_for_our_cards > second_max_for_enemy_cards:
                return 1
            elif second_max_for_our_cards == second_max_for_enemy_cards:
                our_max = max(our_cards_dignity)
                enemy_max = max(enemy_cards_dignity)
                if our_max >= enemy_max:
                    return 1
                else:
                    return 0
            else:
                return 0
        else:
            return 0

    def check_equal_pair(self, our_cards_dignity, enemy_cards_dignity):
        array_our_pairs = []
        for i in our_cards_dignity:
            if our_cards_dignity.count(i) != 1 and i not in array_our_pairs:
                array_our_pairs.append(i)
        max_for_our_cards = max(array_our_pairs)
        array_enemy_pairs = []
        for i in enemy_cards_dignity:
            if enemy_cards_dignity.count(i) != 1 and i not in array_enemy_pairs:
                array_enemy_pairs.append(i)
        max_for_enemy_cards = max(array_enemy_pairs)

        our_cards_dignity.remove(max_for_our_cards)
        our_cards_dignity.remove(max_for_our_cards)

        enemy_cards_dignity.remove(max_for_enemy_cards)
        enemy_cards_dignity.remove(max_for_enemy_cards)

        if max_for_our_cards > max_for_enemy_cards:
            return 1
        elif max_for_our_cards < max_for_enemy_cards:
            return 0
        else:
            first_our_max = max(our_cards_dignity)
            our_cards_dignity.remove(first_our_max)

            first_enemy_max = max(enemy_cards_dignity)
            enemy_cards_dignity.remove(first_enemy_max)
            if first_our_max > first_enemy_max:
                return 1
            elif first_our_max < first_enemy_max:
                return 0
            else:
                second_our_max = max(our_cards_dignity)
                our_cards_dignity.remove(second_our_max)

                second_enemy_max = max(enemy_cards_dignity)
                enemy_cards_dignity.remove(second_enemy_max)

                if second_our_max >= second_enemy_max:
                    return 1
                else:
                    return 0

    def check_equal_high_card(self, our_cards_dignity, enemy_cards_dignity):
        if max(our_cards_dignity) >= max(enemy_cards_dignity):
            return 1
        else:
            return 0

    def check_combination(self, cards_for_check):
        if self.check_royal_flush(cards_for_check) == 1:
            return 'Royal Flush'
        elif self.check_straight_flush(cards_for_check) == 1:
            return 'Straight Flush'
        elif self.check_four_of_a_kind(cards_for_check) == 1:
            return 'Four of a Kind'
        elif self.check_full_house(cards_for_check) == 1:
            return 'Full House'
        elif self.check_flush(cards_for_check) == 1:
            return 'Flush'
        elif self.check_straight(cards_for_check) == 1:
            return 'Straight'
        elif self.check_three_of_a_kind(cards_for_check) >= 1:
            return 'Three of a Kind'
        elif self.check_pair(cards_for_check)[0] >= 2:
            return 'Two Pair'
        elif self.check_pair(cards_for_check)[0] >= 1:
            return 'Pair'
        return 'High Card'

    def check_royal_flush(self, cards):
        cards_for_check = sorted([[int(x[0]), x[1]] for x in cards], key=lambda x: -x[0])
        array_symbols = []
        for i in cards_for_check:
            if i[0] in [13, 12, 11, 10, 9]:
                array_symbols.append(i[1])
        if len(array_symbols) == 5 and array_symbols.count(array_symbols[0]) == 5:
            return 1
        return 0

    def check_straight_flush(self, cards):
        cards_for_check = sorted([[int(x[0]), x[1]] for x in cards], key=lambda x: x[0])
        for i in cards_for_check:
            if i[0] == 13:
                cards_for_check.append([1, i[1]])
                cards_for_check = sorted(cards_for_check, key=lambda x: x[0])
                break
        if len(cards_for_check) == 5:
            count = 0
            for i in range(5):
                if i - 1 >= 0:
                    if cards_for_check[i][0] - cards_for_check[i - 1][0] == 1:
                        if cards_for_check[i][1] == cards_for_check[i - 1][1]:
                            count += 1
            if count == 4:
                return 1
        else:
            for i in range(len(cards_for_check) - 5, -1, -1):
                array = cards_for_check[i:i + 5]
                count = 0
                for j in range(5):
                    if j - 1 >= 0:
                        if array[j][0] - array[j - 1][0] == 1:
                            if array[j][1] == array[j - 1][1]:
                                count += 1
                if count == 4:
                    return 1
        return 0

    def check_four_of_a_kind(self, cards):
        if self.check_pair(cards)[1] >= 1:
            return 1
        return 0

    def check_full_house(self, cards):
        if self.check_pair(cards)[0] >= 1 and self.check_three_of_a_kind(cards) >= 1:
            return 1
        elif self.check_three_of_a_kind(cards) >= 2:
            return 1
        return 0

    def check_flush(self, cards):
        cards_for_check = sorted([int(x[1]) for x in cards])
        for i in cards_for_check:
            if cards_for_check.count(i) >= 5:
                return 1
        return 0

    def check_straight(self, cards):
        cards_for_check = sorted([int(x[0]) for x in cards])
        if 13 in cards_for_check:
            cards_for_check.append(1)
            cards_for_check = sorted(cards_for_check)
        if len(cards_for_check) == 5:
            count = 0
            for i in range(5):
                if i - 1 >= 0:
                    if cards_for_check[i] - cards_for_check[i - 1] == 1:
                        count += 1
            if count == 4:
                return 1
        else:
            for i in range(len(cards_for_check) - 5, -1, -1):
                array = cards_for_check[i:i + 6]
                count = 0
                for j in range(5):
                    if j - 1 >= 0:
                        if array[j] - array[j - 1] == 1:
                            count += 1
                if count == 4:
                    return 1
        return 0

    def check_three_of_a_kind(self, cards):
        count = 0
        cards_for_check = [x[0] for x in cards]
        count_of_cards = {}
        for i in cards_for_check:
            if i not in count_of_cards:
                count_of_cards[i] = 1
            else:
                count_of_cards[i] += 1
        for key in count_of_cards:
            if count_of_cards[key] == 3:
                count += 1
        return count

    def check_pair(self, cards):
        count = 0
        count_fours = 0
        cards_for_check = [x[0] for x in cards]
        count_of_cards = {}
        for i in cards_for_check:
            if i not in count_of_cards:
                count_of_cards[i] = 1
            else:
                count_of_cards[i] += 1
        for key in count_of_cards:
            if count_of_cards[key] == 4:
                count_fours += 1
            elif count_of_cards[key] == 2:
                count += 1
        return [count, count_fours]


class Database:
    def __init__(self):
        self.filename_database = 'statistics_for_game.db'
        self.connect = sqlite3.connect(self.filename_database)
        self.cursor = self.connect.cursor()

    def add_our_cards(self, our_cards):
        self.cursor.execute(f"""INSERT INTO our_cards(first_card, second_card)
                  VALUES ('{our_cards[0]}', '{our_cards[1]}');""")
        self.connect.commit()
        self.connect.close()

    def add_cards_on_desk(self, cards_on_flop):
        if cards_on_flop == '-':
            cards_on_flop = ['Отсутствует'] * 3
        self.cursor.execute(f"""INSERT INTO cards_on_desk(first_card_on_flop,
                                second_card_on_flop, third_card_on_flop,
                                card_on_turn, card_on_river)
                                VALUES ('{cards_on_flop[0]}', '{cards_on_flop[1]}',
                                '{cards_on_flop[2]}', 'Отсутствует', 'Отсутствует');""")
        self.connect.commit()
        self.connect.close()

    def update_cards_on_desk_on_turn(self, new_cards_on_desk):
        card_on_turn = new_cards_on_desk[-1]
        first_card_on_flop = new_cards_on_desk[0]
        second_card_on_flop = new_cards_on_desk[1]
        third_card_on_flop = new_cards_on_desk[2]

        sql_take_table_cards = 'SELECT id_game FROM cards_on_desk ORDER BY id_game DESC'
        self.cursor.execute(sql_take_table_cards)
        game_id = int(self.cursor.fetchone()[0])
        sql_update = f"""UPDATE cards_on_desk
                         SET card_on_turn = '{card_on_turn}',
                         first_card_on_flop = '{first_card_on_flop}',
                         second_card_on_flop = '{second_card_on_flop}',
                         third_card_on_flop = '{third_card_on_flop}'
                         WHERE id_game = {game_id}"""
        self.cursor.execute(sql_update)
        self.connect.commit()
        self.connect.close()

    def update_cards_on_desk_on_river(self, new_cards_on_desk):
        card_on_river = new_cards_on_desk[-1]
        card_on_turn = new_cards_on_desk[-2]
        first_card_on_flop = new_cards_on_desk[0]
        second_card_on_flop = new_cards_on_desk[1]
        third_card_on_flop = new_cards_on_desk[2]

        sql_take_table_cards = 'SELECT id_game FROM cards_on_desk ORDER BY id_game DESC'
        self.cursor.execute(sql_take_table_cards)
        game_id = int(self.cursor.fetchone()[0])
        sql_update = f"""UPDATE cards_on_desk
                         SET card_on_river = '{card_on_river}',
                         card_on_turn = '{card_on_turn}',
                         first_card_on_flop = '{first_card_on_flop}',
                         second_card_on_flop = '{second_card_on_flop}',
                         third_card_on_flop = '{third_card_on_flop}'
                         WHERE id_game = {game_id}"""
        self.cursor.execute(sql_update)
        self.connect.commit()
        self.connect.close()

    def update_main_table_on_turn(self, chance, new_cards_on_desk):
        card_on_turn = new_cards_on_desk[-1]
        first_card_on_flop = new_cards_on_desk[0]
        second_card_on_flop = new_cards_on_desk[1]
        third_card_on_flop = new_cards_on_desk[2]

        sql_take_table_cards = 'SELECT Game_number FROM games ORDER BY Game_number DESC'
        self.cursor.execute(sql_take_table_cards)
        game_id = int(self.cursor.fetchone()[0])
        sql_update = f"""UPDATE Games
                         SET Card_on_turn = '{card_on_turn}', Chance = '{chance}%',
                         First_card_on_flop = '{first_card_on_flop}',
                         Second_card_on_flop = '{second_card_on_flop}',
                         Third_card_on_flop = '{third_card_on_flop}'
                         WHERE Game_number = {game_id}"""
        self.cursor.execute(sql_update)
        self.connect.commit()
        self.connect.close()

    def update_main_table_on_river(self, chance, new_cards_on_desk):
        card_on_river = new_cards_on_desk[-1]
        card_on_turn = new_cards_on_desk[-2]
        first_card_on_flop = new_cards_on_desk[0]
        second_card_on_flop = new_cards_on_desk[1]
        third_card_on_flop = new_cards_on_desk[2]

        sql_take_table_cards = 'SELECT Game_number FROM games ORDER BY Game_number DESC'
        self.cursor.execute(sql_take_table_cards)
        game_id = int(self.cursor.fetchone()[0])
        sql_update = f"""UPDATE Games
                         SET Card_on_river = '{card_on_river}', Chance = '{chance}%',
                         Card_on_turn = '{card_on_turn}',
                         First_card_on_flop = '{first_card_on_flop}',
                         Second_card_on_flop = '{second_card_on_flop}',
                         Third_card_on_flop = '{third_card_on_flop}'
                         WHERE Game_number = {game_id}"""
        self.cursor.execute(sql_update)
        self.connect.commit()
        self.connect.close()

    def add_execute_for_main_table(self, our_chance):
        sql_take_our_cards = 'SELECT * FROM our_cards ORDER BY id_game DESC'
        self.cursor.execute(sql_take_our_cards)
        try:
            our_cards = self.cursor.fetchone()[1::]
        except TypeError:
            our_cards = ['Отсутствует'] * 2
        sql_take_table_cards = 'SELECT * FROM cards_on_desk ORDER BY id_game DESC'
        self.cursor.execute(sql_take_table_cards)
        try:
            cards_on_flop = self.cursor.fetchone()[1::]
        except TypeError:
            cards_on_flop = ['Отсутствует'] * 3
        self.cursor.execute(f"""INSERT INTO games(Chance, First_our_card, Second_our_card,
                                 First_card_on_flop, Second_card_on_flop,
                                 Third_card_on_flop, Card_on_turn, Card_on_river)
                            VALUES ('{our_chance}%', '{our_cards[0]}', '{our_cards[1]}',
                                    '{cards_on_flop[0]}', '{cards_on_flop[1]}',
                                    '{cards_on_flop[2]}', '{cards_on_flop[3]}',
                                    '{cards_on_flop[4]}');""")
        self.connect.commit()
        self.connect.close()

    def clear_all_tables(self):
        self.cursor.execute(f'DELETE FROM cards_on_desk;')
        self.cursor.execute(f'DELETE FROM games;')
        self.cursor.execute(f'DELETE FROM our_cards;')
        self.connect.commit()
        self.connect.close()
