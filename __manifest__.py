# -*- coding: utf-8 -*-
{
    'name': "Stage Constructor Dynamic",
    'summary': """
        State or Stage change button constructor
    """,
    'description': """
        State or Stage change button constructor
    """,
    'author': "QZhub",
    'website': "http://www.qzhub.com",
    'category': 'Productivity',
    'version': '0.1',
    'depends': ['base','hr'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/stage_constructor.xml',
    ], 
    'application': True,
    'assets': {
        'web.assets_backend': [
            "stage_constructor/static/src/js/stage_route_out/form_controller.js",
            "stage_constructor/static/src/js/stage_route_out/form_renderer.js",
            "stage_constructor/static/src/js/stage_route_out/stage_route_out_widget.js",
            "stage_constructor/static/src/scss/style.scss",
        ]
    },
}
