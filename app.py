import os
from flask import Flask, render_template, request
import mysql.connector
import os.path
import mysql.connector
from flask_mysqldb import MySQL
import boto3,botocore

app = Flask(__name__)
app.config['UPLOAD_FOLDER']="static/" #the path for images folder
path = './static/'

@app.route('/')
def main() :
   # con = mysql.connector.connect(host='',username='',password='',database='')
    con = mysql.connector.connect(host = 'localhost', user =  'admin', password = 'Iug1234#', database = 'aws')
    cur = con.cursor()
    num = cur.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'cddb'")
    


@app.route('/request', methods = ['GET','POST'])
def req():  
    if request.method == 'POST' :

        try:
            con=mysql.connector.connect(host='localhost',username='admin',password='Iug1234#',database='aws')
            #con = mysql.connector.connect(host = 'localhost', user = 'root', password = '', database = '')
            cur = con.cursor()    
            key = request.form['keyvalue']
            cur.execute("SELECT keyvalue FROM upload WHERE keyvalue = %s", [key])
            isNewKey = len(cur.fetchall()) == 0

            if not isNewKey :
                 name = s3.generate_presigned_url('get_object', Params = {'Bucket': "yourbucketname", 'Key': key}, ExpiresIn = 100)

            else :
                 return render_template('search.html', keyCheck = "key not found !")

            return render_template('search.html', user_image = name)

        except:
            return("error occur")

        finally:
            con.close()

    return render_template('search.html')

@app.route('/upload', methods = ['POST','GET'])
def upload():
    if request.method=='POST':
        key= request.form['keyvalue']
        con=mysql.connector.connect(host='localhost',username='admin',password='Iug1234#',database='aws')
       #con = mysql.connector.connect(host = 'localhost', user = 'root', password = '', database = '')
        cur = con.cursor()
        image = request.files['upload']

        if image.filename != '':
            filepath=os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
            image.save(filepath)
            print(filepath) #in static folder path
            cur.execute("SELECT keyvalue FROM upload WHERE keyvalue = %s", [key])
            isNewKey = len(cur.fetchall()) == 0
            # saveFile(path + image.filename, image.filename, imagePath)

            if(isNewKey) :
                s3.upload_file(Filename=filepath,Bucket=app.config["S3_BUCKET"],Key=key)
                cur.execute("INSERT INTO upload (keyvalue,image) VALUES(%s,%s)",(key,image.filename))
                #s3.upload_file(Filename=f"{imagePath}/{image.filename}",Bucket=app.config["S3_BUCKET"],Key=key)
                done = "Upload Successfully"
                
            else :
                s3.upload_file(Filename=filepath,Bucket=app.config["S3_BUCKET"], Key = key)
                cur.execute("UPDATE upload SET image = %s WHERE keyvalue = %s", (image.filename,key))
                done = "Update Successfully"

            con.commit()
            con.close()
            return render_template('image.html', done = done)

    return render_template('image.html')

@app.route('/list', methods = ['POST','GET'])
def keyList():
    if request.method == 'GET' :

        try:
            con=mysql.connector.connect(host='',username='admin',password='Iug1234#',database='aws')        
            #con = mysql.connector.connect(host = 'localhost', user = 'root', password = '1955', database = 'db')
            cur = con.cursor()
            cur.execute("SELECT keyvalue FROM upload")
            con.commit()

        except:
            return 'error'

        finally:
            return render_template('show.html', keys=[str(val[0]) for val in cur.fetchall()])

    return render_template('show.html')




if __name__ == '__main__':
    app.run('0.0.0.0',5000,debug=True)