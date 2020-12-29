from flask import Flask, render_template,request,jsonify,Blueprint
from flask_cors import CORS,cross_origin
import sqlite3 as sql
import json
import numpy as np
from flask.logging import create_logger


app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
LOG = create_logger(app)


cors = CORS(app,support_credentials=True)

def convertDictToList(data,last_row_id):
    result = []
    for l in data:
        result.append((last_row_id,l.get('value')))
    return result

def packArgumentsForQuery(data,last_row_id):
    result = []
    for l in data:
        result.append((last_row_id,l))
    return result

def deleteNoteHighlights(id):
    try:
        with sql.connect("database.db") as con:
            cursor = con.cursor() 
            cursor.execute('DELETE FROM HIGHLIGHTS WHERE note_id=?',[id])
            con.commit()
    except sql.Error as er:
        print(er)
        LOG.error('Error on delete highlights')
    finally:
        con.close()
        LOG.debug("Highlights deleted successfully")

def deleteNoteFeatures(id):
    try:
        with sql.connect("database.db") as con:
            cursor = con.cursor() 
            cursor.execute('DELETE FROM FEATURES WHERE note_id=?',[id])
            con.commit()
    except sql.Error as er:
        print(er)
        LOG.error("Error on delete features")
    finally:
        con.close()
        LOG.debug("Features deleted successfully")

def deleteNoteBugFixes(id):
    try:
        with sql.connect("database.db") as con:
            cursor = con.cursor() 
            cursor.execute('DELETE FROM BUG_FIXES WHERE note_id=?',[id])
            con.commit()
    except sql.Error as er:
        print(er)
        LOG.error('Error on delete bug fixes')
    finally:
        con.close()
        LOG.debug("Bug fixes deleted successfully")

@app.route('/get_note_record', methods=['GET'])
def get_note_record():
    note_id = request.args.get('id')
    if request.method == 'GET':
        try:
            with sql.connect("database.db") as con:
                con.row_factory = dict_factory
                cur = con.cursor()
                cur.execute("select * from release_notes where id=?",(note_id))
                row = cur.fetchone()
                row["content"] = get_note_extended_info(note_id)
                return jsonify(row)
        except sql.Error as er:
            print(er)
            LOG.error('Error on getting note record')
            return 'Error on getting record', 400 
        finally:
            con.close()
            LOG.error('Record retrieved successfully')


def insert_highlights(data,id,flag=False):
    try:
        deleteNoteHighlights(id)
        with sql.connect("database.db") as con:
            cursor = con.cursor() 
            if flag: data = convertDictToList(data,id)
            else:data = packArgumentsForQuery(data,id)
            cursor.executemany('INSERT INTO HIGHLIGHTS (note_id,highlight) VALUES(?,?)',data)
            con.commit()
    except sql.Error as er:
        print(er)
        LOG.error("Error on inserting highlights")
    finally:
        con.close()
        LOG.debug("Highlights added successfully")

def insert_features(data,id,flag = False):
    try:
        deleteNoteFeatures(id)
        with sql.connect("database.db") as con:
            cursor = con.cursor() 
            if flag: data = convertDictToList(data,id)
            else:data = packArgumentsForQuery(data,id)
            cursor.executemany('INSERT INTO FEATURES (note_id,feature) VALUES(?,?)',data)
            con.commit()
    except sql.Error as er:
        print(er)
        LOG.error("Error on inserting features")
    finally:
        con.close()
        LOG.debug("Features added successfully")

def insert_bug_fixes(data,id,flag=False):
    try:
        deleteNoteBugFixes(id)
        with sql.connect("database.db") as con:
            cursor = con.cursor() 
            if flag: data = convertDictToList(data,id)
            else:data = packArgumentsForQuery(data,id)
            cursor.executemany('INSERT INTO BUG_FIXES (note_id,bug_fix) VALUES(?,?)',data)
            con.commit()
            msg = "Bug fixes added successfully!"
    except sql.Error as er:
        print(er)
        LOG.error("Error on inserting bug fixes")
    finally:
        con.close()
        LOG.debug("Bug fixes added successfully")


