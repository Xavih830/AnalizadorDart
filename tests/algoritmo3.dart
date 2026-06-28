import 'dart:io';
 
Set<String> palabrasUnicas(String texto) =>
    texto.toLowerCase().split(RegExp(r'\s+')).where((p) => p.isNotEmpty).toSet();
 
int contarVocales(String texto) =>
    texto.toLowerCase().split('').where((c) => 'aeiou'.contains(c)).length;
 
bool esPalindromo(String texto) {
  final s = texto.toLowerCase().replaceAll(RegExp(r'[^a-z]'), '');
  return s == s.split('').reversed.join();
}
 
void main() {
  stdout.write('Ingrese un texto: ');
  String texto = stdin.readLineSync() ?? '';
  Set<String> unicas  = palabrasUnicas(texto);
  int         vocales = contarVocales(texto);
  bool        palind  = esPalindromo(texto.replaceAll(' ', ''));
  print('Palabras unicas (${unicas.length}): $unicas');
  print('Vocales: $vocales');
  print('Es palindromo: $palind');
  Set<String> vocalesSet   = {'a','e','i','o','u'};
  Set<String> letras       = texto.toLowerCase().split('').toSet();
  Set<String> vocalesEnTxt = letras.intersection(vocalesSet);
  print('Vocales presentes: $vocalesEnTxt');
}
