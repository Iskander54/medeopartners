from medeo import create_app
from config_local import ConfigLocal

app = create_app(ConfigLocal)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8888, debug=True) 