
from flask import Blueprint,render_template, request, redirect
from src.utils.db import get_db_connection

module3_bp = Blueprint('module3', __name__)

@module3_bp.route('/module/3', methods=['GET', 'POST'])
def module_3():
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        # Ottieni i dati dal modulo
        spi = request.form.get('id')
        reference_month = request.form.get('reference_month')  # Ora contiene solo il mese (es. "Jan")
        reference_year = request.form.get('reference_year')

        # Inserisci i dati nel database
        try:
            # Check if record exists for safety_data
            cur.execute("""
                SELECT id FROM safety_data WHERE spi = %s AND reference_month = %s AND reference_year = %s
            """, (spi, reference_month, reference_year))
            existing_record = cur.fetchone()
            if existing_record:
                # Update
                cur.execute("""
                    UPDATE safety_data SET spi = %s, reference_month = %s, reference_year = %s
                    WHERE id = %s
                """, (spi, reference_month, reference_year, existing_record[0]))
            else:
                # Insert
                cur.execute("""
                    INSERT INTO safety_data (spi, reference_month, reference_year)
                    VALUES (%s, %s, %s)
                """, (spi, reference_month, reference_year))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Error inserting data: {e}")
            return f"An error occurred: {e}", 500

        return redirect('/module/3')

    # Recupera i dati esistenti dal database
    try:
        cur.execute("""
            SELECT id, spi, reference_month, reference_year, created_at
            FROM safety_data
            ORDER BY created_at DESC
        """)
        safety_data = cur.fetchall()
    except Exception as e:
        print(f"Error fetching data: {e}")
        safety_data = []

    cur.close()
    return render_template('module_3.html', safety_data=safety_data)

def calc_12_months_rolling_average(data):
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
        return []

    ytd_average = []
    total = 0
    count = 0

    for value in data:
        if value is not None:
            total += value
            count += 1
            ytd_average.append(total / count)
        else:
            ytd_average.append(None)

    return ytd_average

def calc_ytd_sum(data):
    """
    Calcola la somma YTD (Year To Date) per i dati forniti.
    """
    if not data:
        return []

    ytd_sum = []
    total = 0

    for value in data:
        if value is not None:
            total += value
        ytd_sum.append(total)

    return ytd_sum