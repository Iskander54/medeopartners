from flask import Blueprint

mesoutils = Blueprint('mesoutils', __name__, url_prefix='/fr/mesoutils')

from medeo.mesoutils import routes  # noqa: F401, E402
