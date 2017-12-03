from wsgiref.simple_server import make_server

from pyramid.config import Configurator
import jsonapidb

SCHEMA = {
    'entities': {
        'offers': {
            'attributes': {
                'lat': {
                    'type': 'string',
                    'validators': {
                    },
                    'required': True
                },
                'lng': {
                    'type': 'string',
                    'validators': {
                    },
                    'required': True
                },
                'subject': {
                    'type': 'string',
                    'validators': {
                    },
                    'required': True
                },
                'price': {
                    'type': 'string',
                    'validators': {
                    },
                    'required': True
                },
                'post_id': {
                    'type': 'string',
                    'validators': {
                    },
                    'required': True
                }
            }
        }
    },
    'relations': {

    }
}


def prototype(host):
    config = Configurator()
    schema = jsonapidb.SchemaProxy(SCHEMA)
    app_builder = jsonapidb.AppBuilder(schema, jsonapidb.AppConfig('mwwa', host))
    return app_builder.build_app(pyramid_config=config)


if __name__ == '__main__':
    server = make_server('localhost', 5000, prototype('http://localhost:5000'))
    print('prototype start')
    server.serve_forever()