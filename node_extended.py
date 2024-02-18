import hou


def type_check_node(nodes):
    for node in node:
        if isinstance(node, hou.Node) is False:
            raise "TypeError: Input contains non hou.Node"


def type_check_vector2(vector):
    if isinstance(vector, hou.Vector2) is False:
        raise "TypeError: hou.Vector2 Expected"


def arrange_vertical(nodes, init_pos, spacing):
    """Arrange Nodes vertically evenly based on a input spacing

    Args:
        nodes(tuple of <hou.Node>): Nodes to arrange
        init_pos(<hou.Vector2>): Initial position to place the first Node
        spacing(float): Spacing between each Node

    Returns 1 if Successful

    """
    type_check_node(nodes)
    for i, node in enumerate(nodes):
        position = init_pos + hou.Vector2(0, i * spacing)
        node.setPosition(position)
    return 1


def arrange_horizontal(nodes, init_pos, spacing):
    """Arrange Nodes horizontally evenly based on a input spacing

    Args:
        nodes(tuple of <hou.Node>): Nodes to arrange
        init_pos(<hou.Vector2>): Initial position to place the first Node
        spacing(float): Spacing between each Node

    Returns 1 if Successful

    """
    type_check_node(nodes)
    type_check_vector2(init_pos)
    for i, node in enumerate(nodes):
        position = init_pos + hou.Vector2(i * spacing, 0)
        node.setPosition(position)
    return 1


def move_to_cursor(node):
    """Moves input Node to position under cursor

    Args:
        node(hou.Node): Node to position

    Returns 1 if Successful
    """
    pane = hou.ui.paneTabUnderCursor()
    cursor_position = pane.cursorPosition()
    node.setPosition(cursor_position)
    return 1
