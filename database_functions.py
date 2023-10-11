import sqlite3
import os
from loggerpy import *


class Database:

    def __init__(self, db_filename):
        logger = get_logger('create_signed_queue()')
        self.db_filename = db_filename

        if os.path.exists(self.db_filename):
            logger.info('database ' + self.db_filename + ' trovato')
        else:
            logger.info('database ' + self.db_filename + ' non trovato')

    # DATABASE FUNCTION

    def connect(self):
        self.db_conn = sqlite3.connect(self.db_filename)
        return self.db_conn

    def close_connection(self):
        self.db_conn.close()

    def create_database(self, query):
        self.connect()
        try:
            self.db_conn.cursor().executescript(query)
            self.db_conn.commit()
        except:
            raise

    # REQUESTS

    def clear_db(self):
        query = """DROP TABLE IF EXISTS tray_status ;"""
        try:
            self.db_conn.cursor().execute(query)
            self.db_conn.commit()
        except:
            raise

    def set_name(self, name):
        query = """INSERT INTO tray_status ("name")
                    VALUES (?);"""
        try:
            self.db_conn.cursor().execute(query, (name, ))
            self.db_conn.commit()
        except:
            raise

    def get_all_name(self):
        query = """SELECT name FROM tray_status;"""
        try:
            curs = self.db_conn.cursor()
            curs.execute(query)
            return curs.fetchall()
        except:
            raise

    def set_dieta(self, name, diet):
        query = """UPDATE tray_status SET diet=(?)
                    WHERE name=(?);"""
        try:
            self.db_conn.cursor().execute(query, (diet, name))
            self.db_conn.commit()
        except:
            raise

    def set_tray(self, name, status):
        query = """UPDATE tray_status SET tray=? WHERE name=?;"""
        try:
            self.db_conn.cursor().execute(query, (status, name))
            self.db_conn.commit()
        except:
            raise

    def get_tray(self, name):
        query = """SELECT tray FROM tray_status WHERE name=?;"""
        try:
            curs = self.db_conn.cursor()
            curs.execute(query, (name,))
            return curs.fetchone()
        except:
            raise
    
    def set_packed(self, name, status):
        query = """UPDATE tray_status SET packed=? WHERE name=?;"""
        try:
            self.db_conn.cursor().execute(query, (status, name))
            self.db_conn.commit()
        except:
            raise

    def get_packed(self, name):
        query = """SELECT packed FROM tray_status WHERE name=?;"""
        try:
            curs = self.db_conn.cursor()
            curs.execute(query, (name,))
            return curs.fetchone()
        except:
            raise

    # trayOrPacked = 0 -> tray
    # trayOrPacked = 1 -> packed
    def get_all(self, trayOrPacked, done):

        query = ""
        
        if trayOrPacked == 0:
            query = """SELECT name,diet FROM tray_status WHERE tray=? AND done=? AND valid=0;"""
        elif trayOrPacked == 1:
            query = """SELECT name,diet FROM tray_status WHERE packed=? AND done=? AND valid=0;"""
        try:
            curs = self.db_conn.cursor()
            curs.execute(query, (1, done))
            return curs.fetchall()
        except Exception as e:
            logger = get_logger('create_signed_queue()')
            logger.error(e)
            raise

    def set_done(self, name, status):
        query = """UPDATE tray_status SET done=(?)
                    WHERE name=(?);"""
        try:
            self.db_conn.cursor().execute(query, (status, name))
            self.db_conn.commit()
        except:
            raise

    def get_done(self, name):
        query = """SELECT done FROM tray_status WHERE name=(?);"""
        try:
            curs = self.db_conn.cursor()
            curs.execute(query, (name,))
            return curs.fetchone()
        except:
            raise

    def set_valid(self, name, value):
        query = """UPDATE tray_status SET valid=(?)
                    WHERE name=(?);"""
        try:
            self.db_conn.cursor().execute(query, (value, name))
            self.db_conn.commit()
        except:
            raise

    def get_valid(self, name):
        query = """SELECT valid FROM tray_status WHERE name=(?);"""
        try:
            curs = self.db_conn.cursor()
            curs.execute(query, (name,))
            return curs.fetchone()
        except:
            raise

    def create_clock(self, last_update):
        query = """INSERT INTO clock ("last_update")
                    VALUES (?);"""
        try:
            self.db_conn.cursor().execute(query, (last_update, ))
            self.db_conn.commit()
        except:
            raise

    def clear_clock(self):
        query = """DROP TABLE IF EXISTS clock ;"""
        try:
            self.db_conn.cursor().execute(query)
            self.db_conn.commit()
        except:
            raise

    def set_last_update(self, last_update):
        query = """UPDATE clock SET last_update=(?);"""
        try:
            self.db_conn.cursor().execute(query, (last_update,))
            self.db_conn.commit()
        except:
            raise

    def get_last_update(self):
        query = """SELECT last_update FROM clock"""
        try:
            curs = self.db_conn.cursor()
            curs.execute(query)
            return curs.fetchone()
        except:
            raise
