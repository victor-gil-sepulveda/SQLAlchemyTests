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


def gen_users(num_users):
    first, mid, last = gen_random_names(num_users)
    ages = gen_random_ages(num_users)
    passwords = gen_random_hashes(num_users)

    return [{
        "first_name": f,
        "mid_name": m,
        "last_name": l,
        "age": a,
        "password_hash": p
        } for f, m, l, a, p in zip(first, mid, last, ages, passwords)]


def get_team_names(num_teams):
    names = [line.strip() for line in open(data.files["team_names"])]
    random.shuffle(names)
    return names[0:num_teams]


def get_roles(num_roles):
    """
    We get only a subset (20) of the roles file.
    :return: a list of string roles
    """
    all_roles = list(set([line.strip().split()[0].replace("'", "") for line in open(data.files["professions"])]))
    return [random.choice(all_roles) for _ in range(num_roles)]


def gen_costs(num_costs):
    return [float("%d.%d" % (
        math.floor(random.random() * 1000), math.floor(random.random() * (10 ** math.ceil(random.random() * 4))))) for _
     in range(num_costs)]


def gen_memberships(num_users, num_teams, num_roles, num_memberships):
    team_ids = [1 + random.choice(range(num_teams)) for _ in range(num_memberships)]
    user_ids = [1 + random.choice(range(num_users)) for _ in range(num_memberships)]
    memb_key = list(set(zip(user_ids, team_ids)))

    costs = gen_costs(num_memberships)
    roles = get_roles(num_roles)
    return [{"user_id": user_id,
             "team_id": team_id,
             "cost": cost,
             "role": random.choice(roles)} for (user_id, team_id), cost in zip(memb_key, costs)]
