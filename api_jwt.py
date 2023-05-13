from parking import *
from flask_restful import Api, Resource, request, reqparse
from flask import Flask, session
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, create_refresh_token

FLASK_DEBUG=1


app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True # Requerido para no recibir codigo 500 por usar flask_restful
api = Api(app)
app.config['JWT_SECRET_KEY'] = '\xb3\x04e\xcc\xcb>\x90\xd5\x14\xf6\x15\xf4\xafj\xbd4' # os.urandom(16)
jwt = JWTManager(app)
CORS(app)
    

class Login(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('nombre', help='Requerido', required=True)
        parser.add_argument('passwd', help='Requerido', required=True)

        data = parser.parse_args()
        admin = LoginAdmin(data["nombre"], data["passwd"])
        if not admin:
            return {"message":"Credenciales incorrectas"}
        access_token = create_access_token(identity=admin[0])
        refresh_token = create_refresh_token(identity=admin[0])
        return {
            "access_token":access_token,
            "refresh_token":refresh_token
        }
    
    
class Test(Resource):
    @jwt_required()
    def get(self):
        return {"message":"Estas autorizado!"},200

api.add_resource(Test, "/Test")
api.add_resource(Login, "/login")

if __name__ == "__main__":
    app.run()
