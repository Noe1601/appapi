from fastapi import FastAPI
import pymysql
import secrets
import os,binascii
import smtplib
from starlette.middleware.cors import CORSMiddleware

db = pymysql.connect(
    host="database-1.ctjuph1brpoe.us-west-1.rds.amazonaws.com",
    user="admin",
    passwd="12345678",
    database="prueba",
    port=3306
)

print(db)

app = FastAPI()
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])


def InsertUser(afiliado,nombre,usuario,genero,fecha,pais,ciudad,estado,telefono,email,imagen,password):
    try:
        token = secrets.token_hex(3)
        conexion = db
        cursor = conexion.cursor()
        sql = """INSERT INTO users(token,token_father,name,username,genre,birthdate,country,city,state,telephone,email,image,password,id_kind,id_ranks,fecha)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW()) """
        campos = (token,afiliado,nombre,usuario,genero,fecha,pais,ciudad,estado,telefono,email,imagen,password,2,1)
        cursor.execute(sql,campos)
        conexion.commit()
        return 1
    except:
        return 0

def InicioSesion(email,password):
    try:
        conexion = db
        cursor = conexion.cursor()
        sql = """SELECT * FROM users WHERE email = '%s' AND password = '%s' AND estatus = 'activo' """
        campos = (email,password)
        cursor.execute(sql,campos)
        cursor.fetchone()
        conexion.commit()
        return 1
    except:
        return 0

@app.get("/")
def Raiz():
    return "Bienvenidos a Noe Medina API"


# Registro de usuarios

@app.get("/usuarios/{afiliado}/{nombre}/{usuario}/{sexo}/{fecha}/{pais}/{ciudad}/{estado}/{telefono}/{email}/{imagen}/{password}")
def Usuarios(afiliado:str,nombre:str,usuario:str,sexo:str,fecha:str,pais:str,ciudad:str,estado:str,telefono:str,email:str,imagen:str,password:str):
    try:
        consulta = InsertUser(afiliado,nombre,usuario,sexo,fecha,pais,ciudad,estado,telefono,email,imagen,password)
        if(consulta != 0):
            return{
                "Afiliado": afiliado,
                "Nombre": nombre,
                "Usuario": usuario,
                "Sexo": sexo,
                "Fecha": fecha,
                "Pais": pais,
                "Ciudad": ciudad,
                "Estado": estado,
                "Telefono": telefono,
                "Correo": email
            }
        else:
            return "No se pudo insertar este usuario"

    except:
        return "ERROR DE API"


@app.get("/logIn/{email},{password}")
def logIn(email:str,password:str):
    try:
        # connection=Connection()
        connection= db
        _cursor=connection.cursor()
        sql="""SELECT * FROM users WHERE email = %s AND password = %s"""
        values=(email,password)
        _cursor.execute(sql,values)
        _result=_cursor.fetchone()
        _result=list(_result)
        return dict(Email=email,Password=password)
    except:
        return dict(Error="Error in DataBase.")


@app.get("/blog/{title},{date},{content},{usuario}")
def blog(title:str,date:str,content:str,usuario:str):
    try:
        # connection=Connection()
        connection= db
        _cursor=connection.cursor()
        sql="INSERT INTO blog1 (title,fecha,content,usuario) VALUES (%s,%s,%s,%s)"
        values=(title,date,content,usuario)
        _cursor.execute(sql,values)
        connection.commit()
        return dict(Title=title,Date=date,Content=content,User=usuario)
    except:
        return dict(Error="Error in DataBase.")

