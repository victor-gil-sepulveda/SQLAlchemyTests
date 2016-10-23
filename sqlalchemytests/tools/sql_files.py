def parse_sql_file(the_file_contents):
    sql_started = False
    new_transaction = False
    all_tests = {}
    last_test_name = None
    transaction_number = 0
    for line in the_file_contents:
        l = line.strip()
        if l != "":
            if line[0:2] == "--":
                # Then is an sql comment and must be skipped
                # except if it has Name
                if "Name" in line:
                    _, name = line[2:].split(":")
                    last_test_name = name.strip()
                    # New SQL test
                    all_tests[last_test_name] = [[]]
                    transaction_number = 0
            if last_test_name is not None:
                all_tests[last_test_name][transaction_number].append(line)
            if line[-1] == ";":
                all_tests[last_test_name].append([])
                transaction_number += 1

    return all_tests


def get_test_sql(name, the_tests):
    all_transactions = []
    for transaction_set in the_tests[name]:
        if transaction_set:
            transaction_text = "\n".join(transaction_set)
            all_transactions.append(transaction_text)
    return all_transactions
