from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime, timedelta
import pandas as pd
import logging
from clickhouse_driver import Client
from typing import Dict, List, Any
import numpy as np

logger = logging.getLogger(__name__)

CLICKHOUSE_CONFIG = {
    'host': 'clickhouse-server',
    'port': 9000,
    'user': 'airflow',
    'password': 'airflow',
    'database': 'olap_db'
}

CRM_QUERIES = {
    'customers': """
        SELECT customer_id, username, email, first_name, last_name, 
               registration_date, role 
        FROM customers
    """,
    'orders': """
        SELECT customer_id, COUNT(*) as total_orders, 
               SUM(total_amount) as total_order_amount,
               STRING_AGG(DISTINCT product_type, ', ') as product_types
        FROM orders 
        WHERE status = 'completed'
        GROUP BY customer_id
    """
}

TELEMETRY_QUERIES = {
    'telemetry': """
        SELECT 
            customer_id,
            session_date,
            SUM(usage_minutes) as daily_usage_minutes,
            SUM(movement_count) as daily_movements,
            SUM(error_count) as daily_errors,
            AVG(battery_level) as avg_battery,
            AVG(signal_quality) as avg_signal_quality
        FROM telemetry_data 
        WHERE session_date >= CURRENT_DATE - INTERVAL '7 days'
        GROUP BY customer_id, session_date
    """,
    'movement': """
        SELECT 
            customer_id,
            session_date,
            AVG(success_rate) as avg_success_rate,
            AVG(response_time_ms) as avg_response_time
        FROM movement_logs 
        WHERE session_date >= CURRENT_DATE - INTERVAL '7 days'
        GROUP BY customer_id, session_date
    """
}

default_args = {
    'owner': 'bionicpro_etl',
    'start_date': datetime(2025, 11, 1),
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': False,
    'email_on_retry': False
}


class ClickHouseConnector:
    
    @staticmethod
    def get_client() -> Client:
        try:
            client = Client(**CLICKHOUSE_CONFIG)
            logger.info("Successfully connected to ClickHouse")
            return client
        except Exception as e:
            logger.error(f"Failed to connect to ClickHouse: {str(e)}")
            raise


class DataExtractor:
    
    @staticmethod
    def _get_postgres_conn(conn_id: str):
        hook = PostgresHook(postgres_conn_id=conn_id)
        return hook.get_conn()
    
    @staticmethod
    def _extract_to_csv(query: str, conn_id: str, output_path: str, 
                        parse_dates: List[str] = None) -> pd.DataFrame:
        try:
            hook = PostgresHook(postgres_conn_id=conn_id)
            df = hook.get_pandas_df(query)
            
            if parse_dates:
                for date_col in parse_dates:
                    if date_col in df.columns:
                        df[date_col] = pd.to_datetime(df[date_col]).dt.date
            
            df.to_csv(output_path, index=False)
            logger.info(f"Extracted {len(df)} records to {output_path}")
            return df
        except Exception as e:
            logger.error(f"Extraction failed: {str(e)}")
            raise
    
    def extract_crm(self) -> None:
        logger.info("Starting CRM data extraction")
        
        customers_df = self._extract_to_csv(
            CRM_QUERIES['customers'], 
            'crm_db', 
            '/tmp/crm_customers.csv',
            parse_dates=['registration_date']
        )
        
        orders_df = self._extract_to_csv(
            CRM_QUERIES['orders'], 
            'crm_db', 
            '/tmp/crm_orders.csv'
        )
        
        merged_df = pd.merge(customers_df, orders_df, on='customer_id', how='left')
        merged_df.fillna({
            'total_orders': 0, 
            'total_order_amount': 0, 
            'product_types': 'No orders'
        }, inplace=True)
        
        merged_df.to_csv('/tmp/crm_extracted_data.csv', index=False)
        logger.info(f"CRM data merged: {len(merged_df)} records")
    
    def extract_telemetry(self) -> None:
        logger.info("Starting telemetry data extraction")
        
        telemetry_df = self._extract_to_csv(
            TELEMETRY_QUERIES['telemetry'], 
            'telemetry_db', 
            '/tmp/telemetry_main.csv',
            parse_dates=['session_date']
        )
        
        movement_df = self._extract_to_csv(
            TELEMETRY_QUERIES['movement'], 
            'telemetry_db', 
            '/tmp/telemetry_movement.csv',
            parse_dates=['session_date']
        )
        
        merged_df = pd.merge(
            telemetry_df, movement_df, 
            on=['customer_id', 'session_date'], 
            how='left'
        )
        merged_df.fillna({'avg_success_rate': 0, 'avg_response_time': 0}, inplace=True)
        
        merged_df.to_csv('/tmp/telemetry_extracted_data.csv', index=False)
        logger.info(f"Telemetry data merged: {len(merged_df)} records")