@app.get("/updateUser/{token},{name},{username},{genre},{birthdate},{country},{city},{state},{telephone},{email},{password}")
def updateUser(token:str,name:str,username:str,genre:str,birthdate:str,country:str,city:str,state:str,telephone:str,email:str,password:str):
    try:
        # connection = Connection()
        connection= db
        _cursor = connection.cursor()
        sql = """UPDATE users SET name=%s,username=%s,genre=%s,birthdate=%s,country=%s,city=%s,state=%s,telephone=%s,email=%s,password=%s WHERE token=%s AND status='activo'"""
        values = (name, username, genre, birthdate, country, city, state, telephone, email, password, token)
        _cursor.execute(sql, values)
        connection.commit()
        return dict(Token=token,Name=name,Username=username,Genre=genre,Birthdate=birthdate,Country=country,City=city,State=state,Telephone=telephone,Email=email,Password=password)
    except:
        return dict(Error="Error in DataBase.")

@app.get("/sendCode/{correo}/{codigo}")
def sendCode(correo:str,codigo:str):
    try:
        token  = secrets.token_hex(4)
        subject = 'Codigo de confirmacion'
        message = "Este es su codigo de confirmacion " + str(token)
        message = 'Subject: {}\n\n{}'.format(subject, message)
        server = smtplib.SMTP('smtp.gmail.com',587)
        server.starttls()
        server.login('pruebafuture16@gmail.com','noemedina') 
        server.sendmail('pruebafuture16@gmail.com',{correo}, message)
        server.quit()
        exito = "Correo enviado exitosamente!"
        connection = db
        cursor = connection.cursor()
        sql = """INSERT INTO tokens(codigo,usuario_identificador) VALUES (%s, (SELECT id FROM users WHERE token = %s))"""
        campos = (token,codigo)
        cursor.execute(sql,campos)
        connection.commit()
        return{
            "Codigo": token,
            "Mensaje": exito
        }
    except:
        return dict(Error="Error")

@app.get("/changePassword/{token},{password}")
def sendPassword(token:str,password:str):
    try:
        # connection = Connection()
        connection= db
        _cursor = connection.cursor()
        sql = """UPDATE users u JOIN tokens t ON t.usuario_identificador = u.id SET u.password = %s WHERE t.codigo = %s"""
        values = (password,token)
        _cursor.execute(sql,values)
        connection.commit()
        return dict(Token=token,Password=password)
    except:
        return dict(Error="Error")

@app.get("/allUsers")
def allUsers():
    try:
        global counter
        # connection = Connection()
        connection= db
        _cursor = connection.cursor()
        sql = """SELECT * FROM users WHERE estatus = 'activo'"""
        _cursor.execute(sql)
        _result=_cursor.fetchall()
        dictionary={}
        _dictionary={}
        counter=0
        for k in _result:
            _dictionary=dict(ID=k[0],Token=k[1],Father=k[2],Name=k[3],Username=k[4],Genre=k[5],Birthdate=k[6],Country=k[7],City=k[8],State=k[9],Telephone=k[10],Email=k[11],Image=k[12],Estatus=k[17])
            dictionary.update({f"User{counter}": _dictionary})
            counter+=1
        return dict(Users=dictionary)
    except:
        return dict(Error="Error")


@app.get("/affiliates/{token}")
def affiliates(token:str):
    try:
        global counter
        # connection = Connection()
        connection= db
        _cursor = connection.cursor()
        sql = f"""SELECT * FROM users WHERE token_father = '{token}'"""
        _cursor.execute(sql)
        _result=_cursor.fetchall()
        dictionary={}
        _dictionary={}
        counter=0
        for k in _result:
            _dictionary=dict(ID=k[0],Token=k[1],Name=k[3],Username=k[4],Genre=k[5],Birthdate=k[6],Country=k[7],City=k[8],State=k[9],Telephone=k[10],Email=k[11],Image=k[12],Estatus=k[17])
            dictionary.update({f"User{counter}": _dictionary})
            counter+=1
        return dict(Users=dictionary)
    except:
        return dict(Error="Error")

