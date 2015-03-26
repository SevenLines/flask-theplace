from application import app
from flask.ext.assets import Environment, Bundle

assets = Environment(app)

js = Bundle('vendor/jquery/dist/jquery.min.js',
            'vendor/jquery.lazyload/jquery.lazyload.js',
            'vendor/bootstrap/dist/js/bootstrap.js',
            'vendor/select2/dist/js/select2.js',
            'vendor/lodash/lodash.min.js',
            'vendor/jquery.cookie/jquery.cookie.js',
            # 'vendor/fullpage.js/jquery.fullPage.min.js',
            'vendor/scrollNav/dist/jquery.scrollNav.min.js',
            # 'js/socket.io.js',
            # 'js/jquery.form.min.js',
            filters='yui_js', output='dist/script.js')

assets.register('js_all', js)

# assets.debug = True
# app.config['ASSETS_DEBUG'] = True
