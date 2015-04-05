from application.app_settings import app
from flask.ext.assets import Environment, Bundle

assets = Environment(app)
assets.auto_build = app.config['ASSETS_DEBUG']

js = Bundle('vendor/jquery/dist/jquery.min.js',
            'vendor/jquery.lazyload/jquery.lazyload.js',
            'vendor/jquery-ui/jquery-ui.js',
            # 'vendor/bootstrap/dist/js/bootstrap.js',
            'vendor/select2/dist/js/select2.js',
            # 'vendor/lodash/lodash.min.js',
            'vendor/jquery.cookie/jquery.cookie.js',
            # 'vendor/mustache.js/mustache.js',
            'vendor/knockout/dist/knockout.js',
            # 'vendor/color-thief/dist/color-thief.min.js',

            # 'js/main.js',

            # 'vendor/fullpage.js/jquery.fullPage.min.js',
            # 'vendor/scrollNav/dist/jquery.scrollNav.min.js',
            # 'js/socket.io.js',
            # 'js/jquery.form.min.js',
            filters='yui_js', output='dist/script.js')

css = Bundle('vendor/select2/dist/css/select2.min.css',
             'vendor/fontawesome/css/font-awesome.min.css',
             'vendor/jquery-ui/themes/cupertino/jquery-ui.css',
             'css/select2-bootstrap.css',
             'vendor/bootstrap/dist/css/bootstrap.css',
             'css/bootstrap-flatty.min.css',
             'sass/style.css',
             filters='cssmin',
             output='dist/style.css')

assets.register('js_all', js)
assets.register('css_all', css)

assets.debug = app.config['ASSETS_DEBUG']