@app.get("/user/{token}")
def user(token:str):
    try:
        connection = db
        cursor = connection.cursor()
        sql  = f"""SELECT * FROM users WHERE token = '{token}'"""
        cursor.execute(sql)
        result = cursor.fetchall()
        dictionary={}
        _dictionary={}
        counter=0
        for k in result:
            _dictionary=dict(ID=k[0],Token=k[1],Name=k[3],Username=k[4],Genre=k[5],Birthdate=k[6],Country=k[7],City=k[8],State=k[9],Telephone=k[10],Email=k[11],Image=k[12],Estatus=k[17])
            dictionary.update({f"User{counter}": _dictionary})
            counter+=1
            return dict(Users=dictionary)
    except:
        return dict(Error="Error")


@app.get("/BlogArticles")
def BlogArticles():
    try:
        global counter
        # connection = Connection()
        connection= db
        _cursor = connection.cursor()
        sql = """SELECT * FROM blog1"""
        _cursor.execute(sql)
        _result=_cursor.fetchall()
        dictionary={}
        _dictionary={}
        counter=0
        for k in _result:
            _dictionary=dict(ID=k[0],TITLE=k[1],DATE=k[2],COMENTARIO=k[3],USER=k[4])
            dictionary.update({f"Articles{counter}": _dictionary})
            counter+=1
        return dict(Blog=dictionary)
    except:
        return dict(Error="Error")

@app.get("/basico/{codigo}")
def Basico(codigo:str):
    try:
        connection = db
        cursor = connection.cursor()
        sql = """UPDATE basico SET codigo = %s"""
        campos = (codigo)
        cursor.execute(sql,campos)
        connection.commit()
        return dict(Codigo=codigo)
    except:
        return dict(Error="Error")

@app.get("/intermedio/{codigo}")
def Intermedio(codigo:str):
    try:
        connection = db
        cursor = connection.cursor()
        sql = """UPDATE intermedio SET codigo = %s"""
        campos = (codigo)
        cursor.execute(sql,campos)
        connection.commit()
        return dict(Codigo=codigo)
    except:
        return dict(Error="Error")

@app.get("/avanzado/{codigo}")
def Avanzado(codigo:str):
    try:
        connection = db
        cursor = connection.cursor()
        sql = """UPDATE avanzado SET codigo = %s"""
        campos = (codigo)
        cursor.execute(sql,campos)
        connection.commit()
        return dict(Codigo=codigo)
    except:
        return dict(Error="Error")

def SelectUser(id):
    try:
        connection = db
        myCursor = connection.cursor()
        sql = f"""SELECT * FROM users WHERE token = '{id}'"""
        myCursor.execute(sql)
        myResult = myCursor.fetchone()
        return [1, myResult]
    except:
        return [0]


@app.get("/selectUser/{codigo}")
def _SelectUser(codigo:str):
    try:
        connection = SelectUser(codigo)
        if(connection[0] != 0):
            array = connection[1]
            return{
                "ID": array[0],
                "Token": array[1],
                "Nombre": array[3],
                "Usuario": array[4],
                "Genero": array[5],
                "Fecha": array[6],
                "Pais": array[7],
                "Ciudad": array[8],
                "Estado": array[9],
                "Telefono": array[10],
                "Correo": array[11],
                "Estatus": array[17]
            }
        else:
            return "Error in database"
    except:
        return "Este usuario no existe"

@app.get("/ClaveAdministrador/{clave}")
def Administrador(clave:str):
    try: 
        connection = db
        cursor = connection.cursor()
        sql = """UPDATE administrador SET codigo = %s """
        campos = (clave)
        cursor.execute(sql,campos)
        connection.commit()
        return{
            "Clave": clave
        }
    except:
        return "Fallo actualizacion de clave"


def SelectToken(id):
    try:
        connection = db
        myCursor = connection.cursor()
        sql = f"""SELECT * FROM users WHERE username = '{id}'"""
        myCursor.execute(sql)
        myResult = myCursor.fetchone()
        return [1, myResult]
    except:
        return [0]

