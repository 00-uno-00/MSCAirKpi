#DATABASE_URL = "postgresql://neondb_owner:npg_ibQE9C0cXNnZ@ep-aged-cake-a2x4wqvv-pooler.eu-central-1.aws.neon.tech/neondb?sslmode=require"

import psycopg2
from flask import g
from datetime import datetime
import os

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    #if 'db_conn' not in g:
    g.db_conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    return g.db_conn


def commit_update_data(updated_spis, conn):
    """
    Inserisce o aggiorna i dati nel database per una lista di spi.
    """
    cur = conn.cursor()

    for spi_name, value, month, year in updated_spis:
        # Inserisci i dati nel database
        try:
            # Check if record exists for safety_data
            cur.execute("""
                SELECT id FROM safety_data WHERE spi = %s AND entry_date = date_trunc('month', date %s)
            """, (spi_name, datetime(year, (month-1), 1)))
            existing_record = cur.fetchone()
            if existing_record:
                # Update
                cur.execute("""
                    UPDATE safety_data SET spi = %s, entry_date = date_trunc('month', date %s), value = %s
                    WHERE id = %s
                """, (spi_name, datetime(year, (month-1), 1), value, existing_record[0])) #TODO ask if user wants to overwrite
            else:
                # Insert
                cur.execute("""
                    INSERT INTO safety_data (spi, value, entry_date)
                    VALUES (%s, %s, %s)
                """, (spi_name, value, datetime(year, (month-1), 1)))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Error inserting data: {e}")
            return f"An error occurred: {e}", 500

def retrieve_data_db(spi_name, start_date, end_date, cur):
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
        cur.execute(
            """
            SELECT value, entry_date FROM safety_data
            WHERE spi = %s AND entry_date BETWEEN date_trunc('month', date %s) AND date_trunc('month', date %s)
            ORDER BY entry_date
            """,
            (spi_name, start_date, end_date)
        )
        data = cur.fetchall()
        # Return both value and entry_date as a list of dicts
        return [{'value': d[0], 'entry_date': d[1]} for d in data]
    except Exception as e:
        print(f"Error fetching data for SPI {spi_name}: {e}")
        return []