import sqlite3;
import json;

class SQLiteConnection:
    def __init__(self, path) -> None:
        self.con = sqlite3.connect(path, check_same_thread=False)
        print("\t** Db connected")
        self._createTables()
    
    
    def _createTables(self)-> None :
        cursor = self.con.cursor()

        # Creating VehiclePosition Table to store vehicle positions
        create_VehiclePos_table_sql = """
            CREATE TABLE IF NOT EXISTS VehiclePosition(
                id TEXT PRIMARY KEY     NOT NULL,
                lat TEXT                NOT NULL, 
                lng TEXT                NOT NULL
            );
        """

        cursor.execute(create_VehiclePos_table_sql)
        print("\t** Created Table VehiclePositions")

        #Populating test data for Vehicles Table
        f = open(".\\db\\test_vehicle_data.json", 'r');
        d = json.load(f)
        
        # Bulk insert to VehiclePostition or Ignore if exists.
        cursor.executemany('INSERT OR IGNORE INTO VehiclePosition (id, lat, lng)'
                           ' VALUES (:id, :lat, :lng)', d['vehicles'])
        
        #Creating Bookings Table
        create_Booking_table_sql = """
            CREATE TABLE IF NOT EXISTS Booking(
                id              INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                vehicle_id     TEXT UNIQUE,
                start_x         TEXT NOT NULL,
                start_y         TEXT NOT NULL,
                end_x           TEXT NOT NULL,
                end_y           TEXT NOT NULL
            )
        """
        cursor.execute(create_Booking_table_sql);
        print("\t** Created Table Bookings")

        self.con.commit()
        cursor.close()
    
    # For Executing sql via connection
    def _read(self, sql) -> sqlite3.Cursor:
        return self.con.execute(sql);

    # Method for formating sql rows.
    def _dict_factory(self, cursor:sqlite3.Cursor, row) -> dict:
        fields = [column[0] for column in cursor.description]
        return {key: value for key, value in zip(fields, row)}

    # Get Data from table VehiclePositions
    def getAllVehicles(self, exludeBooked = False) -> dict:
        sql = 'SELECT * FROM VehiclePosition'
        if exludeBooked:
            sql += " WHERE id not in (SELECT vehicle_id from Booking)"
        cursor = self._read(sql=sql)
        cursor.row_factory = self._dict_factory;
        return cursor.fetchall()

    def book(self, vehicleId, start_x, start_y, end_x, end_y):
        sql = '''INSERT INTO Booking(vehicle_id, start_x, start_y, end_x, end_y) 
                VALUES('{0}', '{1}', '{2}', '{3}', '{4}')'''.format(vehicleId, start_x, start_y, end_x, end_y)
        print(sql);
        cursor = self.con.cursor();
        cursor.execute(sql);
        self.con.commit();
        cursor.close();

    def resetDataState(self):
        self.con.execute('DELETE FROM Booking')
        self.con.execute('DELETE FROM VehiclePosition')
        self._createTables();
    
#Testing
if __name__ == '__main__':
    print(":::SQLiteConnection tests")
    con = SQLiteConnection('.\\test.sqlite3');
    v_pos = con.getAllVehicles();

    for i in v_pos:
        print(i)
