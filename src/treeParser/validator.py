"""
validator.py

Validation framework for the canonical Nokia CLI graph.

The validator never modifies the graph.
It only reports errors and warnings.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto

from graph import CommandGraph, CommandGraphNode

class Severity(Enum):

    INFO = auto()

    WARNING = auto()

    ERROR = auto()

@dataclass(slots=True)
class ValidationMessage:

    severity: Severity

    code: str

    message: str

    path: str

@dataclass(slots=True)
class ValidationReport:

    messages: list[ValidationMessage] = field(
        default_factory=list
    )

    @property
    def has_errors(self):

        return any(

            m.severity == Severity.ERROR

            for m in self.messages

        )

    def add(

        self,

        severity,

        code,

        message,

        path,

    ):

        self.messages.append(

            ValidationMessage(

                severity,

                code,

                message,

                path,

            )

        )

class Validator:

    """
    Performs structural validation of the
    canonical command graph.
    """

    def validate(

        self,

        graph: CommandGraph,

    ) -> ValidationReport:

        self.report = ValidationReport()

        self._check_roots(graph)

        self._check_cycles(graph)

        self._check_paths(graph)

        self._check_duplicate_paths(graph)

        return self.report



    def _check_roots(

        self,

        graph,

    ):

        if not graph.roots:

            self.report.add(

                Severity.ERROR,

                "NO_ROOT",

                "Graph contains no root commands.",

                "",

            )

    def _check_cycles(

        self,

        graph,

    ):

        visited = set()

        stack = set()

        for root in graph.iter_roots():

            self._dfs(

                root,

                visited,

                stack,

            )            


    def _dfs(

        self,

        node,

        visited,

        stack,

    ):

        node_id = id(node)

        if node_id in stack:

            self.report.add(

                Severity.ERROR,

                "CYCLE",

                "Cycle detected.",

                node.path,

            )

            return

        if node_id in visited:

            return

        visited.add(node_id)

        stack.add(node_id)

        for child in node.iter_children():

            self._dfs(

                child,

                visited,

                stack,

            )

        stack.remove(node_id)


    # Path Vlidation
    def _check_paths(

        self,

        graph,

    ):

        for node in graph.walk():

            if not node.path:

                self.report.add(

                    Severity.ERROR,

                    "EMPTY_PATH",

                    "Missing canonical path.",

                    "",

                )


    #Duplicate path validation
    def _check_duplicate_paths(

        self,

        graph,

    ):

        seen = {}

        for node in graph.walk():

            if node.path in seen:

                self.report.add(

                    Severity.ERROR,

                    "DUPLICATE_PATH",

                    "Duplicate canonical path.",

                    node.path,

                )

            else:

                seen[node.path] = node


