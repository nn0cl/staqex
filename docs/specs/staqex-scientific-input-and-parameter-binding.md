# Staqex scientific input and parameter binding acceptance specification

> Coverage note (2026-09-08): The accepted scalar contract below remains in
> force. Metadata Graph and richer typed bindings are a separate
> [Scientific Workflow proposal](staqex-scientific-workflow-acceptance.md),
> with WP-0132/WP-0133 ownership. Deferred geometry/tensor/quality here does
> not limit the complete scientific model or approve those extensions.

## Status

Accepted for LISS-0045 Phase 2 Green. This document is the acceptance
contract for the scalar first slice; it does not authorize provider
integration or deferred tensor/geometry work.

## Scope

The Host boundary accepts validated, typed scalar scientific inputs and binds
them to declared `Param<T>` values. A parameter sweep is an immutable finite
collection of bindings. Kernel theory remains free of file formats, JSON
objects, provider SDK values, and execution settings.

The contract names the following Host-side value objects for the first slice:

- `ScientificInput`
- `ParameterBinding`
- `ParameterSweep`
- `InputProvenance`

Geometry, coefficient tensors, uncertainty/quality metadata, and file
adapters are deferred.

## Acceptance scenarios

### Scalar input with provenance

Given a declared `Param<Angle>` named `theta`, when the Host constructs a
`ParameterBinding` with a finite angle value and unit metadata, then a
`ScientificInput` accepts it only when an `InputProvenance` identifies the
source formula/program and input identity.

### Binding identity and dimensions

Given a declared parameter set, when a binding uses an unknown name or an
incompatible unit/dimension, then construction fails with a hard diagnostic
(`SCIENTIFIC_INPUT_UNKNOWN_PARAMETER` or `SCIENTIFIC_INPUT_DIMENSION_ERROR`).
No coercion or silent unit conversion is allowed in this slice.

### Immutable non-empty sweep

Given valid bindings, when the Host constructs a `ParameterSweep`, then the
sweep is finite, non-empty, and immutable. An empty sweep fails with
`SCIENTIFIC_INPUT_EMPTY_SWEEP`.

### Provenance survives the execution boundary

Given a scientific input and a submitted Job, when a provider-neutral result is
returned, then the result contract retains input identity, binding identity,
source formula/program, units/basis, target, shots or precision, and Job
identity. Simulator-only snapshots remain explicitly non-portable artifacts.

### Kernel isolation

Given a Staqex theory/kernel expression, when a file-format object, generic JSON
value, or execution setting is referenced inside the Kernel, then compilation
fails at the Host/Kernel boundary. The first slice provides no generic data
escape hatch.

## External boundaries

- File and library readers are Host adapters behind ports.
- Provider SDKs and credentials are outside the compiler kernel.
- Phase 1 uses no network, filesystem, provider, or cloud service.
- `JobResult` remains the existing provider-neutral result boundary.

## Out of scope

- Geometry and tensor schemas.
- Canonical CSV, JSON, XYZ, HDF5, or Python file input.
- Automatic unit, basis, mapping, or discretization inference.
- Optimizer implementation and dynamic QPU control.
- Phase 2 simulator/fake-adapter integration.
