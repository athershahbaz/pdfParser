"""
exporter.py

Export CommandGraph into various formats.

Currently supported

- Hierarchical JSON
- Flat JSON
"""

from __future__ import annotations

import json

from pathlib import Path

from graph import (
    CommandGraph,
    CommandGraphNode,
)

class Exporter:

    
    """
    Export graph into external formats.
    """

    def export_json(
        self,
        graph: CommandGraph,
        output_file: Path,
    ):

        document = {}

        for root in graph.iter_roots():

            document[root.name] = self._export_node(
                root
            )

        with output_file.open(
            "w",
            encoding="utf-8",
        ) as fp:

            json.dump(

                document,

                fp,

                indent=4,

                ensure_ascii=False,

            )

    def export_flat_json(
        self,
        graph,
        output_file,
    ):

        flat = {}

        for node in graph.walk():

            flat[node.path] = {

                "command": node.name,

                "children": sorted(

                    node.children.keys()

                ),

            }

        with output_file.open(

            "w",

            encoding="utf-8",

        ) as fp:

            json.dump(

                flat,

                fp,

                indent=4,

                ensure_ascii=False,

            )






    def _export_node(
        self,
        node: CommandGraphNode,
    ):
        """
        Export one node.

        Returns a JSON-compatible object.
        """

        if node.is_leaf:

            return []

        children = []

        for child in sorted(
            node.iter_children(),
            key=lambda n: n.name.lower()
        ):
            children.append(

                {

                    child.name:

                    self._export_node(child)

                }

            )

        return children