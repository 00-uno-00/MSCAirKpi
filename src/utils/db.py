DATABASE_URL = "postgresql://neondb_owner:npg_ibQE9C0cXNnZ@ep-aged-cake-a2x4wqvv-pooler.eu-central-1.aws.neon.tech/neondb?sslmode=require"

import psycopg2
from flask import g
from datetime import datetime
import src.utils.spis as spi_utils
import os

#DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    #if 'db_conn' not in g:    , sslmode='require'
    g.db_conn = psycopg2.connect(DATABASE_URL)
    return g.db_conn


def commit_update_data(updated_spis, conn, table):
    """
    Inserisce o aggiorna i dati nel database per una lista di spi.
    """
    cur = conn.cursor()

    for spi_name, value, month, year in updated_spis:
        # Inserisci i dati nel database
        try:
            # Check if record exists for {table}
            cur.execute(f"""
                SELECT id FROM {table} WHERE spi = %s AND entry_date = date_trunc('month', date %s)
            """, (spi_name, datetime(year, (month-1), 1)))
            existing_record = cur.fetchone()
            if existing_record:
                # Update
                cur.execute(f"""
                    UPDATE {table} SET spi = %s, entry_date = date_trunc('month', date %s), value = %s
                    WHERE id = %s
                """, (spi_name, datetime(year, (month-1), 1), value, existing_record[0]))
            else:
                # Insert
                cur.execute(f"""
                    INSERT INTO {table} (spi, value, entry_date)
                    VALUES (%s, %s, %s)
                """, (spi_name, value, datetime(year, (month-1), 1)))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Error inserting data: {e}")
            return f"An error occurred: {e}", 500

def get_data_spi(spi_name, start_date, end_date, cur, table):
    """
    Recupera i dati dal database per un determinato SPI.
    Args:
        spi_name (str): Il nome dello SPI da cui recuperare i dati.
        start_date (datetime.date): La data di inizio del range.
        end_date (datetime.date): La data di fine del range.
    Returns:
        list: Una lista di dizionari contenenti i valori e le date di inserimento, nella forma:
              [{'value': value1, 'entry_date': date1}, ...]
    N.B. selezionando un range di un solo mese un singolo mese verra' ritornato
    """

    try:
        # Query per ottenere i dati per gli SPIs specificati 
        query = f"""
            SELECT value, entry_date FROM {table}
            WHERE spi = %s AND entry_date BETWEEN date_trunc('month', date %s) AND date_trunc('month', date %s)
            ORDER BY entry_date
            """
        cur.execute(
            query,
            (spi_name, start_date, end_date)
        )
        data = cur.fetchall()
        # Return both value and entry_date as a list of dicts
        return [{'value':  d[0], 'entry_date': d[1]} for d in data]
    except Exception as e:
        print(f"Error fetching data for SPI {spi_name}: {e}")
        return []
    
def get_data_table(table, start_date, end_date, cur):
    """
    Recupera i dati dal database per una tabella specifica.
    Args:
        table (str): Il nome della tabella da cui recuperare i dati.
        start_date (datetime.date): La data di inizio del range.
        end_date (datetime.date): La data di fine del range.
    Returns:
        list: Una lista di dizionari contenenti i valori e le date di inserimento, nella forma:
              [{'spi_name': spi_name, 'data': {'value': value1, 'entry_date': date1}}, ...]
    """
    try:
        query = f"""
            SELECT spi, 
                   json_agg(json_build_object('value', value, 'entry_date', entry_date) ORDER BY entry_date) AS data
            FROM {table}
            WHERE entry_date BETWEEN date_trunc('month', date %s) AND date_trunc('month', date %s)
            GROUP BY spi
            ORDER BY spi
            """
        cur.execute(query, (start_date, end_date))
        data = cur.fetchall()
        output = []
        for d in data:
            spi = spi_utils.get_spi_by_name(d[0])
            if spi:
                # Parse the JSON array and convert entry_date to datetime
                data_list = d[1]
                for entry in data_list:
                    if isinstance(entry['entry_date'], str):
                        entry['entry_date'] = datetime.strptime(entry['entry_date'], '%Y-%m-%d').date()
                                        
                output.append({
                    'id': spi['id'],
                    'spi_name': d[0],
                    'data': data_list,
                    'target_value': spi['target_value'],
                    'sign': spi['sign']
                })
            else :
                print(f"SPI {d[0]} not found in SPI list.")
        
        return output
    except Exception as e:
        print(f"Error fetching data from table {table}: {e}")
        return []
    finally:
        cur.close()