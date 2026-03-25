"""Stage 5: Compare schema-guided vs open-domain extraction metrics."""
import yaml
import falkordb


def load_config():
    with open("config.yaml") as f:
        return yaml.safe_load(f)


def connect(config: dict, database: str):
    client = falkordb.FalkorDB(host=config["falkordb_host"], port=config["falkordb_port"])
    return client.select_graph(database)


def count(graph, cypher: str) -> int:
    try:
        result = graph.query(cypher)
        rows = result.result_set
        return rows[0][0] if rows else 0
    except Exception:
        return 0


def distinct_types(graph, cypher: str) -> list:
    try:
        result = graph.query(cypher)
        return [r[0] for r in result.result_set if r[0]]
    except Exception:
        return []


def analyze(graph, label: str) -> dict:
    node_count = count(graph, "MATCH (n) RETURN count(n)")
    edge_count = count(graph, "MATCH ()-[r]->() RETURN count(r)")
    entity_types = distinct_types(graph, "MATCH (n) RETURN DISTINCT labels(n)")
    relation_types = distinct_types(graph, "MATCH ()-[r]->() RETURN DISTINCT type(r)")

    return {
        "graph": label,
        "nodes": node_count,
        "edges": edge_count,
        "entity_type_count": len(entity_types),
        "relation_type_count": len(relation_types),
        "entity_types": entity_types,
        "relation_types": relation_types,
    }


def print_table(stats: list[dict]):
    print("\n" + "=" * 70)
    print(f"{'Metric':<30} {'Schema-Guided':>18} {'Open-Domain':>18}")
    print("=" * 70)

    keys = [
        ("nodes", "Entity nodes"),
        ("edges", "Relationships"),
        ("entity_type_count", "Entity types"),
        ("relation_type_count", "Relation types"),
    ]
    for key, label in keys:
        s = stats[0].get(key, "N/A")
        o = stats[1].get(key, "N/A")
        print(f"{label:<30} {str(s):>18} {str(o):>18}")

    print("=" * 70)
    print("\nSchema-Guided relation types:")
    print(" ", ", ".join(stats[0]["relation_types"]) or "(none)")
    print("\nOpen-Domain relation types (sample, first 30):")
    print(" ", ", ".join(stats[1]["relation_types"][:30]) or "(none)")


if __name__ == "__main__":
    config = load_config()

    schema_graph = connect(config, "odyssey_schema")
    open_graph = connect(config, "odyssey_open")

    stats = [
        analyze(schema_graph, "odyssey_schema"),
        analyze(open_graph, "odyssey_open"),
    ]

    print_table(stats)
