import 'dart:io';
 
List<int> bubbleSort(List<int> lista) {
  int n = lista.length;
  for (int i = 0; i < n - 1; i++) {
    for (int j = 0; j < n - i - 1; j++) {
      if (lista[j] > lista[j + 1]) {
        int temp     = lista[j];
        lista[j]     = lista[j + 1];
        lista[j + 1] = temp;
      }
    }
  }
  return lista;
}
 
int busquedaBinaria(List<int> lista, int objetivo) {
  int inicio = 0, fin = lista.length - 1;
  while (inicio <= fin) {
    int medio = (inicio + fin) ~/ 2;
    if (lista[medio] == objetivo) return medio;
    if (lista[medio] < objetivo)  inicio = medio + 1;
    else                          fin    = medio - 1;
  }
  return -1;
}
 
void main() {
  List<int> numeros = [64, 34, 25, 12, 22, 11, 90];
  print('Lista original: $numeros');
  List<int> ordenada = bubbleSort(numeros);
  print('Lista ordenada: $ordenada');
  stdout.write('Numero a buscar: ');
  int objetivo = int.parse(stdin.readLineSync()!);
  int indice   = busquedaBinaria(ordenada, objetivo);
  print(indice != -1 ? 'Indice: $indice' : 'No encontrado');
}
