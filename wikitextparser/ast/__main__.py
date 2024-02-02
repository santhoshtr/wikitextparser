from .base import Leaf, Tree

if __name__ == "__main__":
    import rich

    # Creating Leaf objects
    leaf1 = Leaf("Leaf 1")
    leaf2 = Leaf("Leaf 2")
    leaf3 = Leaf("Leaf 3")
    leaf4 = Leaf("Leaf 4")

    # Creating Tree objects
    tree1 = Tree("Tree 1", [leaf1, leaf2, leaf3])
    tree2 = Tree("Tree 2", [leaf4, tree1])

    # Displaying the structure and executing operations
    rich.print(tree2)
    graph = tree2.to_graph()
    graph.write_png("wikiast.png")
