import sqlite3
import pandas as pd
import numpy as np
import datetime as dt

_DB_PATH = "tslab_deals.db"


_UNIX_START_DATE = dt.datetime(1970, 1, 1)  # Unix start date for INT date format in SQLite
# Return number of seconds from '1970-01-01'
def _unix_timedelta(d):
    return int((d - _UNIX_START_DATE).total_seconds())


class TslabDB:
    """
    Class for creating and modifying SQLite database
    SQLite DB used for storing deals from TSLab
    """

    #Static attribute
    _tslab2dataframe = {
        "Статус": "Status",
        "Позиция": "Position",
        "Лоты": "Size",
        "Изменение Лотов": "SizeChange",
        "Дата входа": "OpenDate",
        "Время входа": "OpenTime",
        "Цена входа": "Open",
        "Сигнал входа": "OpenSignal",
        "Дата выхода": "CloseDate",
        "Время выхода": "CloseTime",
        "Цена выхода": "Close",
        "Сигнал выхода": "CloseSignal",
        "Зафиксированная П/У": "PL",
        "П/У": "PL2",
        "Продолж. (баров)": "Bars",
        "Общий П/У": "AccPL",
        "MAE": "MAE",
        "MFE": "MFE"
    }

    _dataframe2sqlite = ["AlgoTicker", "Position", "Size", "OpenDateTime", "OpenSignal", "Open",
                        "CloseDateTime", "CloseSignal", "Close", "PL", "Bars", "AccPL",
                        "MAE", "MFE", "LogPL", "LogMAE", "LogMFE"]


    def __init__(self, db_path=_DB_PATH, new=False):
        """
        Create database or connect to existing one
        """
        self._conn = sqlite3.connect(db_path)
        self._curs = self._conn.cursor()
        if new or db_path == ':memory:':
            self._curs.execute("DROP TABLE IF EXISTS deals")
            self._curs.execute("""CREATE TABLE deals(
                AlgoTicker VARCHAR(15),
                Position VARCHAR(2),
                Size INTEGER,
                OpenDateTime INTEGER,
                Open DECIMAL(12,6),
                OpenSignal VARCHAR(10)
                CloseDateTime INTEGER,
                Close DECIMAL(12,6),
                CloseSignal VARCHAR(10),                 
                PL DECIMAL(9,2),
                Bars INTEGER,
                AccPL DECIMAL(9,2),
                MAE DECIMAL(9,2),
                MFE DECIMAL(9,2),
                LogPL DECIMAL(12,6),
                LogMAE DECIMAL(12,6),
                LogMFE DECIMAL(12,6)
                )""")


    def load_csv(self, source, **kwargs):
        sep = kwargs.get('sep', ';')  # Columns separator, default is ';'
        dtformat = kwargs.get('dtformat', '%d.%m.%Y %H:%M:%S')  # Date format

        df = pd.read_csv(source, sep=sep)  # Read deals file
        df.drop(columns=set(df.columns)-set(TslabDB._tslab2dataframe), inplace=True)
        df.rename(columns=TslabDB._tslab2dataframe, inplace=True)

        df['AlgoTicker'] = source[source.find('\\')+1: source.find('.csv')]  # ONLY ONE TICKER
        df['Position'].apply(lambda s: 'B' if s=='Длинная' else 'S' if s=='Короткая' else '')

        # Unix datetime for Open
        df['OpenDateTime'] = list(map(lambda a, b: f"{a} {b}", df['OpenDate'], df['OpenTime']))
        df['OpenDateTime'] = pd.to_datetime(df['OpenDateTime'], format=dtformat)
        df['OpenDateTime'] = df['OpenDateTime'].apply(_unix_timedelta)

        # Unix datetime for Close
        df['CloseDateTime'] = list(map(lambda a, b: f"{a} {b}", df['CloseDate'], df['CloseTime']))
        df['CloseDateTime'] = pd.to_datetime(df['CloseDateTime'], format=dtformat)
        df['CloseDateTime'] = df['CloseDateTime'].apply(_unix_timedelta)

        df['LogPL'] = np.log(df['Close']/df['Open'])
        df['LogMAE'] = np.log(1+df['MAE']/df['Open'])
        df['LogMFE'] = np.log(1+df['MFE']/df['Open'])

        return df[TslabDB._dataframe2sqlite][df['Status']=='NoError']


    def df2sqlite(self, df):
        pass
