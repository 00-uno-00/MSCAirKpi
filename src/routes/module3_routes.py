from flask import Blueprint,render_template, request, redirect
from src.utils.db import get_db_connection
from datetime import datetime

module3_bp = Blueprint('module3', __name__)
#!!! IDS USED FOR IDENTIFICATION WITHIN THE TABLE NOT TO IDENTIFY SPI CLASS !!!
spis = [
    { "id": 1, "spi_name": "Nr. of Safety Review Board perfomed" },
    { "id": 2, "spi_name": "% of Recommendations implemented (YTD)" },
]
"""{ "id": 3, "spi_name": "Nr. of Emergency Response (ERP) drill performed" },
    { "id": 4, "spi_name": "Nr. of review of Safety Policy & Objectives" },
    { "id": 5, "spi_name": "Nr of Accident" },
    { "id": 6, "spi_name": "Nr of Serious Incident" },
    { "id": 7, "spi_name": "Nr of Operational Incidents (MOR)" },
    { "id": 8, "spi_name": "Nr of Technical Incidents (MOR)" },
    { "id": 9, "spi_name": "Nr of Safety Reports (Voluntary & confidential) per month" },
    { "id": 10, "spi_name": "Nr of Risk Assessments perfomed per month" },
    { "id": 11, "spi_name": "Nr of Hazards identified per month" },
    { "id": 12, "spi_name": "Nr of new Mitigations validated and implemented per month" },
    { "id": 13, "spi_name": "Nr. of Safety Bulletin published" },
    { "id": 14, "spi_name": "Nr. of Safety Flash published" },
    { "id": 15, "spi_name": "Nr. of Runway Incursions per month (Source: Safety report)" },
    { "id": 16, "spi_name": "Nr. of Wildlife Strike per month (Source: Safety report)" },
    { "id": 17, "spi_name": "Nr. of Level Bust per month (Source: Safety report)" },
    { "id": 18, "spi_name": "Nr. of High speed rejected take-off per month (Source: FDM)" },
    { "id": 19, "spi_name": "Nr. of Take-off with abnormal configuration per month (Source: Safety report)" },
    { "id": 20, "spi_name": "Nr of Insufficient take-off performance per month (Source: FDM)" },
    { "id": 21, "spi_name": "Nr of Unstable Approach per month (Source: FDM)" },
    { "id": 22, "spi_name": "Nr of Abnormal pitch at touchdown per month (Source: FDM)" },
    { "id": 23, "spi_name": "Nr. of Hard landing per month (Source: FDM)" },
    { "id": 24, "spi_name": "Nr of Aircraft lateral deviations at high speed on the ground (beginning of landing roll) per month (Source: FDM, LF010 heading change after nose down)" },
    { "id": 25, "spi_name": "Nr of Aircraft lateral deviations at high speed on the ground (till end of take-off roll) per month (Source: FDM, TF300 Takeoff heading range 100knt to rotation)" },
    { "id": 26, "spi_name": "Nr of Short rolling distance at landing per month (Source: FDM)" },
    { "id": 27, "spi_name": "Nr of (E)GPWS/TAWS Warning Trigger per month (Source: FDM)" },
    { "id": 28, "spi_name": "Nr of Pitch attitude high during take off per month (Source: FDM)" },
    { "id": 29, "spi_name": "Nr of Stall protection trigger per month (Source: FDM)" },
    { "id": 30, "spi_name": "Nr of Excessive speed per month (Source: FDM)" },
    { "id": 31, "spi_name": "Nr of Excessive vertical speed during climb per month (Source: FDM)" },
    { "id": 32, "spi_name": "Nr of Excessive vertical speed during descent per month (Source: FDM)" },
    { "id": 33, "spi_name": "Nr of Low go-around or rejected landing per month (Source: FDM)" },
    { "id": 34, "spi_name": "Nr of Reduced margin to manoeuvrability speed per month (Source: FDM)" },
    { "id": 35, "spi_name": "Nr of TCAS/ACAS Resolution Advisory per month (Source: FDM)" },
    { "id": 36, "spi_name": "Nr. of COM flights captured by FDM per month" },
    { "id": 37, "spi_name": "Nr of of fatigue report form received per month" }"""

