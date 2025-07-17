from datetime import datetime
import src.utils.db as db
import calendar

spis = [
    { "id": 1, "spi_name": "Nr. of Safety Review Board perfomed", "target_value": [2], "mode": "sum", "table": "safety_data", "sign": "tozeroy" },
    { "id": 2, "spi_name": "% of Recommendations implemented (YTD)", "target_value": [95], "mode": "avg", "table": "safety_data", "sign": "tozeroy" },
    { "id": 3, "spi_name": "Nr. of Emergency Response (ERP) drill performed", "target_value": [1], "mode": "sum", "table": "safety_data", "sign": "tozeroy" },
    { "id": 4, "spi_name": "Nr. of review of Safety Policy & Objectives", "target_value": [1], "mode": "sum", "table": "safety_data", "sign": "tozeroy" },
    { "id": 5, "spi_name": "Nr of Accident", "target_value": [1], "mode": "sum", "table": "safety_data", "sign": "tozeroy" },
    { "id": 6, "spi_name": "Nr of Serious Incident", "target_value": [1], "mode": "avg", "table": "safety_data", "sign": "toinfy" },
    { "id": 7, "spi_name": "Nr of Operational Incidents (MOR)", "target_value": [1, 1.7, 2.4, 3.1], "mode": "avg", "table": "safety_data", "sign": "toinfy" },
    { "id": 8, "spi_name": "Nr of Technical Incidents (MOR)", "target_value": [1, 2.7, 3.4, 4.1], "mode": "avg", "table": "safety_data", "sign": "toinfy" },
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
    { "id": 37, "spi_name": "Nr of of fatigue report form received per month" },
    { "id": 38, "spi_name": "Flight time -- block hours (HH:MM) - COM flights only", "target_value": 5000, "mode": "sum", "table": "occ_flight_data", "sign": "tozeroy"},
    { "id": 39, "spi_name": "Flight cycles -- COM flights only", "target_value": 475, "mode": "sum", "table": "occ_flight_data", "sign": "tozeroy"},
    { "id": 40, "spi_name": "Flight hours per cycle --", "target_value": 8, "mode": "avg", "table": "occ_flight_data", "sign": "tozeroy"},
    { "id": 41, "spi_name": "Regularity --", "target_value": 95, "mode": "avg", "table": "occ_flight_data", "sign": "tozeroy"},
    { "id": 42, "spi_name": "Departure Punctuality --","target_value": 75, "mode": "avg", "table": "occ_flight_data", "sign": "tozeroy"},
    { "id": 43, "spi_name": "Aircraft daily utilization per month --", "target_value": 475, "mode": "avg", "table": "occ_flight_data", "sign": "tozeroy"},
]

def get_spi_by_id(spi_id):
    return spis[spi_id - 1] if 0 < spi_id <= len(spis) else None

def get_spi_by_name(spi_name):
    """
    Recupera lo SPI corrispondente al nome fornito.
    Args:
        spi_name (str): Il nome dello SPI da cercare.
    Returns:
        dict: Dizionario contenente i dettagli dello SPI, o None se non trovato.
    """
    if spi_name.__contains__('I-MSC'):
        start_index = spi_name.index('I-MSC') - 1
        end_index = start_index + 8
        spi_name = spi_name[:start_index] + spi_name[end_index:] 
        # very stupid and doesn't work for a/c names different than I-MSCX

    for spi in spis:
        if spi['spi_name'] == spi_name:
            return spi
    return None

### DATA PROCESSING FUNCTIONS ###

def process_data(data, spi_id, spi_name=None):
    """
    Processa i dati per calcolare le medie mobili e le somme YTD per un singolo SPI.
    Args:
        data (list): Lista di dizionari contenenti i dati SPI, con chiavi 'value' e 'entry_date'.
        spi_id (int): ID dello SPI per cui calcolare i dati.(se sum o avg)
    returns:
        dict: Dizionario contenente i valori elaborati, la media mobile su 12 mesi
    """
    if not data:
        return {
            'values': [],
            'rolling_avg_sum': None,
            'ytd_avg_sum': None,
            'ytd_sum': None
        }

    # values_with_dates: list of dicts with value and entry_date, like in all_data
    values_with_dates = [{'value': d['value'], 'entry_date': (d['entry_date'])} for d in data]
    rolling_average = calc_12_months_rolling_average(spi_name, get_spi_by_id(spi_id)['mode'], get_spi_by_id(spi_id)['table'])
    ytd_average = calc_ytd_average(values_with_dates, get_spi_by_id(spi_id)['mode'])
    ytd_sum = calc_prev_year_sum(spi_name, values_with_dates, get_spi_by_id(spi_id)['table'])
    return {
        'values': values_with_dates,
        'rolling_avg_sum': round(rolling_average, 3) if rolling_average is not None else 0,
        'ytd_avg_sum': round(ytd_average, 3) if ytd_average is not None else 0,
        'ytd_sum': round(ytd_sum, 3) if ytd_sum is not None else 0
    }

def calc_12_months_rolling_average(spi_name, mode, table):
    """
    Calcola la media mobile su 12 mesi per i dati forniti.
    Args:
        data (list): Lista di valori numerici.
        mode (str): Modalità di calcolo della media ('avg' o 'sum').
    """
    conn = db.get_db_connection()
    cur = conn.cursor()

    dt = datetime.today()
    start_date = dt.replace(year=dt.year - 1, day=1)

    data = db.get_data_spi(spi_name, start_date, end_date=dt.replace(day=calendar.monthrange(dt.year, dt.month)[1]), cur=cur, table=table)

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
        return total if count > 0 else None

def calc_prev_year_sum(spi_name, data, table):
    """
    Calcola la somma YTD (Year To Date) per i dati forniti.
    """
    if not data:
        return []

    # Look for oldest entry considered
    oldest_entry = min(entry['entry_date'] for entry in data if entry is not None)

    # Get the total for the year previous to the oldest entry
    db_conn = db.get_db_connection()
    cur = db_conn.cursor()
    start_date = oldest_entry.replace(year=oldest_entry.year - 1, month=1, day=1)
    end_date = oldest_entry.replace(year=oldest_entry.year - 1, month=12, day=31)
    data = db.get_data_spi(spi_name, start_date, end_date, cur, table)

    total = 0

    for value in data:
        if value is not None and value['entry_date'].year == datetime.today().year-1:
            total += value['value']

    return total if total > 0 else 0