@app.route('/add_note_record', methods=['POST','GET'])
def add_note_record():
    if request.method == 'POST':
        try:
            note_highlights = request.json['highlights']
            note_features = request.json['features']
            note_bug_fixes = request.json['bug_fixes']
            date = request.json['date']
            author = request.json['author']
            version = request.json['version']
            with sql.connect("database.db") as con:
                cursor = con.cursor() 
                cursor.execute("INSERT INTO release_notes (version,date,author) VALUES (?,?,?)",(version,date,author ))
                con.commit()
                insert_highlights(note_highlights,cursor.lastrowid,True)
                insert_features(note_features,cursor.lastrowid,True)
                insert_bug_fixes(note_bug_fixes,cursor.lastrowid,True)
        except:
            con.rollback()
            LOG.error("Error on inserting new release note record")
            return "Error on insertion",400
        finally:
            con.close()
            LOG.debug("Release note record added succesfully")
            return "Record successfully added",200


@app.route('/delete_record', methods=['GET'])
def delete_record():
    note_id = request.args.get('id')
    if request.method == 'GET':
        try:
            with sql.connect("database.db") as con:
                cur = con.cursor()
                cur.execute("delete from release_notes where id=?",(note_id))
                con.commit()
        except:
            con.rollback()
            LOG.error('Error on deleting all records')
            return 'Error on deleting all records', 400 
        finally:
            con.close()
            LOG.debug('Record deleted successfully')
            return 'Record successfully deleted', 200



@app.route('/modify_record', methods=['POST'])
def modify_record():
    if request.method == 'POST':
        try:
            print(request.json)
            id = request.json['id']
            date = request.json['date']
            note_highlights = list(filter(None, request.json['highlights']))
            note_features = list(filter(None, request.json['features']))
            note_bug_fixes = list(filter(None,request.json['bug_fixes']))
            author = request.json['author']
            with sql.connect("database.db") as con:
                cursor = con.cursor() 
                cursor.execute("UPDATE release_notes SET date=?, author=? WHERE id =?",(date,author,id))
                con.commit()
                insert_highlights(note_highlights,id)
                insert_features(note_features,id)
                insert_bug_fixes(note_bug_fixes,id)
        except sql.Error as er:
            print(er)
            con.rollback()
            LOG.debug('Error on updating record')
            return "Error on updating record",400
        finally:
            con.close()
            LOG.debug('Record modified successfully')
            return "Record successfully updated!",200

#Functions
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def get_raw_records():
    try:
        with sql.connect("database.db") as con:
                con.row_factory = dict_factory
                cur = con.cursor()
                cur.execute("select * from release_notes")
                sql_data = cur.fetchall()
    except sql.Error as er:
        print(er)
        LOG.error('Error on getting all raw notes records')
    finally:
        con.close()
        LOG.debug('All raw notes records retrieved successfully')
        return jsonify(sql_data)



def get_note_extended_info(note_id):
    try:
        with sql.connect("database.db") as con:
            cur = con.cursor()
            x = {}
            cur.execute("select highlight from HIGHLIGHTS where note_id=?",(note_id))
            x['highlights'] = convert_data(cur.fetchall())
            cur.execute("select feature from FEATURES where note_id=?",(note_id))
            x['features'] =  convert_data(cur.fetchall())
            cur.execute("select bug_fix from BUG_FIXES where note_id=?",(note_id))
            x['bug_fixes'] =  convert_data(cur.fetchall())
    except sql.Error as e:
        print(e)
        LOG.error('Error on getting record additional info')
        return 'Error on getting record', 400 
    finally:
        con.close()
        LOG.debug('Record additional info retrieved successfully')
        return x

#End-Points
@app.route('/get_all_records', methods=['GET'])
def get_all_records():
    if request.method == 'GET':
        try:
            sql_data = get_raw_records().json
            for row in sql_data:
                note_id = row['id']
                with sql.connect("database.db") as con:
                    cur = con.cursor()
                    x = {}
                    cur.execute("select highlight from HIGHLIGHTS where note_id=?",[note_id])
                    x['highlights'] = convert_data(cur.fetchall())
                    cur.execute("select feature from FEATURES where note_id=?",[note_id])
                    x['features'] =  convert_data(cur.fetchall())
                    cur.execute("select bug_fix from BUG_FIXES where note_id=?",[note_id])
                    x['bug_fixes'] =  convert_data(cur.fetchall())
                row["content"] = x
            return jsonify(sql_data)
        except sql.Error as er:
            print('SQLite error: %s' % (' '.join(er.args)))
            print("Exception class is: ", er.__class__)
            LOG.error('Error on getting all note records')
        finally:
            con.close()
            LOG.debug('Records retrieved successfully')

        

def convert_data(data):
    res=[]
    for d in data:
        res.append(d[0])
    return res

if __name__ == "__main__":
    print("app.py is running on local host")
    app.run(debug=True)