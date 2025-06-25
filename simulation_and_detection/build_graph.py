import json
from neo4j import GraphDatabase

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASS = ""  # Replace with your password

def create_graph(logs):
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE")
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (a:Action) REQUIRE a.name IS UNIQUE")
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (l:Location) REQUIRE l.name IS UNIQUE")
        for log in logs:
            params = {
                "user": log['user'],
                "role": log['role'],
                "location": log['location'],
                "action": log['action'],
                "time": log['time'],
                "is_anomaly": bool(log['is_anomaly']),
                "anomaly_type": log.get('anomaly_type', 'normal'),
                "risk_score": log.get('risk_score', 0),
            }
            session.run("""
                MERGE (u:User {id: $user})
                ON CREATE SET u.role = $role
                MERGE (a:Action {name: $action})
                ON CREATE SET a.risk_score = $risk_score
                MERGE (l:Location {name: $location})
                MERGE (u)-[r:PERFORMED {
                    time: $time, 
                    is_anomaly: $is_anomaly,
                    anomaly_type: $anomaly_type
                }]->(a)
                MERGE (u)-[:LOCATED_AT]->(l)
            """, params)
    driver.close()
    print(f"Graph built successfully with {len(logs)} log entries.")

if __name__ == "__main__":
    with open("logs/sample_logs.json") as f:
        logs = json.load(f)
    create_graph(logs)
