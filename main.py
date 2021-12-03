import flask
import sqlite3
import time
import csv

app = flask.Flask(__name__)
ROWS_PER_PAGE = 5


@app.route("/<hashcode>/downloadDB", methods=['GET'])
def downloadDB(hashcode):
    con = sqlite3.connect('database.db')
    c = con.cursor()
    posts = c.execute("SELECT * from posts").fetchall()
    with open("database.tsv", "w") as f:
        writer = csv.writer(f, delimiter="\t")  # create a CSV writer, tab delimited
        writer.writerows(posts)
    con.commit()
    con.close() 
    return flask.render_template("thankYou.html", hashcode = hashcode, reason = "downloading the database")


@app.route("/<hashcode>/deleteConfirmation/<post_id>", methods=['GET'])
def deleteConfirm(hashcode, post_id):
    return flask.render_template("delete.html", post_id=post_id, hashcode = hashcode)
    
@app.route("/<hashcode>/yesDelete/<post_id>", methods=['GET'])
def yesDelete(hashcode, post_id):
    con = sqlite3.connect('database.db')
    c = con.cursor()
    c.execute("DELETE from posts where post_id = ?", (post_id,)) 

    user_id = c.execute("SELECT user_id from users where hashcode = ?", (hashcode,)).fetchall()[0][0]
    posts = c.execute("SELECT * from posts where poster_user_id = ?", (user_id,)).fetchall()    

    # page = flask.request.args.get('page', 1, type=int)
    
    data = {}
    for i in posts:
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
    return flask.render_template("userpage.html", hashcode = hashcode, user_id = user_id, data = data)
    
@app.route("/<hashcode>/updatePost/<post_id>", methods=['GET'])
def updatePost(hashcode, post_id):
    return flask.render_template("updatePost.html", post_id=post_id, hashcode = hashcode)


@app.route("/posts/<postid>", methods=['GET'])
def show_post(post_id):
    con = sqlite3.connect('database.db')
    c = con.cursor()

    post = c.execute("SELECT * from posts where post_id = ?", (post_id,)).fetchall()    

    data = {}
    for i in post:
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
    return flask.render_template("posts.html", data=data)

@app.route("/<hashcode>/userpage", methods=['GET'])
def show_userpage(hashcode):
    con = sqlite3.connect('database.db')
    c = con.cursor()

    user_id = c.execute("SELECT user_id from users where hashcode = ?", (hashcode,)).fetchall()[0][0]
    posts = c.execute("SELECT * from posts where poster_user_id = ?", (user_id,)).fetchall()    

    # page = flask.request.args.get('page', 1, type=int)
    print(user_id)
    data = {}
    for i in posts:
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
    return flask.render_template("userpage.html", hashcode=hashcode, user_id=user_id, data=data)
"""
- Update (edit) and delete buttons next to posts
    - Delete confirmation
- Move create to top right
"""


def get_latest_post_id(con, c):
    post_ids = c.execute("SELECT post_id from posts").fetchall()
    # max = 0
    if not post_ids:
        post_ids = [0]
    else:
        post_ids = [max(0, i[0]) for i in post_ids]
    return max(post_ids)

@app.route("/<hashcode>/feed/<pagenum>", methods=['GET', 'POST'])
def feedPage(hashcode, pagenum):
    """
    - post in reverse chronological order (most recent first)
    - 5 posts/page
    - Username in top right
        - Clicking redirects to user page
    - Logo in top left
        - Clicking goes to /{hashcode}/feed
    - Upvote/Downvote option
        - changes dynamically (ie as you vote)
        - only one vote
    - *** Exclude self posts ***
    """

    con = sqlite3.connect('database.db')
    c = con.cursor()

    #Get user id using hashcode:
    user_id = c.execute("SELECT user_id from users where hashcode = ?", (hashcode,)).fetchall()[0][0]
    #Get all posts from all but current user:
    posts = c.execute("SELECT * from posts").fetchall()    

    # page = flask.request.args.get('page', 1, type=int)
    
    data = {}
    for i in posts:
        if i[2] != user_id:
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
    return flask.render_template('feed.html', hashcode=hashcode, data=data, pagenum=pagenum, user_id=user_id)

@app.route("/register", methods=['GET','POST'])
def register():
    return flask.render_template("register.html")


@app.route("/register_submit", methods=['POST'])
def register_submit():
    con = sqlite3.connect('database.db')
    c = con.cursor()
    u = flask.request.form['user_id']
    p = flask.request.form['passw']
    h = hash(u)
    e = (c.execute("SELECT * from users where user_id = ?", (u,)).fetchall())
    # if(c.execute("SELECT EXISTS(SELECT * FROM users WHERE hashcode=(?)", (h,)) == None):
    if not e:
        c.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (u,h,p,0))
        c.execute("INSERT INTO posts VALUES (?, ?, ?, ?, ?, ?)", (get_latest_post_id(con, c) + 1,time.ctime(),u,"User's first Post!","Hello World!",0))
    con.commit()
    con.close()
    return flask.render_template('thankYou.html', hashcode = h, reason = "logging in")


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
    u = e[0][0]
    # l = int(e[0][3])
    # l += 1
    l = get_latest_post_id(con, c) + 1
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
    con.commit()
    con.close()
    return flask.render_template('thankYou.html', hashcode = hashcode, reason = "posting")


if __name__ == '__main__':
	# Start the server
    app.run(port=8001, host='127.0.0.1', debug=True, use_evalex=False)