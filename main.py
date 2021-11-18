import flask
import sqlite3
import time

app = flask.Flask(__name__)


@app.route("/register", methods=['GET','POST'])
def register():
	return flask.render_template("register.html")


@app.route("/register_submit", methods=['POST'])
def register_submit():
    """ 
    a=hash(user_id+passw)
    if(a not in users):
        insert into
    """    
    con = sqlite3.connect('database.db')
    c = con.cursor()
    u = flask.request.form['user_id']
    p = flask.request.form['passw']
    h = hash(u)
    print("HASHCODE: " + str(h))
    e = (c.execute("SELECT * from users where user_id = ?", (u,)).fetchall())
    # if(c.execute("SELECT EXISTS(SELECT * FROM users WHERE hashcode=(?)", (h,)) == None):
    if not e:
        c.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (u,h,p,0))
        c.execute("INSERT INTO posts VALUES (?, ?, ?, ?, ?, ?)", (0,"",u,"No posts below here...","",0))
    p = (c.execute("SELECT * from posts where poster_user_id = ?", (u,)).fetchall())
    data = {}
    for i in p:
        cont = {}
        cont["post_id"] = i[0]
        cont["post_timestamp"] = i[1]
        cont["poster_user_id"] = i[2]
        cont["post_title"] = i[3]
        cont["post_content"] = i[4]
        cont["vote_counter"] = i[5]
        data[i[0]] = cont

    con.commit()
    con.close()
    return flask.render_template('userpage.html', user_id = u, hashcode = h, data = data)


@app.route("/<hashcode>/create", methods=['GET','POST'])
def create(hashcode):
	return flask.render_template("create.html", hashcode = hashcode)

@app.route("/<hashcode>/create_submit", methods=['POST'])
def create_submit(hashcode):
    con = sqlite3.connect('database.db')
    c = con.cursor()
    pt = flask.request.form['post_title']
    pc = flask.request.form['post_content']
    e = (c.execute("SELECT * from users where hashcode = ?", (hashcode,)).fetchall())
    #(user_id, hashcode, passw, last_post)
    print(e)
    u = e[0][0]
    l = int(e[0][3])
    l += 1
    t = time.ctime()
    #(post_id, post_timestamp, poster_user_id, post_title, post_content, vote_counter)
    c.execute("INSERT INTO posts VALUES (?, ?, ?, ?, ?, ?)", (l,t,u,pt,pc,0))
    c.execute("UPDATE users SET last_post_id = ? WHERE hashcode = ?", (l, hashcode))
    p = (c.execute("SELECT * from posts where poster_user_id = ?", (u,)).fetchall())
    data = {}
    for i in p:
        cont = {}
        cont["post_id"] = i[0]
        cont["post_timestamp"] = i[1]
        cont["poster_user_id"] = i[2]
        cont["post_title"] = i[3]
        cont["post_content"] = i[4]
        cont["vote_counter"] = i[5]
        data[i[0]] = cont
        print(cont)
    print(data)
    con.commit()
    con.close()
    return flask.render_template('userpage.html', user_id = u, hashcode = hashcode, data = data)


if __name__ == '__main__':
	# Start the server
	app.run(port=8001, host='127.0.0.1', debug=True, use_evalex=False)