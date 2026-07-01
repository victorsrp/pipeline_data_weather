from datetime import datetime, timedelta
from pathlib import Path
import os
import sys

from airflow.sdk import dag, task
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / 'src'))

from extract_data import extract_weather_data
from load_data import load_weather_data
from transform_data import data_transformation

env_path = ROOT_DIR / 'config' / '.env'
load_dotenv(env_path)

API_KEY = os.getenv('API_KEY', '')
url = f"https://api.openweathermap.org/data/2.5/weather?q=Sao%20Paulo,BR&units=metric&appid={API_KEY}"


@task
def extract_weather_task():
    return extract_weather_data(url)


@task
def transform_weather_task(_):
    return data_transformation()


@task
def load_weather_task(df):
    load_weather_data('weather_data', df)
    return 'ok'


@dag(
    dag_id='weather_pipeline',
    default_args={
        'owner': 'airflow',
        'depends_on_past': False,
        'retries': 2,
        'retry_delay': timedelta(minutes=5),
    },
    description='Pipeline ETL - Clima SP',
    schedule='0 */1 * * *',
    start_date=datetime(2024, 1, 1),
    catchup=False,
)
def weather_pipeline():
    extracted = extract_weather_task()
    transformed = transform_weather_task(extracted)
    load_weather_task(transformed)