class DataTransformer:
    
    TELEMETRY_AGGREGATION = {
        'daily_usage_minutes': ['sum', 'mean'],
        'daily_movements': 'sum',
        'daily_errors': 'sum',
        'avg_battery': 'mean',
        'avg_signal_quality': 'mean',
        'avg_success_rate': 'mean',
        'avg_response_time': 'mean'
    }
    
    TELEMETRY_COLUMNS = [
        'total_usage_minutes', 'avg_daily_usage_minutes', 'total_movements',
        'total_errors', 'avg_battery_level', 'avg_signal_quality',
        'avg_success_rate', 'avg_response_time_ms'
    ]
    
    @staticmethod
    def _aggregate_telemetry(telemetry_df: pd.DataFrame) -> pd.DataFrame:
        aggregated = telemetry_df.groupby('customer_id').agg(
            DataTransformer.TELEMETRY_AGGREGATION
        ).round(2)
        
        aggregated.columns = [
            'total_usage_minutes', 'avg_daily_usage_minutes',
            'total_movements', 'total_errors', 'avg_battery_level',
            'avg_signal_quality', 'avg_success_rate', 'avg_response_time_ms'
        ]
        
        return aggregated.reset_index()
    
    @staticmethod
    def _calculate_scores(df: pd.DataFrame) -> pd.DataFrame:
        df['usage_efficiency_score'] = (
            (df['avg_success_rate'] * 0.6) +
            ((100 - df['avg_response_time_ms'] / 2) * 0.4)
        ).round(2)
        
        df['movement_accuracy_score'] = (
            (df['avg_success_rate'] * 0.7) +
            (df['avg_signal_quality'] * 0.3)
        ).round(2)
        
        return df
    
    @staticmethod
    def _prepare_clickhouse_data(final_df: pd.DataFrame) -> List[Dict[str, Any]]:
        clickhouse_data = []
        current_date = datetime.now().date()
        current_datetime = datetime.now()
        
        for idx, row in final_df.iterrows():
            record = {
                'mart_id': idx + 1,
                'customer_id': row['customer_id'],
                'username': str(row['username']),
                'email': str(row['email']),
                'customer_role': str(row['role']),
                'report_date': current_date,
                'total_usage_minutes': int(row['total_usage_minutes']),
                'avg_daily_usage_minutes': float(row['avg_daily_usage_minutes']),
                'total_movements': int(row['total_movements']),
                'avg_success_rate': float(row['avg_success_rate']),
                'avg_response_time_ms': float(row['avg_response_time_ms']),
                'total_errors': int(row['total_errors']),
                'avg_battery_level': float(row['avg_battery_level']),
                'avg_signal_quality': float(row['avg_signal_quality']),
                'registration_date': row['registration_date'],
                'product_type': str(row['product_types']),
                'total_orders': int(row['total_orders']),
                'total_order_amount': float(row['total_order_amount']),
                'usage_efficiency_score': float(row['usage_efficiency_score']),
                'movement_accuracy_score': float(row['movement_accuracy_score']),
                'last_updated': current_datetime
            }
            clickhouse_data.append(record)
        
        return clickhouse_data
    
    def transform(self) -> List[Dict[str, Any]]:
        logger.info("Starting data transformation")
        
        crm_df = pd.read_csv('/tmp/crm_extracted_data.csv')
        telemetry_df = pd.read_csv('/tmp/telemetry_extracted_data.csv')
        
        crm_df['registration_date'] = pd.to_datetime(
            crm_df['registration_date']
        ).dt.date
        
        telemetry_aggregated = self._aggregate_telemetry(telemetry_df)

        merged_df = pd.merge(
            crm_df, telemetry_aggregated, 
            on='customer_id', how='left'
        )
        
        for col in self.TELEMETRY_COLUMNS:
            merged_df[col] = merged_df[col].fillna(0)
        
        merged_df = self._calculate_scores(merged_df)
        
        integer_columns = ['total_usage_minutes', 'total_movements', 
                          'total_errors', 'total_orders']
        for col in integer_columns:
            merged_df[col] = merged_df[col].astype(int)
        
        clickhouse_data = self._prepare_clickhouse_data(merged_df)
        
        logger.info(f"Transformed {len(clickhouse_data)} records")
        return clickhouse_data