@app.get("/ReturnToken/{username}")
def ReturnToken(username:str):
    try:
        connection = SelectToken(username)
        if(connection[0] != 0):
            array = connection[1]
            return{
                "Token": array[1]
            }
    except:
        return "Fallo la busqueda"

def Cantidad():
    try:
        connection = db
        cursor = connection.cursor()
        sql = """SELECT COUNT(*) FROM users"""
        cursor.execute(sql)
        cursor.fetchall()
        return [1]
    except:
        return [0]


@app.get("/CantidadUsers")
def CantidadUsers():
    try:
        connection = db
        cursor = connection.cursor()
        sql = """SELECT COUNT(*) FROM users WHERE estatus='activo'"""
        cursor.execute(sql)
        result = cursor.fetchall()
        dictionary = {}
        dictionary.update({f"Cantidad": result})
        return dictionary
    except:
        return 0

@app.get("/cantidadAfiliados/{token}")
def cantidad(token:str):
    try:
        connection = db
        cursor = connection.cursor()
        sql = f"""SELECT COUNT(*) FROM users WHERE token_father = '{token}'"""
        cursor.execute(sql)
        result = cursor.fetchall()
        dictionary = {}
        dictionary.update({f"Afiliados": result })
        return dictionary
    except:
        return 0


@app.get("/codigobasico/{codigo}")
def CodigoBasico(codigo:str):
    try:
        global counter
        connection = db
        cursor = connection.cursor()
        sql = f"""SELECT * FROM basico WHERE codigo = '{codigo}'"""
        cursor.execute(sql)
        result = cursor.fetchall()
        dictionary = {}
        dictionary.update({f"Basico": result})
        return dictionary
    except:
        return "Este no es el codigo"

@app.get("/codigointermedio/{codigo}")
def CodigoIntermedio(codigo:str):
    try:
        global counter
        connection = db
        cursor = connection.cursor()
        sql = f"""SELECT * FROM intermedio WHERE codigo = '{codigo}'"""
        cursor.execute(sql)
        result = cursor.fetchall()
        dictionary = {}
        dictionary.update({f"Intermedio": result})
        return dictionary
    except:
        return "Este no es el codigo"

@app.get("/codigoavanzado/{codigo}")
def CodigoAvanzado(codigo:str):
    try:
        global counter
        connection = db
        cursor = connection.cursor()
        sql = f"""SELECT * FROM avanzado WHERE codigo = '{codigo}'"""
        cursor.execute(sql)
        result = cursor.fetchall()
        dictionary = {}
        dictionary.update({f"Avanzado": result})
        return dictionary
    except:
        return "Este no es el codigo"

# DELETE FROM users WHERE fecha <= DATE_SUB(CURDATE(), INTERVAL 4 MONTH);

@app.get("/delete4moth")
def DeleteUser4Month():
    try:
        connection = db
        cursor = connection.cursor()
        sql = """DELETE FROM users WHERE fecha <= DATE_SUB(CURDATE(), INTERVAL 4 MONTH)"""
        cursor.execute(sql)
        connection.commit()
        return "Todo correcto"
    except:
        return "Fallo"

@app.get("/activar/{nombre}")
def activar(nombre:str):
    try:
        connection = db
        cursor = connection.cursor()
        sql = f"""UPDATE users SET estatus = 'activo' WHERE name='{nombre}'"""
        cursor.execute(sql)
        connection.commit()
        return {"Message": "Se activaron usuarios"}
    except:
        return "Hubo un fallo"

@app.get("/desactivar/{nombre}")
def desactivar(nombre:str):
    try:
        connection = db
        cursor = connection.cursor()
        sql = f"""UPDATE users SET estatus = 'inactivo' WHERE name='{nombre}'"""
        cursor.execute(sql)
        connection.commit()
        return {"Message":"Se desactivaron usuarios"}
    except:
        return "Hubo un fallo"