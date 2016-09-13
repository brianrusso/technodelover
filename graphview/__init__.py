#! ../env/bin/python

from flask import Flask
from webassets.loaders import PythonLoader as PythonAssetsLoader

from graphview import assets
from graphview.models import db
from graphview.controllers.main import main
from graphview.controllers.keyphrases import keyphrases
from graphview.extensions import assets_env

def run_flask():

    app = Flask(__name__)

    # Import and register the different asset bundles
    assets_env.init_app(app)
    assets_loader = PythonAssetsLoader(assets)
    for name, bundle in assets_loader.load_bundles().items():
        assets_env.register(name, bundle)


    # register our blueprints
    app.register_blueprint(main)
    app.register_blueprint(keyphrases)

    app.run(host="0.0.0.0", debug=True)
    return app
