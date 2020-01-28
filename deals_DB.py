import sqlite3

_DB_PATH = "tslab_deals.db"

class TslabDB:
    """
    Class for creating and modifying SQLite database
    SQLite DB used for storing deals from TSLab
    """

    def __init__(self, db_path=_DB_PATH, new=False):
        """
        Create database or connect to existing one
        """
        self._conn = sqlite3.connect(db_path)
        self._curs = self._conn.cursor()
        if new or db_path == ':memory:':
            self._curs.execute("DROP TABLE IF EXISTS deals_raw")
            self._curs.execute("""CREATE TABLE deals_raw(
                Ticker VARCHAR(15),
                Date VARCHAR(30),
                DateTime INTEGER,
                Open DECIMAL(12,6),
                High DECIMAL(12,6),
                Low DECIMAL(12,6),
                Close DECIMAL(12,6),
                AdjClose DECIMAL(12,6),
                Volume INTEGER
                )""")
            self._curs.execute("DROP TABLE IF EXISTS deals")
            self._curs.execute("""CREATE TABLE deals(
                Script VARCHAR(15),
                Date VARCHAR(30),
                DateTime INTEGER,
                Symbol VARCHAR(5),
                
                High DECIMAL(12,6),
                Low DECIMAL(12,6),
                Close DECIMAL(12,6),
                AdjClose DECIMAL(12,6),
                Volume INTEGER
                )""")

    def load_csv(self, source, **kwargs):
        sep = kwargs.get('sep', ';')  # Columns separator
        dateformat = kwargs.get('dateformat', '%d.%m.%Y')  # Format of date in file

        df = pd.read_csv(source, sep=sep)
        df['Ticker'] = tickers  # ONLY ONE TICKER
        df['DateTime'] = pd.to_datetime(df['Date'], format=format)  # convert str date to datetime
        df['Date'] = df['DateTime'].apply(lambda s: dt.datetime.strftime(s, '%Y-%m-%d'))  # convert date to str
