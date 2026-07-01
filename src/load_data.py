from sqlalchemy import create_engine, text
import os
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

env_path = Path(__file__).resolve().parent.parent / 'config' / '.env'
load_dotenv(env_path)

user = os.getenv('user', 'airflow')
password = os.getenv('password', 'airflow')
database = os.getenv('database', 'airflow')
host = os.getenv('DB_HOST', '127.0.0.1')
port = os.getenv('DB_PORT', '5432')


def get_engine():
    logging.info(f'Conectando em {host}:{port}/{database}')
    return create_engine(
        f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}',
        connect_args={'connect_timeout': 10},
    )


def ensure_database():
    admin_engine = create_engine(
        f'postgresql+psycopg2://{user}:{password}@{host}:{port}/postgres',
        connect_args={'connect_timeout': 10},
    )

    with admin_engine.connect() as conn:
        conn.execute(text("SELECT 1"))
        existing = conn.execute(text("SELECT 1 FROM pg_database WHERE datname = :db"), {'db': database}).scalar()
        if not existing:
            conn.execute(text(f'CREATE DATABASE {database}'))
            logging.info(f'Banco {database} criado com sucesso!')


def load_weather_data(table_name: str, df):
    ensure_database()
    engine = get_engine()

    with engine.begin() as conn:
        conn.execute(text(f'DROP TABLE IF EXISTS {table_name}'))
        columns_sql = []
        for column, dtype in df.dtypes.items():
            if pd.api.types.is_bool_dtype(dtype):
                pg_type = 'BOOLEAN'
            elif pd.api.types.is_integer_dtype(dtype):
                pg_type = 'BIGINT'
            elif pd.api.types.is_float_dtype(dtype):
                pg_type = 'DOUBLE PRECISION'
            elif pd.api.types.is_datetime64_any_dtype(dtype):
                pg_type = 'TIMESTAMP'
            else:
                pg_type = 'TEXT'
            columns_sql.append(f'"{column}" {pg_type}')
        conn.execute(text(f'CREATE TABLE {table_name} ({", ".join(columns_sql)})'))

    df.to_sql(
        name=table_name,
        con=engine,
        if_exists='append',
        index=False,
    )

    logging.info('Dados carregados com sucesso!\n')

    df_check = pd.read_sql(f'SELECT * FROM {table_name}', con=engine)
    logging.info(f'Total de registros na tabela: {len(df_check)}\n')
