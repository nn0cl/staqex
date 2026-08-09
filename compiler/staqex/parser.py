"""Staqex recursive-descent Parser (Phase 2.1 subset)."""

from __future__ import annotations

from .ast_nodes import (
    AssignStmt,
    Attr,
    BinOp,
    BinderOrigin,
    Block,
    BlockExpr,
    Call,
    ClassDecl,
    Coin,
    CompilationUnit,
    Dirac,
    DiscretizationBridgeDecl,
    DiscretizationDecl,
    DynamicQpuStmt,
    EnumDecl,
    MatchArm,
    MatchStmt,
    ExperimentDecl,
    EvolveBody,
    EvolveExpr,
    Expr,
    ExprStmt,
    FieldDecl,
    ForEachStmt,
    FunDecl,
    ImportDecl,
    ImplDecl,
    Inspect,
    Hole,
    H1BasisDecl,
    H1CoordinateDecl,
    H1Evolve,
    H1CoherentControl,
    H1DynamicControl,
    H1Measure,
    H1Mixture,
    H1Observable,
    H1OperatorDecl,
    H1ParameterDecl,
    H1Prepare,
    H1RealizeDecl,
    H1Superposition,
    H1TraceOut,
    H1Uncompute,
    InterfaceDecl,
    IndexDomain,
    BraLit,
    KetLit,
    Lambda,
    ListExpr,
    LetBind,
    LitBool,
    LitFloat,
    LitInt,
    LitString,
    MeasureExpr,
    MainDecl,
    Measure,
    ModuleInfoDecl,
    NamespaceDecl,
    OpBin,
    OpBinder,
    OpCall,
    OpIndexed,
    OpLit,
    OpNumber,
    OpQuadrature,
    OpGridQuad,
    OpHop,
    OpPauli,
    OpPow,
    OpVar,
    OpAttr,
    PackageDecl,
    Param,
    Pipe,
    ReturnStmt,
    RevDomain,
    Snapshot,
    ScientificScopeDecl,
    Span,
    StateBind,
    StructDecl,
    SuzukiPolicy,
    TensorExpr,
    TupleExpr,
    TypeRef,
    TheoryDecl,
    UnitConvert,
    Vacuum,
    Var,
    WhenArm,
    WhenExpr,
    SuperposeArm,
    SuperposeExpr,
)
from .tokens import Token, TokenKind
from .scientific_vocabulary import (
    SCIENTIFIC_NAME_ALIASES,
    normalize_algebra_name,
    normalize_scientific_name,
)


class ParseError(Exception):
    def __init__(
        self,
        message: str,
        line: int,
        col: int,
        *,
        code: str = "PARSE_ERROR",
    ) -> None:
        super().__init__(message)
        self.line = line
        self.col = col
        self.message = message
        self.code = code


def _flatten_namespaces(decls: list) -> list:
    """Expand `namespace A.B { class C … }` → ClassDecl(namespace=[A,B], name=C)."""
    out: list = []
    for d in decls:
        if isinstance(d, NamespaceDecl):
            for inner in _flatten_namespaces(d.decls):
                if isinstance(inner, (ClassDecl, FunDecl, EnumDecl, StructDecl)):
                    inner.namespace = list(d.path) + list(inner.namespace)
                    out.append(inner)
                else:
                    out.append(inner)
        else:
            out.append(d)
    return out


# Names the Operator-DSL parser (_op_expression / _op_primary) reserves for
# itself: `sum`/`product` binders and the Pauli/hop atoms. An `Operator`
# bind's factory-call heuristic must never treat these as an ordinary
# function call, even when immediately followed by `(` (LISS-0051).
_OPERATOR_DSL_RESERVED_ATOMS = {"sum", "product", "adjoint", "I", "X", "Y", "Z", "hop"}
# Algebra Calls that must parse as expression `Call` under `Operator … =`
# (LISS-0207): reserved OpDSL atoms would otherwise become `OpCall` and lose
# qubit domain when rebound through bare `Operator`.
_ALGEBRA_EXPR_CALLEES = frozenset({
    "adjoint",
    "commutator",
    "anticommutator",
    "inner",
    "outer",
    "projector",
})
_SUPPORTED_SOURCE_VERSIONS = frozenset({"1.0"})


