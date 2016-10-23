import sqlalchemytests.tools.data as data
import random
import string
import math


def gen_random_names(num_names):
    first_names = []
    mid_names = []
    last_names = []
    for line in open(data.files["names"]):
        name, surname = line.split()
        first_names.append(name)
        mid_names.extend([name, "", ""])
        last_names.append(surname)
    r_first_names = []
    r_mid_names = []
    r_last_names = []
    for i in range(num_names):
        r_first_names.append(random.choice(first_names))
        r_mid_names.append(random.choice(mid_names))
        r_last_names.append(random.choice(last_names))
    return r_first_names, r_mid_names, r_last_names


def gen_random_ages(num_ages):
    return [(100 * random.random()) + 1 for i in range(num_ages)]


def gen_random_hashes(num_passwords):
    return ["".join([random.choice(string.ascii_lowercase + string.ascii_uppercase) for _ in range(10)]) for _ in
            range(num_passwords)]


def get_team_names():
    return [line.strip() for line in open(data.files["team_names"])]


def get_roles():
    return list(set([line.strip().split()[0].replace("'", "") for line in open(data.files["professions"])]))


def gen_costs(num_costs):
    return [float("%d.%d" % (
        math.floor(random.random() * 1000), math.floor(random.random() * (10 ** math.ceil(random.random() * 4))))) for _
     in range(num_costs)]


def gen_memberships(user_names, teams, costs, roles, max_memberships):
    team_ids = list(set([1 + random.choice(range(len(teams))) for _ in range(max_memberships)]))
    user_ids = list(set([1 + random.choice(range(len(user_names))) for _ in range(max_memberships)]))
    return [{"user_id": user_id,
             "team_id": team_id,
             "cost": cost,
             "role": random.choice(roles)} for user_id, team_id, cost in zip(user_ids, team_ids, costs)]

