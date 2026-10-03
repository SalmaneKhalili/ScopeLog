from rich.style import Style
from rich.text import Text
from textual import on
from textual.widgets import DirectoryTree
from textual.widgets._directory_tree import DirEntry
from textual.widgets._tree import TreeNode


class Sources(DirectoryTree):
    def render_label(
        self, node: TreeNode[DirEntry], base_style: Style, style: Style
    ) -> Text:
        # Fallback to default label if node data isn't a DirEntry instance
        if node.data is None or not isinstance(node.data, DirEntry):
            return super().render_label(node, base_style, style)

        # Build clean label with name only and apply standard text styles
        label = Text(node.data.path.name)
        label.stylize(base_style)
        label.stylize(style)

        return label
