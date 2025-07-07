from datetime import datetime
from src.utils.db import get_db_connection, retrieve_data_db
import calendar

spis = [
    { "id": 1, "spi_name": "Nr. of Safety Review Board perfomed", "target_value": 2, "mode": "sum"},
    { "id": 2, "spi_name": "% of Recommendations implemented (YTD)", "target_value": 95, "mode": "avg"},
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

def get_spi_by_id(spi_id):
    for spi in spis:
        if spi['id'] == spi_id:
            return spi
    return None

### DATA PROCESSING FUNCTIONS ###

def process_data(data, spi_id):
    """
    Processa i dati per calcolare le medie mobili e le somme YTD per un singolo SPI.
    """
    if not data:
        return {
            'values': [],
            'rolling_avg_sum': None,
            'ytd_avg_sum': None,
            'ytd_sum': None
        }

    # values_with_dates: list of dicts with value and entry_date, like in all_data
    values_with_dates = [{'value': d['value'], 'entry_date': d['entry_date']} for d in data]
    rolling_average = calc_12_months_rolling_average(get_spi_by_id(spi_id)['spi_name'], get_spi_by_id(spi_id)['mode'])
    ytd_average = calc_ytd_average(values_with_dates, get_spi_by_id(spi_id)['mode'])
    ytd_sum = calc_prev_year_sum(values_with_dates)
    return {
        'values': values_with_dates,
        'rolling_avg_sum': rolling_average,
        'ytd_avg_sum': ytd_average,
        'ytd_sum': ytd_sum
    }

def calc_12_months_rolling_average(spi_name, mode):
    """
    Calcola la media mobile su 12 mesi per i dati forniti.
    Args:
        data (list): Lista di valori numerici.
        mode (str): Modalità di calcolo della media ('avg' o 'sum').
    """
    conn = get_db_connection()
    cur = conn.cursor()

    dt = datetime.today()
    start_date = dt.replace(year=dt.year - 1, day=1)

    data = retrieve_data_db(spi_name, start_date, dt.replace(day=calendar.monthrange(dt.year, dt.month)[1]), cur)

    if not data:
        return 0
    
    if mode == 'avg':
        total = 0
        count = 0
        for value in data:
            if value is not None:
                total += value['value']
                count += 1
        return total / count if count > 0 else None
    elif mode == 'sum':
        total = 0
        count = 0
        for value in data:
            if value is not None:
                total += value['value']
                count += 1
        return total if count > 0 else None

def calc_ytd_average(data, mode):
    """
    Calcola la media YTD (Year To Date) per i dati forniti.
    Args:
        data (list): Lista di valori numerici.
        mode (str): Modalità di calcolo della media ('avg' o 'sum').
    """
    if not data:
        return None

    total = 0
    count = 0

    if mode == 'avg':
        for value in data:
            if value is not None and value['entry_date'].year == datetime.today().year:
                total += value['value']
                count += 1
        return total / count if count > 0 else None
    elif mode == 'sum':
        for value in data:
            if value is not None and value['entry_date'].year == datetime.today().year:
                total += value['value']
                count += 1
            else:
                total = 0
                count = 0
        return total / count if count > 0 else None

def calc_prev_year_sum(data):
    """
    Calcola la somma YTD (Year To Date) per i dati forniti.
    """
    if not data:
        return []

    total = 0

    for value in data:
        if value is not None and value['entry_date'].year == datetime.today().year-1:
            total += value

    return total if total > 0 else 0
