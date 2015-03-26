from application import app
from flask.ext.assets import Environment, Bundle

assets = Environment(app)

js = Bundle('vendor/jquery/dist/jquery.min.js',
            'vendor/jquery.lazyload/jquery.lazyload.js',
            'vendor/bootstrap/dist/js/bootstrap.js',
            'vendor/select2/dist/js/select2.js',
            'vendor/lodash/lodash.min.js',
            'vendor/jquery.cookie/jquery.cookie.js',
            'vendor/color-thief/dist/color-thief.min.js',

            'js/main.js',
            # 'vendor/fullpage.js/jquery.fullPage.min.js',
            # 'vendor/scrollNav/dist/jquery.scrollNav.min.js',
            # 'js/socket.io.js',
            # 'js/jquery.form.min.js',
            filters='yui_js', output='dist/script.js')

css = Bundle('vendor/select2/dist/css/select2.min.css',
             'vendor/fontawesome/css/font-awesome.min.css',
             'vendor/bootstrap/dist/css/bootstrap.css',
             'css/bootstrap-flatty.min.css',
             'sass/style.css',
             filters='cssmin',
             output='dist/style.css')

assets.register('js_all', js)
assets.register('css_all', css)

assets.debug = app.debug
app.config['ASSETS_DEBUG'] = assets.debug
