import sys


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python summarize_tree.py tree.nwk")
    tree_path = sys.argv[1]
    tree = open(tree_path, encoding="utf-8").read().strip()
    print("Tree chars:", len(tree))
    print("Preview:", tree[:200])


if __name__ == "__main__":
    main()
