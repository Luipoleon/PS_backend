import 'dart:convert';
import 'package:http/http.dart' as http;

void main() async {
  http.Response response = await eliminarLugar("A9");
  print(json.decode(response.body));
}

//CRUD lugares

Future<http.Response> consultarLugar(String ID) {
  return http.get(
    Uri.parse('http://localhost:5000/espacios?id=$ID')
  );
}

Future<http.Response> seleccionarLugares() {
  return http.get(
    Uri.parse('http://localhost:5000/espacios')
  );
}

Future<http.Response> crearLugar(String ID) {
  return http.post(
    Uri.parse('http://localhost:5000/espacios/crear'),
    headers: <String, String>{
      'Content-Type': 'application/json; charset=UTF-8',
    },
    body: jsonEncode(<String, String>{
      'ID': ID,
    }),
  );
}

Future<http.Response> cambiarEstadoLugar(String ID, String estado) {
  return http.post(
    Uri.parse('http://localhost:5000/espacios/estado'),
    headers: <String, String>{
      'Content-Type': 'application/json; charset=UTF-8',
    },
    body: jsonEncode(<String, String>{'ID': ID, 'estado': estado}),
  );
}

Future<http.Response> eliminarLugar(String ID) {
  return http.post(
    Uri.parse('http://localhost:5000/espacios/eliminar'),
    headers: <String, String>{
      'Content-Type': 'application/json; charset=UTF-8',
    },
    body: jsonEncode(<String, String>{'ID': ID}),
  );
}

//Admin

//CRUD Admin


