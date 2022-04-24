from mini_proj import app,db
import os

if __name__ == "__main__":
    db.create_all()
    # os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "1"
    app.run(debug=True)
