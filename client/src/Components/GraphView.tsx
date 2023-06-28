import { useEffect, useState } from "react";
import Graph from "graphology";
// import { SigmaContainer, useLoadGraph } from "@react-sigma/core";
import { SigmaContainer, useLoadGraph } from "react-sigma-v2";
import "@react-sigma/core/lib/react-sigma.min.css";
import { Container } from "@mantine/core";
import { Api, GraphData, SampleData } from "../api/api";

const nodeColors: { [nodetypes: string]: string } = {
    "material": "#1C7ED6",
    "action": "#FD7E14",
    "analysis": "#E03131",
    "measurement": "#37B24D"
} as const;


interface NodeEntry {
    "x": number;
    "y": number;
    "label": string;
    "size": number;
    "color": string;
    "contents": { [otherOptions: string]: any };
}

interface NodeCollection {
    [id: string]: NodeEntry;
}

interface EdgeEntry {
    "source": string;
    "target": string;
    "contents": {
        [otherOptions: string]: any;
    }
}



// export const LoadGraph = (props: { sample_id: string | null }) => {
//     const sample_id = props.sample_id;
//     const [sample, setSample] = useState<SampleData>({
//         "name": "Error",
//         "description": "Error",
//         "created_at": "Error",
//         "nodes": {
//             "Material": [],
//             "Action": [],
//             "Analysis": [],
//             "Measurement": []
//         },
//         "tags": []
//     })
//     const loadGraph = useLoadGraph();

//     const buildGraph = (sample: SampleData) => {
//         var nodes: NodeCollection = {};
//         var edges: EdgeEntry[] = [];
//         var x = 0;
//         var y = 0;
//         var last_node_id: string | null = null;
//         for (const node_type in sample.nodes) {
//             for (const node_id of sample.nodes[node_type]) {
//                 nodes[node_id] = {
//                     "x": x,
//                     "y": y,
//                     "label": node_id,
//                     "size": 15,
//                     "color": nodeColors[node_type]
//                 }
//                 if (last_node_id) {
//                     // console.log(last_node_id + " -> " + node_id)
//                     edges.push({
//                         "source": last_node_id,
//                         "target": node_id,
//                         "contents": {}
//                     })
//                 }
//                 last_node_id = node_id;
//                 y += 15;
//             }
//             y = 0;
//             x += 15;
//         }
//         return { "nodes": nodes, "edges": edges }
//     }

//     useEffect(() => {
//         const graph = new Graph();
//         if (sample_id) {
//             const api = new Api();
//             api.getSample(sample_id)
//                 .then((response) => {
//                     setSample(response.data);
//                 })
//                 .catch((error) => {
//                     console.log(error);
//                 });
//         }

//         const samplegraph = buildGraph(sample)
//         for (const node_id in samplegraph.nodes) {
//             graph.addNode(node_id, samplegraph.nodes[node_id]);
//         }
//         for (const edge of samplegraph.edges) {
//             graph.addEdge(edge.source, edge.target, edge.contents);
//         }

//         loadGraph(graph);
//     }, [loadGraph]);

//     return null;
// };


export const LoadGraph = () => {
    const [graphData, setGraphData] = useState<GraphData>({
        "nodes": [{
            "_id": "Error",
            "x": 0,
            "y": 0,
            "label": "Error",
            "size": 100,
            "contents": {
                "name": "Error",
                "type": "measurement"
            }
        }],
        "edges": []
    })
    const loadGraph = useLoadGraph();

    const buildGraph = (graphData: GraphData) => {
        const graph = new Graph();

        for (const node of graphData.nodes) {
            const nodeEntry: NodeEntry = {
                "x": node.x,
                "y": node.y,
                "label": node.contents.name,
                "size": 5,
                "contents": node.contents,
                "color": nodeColors[node.contents.type]
            }
            console.log(nodeEntry)
            graph.addNode(node._id, nodeEntry);

        }
        for (const edge of graphData.edges) {
            graph.addEdge(edge.source, edge.target, edge.contents);
        }

        return graph
    }

    useEffect(() => {
        const api = new Api();
        api.getCompleteGraph()
            .then((response) => {
                console.log("response: " + response.data.nodes.length);
                setGraphData(response.data);
                loadGraph(buildGraph(response.data));
            })
            .catch((error) => {
                console.log(error);
            });

        loadGraph(buildGraph(graphData));
    }, [loadGraph]);

    return null;
};
export const GraphView = (props: { "sample_id": string | null }) => {
    const sample_id = props.sample_id
    return (
        <Container>
            <SigmaContainer
                graphOptions={{ type: "directed" }}
                initialSettings={{
                    defaultEdgeType: "arrow",
                }}
                style={{ height: "500px", width: "500px" }}
            >
                <LoadGraph />
            </SigmaContainer>
        </Container>
    );
};