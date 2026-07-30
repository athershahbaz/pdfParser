"""
semantic_analyzer.py

Transforms the parsed documentation into a canonical
CommandGraph.

This module never modifies the parser output.
It builds a new graph representation.
"""

from __future__ import annotations

import logging

from config import ParserConfig
from graph import (
    CommandGraph,
    CommandGraphNode,
)
from models import (
    ParseResult,
    SectionNode,
    CommandNode,
)

logger = logging.getLogger(__name__)

#Analyzer Skelton
class SemanticAnalyzer:

    def __init__(
        self,
        config: ParserConfig,
    ):

        self.config = config

    # -----------------------------------------------------

    def analyze(
        self,
        result: ParseResult,
    ) -> CommandGraph:

        self.result = result

        self.graph = CommandGraph()

        #
        # Index every section.
        #
        self.section_index = {

            section.number: section

            for section in result.sections

        }

        #
        # Build graph.
        #
        self._build_graph()

        #
        # Assign canonical paths.
        #
        self.graph.build_path_index()

        return self.graph


    #Build Graph
    # -----------------------------------------------------

    def _build_graph(self):

        #
        # Walk every top-level section.
        #

        for section in self.result.sections:

            #
            # Only sections with root commands
            # contribute to the graph.
            #

            for root in section.commands:

                self._insert_root(

                    root,

                    section,

                )

    #Insert Root
        # -----------------------------------------------------

        def _insert_root(

            self,

            command: CommandNode,

            section: SectionNode,

        ):

            root = self.graph.roots.get(

                command.command

            )

            if root is None:

                root = CommandGraphNode(

                    name=command.command,

                )

                self.graph.add_root(root)

            self._merge_metadata(

                root,

                command,

                section,

            )

            self._walk(

                command,

                root,

                section,

            )


#Recursive Walk
    # -----------------------------------------------------

    def _walk(

        self,

        source: CommandNode,

        target: CommandGraphNode,

        section: SectionNode,

    ):

        #
        # Merge every child.
        #

        for child in source.children:

            graph_child = target.children.get(

                child.command

            )

            if graph_child is None:

                graph_child = CommandGraphNode(

                    name=child.command,

                )

                target.add_child(

                    graph_child

                )

            self._merge_metadata(

                graph_child,

                child,

                section,

            )

            self._walk(

                child,

                graph_child,

                section,

            )


#Merge Metadata
    # -----------------------------------------------------

    def _merge_metadata(

        self,

        graph_node: CommandGraphNode,

        command_node: CommandNode,

        section: SectionNode,

    ):

        if section not in graph_node.sections:

            graph_node.sections.append(

                section

            )

        if command_node.description:

            if graph_node.description:

                graph_node.description += "\n"

            graph_node.description += (

                command_node.description

            )

    