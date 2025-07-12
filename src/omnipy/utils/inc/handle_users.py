import yaml

def handle_users(author: str):
    author_char = author[0].upper()
    data = {letter: [] for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'}
    users_file = join(DIR_HOME, '.users', 'users')
    if exists(users_file):
        with open(users_file, 'r+') as file:
            try:
                data = yaml.safe_load(file) or data
            except yaml.YAMLError:
                data = {letter: [] for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'}
            if author_char not in data:
                data[author_char] = []
            if author not in data[author_char]:
                data[author_char].append(author)
                file.seek(0)
                file.write(yaml.dump(data))
                file.truncate()
    else:
        with open(users_file, 'w') as file:
            yaml.dump(data, file)