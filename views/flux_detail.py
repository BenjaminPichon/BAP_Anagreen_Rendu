import flask
from bokeh.embed import components
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8
from flask import Blueprint
import bokeh_graph as bg

flux_detail_bp = Blueprint('flux_detail_page', __name__)


@flux_detail_bp.route("/flux_detail.html")
def flux_detail_page():
    resources = INLINE.render()
    myscript20, mydiv20 = components(bg.plot(flask.config.source,
                                             xLabel='step',
                                             yLabel='Temp',
                                             xSourceName=['step', 'step'],
                                             ySourceName=['tempIn', 'tempOut'],
                                             title='Temp',
                                             pHeight=350,
                                             lc=['blue', 'red']))
    html = flask.render_template(
        'flux_detail.html',
        script20=myscript20,
        div20=mydiv20,
        config=config,
        resources=resources
    )
    return encode_utf8(html)
