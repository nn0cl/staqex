OPENQASM 3.0;
include "stdgates.inc";
bit[2] outcome;
qubit[2] q;
h q[0];
outcome[0] = measure q[0];
if (outcome[0] == 1) {
  x q[1];
}
reset q[0];
h q[0];
outcome[1] = measure q[0];
