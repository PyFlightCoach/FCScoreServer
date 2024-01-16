from app.app import app
import os

if __name__ == '__main__':
    app.run(debug=True, threaded=False, processes=os.cpu_count())