class DataLoader:
    
    INSERT_QUERY = """
        INSERT INTO customer_telemetry_mart (
            mart_id, customer_id, username, email, customer_role, report_date,
            total_usage_minutes, avg_daily_usage_minutes, total_movements,
            avg_success_rate, avg_response_time_ms, total_errors,
            avg_battery_level, avg_signal_quality, registration_date,
            product_type, total_orders, total_order_amount,
            usage_efficiency_score, movement_accuracy_score, last_updated
        ) VALUES
    """
    
    DELETE_QUERY = """
        ALTER TABLE customer_telemetry_mart 
        DELETE WHERE report_date = %(report_date)s
    """
    
    SUMMARY_QUERY = """
        INSERT INTO daily_telemetry_summary
        SELECT 
            report_date as summary_date,
            customer_role,
            COUNT(*) as total_customers,
            SUM(total_usage_minutes) / 60.0 as total_usage_hours,
            AVG(avg_success_rate) as avg_success_rate,
            AVG(avg_response_time_ms) as avg_response_time_ms,
            SUM(total_errors) as total_errors,
            AVG(avg_battery_level) as avg_battery_level
        FROM customer_telemetry_mart 
        WHERE report_date = %(report_date)s
        GROUP BY report_date, customer_role
    """
    
    def load_to_mart(self, data: List[Dict[str, Any]]) -> None:
        client = ClickHouseConnector.get_client()
        current_date = datetime.now().date()
        
        try:
            client.execute(self.DELETE_QUERY, {'report_date': current_date})
            logger.info("Cleared old records for current report date")
            
            if data:
                client.execute(self.INSERT_QUERY, data)
                logger.info(f"Loaded {len(data)} records to customer_telemetry_mart")
            else:
                logger.warning("No data to load")
                
        except Exception as e:
            logger.error(f"Failed to load data to mart: {str(e)}")
            raise
    
    def create_summary(self) -> None:
        client = ClickHouseConnector.get_client()
        current_date = datetime.now().date()
        
        try:
            client.execute(self.SUMMARY_QUERY, {'report_date': current_date})
            logger.info("Daily summary created successfully")
        except Exception as e:
            logger.error(f"Failed to create daily summary: {str(e)}")
            raise


def extract_crm_data():
    extractor = DataExtractor()
    extractor.extract_crm()


def extract_telemetry_data():
    extractor = DataExtractor()
    extractor.extract_telemetry()


def transform_and_load_to_clickhouse():
    transformer = DataTransformer()
    loader = DataLoader()
    
    transformed_data = transformer.transform()
    loader.load_to_mart(transformed_data)


def create_daily_summary():
    loader = DataLoader()
    loader.create_summary()


with DAG(
    dag_id='bionicpro_clickhouse_etl',
    default_args=default_args,
    description='ETL pipeline for BionicPRO with ClickHouse OLAP',
    schedule_interval='0 2 * * *',
    catchup=False,
    tags=['bionicpro', 'clickhouse', 'etl', 'reports'],
    doc_md="""
    ### ETL Pipeline для BionicPRO
    
    Этот DAG выполняет ETL процесс для загрузки данных в ClickHouse:
    
    1. **extract_crm_data** - извлечение данных из CRM PostgreSQL
    2. **extract_telemetry_data** - извлечение данных из Telemetry PostgreSQL
    3. **transform_and_load_to_clickhouse** - трансформация и загрузка в витрину
    4. **create_daily_summary** - создание ежедневных агрегатов
    """
) as dag:
    
    extract_crm_task = PythonOperator(
        task_id='extract_crm_data',
        python_callable=extract_crm_data,
        retries=3,
        retry_delay=timedelta(minutes=2)
    )
    
    extract_telemetry_task = PythonOperator(
        task_id='extract_telemetry_data',
        python_callable=extract_telemetry_data,
        retries=3,
        retry_delay=timedelta(minutes=2)
    )
    
    transform_load_task = PythonOperator(
        task_id='transform_and_load_to_clickhouse',
        python_callable=transform_and_load_to_clickhouse,
        retries=2,
        retry_delay=timedelta(minutes=5)
    )
    
    create_summary_task = PythonOperator(
        task_id='create_daily_summary',
        python_callable=create_daily_summary
    )
    
    [extract_crm_task, extract_telemetry_task] >> transform_load_task >> create_summary_task