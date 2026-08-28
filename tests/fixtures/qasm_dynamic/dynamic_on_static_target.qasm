OPENQASM 3.0;
bit result;
qubit q;
result = measure q;
if (result == 1) {
  x q;
}