class Parser:
    def __init__(
        self,
        tokens: list[Token],
        *,
        experiment_profile: bool = False,
    ) -> None:
        self.tokens = tokens
        self.i = 0
        self.diagnostics: list[dict] = []
        self._prev: Token | None = None
        # ADR 0176: short experiment surface (optional package + bare main body).
        self.experiment_profile = experiment_profile
        # Resolve reserved operator-looking calls against the complete source
        # declaration set.  A user callable named `Z` must remain a callable;
        # only an unresolved `Z(0)` is retired operator-index syntax.
        self._function_names = {
            tokens[index + 1].lexeme
            for index, token in enumerate(tokens[:-1])
            if token.kind == TokenKind.FUN
            and tokens[index + 1].kind == TokenKind.IDENT
        }
        # LISS-0073 Slice F: Operator-context `[A, B]` → commutator (not ListExpr).
        self._commutator_bracket_context = False
        # ADR 0189: aliases become canonical only after a quantum-state bind;
        # ordinary/type-first names and Dirac paper labels keep source spelling.
        self._scientific_bindings: dict[str, str] = {}

    def parse(self) -> CompilationUnit:
        start = self._span()
        package = None
        source_version = None
        imports: list[ImportDecl] = []
        decls: list = []
        main: MainDecl | None = None
        profile_main_stmts: list = []

        if self._check(TokenKind.PACKAGE):
            package = self._package()
        elif self.experiment_profile:
            from .experiment_profile import DEFAULT_EXPERIMENT_PACKAGE

            package = PackageDecl(
                path=list(DEFAULT_EXPERIMENT_PACKAGE),
                span=start,
            )

        if self._at_package_source_version():
            source_version = self._package_source_version()

        while self._check(TokenKind.IMPORT):
            imports.append(self._import())

        while not self._check(TokenKind.EOF):
            if self._check(TokenKind.IDENT) and self._peek().lexeme in {
                "theory",
                "experiment",
                "workflow",
                "execution",
                "report",
                "system",
            }:
                if (
                    self._peek().lexeme in {"theory", "experiment"}
                    and self._looks_like_h1_scope()
                ):
                    decls.append(self._h1_scope_decl())
                else:
                    decls.append(self._scientific_scope_decl())
            elif self._check(TokenKind.IDENT) and self._peek().lexeme == "realize":
                decls.append(self._h1_realize_decl())
            elif self._check(TokenKind.IDENT) and self._peek().lexeme == "discretization":
                decls.append(self._discretization_decl())
            elif self._check(TokenKind.IDENT) and self._peek().lexeme == "use":
                decls.append(self._use_decl())
            elif self._check(TokenKind.NAMESPACE):
                decls.append(self._namespace_decl())
            elif self._check(TokenKind.ENUM) or (
                self._is_visibility_start() and self._peek_after_visibility() == TokenKind.ENUM
            ):
                vis = self._parse_visibility()
                ed = self._enum_decl()
                ed.visibility = vis  # type: ignore[assignment]
                decls.append(ed)
            elif self._check(TokenKind.STRUCT) or (
                self._is_visibility_start()
                and self._peek_after_visibility() == TokenKind.STRUCT
            ):
                vis = self._parse_visibility()
                sd = self._struct_decl()
                sd.visibility = vis  # type: ignore[assignment]
                decls.append(sd)
            elif (
                self._check(TokenKind.PUBLIC)
               
                or self._check(TokenKind.PRIVATE)
                or self._check(TokenKind.FUN)
            ):
                nxt = self._peek_after_visibility()
                if nxt == TokenKind.CLASS:
                    vis = self._parse_visibility()
                    cd = self._class_decl()
                    cd.visibility = vis  # type: ignore[assignment]
                    decls.append(cd)
                elif nxt == TokenKind.ENUM:
                    vis = self._parse_visibility()
                    ed = self._enum_decl()
                    ed.visibility = vis  # type: ignore[assignment]
                    decls.append(ed)
                elif nxt == TokenKind.STRUCT:
                    vis = self._parse_visibility()
                    sd = self._struct_decl()
                    sd.visibility = vis  # type: ignore[assignment]
                    decls.append(sd)
                else:
                    fun = self._fun_decl()
                    if fun.name == "main":
                        if fun.return_type is None:
                            self.diagnostics.append(
                                {
                                    "code": "MISSING_RETURN_TYPE",
                                    "line": fun.span.line,
                                    "col": fun.span.col,
                                    "message": "`main` must declare `-> Unit`",
                                }
                            )
                        elif fun.return_type.name != "Unit":
                            self.diagnostics.append(
                                {
                                    "code": "MAIN_RETURN_TYPE_ERROR",
                                    "line": fun.span.line,
                                    "col": fun.span.col,
                                    "message": "`main` must return `Unit`",
                                }
                            )
                        if any(isinstance(stmt, ReturnStmt) for stmt in fun.body.stmts):
                            self.diagnostics.append(
                                {
                                    "code": "MAIN_RETURN_ERROR",
                                    "line": fun.span.line,
                                    "col": fun.span.col,
                                    "message": (
                                        "`main` must terminate with terminal `measure`; "
                                        "it cannot return a value"
                                    ),
                                }
                            )
                        elif fun.body.result is not None:
                            self.diagnostics.append(
                                {
                                    "code": "MAIN_RESULT_ERROR",
                                    "line": fun.span.line,
                                    "col": fun.span.col,
                                    "message": (
                                        "`main` must terminate with terminal `measure`; "
                                        "it cannot return a final expression"
                                    ),
                                }
                            )
                        if main is not None:
                            self.diagnostics.append(
                                {
                                    "code": "PARSE_ERROR",
                                    "line": fun.span.line,
                                    "col": fun.span.col,
                                    "message": "duplicate `main` entry point",
                                }
                            )
                        main = MainDecl(
                            params=fun.params,
                            body=fun.body,
                            span=fun.span,
                            return_type=fun.return_type,
                        )
                    else:
                        decls.append(fun)
            elif self._check(TokenKind.CLASS) or (
                self._is_visibility_start()
                and self._peek_after_visibility() == TokenKind.CLASS
            ):
                vis = self._parse_visibility()
                cd = self._class_decl()
                cd.visibility = vis  # type: ignore[assignment]
                decls.append(cd)
            elif self._check(TokenKind.INTERFACE):
                decls.append(self._interface_decl())
            elif self._check(TokenKind.IMPL):
                decls.append(self._impl_decl())
            elif self._is_toplevel_executable_start():
                if self.experiment_profile:
                    # ADR 0176: bare top-level statements desugar into synthetic main.
                    try:
                        profile_main_stmts.append(self._stmt())
                    except ParseError as e:
                        self.diagnostics.append(
                            {
                                "code": "PARSE_ERROR",
                                "line": e.line,
                                "col": e.col,
                                "message": e.message,
                            }
                        )
                        self._skip_until_toplevel_resync()
                else:
                    tok = self._peek()
                    self.diagnostics.append(
                        {
                            "code": "TOPLEVEL_EXECUTION_ERROR",
                            "line": tok.line,
                            "col": tok.col,
                            "message": (
                                "executable statements are forbidden at top level; "
                                "place them inside `pub fn main() -> Unit { … }` "
                                "or declare `// staqex-profile: experiment`"
                            ),
                        }
                    )
                    self._skip_until_toplevel_resync()
            elif self._check(TokenKind.FORBIDDEN) or self._check(TokenKind.RETIRED):
                self._advance()
            elif self._check(TokenKind.ERROR):
                self._advance()
            else:
                tok = self._peek()
                if tok.kind == TokenKind.EOF:
                    break
                self.diagnostics.append(
                    {
                        "code": "PARSE_ERROR",
                        "line": tok.line,
                        "col": tok.col,
                        "message": f"unexpected token `{tok.lexeme}` at top level",
                    }
                )
                self._advance()

        if profile_main_stmts:
            if main is not None:
                self.diagnostics.append(
                    {
                        "code": "PARSE_ERROR",
                        "line": profile_main_stmts[0].span.line,
                        "col": profile_main_stmts[0].span.col,
                        "message": (
                            "experiment profile: cannot mix bare top-level "
                            "statements with an explicit `main`"
                        ),
                    }
                )
            else:
                body_span = profile_main_stmts[0].span
                main = MainDecl(
                    params=[],
                    body=Block(
                        stmts=profile_main_stmts,
                        span=body_span,
                        result=None,
                    ),
                    span=body_span,
                    return_type=TypeRef(name="Unit", args=[]),
                )

        self._check_scientific_scope_graph(decls)
        decls = _flatten_namespaces(decls)
        return CompilationUnit(
            package=package,
            imports=imports,
            decls=decls,
            main=main,
            span=start,
            source_version=source_version,
        )

    def _package_source_version(self) -> str | None:
        tok = self._peek()
        self._expect_ident_like()  # staqex_version
        self._expect(TokenKind.EQ)
        value = self._expect(TokenKind.STRING)
        version = str(value.literal)
        if version in _SUPPORTED_SOURCE_VERSIONS:
            return version
        self.diagnostics.append(self._unsupported_source_version_diag(tok.line, tok.col, version))
        return version

    def _at_package_source_version(self) -> bool:
        return self._check(TokenKind.IDENT) and self._peek().lexeme == "staqex_version"

    @staticmethod
    def _unsupported_source_version_diag(
        line: int, col: int, version: str
    ) -> dict[str, object]:
        return {
            "code": "UNSUPPORTED_QPEX_VERSION",
            "line": line,
            "col": col,
            "message": f"unsupported staqex_version `{version}`",
        }

    def _looks_like_h1_scope(self) -> bool:
        """Detect reviewed H1 markers without changing legacy scope parsing."""

        depth = 0
        for offset in range(self.i, len(self.tokens)):
            token = self.tokens[offset]
            if token.kind == TokenKind.LBRACE:
                depth += 1
            elif token.kind == TokenKind.RBRACE:
                depth -= 1
                if depth == 0:
                    break
            elif depth > 0:
                if token.lexeme in {
                    "parameter",
                    "operator",
                    "prepare",
                    "realize",
                    "state",
                    "evolve",
                    "measure",
                }:
                    return True
                if (
                    token.lexeme == "observable"
                    and offset + 1 < len(self.tokens)
                    and self.tokens[offset + 1].lexeme != "="
                ):
                    return True
        return False

    def _h1_realize_decl(self) -> H1RealizeDecl:
        """Parse the top-level `realize qpu:<target>` H1 target selection."""

        start = self._span()
        self._advance()  # "realize"
        self._expect_ident_like()  # fixed "qpu" prefix
        self._expect(TokenKind.COLON)
        target = self._expect_ident_like()
        return H1RealizeDecl(target=target, span=start)

    def _h1_scope_decl(self) -> TheoryDecl | ExperimentDecl:
        """Parse the source-preserving H1 declaration skeleton."""

        start = self._span()
        kind = self._advance().lexeme
        name = self._expect_ident_like()
        params: list[Param] = []
        if kind == "experiment" and self._match(TokenKind.LPAREN):
            while not self._check(TokenKind.RPAREN):
                param_name = self._expect_ident_like()
                if self._match(TokenKind.EQ):
                    self._advance()
                params.append(Param(name=param_name, ty=None))
                if not self._match(TokenKind.COMMA):
                    break
            self._expect(TokenKind.RPAREN)
        self._expect(TokenKind.LBRACE)
        body: list[Token] = []
        depth = 1
        while depth > 0 and not self._check(TokenKind.EOF):
            token = self._advance()
            if token.kind == TokenKind.LBRACE:
                depth += 1
            elif token.kind == TokenKind.RBRACE:
                depth -= 1
                if depth == 0:
                    break
            body.append(token)
        if kind == "theory":
            parameters, operators, basis, coordinate = self._parse_h1_theory_members(body)
            return TheoryDecl(
                name=name,
                parameters=parameters,
                operators=operators,
                span=start,
                basis=basis,
                coordinate=coordinate,
            )
        return ExperimentDecl(
            name=name,
            parameters=params,
            body=self._parse_h1_experiment_body(body),
            span=start,
        )

    _H1_THEORY_MEMBER_KEYWORDS = frozenset({"parameter", "operator", "basis", "coordinate"})

    def _parse_h1_theory_members(
        self, body: list[Token]
    ) -> tuple[
        list[H1ParameterDecl],
        list[H1OperatorDecl],
        H1BasisDecl | None,
        H1CoordinateDecl | None,
    ]:
        parameters: list[H1ParameterDecl] = []
        operators: list[H1OperatorDecl] = []
        basis: H1BasisDecl | None = None
        coordinate: H1CoordinateDecl | None = None
        index = 0
        while index < len(body):
            token = body[index]
            if token.lexeme == "parameter" and index + 3 < len(body):
                parameters.append(
                    H1ParameterDecl(
                        name=body[index + 1].lexeme,
                        ty=TypeRef(name=body[index + 3].lexeme, args=[]),
                        span=Span(line=token.line, col=token.col),
                    )
                )
                index += 4
                continue
            if token.lexeme == "operator" and index + 1 < len(body):
                operator_name = body[index + 1]
                cursor = index + 2
                operator_params: list[str] = []
                if cursor < len(body) and body[cursor].kind == TokenKind.LPAREN:
                    cursor += 1
                    while cursor < len(body) and body[cursor].kind != TokenKind.RPAREN:
                        if body[cursor].kind == TokenKind.IDENT:
                            operator_params.append(body[cursor].lexeme)
                        cursor += 1
                    cursor += 1
                while cursor < len(body) and body[cursor].kind != TokenKind.EQ:
                    cursor += 1
                if cursor < len(body):
                    cursor += 1
                expression: list[str] = []
                expression_tokens: list[Token] = []
                while (
                    cursor < len(body)
                    and body[cursor].lexeme not in self._H1_THEORY_MEMBER_KEYWORDS
                ):
                    expression.append(body[cursor].lexeme)
                    expression_tokens.append(body[cursor])
                    cursor += 1
                parsed_expression = self._parse_h1_operator_expression(expression_tokens)
                parameter_types = {
                    parameter.name: parameter.ty.name for parameter in parameters
                }
                operators.append(
                    H1OperatorDecl(
                        name=operator_name.lexeme,
                        parameters=operator_params,
                        source_tokens=tuple(expression),
                        span=Span(line=token.line, col=token.col),
                        expression=parsed_expression,
                        dimension=(
                            parameter_types[operator_params[0]]
                            if operator_params and operator_params[0] in parameter_types
                            else None
                        ),
                        parameter_types=parameter_types,
                    )
                )
                index = cursor
                continue
            if (
                token.lexeme == "basis"
                and index + 2 < len(body)
                and body[index + 2].kind == TokenKind.EQ
            ):
                name = body[index + 1].lexeme
                cursor = index + 3
                expression_tokens: list[Token] = []
                while (
                    cursor < len(body)
                    and body[cursor].lexeme not in self._H1_THEORY_MEMBER_KEYWORDS
                ):
                    expression_tokens.append(body[cursor])
                    cursor += 1
                basis = H1BasisDecl(
                    name=name,
                    expression=self._parse_h1_operator_expression(expression_tokens),
                    source_tokens=tuple(tok.lexeme for tok in expression_tokens),
                    span=Span(line=token.line, col=token.col),
                )
                index = cursor
                continue
            if token.lexeme == "coordinate" and index + 3 < len(body):
                name = body[index + 1].lexeme
                kind_name = body[index + 3].lexeme
                cursor = index + 4
                size: int | None = None
                if cursor < len(body) and body[cursor].kind == TokenKind.LT:
                    cursor += 1
                    if cursor < len(body) and body[cursor].kind == TokenKind.INT:
                        try:
                            size = int(body[cursor].lexeme)
                        except ValueError:
                            size = None
                        cursor += 1
                    while cursor < len(body) and body[cursor].kind != TokenKind.GT:
                        cursor += 1
                    if cursor < len(body):
                        cursor += 1
                coordinate = H1CoordinateDecl(
                    name=name,
                    kind=kind_name,
                    size=size,
                    span=Span(line=token.line, col=token.col),
                )
                index = cursor
                continue
            index += 1
        return parameters, operators, basis, coordinate

    def _parse_h1_operator_expression(self, tokens: list[Token]) -> object | None:
        if not tokens:
            return None
        last = tokens[-1]
        nested = Parser(
            tokens + [Token(TokenKind.EOF, "", last.line, last.col)]
        )
        try:
            expression = nested._op_expression()
        except ParseError:
            return None
        self.diagnostics.extend(nested.diagnostics)
        return expression

    def _parse_h1_experiment_body(self, body: list[Token]) -> list[object]:
        """Preserve one reviewed H1 operation per source line."""

        lines: list[list[Token]] = []
        for token in body:
            if not lines or lines[-1][0].line != token.line:
                lines.append([])
            lines[-1].append(token)
        statements: list[object] = []
        for line in lines:
            if not line:
                continue
            lexemes = tuple(token.lexeme for token in line)
            first = line[0]
            span = Span(line=first.line, col=first.col)
            if first.lexeme == "dynamic" or "dynamic" in lexemes:
                statements.append(H1DynamicControl(source_tokens=lexemes, span=span))
            elif "mix" in lexemes:
                statements.append(H1Mixture(source_tokens=lexemes, span=span))
            elif "superpose" in lexemes:
                statements.append(
                    H1Superposition(source_tokens=lexemes, span=span)
                )
            elif "capply" in lexemes:
                statements.append(H1CoherentControl(source_tokens=lexemes, span=span))
            elif first.lexeme == "state" or "prepare" in lexemes:
                state_name = (
                    line[1].lexeme if first.lexeme == "state" and len(line) > 1 else None
                )
                bound_to: tuple[str, str] | None = None
                if "over" in lexemes:
                    over_index = lexemes.index("over")
                    if (
                        over_index + 3 < len(lexemes)
                        and line[over_index + 2].kind == TokenKind.DOT
                    ):
                        bound_to = (lexemes[over_index + 1], lexemes[over_index + 3])
                statements.append(
                    H1Prepare(
                        source_tokens=lexemes,
                        span=span,
                        state_name=state_name,
                        bound_to=bound_to,
                    )
                )
            elif "evolve" in lexemes:
                state_name = (
                    first.lexeme if first.kind == TokenKind.IDENT else None
                )
                theory_name = None
                if "under" in lexemes:
                    under_index = lexemes.index("under")
                    if under_index + 1 < len(lexemes):
                        theory_name = lexemes[under_index + 1]
                statements.append(
                    H1Evolve(
                        source_tokens=lexemes,
                        span=span,
                        state_name=state_name,
                        theory_name=theory_name,
                    )
                )
            elif "uncompute" in lexemes:
                statements.append(H1Uncompute(source_tokens=lexemes, span=span))
            elif "tracing_out" in lexemes:
                statements.append(H1TraceOut(source_tokens=lexemes, span=span))
            elif first.lexeme == "observable":
                statements.append(H1Observable(source_tokens=lexemes, span=span))
            elif first.lexeme == "measure":
                statements.append(H1Measure(source_tokens=lexemes, span=span))
        return statements

    def _scientific_scope_decl(self) -> ScientificScopeDecl:
        start = self._span()
        kind = self._advance().lexeme
        name = self._expect_ident_like()
        self._expect(TokenKind.LBRACE)
        depth = 1
        body: list[Token] = []
        while depth > 0 and not self._check(TokenKind.EOF):
            tok = self._advance()
            if tok.kind == TokenKind.LBRACE:
                depth += 1
            elif tok.kind == TokenKind.RBRACE:
                depth -= 1
                if depth == 0:
                    break
            body.append(tok)
        references: list[str] = []
        symbols: list[str] = []
        field_bindings: list[tuple[str, str, Span]] = []
        for index, tok in enumerate(body):
            if tok.kind != TokenKind.IDENT:
                continue
            direct_reference = index and body[index - 1].lexeme in {
                "theory",
                "experiment",
                "workflow",
                "uses",
            }
            assigned_reference = (
                index >= 2
                and body[index - 1].kind == TokenKind.EQ
                and body[index - 2].lexeme in {
                    "theory",
                    "experiment",
                    "workflow",
                    "uses",
                }
            )
            if direct_reference or assigned_reference:
                references.append(tok.lexeme)
            if index + 1 < len(body) and body[index + 1].kind == TokenKind.EQ:
                symbols.append(tok.lexeme)
                if (
                    index + 2 < len(body)
                    and body[index + 2].kind == TokenKind.IDENT
                ):
                    rhs = body[index + 2]
                    field_bindings.append(
                        (
                            tok.lexeme,
                            rhs.lexeme,
                            Span(line=rhs.line, col=rhs.col),
                        )
                    )
        if kind == "theory" and any(
            tok.lexeme in {"shots", "backend", "retry", "Host"} for tok in body
        ):
            self.diagnostics.append(
                {
                    "code": "PHASE_SCOPE_DEPENDENCY_ERROR",
                    "line": start.line,
                    "col": start.col,
                    "message": "Theory scope cannot reference execution/Host symbols",
                }
            )
        if kind == "theory" and any(tok.lexeme == "continuous_operator" for tok in body):
            self.diagnostics.append(
                {
                    "code": "DISCRETIZATION_REQUIRED_ERROR",
                    "line": start.line,
                    "col": start.col,
                    "message": "continuous operators require an explicit discretization contract",
                }
            )
        body_declarations = self._parse_scientific_body_declarations(body)
        registers = self._parse_system_registers(body) if kind == "system" else []
        if kind == "system":
            seen_registers: set[str] = set()
            for register_name, width in registers:
                if register_name in seen_registers:
                    self.diagnostics.append(
                        {
                            "code": "MULTI_REGISTER_SHAPE_ERROR",
                            "line": start.line,
                            "col": start.col,
                            "message": f"duplicate register `{register_name}` in system `{name}`",
                        }
                    )
                if width <= 0:
                    self.diagnostics.append(
                        {
                            "code": "MULTI_REGISTER_SHAPE_ERROR",
                            "line": start.line,
                            "col": start.col,
                            "message": f"register `{register_name}` requires a positive static width",
                        }
                    )
                seen_registers.add(register_name)
        workflow_fields, workflow_parameter_types = (
            self._parse_workflow_fields(body) if kind == "workflow" else ([], [])
        )
        return ScientificScopeDecl(
            kind=kind,
            name=name,
            references=references,
            symbols=symbols,
            span=start,
            body_declarations=tuple(body_declarations),
            workflow_fields=tuple(workflow_fields),
            workflow_parameter_types=tuple(workflow_parameter_types),
            registers=tuple(registers),
            field_bindings=tuple(field_bindings),
        )

    @staticmethod
    def _parse_system_registers(body: list[Token]) -> list[tuple[str, int]]:
        """Read the small, declarative `system` register-shape surface."""
        registers: list[tuple[str, int]] = []
        index = 0
        while index + 6 < len(body):
            if (
                body[index].lexeme == "register"
                and body[index + 1].kind == TokenKind.IDENT
                and body[index + 2].kind == TokenKind.COLON
                and body[index + 3].lexeme == "QubitRegister"
                and body[index + 4].kind == TokenKind.LT
                and body[index + 5].kind == TokenKind.INT
                and body[index + 6].kind in {TokenKind.GT, TokenKind.GE}
            ):
                width = int(body[index + 5].literal)
                registers.append((body[index + 1].lexeme, width))
                index += 7
                continue
            index += 1
        return registers

    def _discretization_decl(self) -> DiscretizationDecl:
        start = self._span()
        self._expect_ident_like()  # discretization
        name = self._expect_ident_like()
        self._expect(TokenKind.LBRACE)
        body: list[Token] = []
        depth = 1
        while depth > 0 and not self._check(TokenKind.EOF):
            token = self._advance()
            if token.kind == TokenKind.LBRACE:
                depth += 1
            elif token.kind == TokenKind.RBRACE:
                depth -= 1
                if depth == 0:
                    break
            body.append(token)
        field_heads = {"domain", "basis", "resolution", "boundary", "approximation", "error_bound"}
        fields: list[tuple[str, str]] = []
        index = 0
        while index < len(body):
            if body[index].lexeme not in field_heads:
                index += 1
                continue
            key = body[index].lexeme
            index += 1
            if index < len(body) and body[index].kind == TokenKind.EQ:
                index += 1
            values: list[str] = []
            while index < len(body) and body[index].lexeme not in field_heads:
                values.append(body[index].lexeme)
                index += 1
            if values:
                fields.append((key, self._normalize_contract_value(values)))
        return DiscretizationDecl(name=name, fields=tuple(fields), span=start)

    def _use_decl(self) -> Any:
        """`use Enum.*` (ADR 0177) or discretization `use Contract for … as …`."""
        start = self._span()
        self._expect_ident_like()  # use
        first = self._expect_ident_like()
        # ADR 0177: use OpsPhase.*
        if self._match(TokenKind.DOT) and self._match(TokenKind.STAR):
            from .ast_nodes import EnumUseDecl

            return EnumUseDecl(enum_name=first, span=start)
        # Discretization bridge: use Contract for source as alias
        contract = first
        self._expect(TokenKind.FOR)
        source_parts = [self._expect_ident_like()]
        while self._match(TokenKind.DOT):
            source_parts.append(self._expect_ident_like())
        as_name = self._expect_ident_like()
        if as_name != "as":
            raise ParseError("expected `as` in discretization bridge", start.line, start.col)
        alias = self._expect_ident_like()
        self._match(TokenKind.SEMI)
        return DiscretizationBridgeDecl(
            contract=contract,
            source=".".join(source_parts),
            alias=alias,
            span=start,
        )

    def _discretization_bridge_decl(self) -> DiscretizationBridgeDecl:
        """Legacy entry; prefer `_use_decl`."""
        return self._use_decl()  # type: ignore[return-value]

    @staticmethod
    def _normalize_contract_value(values: list[str]) -> str:
        value = " ".join(values)
        value = value.replace(" (", "(")
        value = value.replace("( ", "(").replace(" )", ")")
        value = value.replace("[ ", "[").replace(" ]", "]")
        return value

    def _parse_workflow_fields(self, body: list[Token]) -> tuple[list[tuple[str, str]], list[str]]:
        fields: list[tuple[str, str]] = []
        parameter_types: list[str] = []
        field_heads = {"experiment", "parameter", "observable", "until", "update", "backend"}
        index = 0
        while index < len(body):
            token = body[index]
            if token.lexeme not in field_heads:
                index += 1
                continue
            key = token.lexeme
            if key == "backend":
                self.diagnostics.append(
                    {
                        "code": "WORKFLOW_SURFACE_ERROR",
                        "line": token.line,
                        "col": token.col,
                        "message": "workflow surface cannot contain provider/backend values",
                    }
                )
            index += 1
            if key == "experiment" and index < len(body) and body[index].kind == TokenKind.EQ:
                index += 1
            if key == "update" and index < len(body) and body[index].kind == TokenKind.EQ:
                index += 1
            if key == "parameter":
                if index < len(body) and body[index].kind == TokenKind.IDENT:
                    fields.append((key, body[index].lexeme))
                    index += 1
                    if index < len(body) and body[index].kind == TokenKind.COLON:
                        index += 1
                        type_tokens: list[str] = []
                        while index < len(body) and body[index].lexeme not in field_heads:
                            type_tokens.append(body[index].lexeme)
                            index += 1
                        parameter_types.append("".join(type_tokens))
                continue
            if key == "observable":
                if index < len(body) and body[index].kind == TokenKind.IDENT:
                    value = body[index].lexeme
                    if value in {"Job", "Task", "ProviderSdk"}:
                        self.diagnostics.append(
                            {
                                "code": "WORKFLOW_SURFACE_ERROR",
                                "line": body[index].line,
                                "col": body[index].col,
                                "message": f"workflow cannot observe Host value `{value}`",
                            }
                        )
                    fields.append((key, value))
                    index += 1
                continue
            if key == "experiment":
                if index < len(body) and body[index].kind == TokenKind.IDENT:
                    fields.append((key, body[index].lexeme))
                    index += 1
                continue
            if key == "update":
                expression: list[Token] = []
                while index < len(body) and body[index].lexeme not in field_heads:
                    expression.append(body[index])
                    index += 1
                if len(expression) == 1 and expression[0].kind == TokenKind.IDENT:
                    fields.append((key, expression[0].lexeme))
                else:
                    self.diagnostics.append(
                        {
                            "code": "WORKFLOW_SURFACE_ERROR",
                            "line": token.line,
                            "col": token.col,
                            "message": "update must name a Host callback",
                        }
                    )
                continue
            expression: list[str] = []
            while index < len(body) and body[index].lexeme not in field_heads:
                expression.append(body[index].lexeme)
                index += 1
            if key == "until" and expression:
                fields.append((key, " ".join(expression)))
        return fields, parameter_types

    def _parse_scientific_body_declarations(self, body: list[Token]) -> list[Any]:
        """Preserve supported declaration forms inside a scientific scope."""

        if not body:
            return []
        eof = body[-1]
        nested = Parser(body + [Token(TokenKind.EOF, "", eof.line, eof.col)])
        declarations: list[Any] = []
        while not nested._check(TokenKind.EOF):
            if nested._is_type_first_start():
                saved = nested.i
                try:
                    declarations.append(nested._type_first_bind())
                    nested._match(TokenKind.SEMI)
                    continue
                except ParseError:
                    nested.i = saved
            nested._advance()
        self.diagnostics.extend(nested.diagnostics)
        return declarations

    def _check_scientific_scope_graph(self, decls: list) -> None:
        scopes = {d.name: d for d in decls if isinstance(d, ScientificScopeDecl)}
        graph = {
            name: [ref for ref in decl.references if ref in scopes]
            for name, decl in scopes.items()
        }
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(name: str) -> None:
            if name in visiting:
                decl = scopes[name]
                self.diagnostics.append(
                    {
                        "code": "PHASE_SCOPE_CYCLE_ERROR",
                        "line": decl.span.line,
                        "col": decl.span.col,
                        "message": f"scientific scope dependency cycle includes `{name}`",
                    }
                )
                return
            if name in visited:
                return
            visiting.add(name)
            for child in graph.get(name, []):
                visit(child)
            visiting.remove(name)
            visited.add(name)

        for name in graph:
            visit(name)

    def _is_toplevel_executable_start(self) -> bool:
        # ADR 0180: bare `name = expr` inferred bind is executable.
        bare_infer = (
            self._check(TokenKind.IDENT) and self._peek_at_kind(1) == TokenKind.EQ
        )
        # ADR 0184 / LISS-0305: `J, h = 1.0, 0.5` multi-name inferred bind.
        multi_infer = (
            self._check(TokenKind.IDENT)
            and self._peek_at_kind(1) == TokenKind.COMMA
        )
        return (
            bare_infer
            or multi_infer
            or self._check(TokenKind.STATE)
            or self._check(TokenKind.MEASURE)
            or self._check(TokenKind.SNAPSHOT)
            or self._check(TokenKind.LET)
            or self._check(TokenKind.LPAREN)
            or self._is_type_first_start()
            or self._check(TokenKind.EVOLVE)
            or self._check(TokenKind.WHEN)
            or self._check(TokenKind.SUPERPOSE)
            or self._check(TokenKind.COIN)
            or self._check(TokenKind.DIRAC)
            or self._check(TokenKind.VACUUM)
            or self._check(TokenKind.INSPECT)
            or self._check(TokenKind.FOREACH)
        )

    def _skip_until_toplevel_resync(self) -> None:
        """Recover after TOPLEVEL_EXECUTION_ERROR: skip one statement-ish chunk."""
        # Prefer consuming a well-formed stmt so diagnostics stay localized.
        try:
            self._stmt()
            return
        except ParseError:
            pass
        depth = 0
        while not self._check(TokenKind.EOF):
            tok = self._peek()
            if depth == 0 and tok.kind in {
                TokenKind.PUBLIC,
                TokenKind.FUN,
                TokenKind.CLASS,
                TokenKind.INTERFACE,
                TokenKind.PACKAGE,
                TokenKind.IMPORT,
            }:
                return
            if tok.kind == TokenKind.LBRACE:
                depth += 1
            elif tok.kind == TokenKind.RBRACE:
                depth = max(0, depth - 1)
            self._advance()

    def _package(self) -> PackageDecl:
        sp = self._span()
        self._expect(TokenKind.PACKAGE)
        path = self._dotted_path()
        return PackageDecl(path=path, span=sp)

    def _import(self) -> ImportDecl:
        """`import a.b.mod` / selective `{A,B}` (0177) / relative `.path` (0183)."""
        sp = self._span()
        self._expect(TokenKind.IMPORT)
        path: list[str] = []
        # ADR 0183: leading `.` / `..` package-relative segments.
        # Lexer emits `..` as RANGE, not DOT+DOT.
        while True:
            if self._match(TokenKind.DOT):
                path.append(".")
                continue
            if self._match(TokenKind.RANGE):
                path.append(".")
                path.append(".")
                continue
            break
        if not path:
            path.append(self._expect_ident_like())
        else:
            # `.domain` or `..shared` after one or more dots
            if self._check(TokenKind.IDENT) or self._check(TokenKind.LBRACE):
                if self._check(TokenKind.IDENT):
                    path.append(self._expect_ident_like())
            else:
                raise ParseError(
                    "relative import expects a path after `.`", sp.line, sp.col
                )
        selected: list[str] | None = None
        while self._match(TokenKind.DOT):
            if self._check(TokenKind.LBRACE):
                self._expect(TokenKind.LBRACE)
                selected = [self._expect_ident_like()]
                while self._match(TokenKind.COMMA):
                    selected.append(self._expect_ident_like())
                self._expect(TokenKind.RBRACE)
                break
            if self._match(TokenKind.STAR):
                path.append("*")
                break
            path.append(self._expect_ident_like())
        # trailing selective after relative: import .domain.{A}
        if selected is None and self._match(TokenKind.LBRACE):
            selected = [self._expect_ident_like()]
            while self._match(TokenKind.COMMA):
                selected.append(self._expect_ident_like())
            self._expect(TokenKind.RBRACE)
        name = path[-1] if path else ""
        return ImportDecl(path=path, name=name, span=sp, selected=selected)

    def _dotted_path(self) -> list[str]:
        parts = [self._expect_ident_like()]
        while self._match(TokenKind.DOT):
            parts.append(self._expect_ident_like())
        return parts

    def _dotted_path_import(self) -> list[str]:
        """`staqex.math` or `staqex.math.*` (legacy helper; prefer `_import`)."""
        parts = [self._expect_ident_like()]
        while self._match(TokenKind.DOT):
            if self._match(TokenKind.STAR):
                parts.append("*")
                break
            parts.append(self._expect_ident_like())
        return parts

    def _is_visibility_start(self) -> bool:
        return self._check(TokenKind.PUBLIC) or self._check(TokenKind.PRIVATE)

    def _peek_after_visibility(self) -> TokenKind | None:
        """Look at token after an optional visibility keyword (`pub`/`private`)."""
        j = self.i
        if self.tokens[j].kind in {TokenKind.PUBLIC, TokenKind.PRIVATE}:
            j += 1
        if j < len(self.tokens):
            return self.tokens[j].kind
        return None

    def _parse_visibility(self) -> str:
        """ADR 0058: `pub` | `private` | (default → module-private)."""
        if self._match(TokenKind.PUBLIC):
            return "public"
        if self._match(TokenKind.PRIVATE):
            return "private"
        return "module"

    @staticmethod
    def _apply_underscore_privacy(name: str, vis: str) -> str:
        """Leading `_` ⇒ class/file private (noise-free encapsulation)."""
        if name.startswith("_") and not name.startswith("__"):
            return "private"
        return vis

    def parse_module_info(self) -> ModuleInfoDecl:
        """Parse a `module-info.sqx` compilation unit (ADR 0058)."""
        sp = self._span()
        self._expect(TokenKind.MODULE)
        name = self._dotted_path()
        exports: list[list[str]] = []
        requires: list[list[str]] = []
        self._expect(TokenKind.LBRACE)
        while not self._check(TokenKind.RBRACE) and not self._check(TokenKind.EOF):
            if self._match(TokenKind.EXPORTS):
                exports.append(self._dotted_path())
                self._match(TokenKind.SEMI)
            elif self._match(TokenKind.REQUIRES):
                requires.append(self._dotted_path())
                self._match(TokenKind.SEMI)
            elif self._check(TokenKind.FORBIDDEN) or self._check(TokenKind.RETIRED):
                self._advance()
            else:
                tok = self._peek()
                self.diagnostics.append(
                    {
                        "code": "PARSE_ERROR",
                        "line": tok.line,
                        "col": tok.col,
                        "message": (
                            f"expected `exports` or `requires` in module, "
                            f"got `{tok.lexeme}`"
                        ),
                    }
                )
                self._advance()
        self._expect(TokenKind.RBRACE)
        return ModuleInfoDecl(name=name, exports=exports, requires=requires, span=sp)

    def _fun_decl(self) -> FunDecl:
        sp = self._span()
        vis = self._parse_visibility()
        self._expect(TokenKind.FUN)
        name = self._expect_ident_like()
        vis = self._apply_underscore_privacy(name, vis)
        generic_bounds = self._generic_bounds()
        self._expect(TokenKind.LPAREN)
        params: list[Param] = []
        if not self._check(TokenKind.RPAREN):
            params.append(self._param())
            while self._match(TokenKind.COMMA):
                params.append(self._param())
        self._expect(TokenKind.RPAREN)
        return_type = None
        if self._match(TokenKind.ARROW):
            return_type = self._type_ref()
        effects = self._effects_clause()
        operator_return = return_type is not None and return_type.name == "Operator"
        body = self._block(operator_return=operator_return)
        if name not in {"init", "main"} and return_type is None:
            self.diagnostics.append(
                {
                    "code": "MISSING_RETURN_TYPE",
                    "line": sp.line,
                    "col": sp.col,
                    "message": f"`{name}` must declare an explicit return type",
                }
            )
        return FunDecl(
            name=name,
            params=params,
            body=body,
            span=sp,
            return_type=return_type,
            visibility=vis,
            effects=tuple(effects),
            generic_bounds=tuple(generic_bounds),
        )

    def _effects_clause(self) -> list[str]:
        """Parse the optional fixed effect annotation after a return type."""
        if self._peek().lexeme != "effects":
            return []
        self._advance()
        self._expect(TokenKind.LBRACE)
        effects: list[str] = []
        if not self._check(TokenKind.RBRACE):
            effects.append(self._expect_ident_like())
            while self._match(TokenKind.COMMA):
                effects.append(self._expect_ident_like())
        self._expect(TokenKind.RBRACE)
        return effects

    def _generic_bounds(self) -> list[tuple[str, str]]:
        """Parse the accepted inline `<T: Interface>` bound form."""
        if not self._match(TokenKind.LT):
            return []
        bounds: list[tuple[str, str]] = []
        while True:
            type_param = self._expect_ident_like()
            self._expect(TokenKind.COLON)
            bounds.append((type_param, self._expect_ident_like()))
            if not self._match(TokenKind.COMMA):
                break
        self._expect(TokenKind.GT)
        return bounds

    def _param(self) -> Param:
        name = self._expect_ident_like()
        ty = None
        if self._match(TokenKind.COLON):
            ty = self._type_ref()
        return Param(name=name, ty=ty)

    def _type_ref(self) -> TypeRef:
        """Type reference with symbolic/numeric args, e.g. `QubitRegister<3>`."""
        # Product carrier: (T1, T2, …)
        if self._match(TokenKind.LPAREN):
            args = [self._type_ref()]
            while self._match(TokenKind.COMMA):
                args.append(self._type_ref())
            self._expect(TokenKind.RPAREN)
            return TypeRef(name="Tuple", args=args)

        tok = self._peek()
        if tok.kind == TokenKind.INT:
            name = str(self._advance().literal)
        elif tok.kind == TokenKind.IDENT:
            name = self._advance().lexeme
            # ADR 0055: dotted type path Topology.ChainLattice
            while self._match(TokenKind.DOT):
                name = name + "." + self._expect_ident_like()
        elif tok.kind == TokenKind.STATE and tok.lexeme == "State":
            name = self._advance().lexeme
        else:
            raise ParseError(f"expected type name, got `{tok.lexeme}`", tok.line, tok.col)
        args: list[TypeRef] = []
        # LISS-0143 / LISS-0144: `Float[N]` / `Float[N][M]…` classical tensors
        if name == "Float" and self._check(TokenKind.LBRACKET):
            dims: list[TypeRef] = []
            while self._match(TokenKind.LBRACKET):
                n_tok = self._peek()
                if n_tok.kind != TokenKind.INT:
                    raise ParseError(
                        "`Float[N]…` requires positive integer lengths",
                        n_tok.line,
                        n_tok.col,
                    )
                self._advance()
                self._expect(TokenKind.RBRACKET)
                dims.append(TypeRef(name=str(n_tok.literal)))
            return TypeRef(name="Float", args=dims)
        if self._match(TokenKind.LT):
            args.append(self._type_ref())
            if self._match(TokenKind.RANGE):
                if name != "Index":
                    tok = self._peek()
                    raise ParseError("inclusive ranges are only valid for `Index`", tok.line, tok.col)
                args.append(self._type_ref())
            else:
                while self._match(TokenKind.COMMA):
                    args.append(self._type_ref())
            if self._check(TokenKind.GT):
                self._advance()
            elif self._check(TokenKind.GE):
                self._advance()
            else:
                t = self._peek()
                raise ParseError("expected `>` to close type arguments", t.line, t.col)
        return TypeRef(name=name, args=args)

    def _namespace_decl(self) -> NamespaceDecl:
        """`namespace Topology` / `namespace Physics.Parameters { … }` (ADR 0055)."""
        sp = self._span()
        self._expect(TokenKind.NAMESPACE)
        path = [self._expect_ident_like()]
        while self._match(TokenKind.DOT):
            path.append(self._expect_ident_like())
        decls: list = []
        self._expect(TokenKind.LBRACE)
        while not self._check(TokenKind.RBRACE) and not self._check(TokenKind.EOF):
            if self._check(TokenKind.NAMESPACE):
                decls.append(self._namespace_decl())
            elif self._check(TokenKind.ENUM) or (
                self._is_visibility_start()
                and self._peek_after_visibility() == TokenKind.ENUM
            ):
                vis = self._parse_visibility()
                ed = self._enum_decl()
                ed.visibility = vis  # type: ignore[assignment]
                decls.append(ed)
            elif self._check(TokenKind.STRUCT) or (
                self._is_visibility_start()
                and self._peek_after_visibility() == TokenKind.STRUCT
            ):
                vis = self._parse_visibility()
                sd = self._struct_decl()
                sd.visibility = vis  # type: ignore[assignment]
                decls.append(sd)
            elif (
                self._check(TokenKind.PUBLIC)
               
                or self._check(TokenKind.PRIVATE)
                or self._check(TokenKind.FUN)
            ):
                nxt = self._peek_after_visibility()
                if nxt == TokenKind.CLASS or (
                    self._is_visibility_start()
                    and self._peek_after_visibility() == TokenKind.CLASS
                ):
                    vis = self._parse_visibility()
                    cd = self._class_decl()
                    cd.visibility = vis  # type: ignore[assignment]
                    decls.append(cd)
                else:
                    decls.append(self._fun_decl())
            elif self._check(TokenKind.CLASS) or (
                self._is_visibility_start()
                and self._peek_after_visibility() == TokenKind.CLASS
            ):
                vis = self._parse_visibility()
                cd = self._class_decl()
                cd.visibility = vis  # type: ignore[assignment]
                decls.append(cd)
            elif self._check(TokenKind.INTERFACE):
                decls.append(self._interface_decl())
            elif self._check(TokenKind.FORBIDDEN) or self._check(TokenKind.RETIRED):
                self._advance()
            elif self._check(TokenKind.ERROR):
                self._advance()
            else:
                tok = self._peek()
                self.diagnostics.append(
                    {
                        "code": "PARSE_ERROR",
                        "line": tok.line,
                        "col": tok.col,
                        "message": (
                            f"unexpected `{tok.lexeme}` inside namespace "
                            f"`{'.'.join(path)}`"
                        ),
                    }
                )
                self._advance()
        self._expect(TokenKind.RBRACE)
        return NamespaceDecl(path=path, decls=decls, span=sp)

    def _enum_decl(self) -> EnumDecl:
        sp = self._span()
        self._expect(TokenKind.ENUM)
        name = self._expect_ident_like()
        variants: list[str] = []
        self._expect(TokenKind.LBRACE)
        while not self._check(TokenKind.RBRACE) and not self._check(TokenKind.EOF):
            variants.append(self._expect_ident_like())
            self._match(TokenKind.COMMA)  # optional trailing commas
        self._expect(TokenKind.RBRACE)
        if not variants:
            self.diagnostics.append(
                {
                    "code": "PARSE_ERROR",
                    "line": sp.line,
                    "col": sp.col,
                    "message": f"enum `{name}` must declare at least one variant",
                }
            )
        return EnumDecl(name=name, variants=variants, span=sp)

    def _struct_decl(self) -> StructDecl:
        sp = self._span()
        self._expect(TokenKind.STRUCT)
        name = self._expect_ident_like()
        fields: list[FieldDecl] = []
        self._expect(TokenKind.LBRACE)
        while not self._check(TokenKind.RBRACE) and not self._check(TokenKind.EOF):
            fields.append(self._field_decl(default_mutable=False))
            self._match(TokenKind.COMMA)
        self._expect(TokenKind.RBRACE)
        # struct fields are always immutable values
        for f in fields:
            f.mutable = False
        return StructDecl(name=name, fields=fields, span=sp)

    def _field_decl(self, *, default_mutable: bool) -> FieldDecl:
        """`[vis] val|var name: Type [= e]`."""
        sp = self._span()
        vis = self._parse_visibility()
        mutable = default_mutable
        if self._match(TokenKind.VAR):
            mutable = True
        elif self._match(TokenKind.VAL):
            mutable = False
        name = self._expect_ident_like()
        vis = self._apply_underscore_privacy(name, vis)
        self._expect(TokenKind.COLON)
        ty = self._type_ref()
        default = None
        if self._match(TokenKind.EQ):
            default = self._expression()
        return FieldDecl(
            name=name,
            ty=ty,
            mutable=mutable,
            default=default,
            span=sp,
            visibility=vis,  # type: ignore[arg-type]
        )

    def _class_decl(self) -> ClassDecl:
        sp = self._span()
        self._expect(TokenKind.CLASS)
        name = self._expect_ident_like()
        ifaces: list[str] = []
        if self._match(TokenKind.COLON):
            ifaces.append(self._expect_ident_like())
            while self._match(TokenKind.COMMA):
                ifaces.append(self._expect_ident_like())
        fields: list[StateBind] = []
        members: list[FieldDecl] = []
        methods: list[FunDecl] = []
        if self._match(TokenKind.LBRACE):
            while not self._check(TokenKind.RBRACE) and not self._check(TokenKind.EOF):
                if self._check(TokenKind.FORBIDDEN) or self._check(TokenKind.RETIRED):
                    self._advance()
                    continue
                if (
                    self._check(TokenKind.PUBLIC)
                   
                    or self._check(TokenKind.PRIVATE)
                    or self._check(TokenKind.FUN)
                ):
                    # method or vis+val — distinguish by peek
                    nxt = self._peek_after_visibility()
                    if nxt == TokenKind.FUN or self._check(TokenKind.FUN):
                        methods.append(self._fun_decl())
                        continue
                    if nxt in {TokenKind.VAL, TokenKind.VAR}:
                        members.append(self._field_decl(default_mutable=False))
                        continue
                if self._check(TokenKind.VAL) or self._check(TokenKind.VAR):
                    members.append(self._field_decl(default_mutable=False))
                    continue
                if self._is_type_first_start():
                    fields.append(self._type_first_bind())
                else:
                    tok = self._peek()
                    self.diagnostics.append(
                        {
                            "code": "PARSE_ERROR",
                            "line": tok.line,
                            "col": tok.col,
                            "message": (
                                f"class `{name}` expects Type-First / val/var field "
                                f"or `fn` method; got `{tok.lexeme}`"
                            ),
                        }
                    )
                    self._advance()
            self._expect(TokenKind.RBRACE)
        return ClassDecl(
            name=name,
            ifaces=ifaces,
            span=sp,
            fields=fields,
            members=members,
            methods=methods,
        )

    def _interface_decl(self) -> InterfaceDecl:
        sp = self._span()
        self._expect(TokenKind.INTERFACE)
        name = self._expect_ident_like()
        type_params: list[str] = []
        if self._match(TokenKind.LT):
            type_params.append(self._expect_ident_like())
            while self._match(TokenKind.COMMA):
                type_params.append(self._expect_ident_like())
            self._expect(TokenKind.GT)
        if self._match(TokenKind.LBRACE):
            depth = 1
            while depth > 0 and not self._check(TokenKind.EOF):
                if self._check(TokenKind.LBRACE):
                    depth += 1
                elif self._check(TokenKind.RBRACE):
                    depth -= 1
                self._advance()
        return InterfaceDecl(name=name, span=sp, type_params=tuple(type_params))

    def _impl_decl(self) -> ImplDecl:
        sp = self._span()
        self._expect(TokenKind.IMPL)
        interface = self._type_ref()
        self._expect(TokenKind.FOR)
        target = self._type_ref()
        self._expect(TokenKind.LBRACE)
        methods: list[FunDecl] = []
        while not self._check(TokenKind.RBRACE) and not self._check(TokenKind.EOF):
            methods.append(self._fun_decl())
        self._expect(TokenKind.RBRACE)
        return ImplDecl(interface=interface, target=target, methods=methods, span=sp)

    def _block(self, *, operator_return: bool = False) -> Block:
        sp = self._span()
        self._expect(TokenKind.LBRACE)
        stmts = []
        result = None
        while not self._check(TokenKind.RBRACE) and not self._check(TokenKind.EOF):
            if self._check(TokenKind.FORBIDDEN) or self._check(TokenKind.RETIRED):
                self._advance()
                continue
            if self._check(TokenKind.ERROR):
                self._advance()
                continue
            if self._check(TokenKind.RETURN):
                returned = self._return_stmt(operator_return=operator_return)
                stmts.append(returned)
                result = returned.expr
                if not self._check(TokenKind.RBRACE):
                    tok = self._peek()
                    self.diagnostics.append(
                        {
                            "code": "RETURN_NOT_TERMINAL",
                            "line": tok.line,
                            "col": tok.col,
                            "message": "`return` must be the final statement in a function",
                        }
                    )
                    while not self._check(TokenKind.RBRACE) and not self._check(TokenKind.EOF):
                        self._advance()
                break
            saved = self.i
            try:
                stmts.append(self._stmt())
            except ParseError as e:
                # Named hard diagnostics (e.g. ADR 0193 timing-intent failures)
                # must not be swallowed by the implicit-final-expression recovery.
                if getattr(e, "code", "PARSE_ERROR") != "PARSE_ERROR":
                    raise
                # Implicit final expressions are retained only for parser
                # recovery; the typechecker rejects them for ordinary fns.
                self.i = saved
                result = self._expression()
                if not self._check(TokenKind.RBRACE):
                    tok = self._peek()
                    raise ParseError(
                        "function result expression must be the final item in a block",
                        tok.line,
                        tok.col,
                    )
                break
        self._expect(TokenKind.RBRACE)
        return Block(stmts=stmts, span=sp, result=result)

    def _return_stmt(self, *, operator_return: bool = False) -> ReturnStmt:
        sp = self._span()
        self._expect(TokenKind.RETURN)
        expression = self._op_expression() if operator_return else self._expression()
        return ReturnStmt(expr=expression, span=sp)

    def _stmt(self):
        if self._check(TokenKind.FOREACH):
            return self._foreach_stmt()
        if self._check(TokenKind.DYNAMIC):
            return self._dynamic_qpu_stmt()
        if self._check(TokenKind.STATE):
            return self._state_bind()
        if self._check(TokenKind.MEASURE):
            return self._measure()
        if self._check(TokenKind.SNAPSHOT):
            return self._snapshot()
        if self._check(TokenKind.LPAREN):
            return self._tuple_bind()
        if self._is_type_first_start():
            return self._type_first_bind()
        # ADR 0197 / LISS-0382: contextual soft `match <ctrl> { … }`.
        if self._check(TokenKind.IDENT) and self._peek().lexeme == "match":
            return self._match_stmt()
        # ADR 0180: inferred local bind `name = expr` (no type annotation).
        if self._check(TokenKind.IDENT) and self._peek_at_kind(1) == TokenKind.EQ:
            return self._inferred_bind()
        # ADR 0184 / LISS-0305: multi-name inferred bind `J, h = 1.0, 0.5`.
        if self._check(TokenKind.IDENT) and self._peek_at_kind(1) == TokenKind.COMMA:
            return self._multi_inferred_bind()
        # `this.field = expr` / `obj.field = expr`
        if self._check(TokenKind.THIS) or self._check(TokenKind.IDENT):
            saved = self.i
            try:
                target = self._call()
                if self._match(TokenKind.EQ) and isinstance(target, Attr):
                    sp = target.span
                    value = self._expression()
                    return AssignStmt(target=target, value=value, span=sp)
                if isinstance(target, Call):
                    return ExprStmt(expr=target, span=target.span)
            except ParseError:
                pass
            self.i = saved
        tok = self._peek()
        raise ParseError(f"expected statement, got `{tok.lexeme}`", tok.line, tok.col)

    def _inferred_bind(self) -> StateBind:
        """ADR 0180: `J = 1.0` / `H = Z + X` without a leading type."""
        sp = self._span()
        name = self._expect_ident_like()
        self._expect(TokenKind.EQ)
        # Prefer OpDSL when RHS looks like an operator atom/family.
        if (
            self._peek().kind == TokenKind.IDENT
            and self._peek().lexeme in _OPERATOR_DSL_RESERVED_ATOMS
        ) or self._peek().kind in (TokenKind.MINUS,):
            # Heuristic: leading `-` or Pauli-like atom → Operator RHS.
            saved = self.i
            try:
                expr = self._op_expression()  # type: ignore[assignment]
            except ParseError:
                self.i = saved
                expr = self._expression()
        else:
            expr = self._expression()
        return StateBind(names=[name], expr=expr, span=sp, ty=None)

    def _multi_inferred_bind(self) -> StateBind:
        """ADR 0184: `J, h = 1.0, 0.5` / `s0, s1 = |+>, |+>` (no parens)."""
        sp = self._span()
        names = [self._expect_ident_like()]
        while self._match(TokenKind.COMMA):
            names.append(self._expect_ident_like())
        if len(names) < 2:
            raise ParseError(
                "multi-name bind expects at least two names",
                sp.line,
                sp.col,
            )
        self._expect(TokenKind.EQ)
        items = [self._expression()]
        while self._match(TokenKind.COMMA):
            items.append(self._expression())
        if len(items) != len(names):
            raise ParseError(
                f"multi-name bind arity mismatch: {len(names)} names vs "
                f"{len(items)} values",
                sp.line,
                sp.col,
            )
        return StateBind(
            names=names,
            expr=TupleExpr(items=items, span=sp),
            span=sp,
            ty=None,
        )

    def _foreach_stmt(self) -> ForEachStmt:
        """Parse static circuit elaboration: `forEach q in register(3) { … }`."""
        sp = self._span()
        self._expect(TokenKind.FOREACH)
        element = self._expect_ident_like()
        self._expect(TokenKind.IN)
        collection = self._expression()
        body = self._block()
        return ForEachStmt(element=element, collection=collection, body=body, span=sp)

    def _dynamic_qpu_stmt(self) -> DynamicQpuStmt:
        """Parse an explicit dynamic lane for capability diagnostics.

        ADR 0193 / LISS-0381: optional contextual soft keyword
        `within <name>` after `dynamic qpu`. `within` is not a global hard
        keyword (vision §2.2 — ordinary identifier `within` must remain
        usable outside this clause).
        """
        sp = self._span()
        self._expect(TokenKind.DYNAMIC)
        name = self._expect_ident_like()
        if name != "qpu":
            raise ParseError(
                "dynamic lane must be written as `dynamic qpu { … }`",
                sp.line,
                sp.col,
            )
        timing_intent = self._optional_dynamic_timing_intent()
        return DynamicQpuStmt(
            body=self._block(),
            span=sp,
            timing_intent=timing_intent,
        )

    def _match_stmt(self) -> MatchStmt:
        """Parse soft `match <scrutinee> { <pat> => {…} … }` (ADR 0197)."""
        sp = self._span()
        match_tok = self._advance()
        if match_tok.lexeme != "match":
            raise ParseError(
                "expected `match`",
                match_tok.line,
                match_tok.col,
            )
        scrutinee = self._expect_ident_like()
        self._expect(TokenKind.LBRACE)
        arms: list[MatchArm] = []
        while not self._check(TokenKind.RBRACE) and not self._check(TokenKind.EOF):
            arm_sp = self._span()
            pat_tok = self._peek()
            if pat_tok.kind == TokenKind.INT:
                pattern = self._advance().lexeme
            elif pat_tok.kind == TokenKind.IDENT:
                pattern = self._expect_ident_like()
            else:
                raise ParseError(
                    "match arm expects an integer or identifier pattern",
                    pat_tok.line,
                    pat_tok.col,
                )
            self._expect(TokenKind.FAT_ARROW)
            body = self._block()
            arms.append(MatchArm(pattern=pattern, body=body, span=arm_sp))
        self._expect(TokenKind.RBRACE)
        if not arms:
            raise ParseError(
                "`match` requires at least one finite arm",
                sp.line,
                sp.col,
            )
        return MatchStmt(scrutinee=scrutinee, arms=arms, span=sp)

    def _optional_dynamic_timing_intent(self) -> str | None:
        """Parse optional `within <name>`; fail closed on malformed forms."""
        peek = self._peek()
        if not (peek.kind == TokenKind.IDENT and peek.lexeme == "within"):
            return None
        within_tok = self._advance()
        intent_tok = self._peek()
        if intent_tok.kind != TokenKind.IDENT:
            raise ParseError(
                "dynamic qpu `within` requires a timing-intent identifier",
                within_tok.line,
                within_tok.col,
                code="DYNAMIC_TIMING_INTENT_MALFORMED",
            )
        if self._peek_at_kind(1) == TokenKind.LPAREN:
            raise ParseError(
                "dynamic qpu `within` requires a bare timing-intent "
                "identifier, not a call",
                intent_tok.line,
                intent_tok.col,
                code="DYNAMIC_TIMING_INTENT_MALFORMED",
            )
        return self._expect_ident_like()

    def _is_type_first_start(self) -> bool:
        """Type-First: physical quantity / State / Delta heads the declaration."""
        from .dimensions import TYPE_HEADS

        tok = self._peek()
        if tok.kind != TokenKind.IDENT:
            return False
        name = tok.lexeme
        # ADR 0180: `Name = expr` is inferred bind, not Type-First (no second name).
        if self._peek_at_kind(1) == TokenKind.EQ:
            return False
        if name in TYPE_HEADS:
            return True
        # Capitalized / dotted type head: `Float J`, `D.Item a`, `Float[N] a`, …
        if not (name and name[0].isupper()):
            return False
        j = 1
        # Skip `Type.Path` segments and optional type args `[…]` / `<…>`
        while True:
            k = self._peek_at_kind(j)
            if k == TokenKind.DOT and self._peek_at_kind(j + 1) == TokenKind.IDENT:
                j += 2
                continue
            if k in (TokenKind.LBRACKET, TokenKind.LT):
                # Approximate: treat as type-first when binder name follows later.
                return True
            break
        return self._peek_at_kind(j) == TokenKind.IDENT

    def _second_quantized_rhs_is_op_dsl(self) -> bool:
        """`FermionOperator`/`BosonOperator`/`SpinOperator`/`QubitOperator`
        RHS: detect a second-quantized OpDSL expression (`create[i]`/
        `annihilate[i]` atoms) even behind a chain of leading scalar
        coefficients -- a bare literal or name (`1.0 * create[0]...`,
        `e0 * create[0]...`), or a parenthesized compound expression
        (`(e0 + e1) * create[0]...`) -- not just when the atom is the very
        first token (LISS-0331)."""
        offset = 0
        for _ in range(6):  # bounded: a handful of coefficient terms at most
            if (
                self._peek_at_kind(offset) == TokenKind.IDENT
                and self._peek_at_kind(offset + 1) == TokenKind.LBRACKET
            ):
                return True
            if self._peek_at_kind(offset) == TokenKind.LPAREN:
                depth = 1
                inner_start = offset + 1
                offset += 1
                while depth > 0:
                    kind = self._peek_at_kind(offset)
                    if kind is None:
                        return False
                    if kind == TokenKind.LPAREN:
                        depth += 1
                    elif kind == TokenKind.RPAREN:
                        depth -= 1
                    offset += 1
                # LISS-0367: the parenthesized group may itself contain
                # the second-quantized atom (`K * (create[0] *
                # annihilate[0])`), not just wrap a compound coefficient
                # ahead of a further `* create[...]` chain -- scan
                # inside it too before assuming it was only a
                # coefficient grouping.
                for inner_offset in range(inner_start, offset - 1):
                    if (
                        self._peek_at_kind(inner_offset) == TokenKind.IDENT
                        and self._peek_at_kind(inner_offset + 1) == TokenKind.LBRACKET
                    ):
                        return True
            elif self._peek_at_kind(offset) in (
                TokenKind.INT,
                TokenKind.FLOAT,
                TokenKind.IDENT,
            ):
                offset += 1
            else:
                return False
            if self._peek_at_kind(offset) != TokenKind.STAR:
                return False
            offset += 1
        return False

    def _type_first_bind(self) -> StateBind:
        """`Mass m = e` / `State<(A,B)> (c, x) = e` / `Operator H = …`."""
        sp = self._span()
        ty = self._type_ref()
        if self._match(TokenKind.LPAREN):
            names = [self._expect_ident_like()]
            while self._match(TokenKind.COMMA):
                names.append(self._expect_ident_like())
            self._expect(TokenKind.RPAREN)
        else:
            names = [self._expect_ident_like()]
        self._expect(TokenKind.EQ)
        if ty.name == "Operator":
            if len(names) != 1:
                raise ParseError("Operator bind expects a single name", sp.line, sp.col)
            # LISS-0073: Dirac ket/bra and algebra brackets desugar to `Call`
            # nodes (`outer` / `projector` / `inner` / `commutator` /
            # `anticommutator`), not OpDSL atoms.
            if self._peek().kind in (TokenKind.KET, TokenKind.BRA):
                expr = self._expression()
            elif self._peek().kind in (TokenKind.LBRACKET, TokenKind.LBRACE):
                self._commutator_bracket_context = (
                    self._peek().kind == TokenKind.LBRACKET
                )
                try:
                    expr = self._expression()
                finally:
                    self._commutator_bracket_context = False
            elif (
                self._peek().kind == TokenKind.IDENT
                and (
                    self._peek().lexeme not in _OPERATOR_DSL_RESERVED_ATOMS
                    or self._peek().lexeme in self._function_names
                    or self._peek().lexeme in _ALGEBRA_EXPR_CALLEES
                )
                and self._peek_at_kind(1) == TokenKind.LPAREN
            ):
                expr = self._expression()
            elif (
                # LISS-0139 / LISS-0358: Operator H = recv.method(…), any
                # depth of dotted attribute chain before the call (e.g.
                # `outer.inner.method()`), not just exactly one `.`.
                self._peek().kind == TokenKind.IDENT
                and self._dotted_call_lookahead()
            ):
                expr = self._expression()
            else:
                expr = self._op_expression()  # type: ignore[assignment]
        elif ty.name in {
            "FermionOperator",
            "BosonOperator",
            "SpinOperator",
            "QubitOperator",
        }:
            if self._second_quantized_rhs_is_op_dsl():
                # Second-quantized indexed atoms share the Operator DSL AST;
                # only mapping calls such as `map(Hf, JordanWigner)` remain
                # ordinary expression calls.
                expr = self._op_expression()
            else:
                expr = self._expression()
        elif (
            # ADR 0118 / LISS-0149: `Float[M…] row = h[i]` OpDSL indexed
            # RHS -- LISS-0369: any depth of dotted field access before
            # the index (`m.h[i]`), not just a bare variable.
            ty.name == "Float"
            and len(ty.args) >= 1
            and self._peek().kind == TokenKind.IDENT
            and self._dotted_index_lookahead()
        ):
            expr = self._op_expression()  # type: ignore[assignment]
        else:
            expr = self._expression()
        return StateBind(names=names, expr=expr, span=sp, ty=ty)  # type: ignore[arg-type]

    def _tuple_bind(self) -> StateBind:
        """`(x, p) = expr` — Type-First-friendly tuple bind without `state`."""
        sp = self._span()
        self._expect(TokenKind.LPAREN)
        names = [self._expect_ident_like()]
        while self._match(TokenKind.COMMA):
            names.append(self._expect_ident_like())
        self._expect(TokenKind.RPAREN)
        self._expect(TokenKind.EQ)
        expr = self._expression()
        return StateBind(names=names, expr=expr, span=sp, ty=None)

    def _state_bind(self) -> StateBind:
        """`state x = e` / ADR 0115 `state x: State<T> = e` / tuple forms."""
        sp = self._span()
        self._expect(TokenKind.STATE)
        if self._match(TokenKind.LPAREN):
            raw_names = [self._expect_ident_like()]
            while self._match(TokenKind.COMMA):
                raw_names.append(self._expect_ident_like())
            self._expect(TokenKind.RPAREN)
        else:
            raw_names = [self._expect_ident_like()]
        names = list(raw_names)
        self._register_scientific_state_names(names)
        ty = None
        if self._match(TokenKind.COLON):
            # LISS-0129 / ADR 0115: optional State carrier annotation.
            ty = self._type_ref()
        self._expect(TokenKind.EQ)
        expr = self._expression()
        return StateBind(
            names=names, expr=expr, span=sp, ty=ty, via_state_keyword=True
        )

    def _register_scientific_state_names(self, names: list[str]) -> None:
        """Register aliases without rewriting the source spelling of a bind."""
        for source_name in names:
            canonical = normalize_scientific_name(source_name)
            if (
                canonical == source_name
                and source_name not in SCIENTIFIC_NAME_ALIASES.values()
            ):
                continue
            self._scientific_bindings[source_name] = source_name
            self._scientific_bindings[canonical] = source_name
            for alias, alias_canonical in SCIENTIFIC_NAME_ALIASES.items():
                if alias_canonical == canonical:
                    self._scientific_bindings[alias] = source_name

    def _measure(self) -> Measure:
        sp = self._span()
        self._expect(TokenKind.MEASURE)
        # ADR 0029 sink `to` must not be eaten as ADR 0124 unit convert.
        prev = getattr(self, "_allow_unit_convert", True)
        self._allow_unit_convert = False
        try:
            expr = self._expression()
        finally:
            self._allow_unit_convert = prev
        povm = None
        if self._peek().kind == TokenKind.IDENT and self._peek().lexeme == "with":
            self._advance()
            povm = self._expression()
        sink = None
        if self._match(TokenKind.TO):
            sink = self._expect_ident_like()
        # ADR 0173: measure <primary> [with …] [to …] tracing_out name [, name …]
        tracing_out: list[str] = []
        if self._peek().kind == TokenKind.IDENT and self._peek().lexeme == "tracing_out":
            self._advance()
            tracing_out.append(self._expect_ident_like())
            while self._match(TokenKind.COMMA):
                tracing_out.append(self._expect_ident_like())
        return Measure(
            expr=expr, span=sp, sink=sink, povm=povm, tracing_out=tracing_out
        )

    def _snapshot(self) -> Snapshot:
        sp = self._span()
        self._expect(TokenKind.SNAPSHOT)
        prev = getattr(self, "_allow_unit_convert", True)
        self._allow_unit_convert = False
        try:
            expr = self._expression()
        finally:
            self._allow_unit_convert = prev
        self._expect(TokenKind.TO)
        sink = self._expect_ident_like()
        return Snapshot(expr=expr, sink=sink, span=sp)

    # --- expressions (precedence climbing) ---

    def _expression(self):
        return self._pipe()

    def _pipe(self):
        expr = self._logical_or()
        while self._match(TokenKind.PIPE_OP):
            sp = self._span()
            rhs = self._logical_or()
            expr = Pipe(lhs=expr, rhs=rhs, span=sp)
        return expr

    def _logical_or(self):
        """ADR 0196: general-expression `||` -- total pushforward, distinct
        from the Operator-DSL's own `_op_guard` binder-guard `||`."""
        expr = self._logical_and()
        while self._match(TokenKind.OR):
            sp = self._span()
            rhs = self._logical_and()
            expr = BinOp(op="||", lhs=expr, rhs=rhs, span=sp)
        return expr

    def _logical_and(self):
        """ADR 0196: general-expression `&&` -- total pushforward, distinct
        from the Operator-DSL's own `_op_guard_and` binder-guard `&&`."""
        expr = self._comparison()
        while self._match(TokenKind.AND):
            sp = self._span()
            rhs = self._comparison()
            expr = BinOp(op="&&", lhs=expr, rhs=rhs, span=sp)
        return expr

    def _comparison(self):
        expr = self._term()
        while True:
            op = None
            if self._match(TokenKind.GE):
                op = ">="
            elif self._match(TokenKind.LE):
                op = "<="
            elif self._match(TokenKind.GT):
                op = ">"
            elif self._match(TokenKind.LT):
                op = "<"
            elif self._match(TokenKind.EQEQ):
                op = "=="
            elif self._match(TokenKind.NEQ):
                op = "!="
            else:
                break
            sp = self._span()
            rhs = self._term()
            expr = BinOp(op=op, lhs=expr, rhs=rhs, span=sp)
        return expr

    def _term(self):
        expr = self._factor()
        while True:
            if self._match(TokenKind.PLUS):
                op, sp = "+", self._span()
            elif self._match(TokenKind.MINUS):
                op, sp = "-", self._span()
            else:
                break
            rhs = self._factor()
            expr = BinOp(op=op, lhs=expr, rhs=rhs, span=sp)
        return expr

    def _factor(self):
        expr = self._tensor()
        while True:
            if self._match(TokenKind.STAR):
                op, sp = "*", self._span()
            elif self._match(TokenKind.SLASH):
                op, sp = "/", self._span()
            else:
                break
            rhs = self._tensor()
            expr = BinOp(op=op, lhs=expr, rhs=rhs, span=sp)
        return expr

    def _tensor(self):
        expr = self._unary()
        while self._match(TokenKind.TENSOR_OP):
            sp = self._span()
            rhs = self._unary()
            expr = TensorExpr(left=expr, right=rhs, span=sp)
        return expr

    def _unary(self):
        if self._match(TokenKind.BANG):
            sp = self._span()
            inner = self._unary()
            from .ast_nodes import UnaryNot

            return UnaryNot(expr=inner, span=sp)
        if self._match(TokenKind.MINUS):
            sp = self._span()
            inner = self._unary()
            # desugar -e as 0 - e (LitInt 0 or LitFloat 0.0)
            zero = LitFloat(value=0.0, span=sp)
            return BinOp(op="-", lhs=zero, rhs=inner, span=sp)
        return self._call()

    def _call(self):
        expr = self._primary()
        while True:
            if self._check(TokenKind.LPAREN):
                # Newline before '(' → not a Call (avoids `x\n(y,z)` eating tuple results)
                if self._prev is not None and self._peek().line > self._prev.line:
                    break
                self._advance()  # (
                sp = self._span()
                args = []
                kwargs = []
                if not self._check(TokenKind.RPAREN):
                    if (
                        self._check(TokenKind.IDENT)
                        and self._peek_at_kind(1) == TokenKind.EQ
                    ):
                        while True:
                            key = self._expect_ident_like()
                            self._expect(TokenKind.EQ)
                            kwargs.append((key, self._expression()))
                            if not self._match(TokenKind.COMMA):
                                break
                            if self._check(TokenKind.RPAREN):
                                break
                    else:
                        args.append(self._call_arg())
                        while self._match(TokenKind.COMMA):
                            if self._check(TokenKind.RPAREN):
                                break
                            args.append(self._call_arg())
                self._expect(TokenKind.RPAREN)
                if isinstance(expr, (Coin, Dirac, Vacuum)):
                    continue
                if isinstance(expr, Inspect):
                    continue
                if isinstance(expr, Var):
                    expr = Var(
                        name=normalize_algebra_name(expr.name),
                        span=expr.span,
                    )
                if (
                    isinstance(expr, Var)
                    and expr.name == "tensor"
                    and len(args) == 2
                    and not kwargs
                ):
                    # `tensor(a, b)` is a source alias, not a generic
                    # collection constructor. Normalize it at parse time so
                    # alias and `a *|* b` share one semantic AST node.
                    expr = TensorExpr(left=args[0], right=args[1], span=sp)
                else:
                    expr = Call(callee=expr, args=args, span=sp, kwargs=kwargs or None)
            # ADR 0181: Type { field: expr, … } named struct construction.
            # Require `IDENT :` after `{` so statement blocks (`forEach … {`)
            # and evolve bodies are not eaten as named fields.
            elif (
                self._check(TokenKind.LBRACE)
                and isinstance(expr, (Var, Attr))
                and self._peek_at_kind(1) == TokenKind.IDENT
                and self._peek_at_kind(2) == TokenKind.COLON
            ):
                if self._prev is not None and self._peek().line > self._prev.line:
                    break
                sp = self._span()
                self._expect(TokenKind.LBRACE)
                kwargs: list[tuple[str, object]] = []
                if not self._check(TokenKind.RBRACE):
                    while True:
                        key = self._expect_ident_like()
                        self._expect(TokenKind.COLON)
                        val = self._expression()
                        kwargs.append((key, val))
                        if not self._match(TokenKind.COMMA):
                            break
                self._expect(TokenKind.RBRACE)
                expr = Call(callee=expr, args=[], span=sp, kwargs=kwargs)
            elif self._match(TokenKind.DOT):
                sp = self._span()
                name = self._expect_ident_like()
                if self._match(TokenKind.LPAREN):
                    args = []
                    if not self._check(TokenKind.RPAREN):
                        args.append(self._expression())
                        while self._match(TokenKind.COMMA):
                            args.append(self._expression())
                    self._expect(TokenKind.RPAREN)
                    if name == "inspect":
                        label = None
                        if args and isinstance(args[0], LitString):
                            label = args[0].value
                        expr = Inspect(expr=expr, label=label, span=sp)
                    else:
                        # recv.name(args) → Call(Attr(recv, name), args)
                        expr = Call(
                            callee=Attr(obj=expr, name=name, span=sp),
                            args=args,
                            span=sp,
                        )
                else:
                    expr = Attr(obj=expr, name=name, span=sp)
            elif self._match(TokenKind.DAGGER):
                # LISS-0073 Slice E: expression postfix † → adjoint(…)
                # (OpDSL keeps OpCall("adjoint") via _op_postfix).
                expr = self._algebra_call("adjoint", [expr], expr.span)
            elif getattr(self, "_allow_unit_convert", True) and self._match(
                TokenKind.TO
            ):
                # ADR 0124: `expr to unit` explicit SI scale conversion.
                # Disabled inside `measure` / `snapshot` observe forms so
                # statement-level `to <sink>` (ADR 0029) wins (LISS-0240).
                sp = self._span()
                unit = self._expect_ident_like()
                expr = UnitConvert(expr=expr, target_unit=unit, span=sp)
            else:
                break
        return expr

    def _primary(self):
        sp = self._span()
        tok = self._peek()

        if self._match(TokenKind.INT):
            return LitInt(value=int(tok.literal), span=sp)
        if self._match(TokenKind.FLOAT):
            return LitFloat(value=float(tok.literal), span=sp)
        if self._match(TokenKind.TRUE):
            return LitBool(value=True, span=sp)
        if self._match(TokenKind.FALSE):
            return LitBool(value=False, span=sp)
        if self._match(TokenKind.STRING):
            return LitString(value=str(tok.literal), span=sp)

        if self._match(TokenKind.THIS):
            return Var(name="this", span=sp)

        if self._match(TokenKind.COIN):
            if self._match(TokenKind.LPAREN):
                self._expect(TokenKind.RPAREN)
            return Coin(span=sp)

        if self._match(TokenKind.DIRAC):
            self._expect(TokenKind.LPAREN)
            arg = self._expression()
            self._expect(TokenKind.RPAREN)
            return Dirac(arg=arg, span=sp)

        if self._match(TokenKind.KET):
            return self._ket_or_outer(tok, sp)
        if self._match(TokenKind.BRA):
            return self._bra_or_inner(tok, sp)

        if self._match(TokenKind.VACUUM):
            if self._match(TokenKind.LPAREN):
                self._expect(TokenKind.RPAREN)
            return Vacuum(span=sp)

        if self._match(TokenKind.INSPECT):
            self._expect(TokenKind.LPAREN)
            inner = self._expression()
            label = None
            if self._match(TokenKind.COMMA):
                lab = self._expression()
                if isinstance(lab, LitString):
                    label = lab.value
            self._expect(TokenKind.RPAREN)
            return Inspect(expr=inner, label=label, span=sp)

        if self._match(TokenKind.MEASURE):
            # Expression-position measurement is retained only so a boundary
            # checker can reject it precisely (especially in a forEach bound).
            inner = self._expression()
            return MeasureExpr(expr=inner, span=sp)

        if self._match(TokenKind.WHEN):
            return self._when_expr(sp)

        if self._match(TokenKind.SUPERPOSE):
            return self._superpose_expr(sp)

        if self._match(TokenKind.EVOLVE):
            return self._evolve_expr(sp)

        if self._match(TokenKind.LPAREN):
            # grouping or tuple
            if self._check(TokenKind.RPAREN):
                self._advance()
                raise ParseError("empty tuple", sp.line, sp.col)
            first = self._expression()
            if self._match(TokenKind.COMMA):
                items = [first, self._expression()]
                while self._match(TokenKind.COMMA):
                    items.append(self._expression())
                self._expect(TokenKind.RPAREN)
                return TupleExpr(items=items, span=sp)
            self._expect(TokenKind.RPAREN)
            # Preserve the fact that a tensor expression was explicitly
            # grouped; the typechecker uses this to distinguish `(a *|* b) * c`
            # from the ungrouped `a *|* b * c`.
            if isinstance(first, TensorExpr):
                setattr(first, "_explicitly_grouped", True)
            return first

        # ADR 0153 bare block `{ let …; result }` vs Slice F `{A, B}` anticommutator.
        # Prefer anticommutator unless the body starts with `let`.
        if self._check(TokenKind.LBRACE):
            nxt = self._peek_at(1)
            if nxt is not None and nxt.kind == TokenKind.LET:
                body = self._evolve_body()
                return BlockExpr(lets=body.lets, result=body.result, span=body.span)
            self._advance()  # LBRACE
            items = self._comma_expr_items(TokenKind.RBRACE)
            if len(items) != 2:
                raise ParseError(
                    "anticommutator braces `{A, B}` require exactly two operands",
                    sp.line,
                    sp.col,
                )
            return self._algebra_call("anticommutator", items, sp)

        if self._match(TokenKind.LBRACKET):
            items = self._comma_expr_items(TokenKind.RBRACKET)
            # Slice F: Operator-context exactly-two `[A, B]` → commutator.
            if self._commutator_bracket_context:
                if len(items) != 2:
                    raise ParseError(
                        "commutator brackets `[A, B]` require exactly two operands",
                        sp.line,
                        sp.col,
                    )
                return self._algebra_call("commutator", items, sp)
            return ListExpr(items=items, span=sp)

        if (
            self._check(TokenKind.IDENT)
            and tok.lexeme == "project"
            and self._peek_at_kind(1) != TokenKind.LPAREN
        ):
            self._advance()
            source = self._expression()
            if self._match(TokenKind.ONTO):
                target = self._expression()
                return Call(
                    callee=Var(name="project", span=sp),
                    args=[source, target],
                    span=sp,
                )
            return Var(name="project", span=sp)

        if self._match(TokenKind.IDENT):
            name = self._scientific_bindings.get(tok.lexeme, tok.lexeme)
            if name == "_":
                return Hole(span=sp)
            if self._check(TokenKind.ARROW):
                self._advance()
                body = self._expression()
                return Lambda(param=name, body=body, span=sp)
            return Var(name=name, span=sp)

        # Forbidden/Retired in expr position — recover with dummy
        if self._match(TokenKind.FORBIDDEN) or self._match(TokenKind.RETIRED):
            return Var(name=tok.lexeme, span=sp)

        raise ParseError(f"unexpected token in expression: `{tok.lexeme}`", tok.line, tok.col)

    def _call_arg(self):
        """Call argument: expression or partial hole `_` (ADR 0123)."""
        if self._check(TokenKind.IDENT) and self._peek().lexeme == "_":
            sp = self._span()
            self._advance()
            return Hole(span=sp)
        return self._expression()

    def _when_expr(self, sp: Span) -> WhenExpr:
        self._expect(TokenKind.LPAREN)
        ctrl = self._expression()
        self._expect(TokenKind.RPAREN)
        self._expect(TokenKind.LBRACE)
        arms: list[WhenArm] = []
        while not self._check(TokenKind.RBRACE) and not self._check(TokenKind.EOF):
            if self._match(TokenKind.ELSE):
                self._expect(TokenKind.ARROW)
                body = self._expression()
                self._match(TokenKind.COMMA)
                arms.append(WhenArm(pat=None, body=body, is_else=True))
                continue
            # pattern: literal or ident
            pat_tok = self._peek()
            if self._match(TokenKind.INT):
                pat = int(pat_tok.literal)
            elif self._match(TokenKind.FLOAT):
                pat = float(pat_tok.literal)
            elif self._match(TokenKind.TRUE):
                pat = True
            elif self._match(TokenKind.FALSE):
                pat = False
            elif self._match(TokenKind.IDENT):
                pat = pat_tok.lexeme
            else:
                self.diagnostics.append(
                    {
                        "code": "PARSE_ERROR",
                        "line": pat_tok.line,
                        "col": pat_tok.col,
                        "message": f"bad mix pattern `{pat_tok.lexeme}`",
                    }
                )
                self._advance()
                continue
            self._expect(TokenKind.ARROW)
            body = self._expression()
            self._match(TokenKind.COMMA)
            arms.append(WhenArm(pat=pat, body=body, is_else=False))
        self._expect(TokenKind.RBRACE)
        return WhenExpr(ctrl=ctrl, arms=arms, span=sp)

    def _superpose_expr(self, sp: Span) -> SuperposeExpr:
        """LISS-0320: `superpose (control) { pat -> expr, … }`.

        Structurally mirrors `_when_expr`; produces a distinct
        `SuperposeExpr`/`SuperposeArm` so this is never confused with
        `mix`/`WhenExpr` downstream. Coherent amplitude/phase execution is a
        separate, later slice — this method only builds the AST node.
        """

        self._expect(TokenKind.LPAREN)
        ctrl = self._expression()
        self._expect(TokenKind.RPAREN)
        self._expect(TokenKind.LBRACE)
        arms: list[SuperposeArm] = []
        while not self._check(TokenKind.RBRACE) and not self._check(TokenKind.EOF):
            if self._match(TokenKind.ELSE):
                self._expect(TokenKind.ARROW)
                body = self._expression()
                self._match(TokenKind.COMMA)
                arms.append(SuperposeArm(pat=None, body=body, is_else=True))
                continue
            pat_tok = self._peek()
            if self._match(TokenKind.INT):
                pat = int(pat_tok.literal)
            elif self._match(TokenKind.FLOAT):
                pat = float(pat_tok.literal)
            elif self._match(TokenKind.TRUE):
                pat = True
            elif self._match(TokenKind.FALSE):
                pat = False
            elif self._match(TokenKind.IDENT):
                pat = pat_tok.lexeme
            else:
                self.diagnostics.append(
                    {
                        "code": "PARSE_ERROR",
                        "line": pat_tok.line,
                        "col": pat_tok.col,
                        "message": f"bad superpose pattern `{pat_tok.lexeme}`",
                    }
                )
                self._advance()
                continue
            self._expect(TokenKind.ARROW)
            body = self._expression()
            self._match(TokenKind.COMMA)
            arms.append(SuperposeArm(pat=pat, body=body, is_else=False))
        self._expect(TokenKind.RBRACE)
        return SuperposeExpr(ctrl=ctrl, arms=arms, span=sp)

    def _evolve_expr(self, sp: Span) -> EvolveExpr:
        # Forms:
        #   evolve (seeds) times N { body }
        #   evolve (seeds) for dt { body }
        #   evolve psi under H for t          (ADR 0038)
        #   evolve (psi) under H for t
        if self._match(TokenKind.LPAREN):
            seeds = [self._expression()]
            while self._match(TokenKind.COMMA):
                seeds.append(self._expression())
            self._expect(TokenKind.RPAREN)
        else:
            seeds = [self._expression()]

        duration = None
        hamiltonian = None
        times = 1
        body: EvolveBody | None = None

        if self._match(TokenKind.UNDER):
            hamiltonian = self._expression()
            self._expect(TokenKind.FOR)
            duration = self._expression()
            suzuki = self._suzuki_policy()
            until_predicate = None
            max_steps = None
            if self._match(TokenKind.UNTIL):
                until_predicate = self._expression()
                if self._match(TokenKind.MAX):
                    max_steps = self._expression()
            times = 1
            if self._check(TokenKind.LBRACE):
                body = self._evolve_body()
            return EvolveExpr(
                seeds=seeds,
                times=times,
                body=body,
                span=sp,
                duration=duration,
                hamiltonian=hamiltonian,
                until_predicate=until_predicate,
                max_steps=max_steps,
                suzuki=suzuki,
            )

        if self._match(TokenKind.TIMES):
            # ADR 0060: integer literal or closed classical expression
            times = self._expression()
            body = self._evolve_body()
            return EvolveExpr(
                seeds=seeds, times=times, body=body, span=sp, duration=None
            )

        if self._match(TokenKind.FOR):
            duration = self._expression()
            times = 1
            body = self._evolve_body()
            return EvolveExpr(
                seeds=seeds, times=times, body=body, span=sp, duration=duration
            )

        tok = self._peek()
        raise ParseError(
            "evolve expects `times N`, `for duration`, or `under H for t`",
            tok.line,
            tok.col,
        )

    def _suzuki_policy(self) -> SuzukiPolicy | None:
        if self._peek().lexeme != "using":
            return None
        sp = self._span()
        self._advance()
        name = self._expect_ident_like()
        if name != "Suzuki":
            raise ParseError(
                "evolve `using` currently supports only `Suzuki(...)`",
                sp.line,
                sp.col,
            )
        self._expect(TokenKind.LPAREN)
        values: dict[str, Expr] = {}
        while not self._check(TokenKind.RPAREN):
            key = self._expect_ident_like()
            self._expect(TokenKind.EQ)
            values[key] = self._expression()
            if not self._match(TokenKind.COMMA):
                break
        self._expect(TokenKind.RPAREN)
        order = values.get("order", LitInt(value=0, span=sp))
        error_mode = None
        error = values.get("error")
        if isinstance(error, Var):
            error_mode = error.name
        return SuzukiPolicy(
            order=order,
            steps=values.get("steps"),
            tolerance=values.get("tolerance"),
            error_mode=error_mode,
            span=sp,
        )

    def _evolve_body(self) -> EvolveBody:
        sp = self._span()
        self._expect(TokenKind.LBRACE)
        lets: list[LetBind] = []
        result = None
        while not self._check(TokenKind.RBRACE) and not self._check(TokenKind.EOF):
            if self._match(TokenKind.LET):
                lsp = self._span()
                name = self._expect_ident_like()
                self._expect(TokenKind.EQ)
                expr = self._expression()
                lets.append(LetBind(name=name, expr=expr, span=lsp))
                continue
            # result expression (may be tuple or plain)
            result = self._expression()
            break
        if result is None:
            tok = self._peek()
            raise ParseError("evolve body missing result expression", tok.line, tok.col)
        self._expect(TokenKind.RBRACE)
        return EvolveBody(lets=lets, result=result, span=sp)

    # --- helpers ---

    def _ket_or_outer(self, ket_tok: Token, span: Span):
        """Alone ket or Slice D `|ψ⟩⟨φ|` → `outer` / matching-label `projector`.

        ADR 0169: identifier-shaped labels in outer/projector Calls desugar to
        ``Var``; numeric/`+`/`-` labels stay ``KetLit``/``BraLit``.
        """
        ket_label = str(ket_tok.literal)
        ket = self._dirac_operand(ket_label, span, kind="ket")
        if not self._check(TokenKind.BRA):
            return ket if isinstance(ket, KetLit) else KetLit(label=ket_label, span=span)
        bra_tok = self._advance()
        bra_label = str(bra_tok.literal)
        bra = self._dirac_operand(bra_label, span, kind="bra")
        # Matching paper-var or matching literal labels → projector.
        if ket_label == bra_label:
            return self._algebra_call(
                "projector",
                [self._dirac_operand(ket_label, span, kind="ket")],
                span,
            )
        return self._algebra_call("outer", [ket, bra], span)

    def _bra_or_inner(self, bra_tok: Token, span: Span):
        """Alone bra, `⟨φ|ψ⟩` inner, or `⟨φ|A|ψ⟩` → `inner(φ, A(ψ))` (Slices A–C).

        ADR 0169: identifier-shaped labels in ``inner`` Calls desugar to ``Var``.
        """
        bra_label = str(bra_tok.literal)
        bra = self._dirac_operand(bra_label, span, kind="bra")
        if self._check(TokenKind.KET):
            ket_tok = self._advance()
            ket = self._dirac_operand(str(ket_tok.literal), Span(line=ket_tok.line, col=ket_tok.col), kind="ket")
            return self._inner_call(bra, ket, span)
        # Slice C: speculative mid-expr then trailing ket (restore on miss).
        saved_i, saved_prev = self.i, self._prev
        try:
            mid = self._call()
        except ParseError:
            self.i, self._prev = saved_i, saved_prev
            return bra if isinstance(bra, BraLit) else BraLit(label=bra_label, span=span)
        if not self._check(TokenKind.KET):
            self.i, self._prev = saved_i, saved_prev
            return bra if isinstance(bra, BraLit) else BraLit(label=bra_label, span=span)
        ket_tok = self._advance()
        ket = self._dirac_operand(
            str(ket_tok.literal),
            Span(line=ket_tok.line, col=ket_tok.col),
            kind="ket",
        )
        applied = Call(callee=mid, args=[ket], span=span)
        return self._inner_call(bra, applied, span)

    def _take_ket_lit(self) -> KetLit:
        ket_tok = self._advance()
        return KetLit(
            label=str(ket_tok.literal),
            span=Span(line=ket_tok.line, col=ket_tok.col),
        )

    @staticmethod
    def _is_paper_var_label(label: str) -> bool:
        """True when a Dirac interior should be a ``Var`` in paper sugar Calls."""
        if not label or label in {"+", "-"} or label.isdigit():
            return False
        if not (label[0].isalpha() or label[0] == "_"):
            return False
        return all(c.isalnum() or c == "_" for c in label)

    def _dirac_operand(self, label: str, span: Span, *, kind: str):
        """Bra/ket operand: paper-var ``Var`` or literal ``BraLit``/``KetLit``."""
        if self._is_paper_var_label(label):
            return Var(name=label, span=span)
        if kind == "bra":
            return BraLit(label=label, span=span)
        return KetLit(label=label, span=span)

    def _inner_call(self, left: Expr, right: Expr, span: Span) -> Call:
        return self._algebra_call("inner", [left, right], span)

    def _algebra_call(self, name: str, args: list[Expr], span: Span) -> Call:
        return Call(callee=Var(name=name, span=span), args=args, span=span)

    def _comma_expr_items(self, closer: TokenKind) -> list[Expr]:
        items: list[Expr] = []
        if not self._check(closer):
            items.append(self._expression())
            while self._match(TokenKind.COMMA):
                if self._check(closer):
                    break  # trailing comma
                items.append(self._expression())
        self._expect(closer)
        return items

    def _comma_op_expr_items(self, closer: TokenKind) -> list:
        items: list = []
        if not self._check(closer):
            items.append(self._op_expression())
            while self._match(TokenKind.COMMA):
                if self._check(closer):
                    break  # trailing comma
                items.append(self._op_expression())
        self._expect(closer)
        return items

    def _peek(self) -> Token:
        return self.tokens[self.i]

    def _peek_at(self, offset: int) -> Token | None:
        index = self.i + offset
        if index >= len(self.tokens):
            return None
        return self.tokens[index]

    def _peek_at_kind(self, offset: int) -> TokenKind | None:
        tok = self._peek_at(offset)
        return None if tok is None else tok.kind

    def _dotted_index_lookahead(self) -> bool:
        """LISS-0369: does the current position start `a[...]` or
        `a.b[...]` etc. -- any depth (including zero) of `.<ident>`
        hops before an index bracket, with the current token already
        confirmed IDENT by the caller."""
        offset = 1
        while self._peek_at_kind(offset) == TokenKind.DOT:
            if self._peek_at_kind(offset + 1) != TokenKind.IDENT:
                return False
            offset += 2
        return self._peek_at_kind(offset) == TokenKind.LBRACKET

    def _dotted_call_lookahead(self) -> bool:
        """LISS-0358: does the current position start `a.b(...)` or
        `a.b.c(...)` etc. -- one or more `.<ident>` hops before a call,
        with the current token already confirmed IDENT by the caller."""
        offset = 1
        if self._peek_at_kind(offset) != TokenKind.DOT:
            return False
        while self._peek_at_kind(offset) == TokenKind.DOT:
            if self._peek_at_kind(offset + 1) != TokenKind.IDENT:
                return False
            offset += 2
        return self._peek_at_kind(offset) == TokenKind.LPAREN

    def _check(self, kind: TokenKind) -> bool:
        return self._peek().kind == kind

    def _advance(self) -> Token:
        tok = self._peek()
        if tok.kind != TokenKind.EOF:
            self.i += 1
            self._prev = tok
        return tok

    def _match(self, kind: TokenKind) -> bool:
        if self._check(kind):
            self._advance()
            return True
        return False

    def _expect(self, kind: TokenKind) -> Token:
        if self._check(kind):
            return self._advance()
        tok = self._peek()
        raise ParseError(f"expected {kind.name}, got `{tok.lexeme}`", tok.line, tok.col)

    def _expect_ident_like(self) -> str:
        tok = self._peek()
        if tok.kind == TokenKind.IDENT:
            self._advance()
            return tok.lexeme
        raise ParseError(f"expected identifier, got `{tok.lexeme}`", tok.line, tok.col)

    def _span(self) -> Span:
        tok = self._peek()
        return Span(line=tok.line, col=tok.col)

    # --- Operator expressions (Type-First `Operator H = …`) ---

    def _op_expression(self):
        return self._op_comparison()

    def _op_guard(self):
        """Binder `where`: comparisons with `&&` (higher) and `||` (LISS-0145)."""
        expr = self._op_guard_and()
        while self._match(TokenKind.OR):
            sp = self._span()
            rhs = self._op_guard_and()
            expr = OpBin(op="||", lhs=expr, rhs=rhs, span=sp)
        return expr

    def _op_guard_and(self):
        expr = self._op_comparison()
        while self._match(TokenKind.AND):
            sp = self._span()
            rhs = self._op_comparison()
            expr = OpBin(op="&&", lhs=expr, rhs=rhs, span=sp)
        return expr

    def _op_comparison(self):
        expr = self._op_sum()
        while True:
            op = None
            if self._match(TokenKind.GE):
                op = ">="
            elif self._match(TokenKind.LE):
                op = "<="
            elif self._match(TokenKind.GT):
                op = ">"
            elif self._match(TokenKind.LT):
                op = "<"
            elif self._match(TokenKind.EQEQ):
                op = "=="
            elif self._match(TokenKind.NEQ):
                op = "!="
            else:
                break
            sp = self._span()
            rhs = self._op_sum()
            expr = OpBin(op=op, lhs=expr, rhs=rhs, span=sp)
        return expr

    def _op_sum(self):
        expr = self._op_product()
        while True:
            if self._match(TokenKind.PLUS):
                op, sp = "+", self._span()
            elif self._match(TokenKind.MINUS):
                op, sp = "-", self._span()
            else:
                break
            rhs = self._op_product()
            expr = OpBin(op=op, lhs=expr, rhs=rhs, span=sp)
        return expr

    def _op_product(self):
        expr = self._op_power()
        while self._match(TokenKind.STAR):
            sp = self._span()
            rhs = self._op_power()
            expr = OpBin(op="*", lhs=expr, rhs=rhs, span=sp)
        return expr

    def _op_power(self):
        expr = self._op_unary()
        if self._match(TokenKind.CARET):
            sp = self._span()
            tok = self._expect(TokenKind.INT)
            return OpPow(base=expr, exp=int(tok.literal), span=sp)
        return expr

    def _op_unary(self):
        if self._match(TokenKind.MINUS):
            sp = self._span()
            inner = self._op_unary()
            return OpBin(op="*", lhs=OpLit(value=-1.0, span=sp), rhs=inner, span=sp)
        return self._op_postfix()

    def _op_postfix(self):
        """Apply zero or more postfix operator-DSL suffixes.

        LISS-0069: postfix `†` is dual-accept sugar for `adjoint(…)`.
        """
        expr = self._op_primary()
        while self._match(TokenKind.DAGGER):
            expr = OpCall(name="adjoint", args=[expr], span=expr.span)
        return expr

    def _op_primary(self):
        sp = self._span()
        if self._match(TokenKind.LPAREN):
            expr = self._op_expression()
            self._expect(TokenKind.RPAREN)
            return expr
        if self._match(TokenKind.LBRACKET):
            # LISS-0073 Slice F: OpDSL `[A, B]` → commutator (expression Call).
            items = self._comma_op_expr_items(TokenKind.RBRACKET)
            if len(items) != 2:
                raise ParseError(
                    "commutator brackets `[A, B]` require exactly two operands",
                    sp.line,
                    sp.col,
                )
            return self._algebra_call("commutator", items, sp)
        if self._match(TokenKind.LBRACE):
            items = self._comma_op_expr_items(TokenKind.RBRACE)
            if len(items) != 2:
                raise ParseError(
                    "anticommutator braces `{A, B}` require exactly two operands",
                    sp.line,
                    sp.col,
                )
            return self._algebra_call("anticommutator", items, sp)
        if self._match(TokenKind.INT):
            tok = self._prev
            assert tok is not None
            return OpLit(value=float(tok.literal), span=sp)
        if self._match(TokenKind.FLOAT):
            tok = self._prev
            assert tok is not None
            return OpLit(value=float(tok.literal), span=sp)
        tok = self._peek()
        if tok.kind == TokenKind.IDENT:
            name = tok.lexeme
            self._advance()
            if name in {"sum", "product"}:
                return self._op_binder(name, sp)
            if name in {"N", "Q", "P"}:
                # LISS-0227: parse as OpVar so a local `Operator P = …; return P`
                # shadows the ADR 0049 Fock atom. Unbound P/Q/N still resolve to
                # OpNumber / OpQuadrature in hamiltonian._resolve_var.
                base = OpVar(name=name, span=sp)
                while self._match(TokenKind.DOT):
                    field = self._expect(TokenKind.IDENT)
                    base = OpAttr(obj=base, name=field.lexeme, span=sp)
                while self._match(TokenKind.LBRACKET):
                    index = self._op_expression()
                    self._expect(TokenKind.RBRACKET)
                    base = OpIndexed(base=base, index=index, span=sp)
                return base
            if name == "hop":
                # hop(i, j) → |i⟩⟨j| on discrete site / Fock-label basis.
                # Any reserved name parsed here that can be immediately
                # followed by `(` must stay listed in
                # _OPERATOR_DSL_RESERVED_ATOMS (LISS-0051), or an
                # `Operator` bind's factory-call heuristic will shadow it.
                self._expect(TokenKind.LPAREN)
                i_tok = self._expect(TokenKind.INT)
                self._expect(TokenKind.COMMA)
                j_tok = self._expect(TokenKind.INT)
                self._expect(TokenKind.RPAREN)
                return OpHop(i=int(i_tok.literal), j=int(j_tok.literal), span=sp)
            if name in {"I", "X", "Y", "Z"}:
                # Pauli atom with an optional site, e.g. `Z(0)`. Listed in
                # _OPERATOR_DSL_RESERVED_ATOMS (LISS-0051) so an `Operator`
                # bind's factory-call heuristic never shadows it.
                site = None
                if self._match(TokenKind.LPAREN):
                    args: list = []
                    if not self._check(TokenKind.RPAREN):
                        args.append(self._op_expression())
                        while self._match(TokenKind.COMMA):
                            args.append(self._op_expression())
                    self._expect(TokenKind.RPAREN)
                    # A declaration named like an atom is handled by the
                    # generic expression path in `_type_first_bind`; this
                    # marker is only used for unresolved operator syntax.
                    return OpCall(name=name, args=args, span=sp)
                base = OpPauli(kind=name.upper(), site=site, span=sp)
            else:
                if self._match(TokenKind.LPAREN):
                    args: list = []
                    if not self._check(TokenKind.RPAREN):
                        args.append(self._op_expression())
                        while self._match(TokenKind.COMMA):
                            args.append(self._op_expression())
                    self._expect(TokenKind.RPAREN)
                    return OpCall(name=name, args=args, span=sp)
                base = OpVar(name=name, span=sp)
                while self._match(TokenKind.DOT):
                    field = self._expect(TokenKind.IDENT)
                    base = OpAttr(obj=base, name=field.lexeme, span=sp)
                # LISS-0144: allow chained `a[i][j][k][l]`
                while self._match(TokenKind.LBRACKET):
                    index = self._op_expression()
                    self._expect(TokenKind.RBRACKET)
                    base = OpIndexed(base=base, index=index, span=sp)
                return base
            if self._match(TokenKind.LBRACKET):
                index = self._op_expression()
                self._expect(TokenKind.RBRACKET)
                return OpIndexed(base=base, index=index, span=sp)
            return base
        raise ParseError(
            f"expected operator expression, got `{tok.lexeme}`", tok.line, tok.col
        )

    def _static_index_endpoint(self):
        """ADR 0117: literal / name / ± additive endpoint inside Index<a..b>."""
        return self._static_index_sum()

    def _static_index_sum(self):
        expr = self._static_index_primary()
        while True:
            if self._match(TokenKind.PLUS):
                sp = self._span()
                rhs = self._static_index_primary()
                expr = OpBin(op="+", lhs=expr, rhs=rhs, span=sp)
            elif self._match(TokenKind.MINUS):
                sp = self._span()
                rhs = self._static_index_primary()
                expr = OpBin(op="-", lhs=expr, rhs=rhs, span=sp)
            else:
                break
        return expr

    def _static_index_primary(self):
        sp = self._span()
        if self._match(TokenKind.MINUS):
            inner = self._static_index_primary()
            return OpBin(
                op="-",
                lhs=OpLit(value=0, span=sp),
                rhs=inner,
                span=sp,
            )
        if self._match(TokenKind.LPAREN):
            expr = self._static_index_sum()
            self._expect(TokenKind.RPAREN)
            return expr
        tok = self._peek()
        if tok.kind == TokenKind.INT:
            self._advance()
            return OpLit(value=int(tok.literal), span=sp)
        if tok.kind == TokenKind.IDENT:
            name = self._advance().lexeme
            return OpVar(name=name, span=sp)
        raise ParseError(
            f"expected static Index endpoint, got `{tok.lexeme}`",
            tok.line,
            tok.col,
        )

    def _binder_domain(self):
        """Parse a binder domain: Index<…>, rev(…), or named domain."""
        sp = self._span()
        if self._check(TokenKind.IDENT) and self._peek().lexeme == "rev":
            self._advance()
            self._expect(TokenKind.LPAREN)
            inner = self._binder_domain()
            self._expect(TokenKind.RPAREN)
            return RevDomain(inner=inner, span=sp)
        if self._check(TokenKind.IDENT) and self._peek().lexeme == "Index":
            self._advance()
            self._expect(TokenKind.LT)
            start = self._static_index_endpoint()
            if self._match(TokenKind.RANGE):
                end = self._static_index_endpoint()
                if self._check(TokenKind.GT):
                    self._advance()
                elif self._check(TokenKind.GE):
                    self._advance()
                else:
                    t = self._peek()
                    raise ParseError(
                        "expected `>` to close Index range", t.line, t.col
                    )
                return IndexDomain(start=start, end=end, span=sp)
            # Index<N> single-arg form → TypeRef for compatibility
            if not isinstance(start, OpLit):
                raise ParseError(
                    "`Index<N>` requires a literal size or use `Index<a..b>`",
                    sp.line,
                    sp.col,
                )
            args = [TypeRef(name=str(int(start.value)))]
            while self._match(TokenKind.COMMA):
                ep = self._static_index_endpoint()
                if not isinstance(ep, OpLit):
                    raise ParseError(
                        "Index type arguments must be literals here",
                        sp.line,
                        sp.col,
                    )
                args.append(TypeRef(name=str(int(ep.value))))
            if self._check(TokenKind.GT):
                self._advance()
            elif self._check(TokenKind.GE):
                self._advance()
            else:
                t = self._peek()
                raise ParseError("expected `>` to close type arguments", t.line, t.col)
            return TypeRef(name="Index", args=args)
        if self._check(TokenKind.IDENT) and self._peek_at_kind(1) == TokenKind.LT:
            return self._type_ref()
        return OpVar(name=self._expect_ident_like(), span=self._span())

    def _op_binder(self, kind: str, sp: Span):
        self._expect(TokenKind.LPAREN)
        bindings = []
        while True:
            variable = self._expect_ident_like()
            self._expect(TokenKind.IN)
            domain = self._binder_domain()
            bindings.append((variable, domain))
            if not self._match(TokenKind.COMMA):
                break
        self._expect(TokenKind.RPAREN)
        guard = None
        if self._check(TokenKind.IDENT) and self._peek().lexeme == "where":
            self._advance()
            guard = self._op_guard()
        self._expect(TokenKind.LBRACE)
        body = self._op_expression()
        self._expect(TokenKind.RBRACE)
        origin = BinderOrigin(
            source_span=sp,
            variables=tuple(variable for variable, _domain in bindings),
            desugared=len(bindings) > 1,
        )
        for variable, domain in reversed(bindings):
            body = OpBinder(
                kind=kind,
                variable=variable,
                domain=domain,
                body=body,
                span=sp,
                guard=guard,
                origin=origin,
            )
            guard = None
        return body
