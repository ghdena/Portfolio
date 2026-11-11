from airflow.decorators import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime, timedelta
import pandas as pd
from psycopg2.extras import execute_values

default_args = {
    'owner': 'owner_name',
    'retries': 2,
    'retry_delay': timedelta(minutes=10),
}

@dag(
    dag_id='cbr_currency_daily_update',
    default_args=default_args,
    schedule_interval='0 14 * * *',     # Каждый день в 14:00
    start_date=datetime(2026, 1, 1),
    catchup=False,                      # Не выполнять пропущенные запуски
    tags=['cbr'],
    description='Ежедневное обновление курсов валют с сайта ЦБ РФ',
)
def cbr_currency_dag():
    
    @task
    def load_new_rates():
        pg_hook = PostgresHook(postgres_conn_id='сonnection_name')
        conn = pg_hook.get_conn()
        
        try:
            # Получаем последнюю дату
            with conn.cursor() as cur:
                cur.execute("SELECT MAX(rate_date) FROM currency_rates")
                last_date = cur.fetchone()[0]
            
            if last_date is None:
                start_date = datetime(2013, 1, 1).date()
                print("Таблица пуста. Загружаем с 2013-01-01")
            else:
                start_date = last_date + timedelta(days=1)
                print(f"Последняя дата: {last_date}")
            
            today = datetime.now().date()
            if start_date > today:
                print("Данные актуальны")
                return
            
            # Загружаем данные
            all_data = []
            current_date = start_date
            
            while current_date <= today:
                date_str = current_date.strftime("%d.%m.%Y")
                print(f"Загружаем {date_str}...")
                
                url = f"https://www.cbr.ru/scripts/XML_daily.asp?date_req={date_str}"
                
                try:
                    df = pd.read_xml(url, encoding='windows-1251')
                    df = df.rename(columns={
                        'NumCode': 'digital_code',
                        'CharCode': 'letter_code',
                        'Nominal': 'units',
                        'Name': 'currency_name',
                        'Value': 'rate'
                    })
                    df['rate'] = df['rate'].str.replace(',', '.').astype(float)
                    df['units'] = df['units'].astype(int)
                    df['digital_code'] = df['digital_code'].astype(str).str.zfill(3)
                    df['rate_date'] = current_date
                    
                    all_data.extend(
                        df[['rate_date', 'digital_code', 'letter_code', 'units', 'currency_name', 'rate']]
                        .to_records(index=False)
                        .tolist()
                        )
                    
                except Exception as e:
                    print(f"Ошибка за {date_str}: {e}")
                
                current_date += timedelta(days=1)
            
            # Вставляем в БД
            if all_data:
                insert_query = """
                    INSERT INTO currency_rates 
                    (rate_date, digital_code, letter_code, units, currency_name, rate)
                    VALUES %s
                    ON CONFLICT (rate_date, letter_code) DO NOTHING
                """
                with conn.cursor() as cur:
                    execute_values(cur, insert_query, all_data)
                conn.commit()
                print(f"Добавлено {len(all_data)} записей")
            else:
                print("Нет новых данных")
                
        except Exception as e:
            conn.rollback()
            print(f"Ошибка: {e}")
            raise
        finally:
            conn.close()
    
    # Запускаем задачу
    load_new_rates()

# Запускаем DAG
cbr_currency_dag()
