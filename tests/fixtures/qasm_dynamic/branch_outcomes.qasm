OPENQASM 3.0;
bit branch;
qubit q;
branch = measure q;
if (branch == 0) {
  x q;
} else {
  z q;
}
