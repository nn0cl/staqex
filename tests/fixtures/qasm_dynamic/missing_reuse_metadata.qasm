OPENQASM 3.0;
bit result;
qubit q;
result = measure q;
reset q;
h q;
result = measure q;
