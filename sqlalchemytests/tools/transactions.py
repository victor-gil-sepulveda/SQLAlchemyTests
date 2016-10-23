from sqlalchemy import create_engine


def open_connection(database_uri):
    engine = create_engine(database_uri)
    connection = engine.connect()
    return connection


def run_transactions(connection, transaction_set):
    trans = connection.begin()
    try:
        for trans_part in transaction_set:
            result = connection.execute(trans_part)
        trans.commit()
        return result
    except:
        trans.rollback()
        raise

