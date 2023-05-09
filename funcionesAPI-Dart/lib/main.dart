import 'dart:convert';
import 'package:http/http.dart' as http;

void main() async {
  http.Response response = await seleccionarAdmin();
  print(json.decode(response.body));
}

//CRUD lugares

Future<http.Response> consultarLugar(String id) {
  return http.get(
    Uri.parse('http://localhost:5000/espacios?id=$id')
  );
}

Future<http.Response> seleccionarLugares() {
  return http.get(
    Uri.parse('http://localhost:5000/espacios')
  );
}

Future<http.Response> crearLugar(String id, String direccion, String tipo, int x, int y) {
  return http.post(
    Uri.parse('http://localhost:5000/espacios/crear'),
    headers: <String, String>{
      'Content-Type': 'application/json; charset=UTF-8',
    },
    body: jsonEncode(<String, String>{
      'ID': id,
      'direccion': direccion,
      'tipo': tipo,
      'x': x,
      'y': y,
    }),
  );
}

Future<http.Response> cambiarEstadoLugar(String id, String estado) {
  return http.post(
    Uri.parse('http://localhost:5000/espacios/estado'),
    headers: <String, String>{
      'Content-Type': 'application/json; charset=UTF-8',
    },
    body: jsonEncode(<String, String>{'ID': id, 'estado': estado}),
  );
}

Future<http.Response> eliminarLugar(String id) {
  return http.post(
    Uri.parse('http://localhost:5000/espacios/eliminar'),
    headers: <String, String>{
      'Content-Type': 'application/json; charset=UTF-8',
    },
    body: jsonEncode(<String, String>{'ID': id}),
  );
}

//Admin



//CRUD Admin

Future<http.Response> seleccionarAdmin() {
  return http.get(
    Uri.parse('http://localhost:5000/administradores')
  );
}

Future<http.Response> crearAdmin(String rfc, String curp, String passwd, String nombre)
 {
  return http.post(
    Uri.parse('http://localhost:5000/administradores/crear')
    ,headers: <String, String>{
      'Content-Type': 'application/json; charset=UTF-8',
    },
    body: jsonEncode(<String, String>{'RFC': rfc,'CURP':curp,'passwd':passwd,'nombre':nombre}),
  );
}

Future<http.Response> eliminarAdmin(String rfc)
 {
  return http.post(
    Uri.parse('http://localhost:5000/administradores/eliminar')
    ,headers: <String, String>{
      'Content-Type': 'application/json; charset=UTF-8',
    },
    body: jsonEncode(<String, String>{'RFC': rfc}),
  );
}

Future<http.Response> actualizarAdmin(String rfc, String new_curp, String new_passwd, String new_nombre)
 {
  return http.post(
    Uri.parse('http://localhost:5000/administradores/actualizar')
    ,headers: <String, String>{
      'Content-Type': 'application/json; charset=UTF-8',
    },
    body: jsonEncode(<String, String>{'RFC': rfc,'CURP':new_curp,'passwd':new_passwd,'nombre':new_nombre}),
  );
}





