import 'dart:io';
 
class Producto {
  final String nombre;
  int    cantidad;
  double precio;
  Producto({required this.nombre, required this.cantidad, required this.precio});
  double get valorTotal => cantidad * precio;
  @override
  String toString() => '$nombre: $cantidad uds @ \$$precio';
}
 
void mostrarInventario(Map<String, Producto> inv) {
  print('\n=== INVENTARIO ===');
  for (var e in inv.entries) print('  [${e.key}] ${e.value}');
  double total = inv.values.fold(0.0, (s, p) => s + p.valorTotal);
  print('Valor total: \$$total');
}
 
void main() {
  Map<String, Producto> inventario = {
    'P001': Producto(nombre: 'Laptop',  cantidad: 5,  precio: 899.99),
    'P002': Producto(nombre: 'Mouse',   cantidad: 20, precio: 25.50),
    'P003': Producto(nombre: 'Teclado', cantidad: 15, precio: 45.00),
  };
  mostrarInventario(inventario);
  stdout.write('Codigo a actualizar: ');
  String cod = stdin.readLineSync()!;
  if (inventario.containsKey(cod)) {
    stdout.write('Nueva cantidad: ');
    inventario[cod]!.cantidad = int.parse(stdin.readLineSync()!);
    print('Actualizado.');
  } else { print('No encontrado.'); }
  mostrarInventario(inventario);
}
