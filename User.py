import random
import time
users = [[]]*547
mood = random.randrange(-20, 20)


class User:
    def __init__(self, user_id, name, is_admin, favor):
        self.id = user_id
        self.name = name
        self.is_admin = is_admin
        self.favor = favor
        self.cur_favor = 0
        self.messages = set()
        self.message_times = set()
        self.num_spams = 0

    def is_spamming(self):
        current = time.time()
        self.message_times.add(time.time())
        count = len(self.message_times)-3
        if count < 1:
            return False
        last_time = min(self.message_times)
        average_message_time = (current-last_time)/count
        if average_message_time < 60:
            return True
        if average_message_time > 180:
            self.message_times.clear()
            self.num_spams = 0
        return False

    def update_favor(self):
        self.favor += self.cur_favor
        self.cur_favor = 0
        if self.favor < -20:
            self.favor = -20
        if self.favor > 100:
            self.favor = 100

    def add_favor(self, response_id):
        if self.cur_favor < 5 and response_id not in self.messages:
            self.messages.add(response_id)
            self.cur_favor += 1

    def make_admin(self):
        self.is_admin = True

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        if type(self) is type(other) and hash(self) == hash(other):
            return True
        return False

    def calculate_favor(self):
        favor = self.favor+self.cur_favor+mood+random.randrange(-20, 20)
        if favor < 0:
            favor = 0
        if favor > 100:
            favor = 100
        return favor


def create_from_element(element):
    user_id, name, is_admin, message = element.split("\t")
    is_admin = is_admin == "true"
    user_id = int(user_id)
    return User(user_id, name, is_admin, 0), message


def find_user_by_name(name):
    for user_list in users:
        if not user_list:
            continue
        for user in user_list:
            if user.name.lower() == name.lower():
                return user
    return User(0, name, False, 0)


def users_hash(user):
    return hash(user) % len(users)


def get_user(user):
    user_list = users[users_hash(user)]
    if not user_list:
        users[users_hash(user)] = [user]
        return user
    for i in user_list:
        if i == user:
            return i
    user_list.append(user)
    return user


def read_users():
    user_file = open("users.txt")
    user_lines = user_file.read().splitlines()
    user_file.close()
    for line in user_lines:
        user_id, name, admin, favor = line.split("\t")
        is_admin = admin == "T"
        get_user(User(int(user_id), name, is_admin, int(favor)))


def write_users():
    user_file = open("users.txt", "w")
    for user_list in users:
        for user in user_list:
            if user.is_admin or user.favor != 0:
                user_file.write(str(user.id)+"\t")
                user_file.write(str(user.name)+"\t")
                user_file.write("T\t" if user.is_admin else "F\t")
                user_file.write(str(user.favor+user.cur_favor)+"\n")
    user_file.close()