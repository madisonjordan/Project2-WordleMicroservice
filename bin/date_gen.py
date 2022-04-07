def convert(value): 
    import datetime; 
    from datetime import date, timedelta; 
    start_day = date.today();
    day = (start_day + timedelta(days=(value))).strftime('%Y-%m-%d'); 
    return day;