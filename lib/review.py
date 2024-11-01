from __init__ import CURSOR, CONN
from employee import Employee

class Review:

    # Dictionary of objects saved to the database.
    all = {}

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        if not isinstance(value, int):
            raise ValueError("Year must be an integer.")
        if value < 2000:
            raise ValueError("Year must be greater than or equal to 2000.")
        self._year = value

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        if not isinstance(value, str) or len(value) == 0:
            raise ValueError("Summary must be a non-empty string.")
        self._summary = value
    
    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, value):
        # Validate if the employee_id exists in the employees table
        sql = "SELECT COUNT(*) FROM employees WHERE id = ?"
        CURSOR.execute(sql, (value,))
        count = CURSOR.fetchone()[0]
        if count == 0:
            raise ValueError(f"Employee ID {value} does not exist.")
        self._employee_id = value

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year  # Triggers year validation
        self.summary = summary  # Triggers summary validation
        self.employee_id = employee_id

    def __repr__(self):
        return (
            f"<Review {self.id}: {self.year}, {self.summary}, "
            f"Employee: {self.employee_id}>"
        )

    @classmethod
    def create_table(cls):
        """ Create a new table to persist the attributes of Review instances """
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            year INT,
            summary TEXT,
            employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employees(id))
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """ Drop the table that persists Review instances """
        sql = """
            DROP TABLE IF EXISTS reviews;
        """
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        """ Insert a new row with the year, summary, and employee id values of the current Review object.
        Update object id attribute using the primary key value of the new row.
        Save the object in local dictionary using table row's PK as dictionary key."""
        sql = "INSERT INTO reviews (year, summary, employee_id) VALUES (?, ?, ?)"
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id))
        self.id = CURSOR.lastrowid  # Get the last inserted id
        Review.all[self.id] = self  # Save in local dictionary
        CONN.commit()

    @classmethod
    def create(cls, year, summary, employee_id):
        """ Initialize a new Review instance and save the object to the database. Return the new instance. """
        review = cls(year, summary, employee_id)
        review.save()  # Save the new instance to the database
        return review
   
    @classmethod
    def instance_from_db(cls, row):
        """Return a Review instance having the attribute values from the table row."""
        return cls(year=row[1], summary=row[2], employee_id=row[3], id=row[0])

    @classmethod
    def find_by_id(cls, id):
        """Return a Review instance having the attribute values from the table row."""
        sql = "SELECT * FROM reviews WHERE id = ?"
        CURSOR.execute(sql, (id,))
        row = CURSOR.fetchone()
        if row:
            return cls.instance_from_db(row)  # Return an instance if found
        return None  # Return None if not found

    def update(self):
        """Update the table row corresponding to the current Review instance."""
        sql = "UPDATE reviews SET year = ?, summary = ?, employee_id = ? WHERE id = ?"
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id, self.id))
        CONN.commit()

    def delete(self):
        """Delete the table row corresponding to the current Review instance,
        delete the dictionary entry, and reassign id attribute."""
        sql = "DELETE FROM reviews WHERE id = ?"
        CURSOR.execute(sql, (self.id,))
        del Review.all[self.id]  # Remove from local dictionary
        self.id = None  # Reset the id attribute
        CONN.commit()

    @classmethod
    def get_all(cls):
        """Return a list containing one Review instance per table row"""
        sql = "SELECT * FROM reviews"
        CURSOR.execute(sql)
        rows = CURSOR.fetchall()
        return [cls.instance_from_db(row) for row in rows]
