from flask import Flask,render_template,request,redirect,url_for
from pymysql import connections
import user
app = Flask(__name__)


db_con=connections.Connection(
    host="database-3.cujavq47oj5k.us-east-1.rds.amazonaws.com",
    port=3306,
    user="admin",
    password="12345678",
    db="book_store")

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register")
def registor():
    return render_template("form.html")

@app.route("/login")
def login():
    return render_template("form2.html")

@app.route("/Admin")
def adminlogin():
    return render_template("Admin.html")


@app.route('/login', methods=['POST'])
def Authenticate():
    username=request.form['mailid']
    password=request.form['pass']
    cursor=db_con.cursor()
    cursor.execute("select usernames,passwords from Credentials where usernames='" + username + "' and passwords='" + password + "'")
    data=cursor.fetchone()
    if data is None:
        return render_template("form2.html",alert1="Username or Password is Invalid")
    else:
        user.user=username
        return redirect(url_for("bookdetails"))
    
@app.route("/register",methods=['POST'])
def adduser():
    fname=request.form['fname']
    lname=request.form['lname']
    email=request.form['mailid']
    passw=request.form['pass']
    ph=request.form['Pnmber']
    sname=request.form['sname']
    pcode=request.form['pcode']
    country=request.form['country']
    cursor = db_con.cursor()
    sql = "INSERT INTO Customers (firstName, lastName, email, phoneNumber, streetName, postalCode, country) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    val = (fname,lname,email,ph,sname,pcode,country)
    cursor.execute(sql, val)
    cursor.execute("select customerID from Customers where email='"+email+"'")
    userid=cursor.fetchone()
    sql2 = "INSERT INTO Credentials (customerID,usernames,passwords) VALUES (%s, %s, %s)"
    val2 =(userid,email,passw)
    cursor.execute(sql2,val2)
    db_con.commit()
    return render_template("form2.html")

@app.route('/profile')
def details():
    cursor=db_con.cursor()
    cursor.execute("select * from Customers where email='"+user.user+"'")
    res=cursor.fetchone()
    cursor.execute("select o.orderID,o.bookID,b.bookName,o.orderDate,b.price from Orders o inner join Books b on o.bookID=b.bookID where customerID='%d'"%(res[0]))
    res1=cursor.fetchall()
    return render_template("userdetails.html",datas=res,datas1=res1)

@app.route('/orders/<string:id>')
def orders(id):
    cursor=db_con.cursor()
    cursor.execute("select * from Books where bookID='"+id+"'")
    ordres=cursor.fetchone()
    return render_template("orders.html",orderdata=ordres)

@app.route('/orderplaced/<int:id>')
def orderplaced(id):
    cursor=db_con.cursor()
    cursor.execute("select * from Customers where email='"+user.user+"'")
    reso=cursor.fetchone()
    cursor.execute("select curdate()")
    date=cursor.fetchone()
    sql="INSERT INTO Orders (customerID,bookID,orderDate) VALUES(%s, %s, %s)"
    val=(reso[0],id,date)
    cursor.execute(sql,val)
    db_con.commit()
    return render_template("orderplaced.html",ouser=reso[1]+" "+reso[2])
    

@app.route('/books')
def bookdetails():
    cursor=db_con.cursor()
    cursor.execute("select * from Books")
    bd=cursor.fetchall()
    cursor.execute("select firstName,lastName from Customers where email='"+user.user+"'")
    uname=cursor.fetchone()
    return render_template("books.html",bdata=bd,udata="Welcome, "+uname[0]+" "+uname[1])
    
@app.route('/analysis',methods=['POST'])
def Authenticate2():
    username=request.form['uname']
    password=request.form['pass']
    cursor=db_con.cursor()
    cursor.execute("select usernames,passwords from Adminuser where usernames='" + username + "' and passwords='" + password + "'")
    data=cursor.fetchone()
    if data is None:
        return render_template("form2.html",alert1="Username or Password is Invalid")
    else:
        cursor=db_con.cursor()
        cursor.execute("select b.bookID,b.bookName,b.authorName,count(b.bookName) as sales_count from Books b inner join Orders o on b.bookID=o.bookID group by b.bookID order by sales_count desc ")
        anldata=cursor.fetchall()
        return render_template("analysis.html",ansdata=anldata)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