@module3_bp.route('/module/3', methods=['GET', 'POST'])
def module_3():#!!!!ID USATO PER INDIVISUARE ISTANZA DI SPI NON CLASSE DI SPI!!!!
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        new_data = [] #buffer for one commit

        # Ottieni i dati dal modulo
        reference_month = datetime.today().month  # Usa il mese corrente come riferimento
        reference_year = datetime.today().year  # Usa l'anno corrente come riferimento
        for spi in spis:
            spi_id = spi['id']
            spi_value = request.form.get(f'{spi_id}')
            if spi_value is not None:
                try:
                    spi_value = int(spi_value)
                    if spi_value < 0:
                        return f"Invalid value for SPI {spi_id}: Value cannot be negative", 400
                    
                    # Aggiungi i dati al buffer
                    new_data.append((spi['spi_name'], spi_value, reference_month, reference_year))
                    # perform commit
                except ValueError:
                    return f"Invalid value for SPI {spi_id}", 400 #TODO add a popup
            else:
                spi_value = None
        # Commit all data in one go
        # Commit the update to the database
        commit_update_data(new_data, conn) 

        return redirect('/module/3')

    # Recupera i dati esistenti dal database
    if request.method == 'GET':
        # Use request.args for GET parameters
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')

        # Requires formatting or default values
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        else:
            start_date = datetime.today().replace(month=1, day=1)
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        else:
            end_date = datetime.today().replace(day=1)

        

        all_data = []
        for spi in spis:
            try:
                spi_data = retrieve_data_db(spi['spi_name'], datetime.date(start_date), datetime.date(end_date), cur)
                all_data.append({'id': spi['id'], 'spi_name': spi['spi_name'], 'values': spi_data})
                ###
                #id
                #spi_name
                #values
                #   | spi_data = ['value', 'entry_date']
                ###
            except Exception as e:
                print(f"Error fetching data for SPI {spi['spi_name']}: {e}")

        cur.close()
        conn.close()

        processed_data = []
        for spi in all_data:
            spi_values = spi['values']
            processed_spi = {
                'id': spi['id'],
                'spi_name': spi['spi_name'],
                'data': process_data(spi_values)
            }
            processed_data.append(processed_spi)

        return render_template('SAFETY.html', rows=processed_data, start_date_value=start_date.strftime('%Y-%m-%d'), end_date_value=end_date.strftime('%Y-%m-%d'))

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
            """, (spi_name, datetime(year, month, 1)))
            existing_record = cur.fetchone()
            if existing_record:
                # Update
                cur.execute("""
                    UPDATE safety_data SET spi = %s, entry_date = date_trunc('month', date %s)
                    value = %s
                    WHERE id = %s
                """, (spi_name,  existing_record[0])) #TODO ask if user wants to overwrite
            else:
                # Insert
                cur.execute("""
                    INSERT INTO safety_data (spi, value, entry_date)
                    VALUES (%s, %s, %s)
                """, (spi_name, value, datetime(year, month, 1)))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Error inserting data: {e}")
            return f"An error occurred: {e}", 500

def retrieve_data_db(spi_name, start_date, end_date, cur):
    """
    Recupera i dati dal database per un determinato SPI.
    """

    try:
        # Query per ottenere i dati per gli SPIs specificati 
        # N.B. selezionando un range di un solo mese un singolo mese verra' ritornato
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
    
def process_data(data):
    """
    Processa i dati per calcolare le medie mobili e le somme YTD.
    """
    if not data:
        return {
            'values': [],
            'rolling_average': [],
            'ytd_average': None,
            'ytd_sum': 0
        }

    # values_with_dates: list of dicts with value and entry_date, like in all_data
    values_with_dates = [{'value': d['value'], 'entry_date': d['entry_date']} for d in data]
    values = [d['value'] for d in data]
    rolling_average = calc_12_months_rolling_average(values)
    ytd_average = calc_ytd_average(values)
    ytd_sum = calc_ytd_sum(values)
    print(f"Processed data: {values_with_dates}, {rolling_average}, {ytd_average}, {ytd_sum}")
    return {
        'values': values_with_dates,
        #'rolling_average': rolling_average,
        'ytd_average': ytd_average,
        'ytd_sum': ytd_sum
    }

def calc_12_months_rolling_average(data):#TODO
    """
    Calcola la media mobile su 12 mesi per i dati forniti.
    """
    if not data:
        return []

    rolling_average = []
    for i in range(len(data)):
        if i < 11:
            # Non abbiamo abbastanza dati per calcolare la media mobile su 12 mesi
            rolling_average.append(None)
        else:
            # Calcola la media degli ultimi 12 mesi
            avg = sum(data[i-11:i+1]) / 12
            rolling_average.append(avg)

    return rolling_average

def calc_ytd_average(data):
    """
    Calcola la media YTD (Year To Date) per i dati forniti.
    """
    if not data:
        return None

    total = 0
    count = 0

    for value in data:
        if value is not None:
            total += value
            count += 1
        else:
            total = 0
            count = 0
    

    return total / count if count > 0 else None

def calc_ytd_sum(data):
    """
    Calcola la somma YTD (Year To Date) per i dati forniti.
    """
    if not data:
        return []

    total = 0

    for value in data:
        if value is not None:
            total += value

    return total if total > 0 else 0