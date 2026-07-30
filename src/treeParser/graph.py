"""
graph.py

Canonical command graph for Nokia Classic CLI.

The parser preserves the documentation hierarchy.
The semantic analyzer builds this graph.

The graph is the authoritative representation used by
validation, JSON export, searching, and future tooling.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator

from models import SectionNode


# ---------------------------------------------------------
# Graph Node
# ---------------------------------------------------------

@dataclass(slots=True)
class CommandGraphNode:
    """
    Canonical CLI command node.

    Every logical CLI command exists exactly once in the graph.
    """

    #
    # Command keyword
    #
    name: str

    #
    # Parent node
    #
    parent: "CommandGraphNode | None" = None

    #
    # Children indexed by command keyword
    #
    children: dict[str, "CommandGraphNode"] = field(
        default_factory=dict
    )

    #
    # Documentation sections describing this command.
    #
    sections: list[SectionNode] = field(
        default_factory=list
    )

    #
    # Free-form description collected from all sections.
    #
    description: str = ""

    #
    # Canonical CLI path
    #
    path: str = ""

    #
    # Arbitrary metadata
    #
    metadata: dict[str, str] = field(
        default_factory=dict
    )

    # -----------------------------------------------------

    def add_child(
        self,
        child: "CommandGraphNode",
    ) -> "CommandGraphNode":
        """
        Add or reuse a child.

        Returns the canonical child.
        """

        existing = self.children.get(child.name)

        if existing is not None:
            return existing

        child.parent = self

        self.children[child.name] = child

        return child

    # -----------------------------------------------------

    def get_child(
        self,
        name: str,
    ) -> "CommandGraphNode | None":

        return self.children.get(name)

    # -----------------------------------------------------

    def iter_children(
        self,
    ) -> Iterator["CommandGraphNode"]:

        yield from self.children.values()

    # -----------------------------------------------------

    @property
    def is_root(self) -> bool:

        return self.parent is None

    # -----------------------------------------------------

    @property
    def is_leaf(self) -> bool:

        return len(self.children) == 0

    # -----------------------------------------------------

    @property
    def depth(self) -> int:

        depth = 0

        node = self.parent

        while node is not None:

            depth += 1

            node = node.parent

        return depth



#Command Graph Container
# ---------------------------------------------------------
# Entire CLI Graph
# ---------------------------------------------------------

class CommandGraph:
    """
    Canonical Nokia CLI graph.

    Maintains unique nodes and provides efficient lookup.
    """

    def __init__(self):

        #
        # Root commands.
        #
        self.roots: dict[str, CommandGraphNode] = {}

        #
        # Fast lookup by canonical path.
        #
        self.by_path: dict[str, CommandGraphNode] = {}

    # -----------------------------------------------------

    def add_root(
        self,
        node: CommandGraphNode,
    ) -> CommandGraphNode:

        existing = self.roots.get(node.name)

        if existing is not None:
            return existing

        self.roots[node.name] = node

        return node

    # -----------------------------------------------------

    def iter_roots(
        self,
    ) -> Iterator[CommandGraphNode]:

        yield from self.roots.values()

    # -----------------------------------------------------

    def walk(
        self,
    ) -> Iterator[CommandGraphNode]:

        for root in self.roots.values():

            yield from self._walk(root)

    # -----------------------------------------------------

    def _walk(
        self,
        node: CommandGraphNode,
    ) -> Iterator[CommandGraphNode]:

        yield node

        for child in node.children.values():

            yield from self._walk(child)

    # -----------------------------------------------------

    def find(
        self,
        path: str,
    ) -> CommandGraphNode | None:

        return self.by_path.get(path)

    # -----------------------------------------------------

    def build_path_index(
        self,
    ) -> None:

        self.by_path.clear()

        for root in self.roots.values():

            self._assign_paths(root, "")

    # -----------------------------------------------------

    def _assign_paths(
        self,
        node: CommandGraphNode,
        parent_path: str,
    ) -> None:

        if parent_path:

            node.path = f"{parent_path}/{node.name}"

        else:

            node.path = node.name

        self.by_path[node.path] = node

        for child in node.children.values():

            self._assign_paths(
                child,
                node.path,
            )