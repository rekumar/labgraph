import { useEffect, useState } from "react";
import Graph from "graphology";
import { SigmaContainer, useLoadGraph } from "@react-sigma/core";
import "@react-sigma/core/lib/react-sigma.min.css";
import { Container } from "@mantine/core";
import { Api, SampleData } from "../api/api";

const nodeColors: { [nodetypes: string]: string } = {
    "Material": "#1C7ED6",
    "Action": "#FD7E14",
    "Analysis": "#E03131",
    "Measurement": "#37B24D"
} as const;

interface NodeEntry {
    "x": number;
    "y": number;
    "label": string;
    "size": number;
    "color": string;
    [otherOptions: string]: any;
}

interface NodeCollection {
    [id: string]: NodeEntry;
}

interface EdgeEntry {
    "key": string;
    "source": string;
    "target": string;
    "contents": {
        [otherOptions: string]: any;
    }
}


// const loadSampleGraph = (sample_id: string) => {
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


//     const buildGraph = (sample: SampleData) => {
//         var nodes: NodeCollection = {};
//         var edges: EdgeEntry[] = [];
//         var x = 0;
//         var y = 0;
//         var last_node_id: string | null = null;
//         for (const node_type in sample.nodes) {
//             for (const node_id in sample.nodes[node_type]) {
//                 const node = sample.nodes[node_type][node_id];
//                 nodes[node_id] = {
//                     "x": x,
//                     "y": y,
//                     "label": node,
//                     "size": 15,
//                     "color": nodeColors[node_type]
//                 }
//                 y += 15;
//                 if (last_node_id) {
//                     edges.push({
//                         "key": last_node_id + " -> " + node_id,
//                         "source": last_node_id,
//                         "target": node_id,
//                         "contents": {}
//                     })
//                 }
//             }
//             x += 15;
//             return { "nodes": nodes, "edges": edges }
//         }

//     }

//     const api = new Api();
//     api.getSample(sample_id)
//         .then((response) => {
//             setSample(response.data);
//         })
//         .catch((error) => {
//             console.log(error);
//         });
//     return buildGraph(sample);

// }


export const LoadGraph = (props: { sample_id: string | null }) => {
    const sample_id = props.sample_id;
    const [sample, setSample] = useState<SampleData>({
        "name": "Error",
        "description": "Error",
        "created_at": "Error",
        "nodes": {
            "Material": [],
            "Action": [],
            "Analysis": [],
            "Measurement": []
        },
        "tags": []
    })
    const loadGraph = useLoadGraph();

    const buildGraph = (sample: SampleData) => {
        var nodes: NodeCollection = {};
        var edges: EdgeEntry[] = [];
        var x = 0;
        var y = 0;
        var last_node_id: string | null = null;
        for (const node_type in sample.nodes) {
            for (const node_id of sample.nodes[node_type]) {
                nodes[node_id] = {
                    "x": x,
                    "y": y,
                    "label": node_id,
                    "size": 15,
                    "color": nodeColors[node_type]
                }
                if (last_node_id) {
                    // console.log(last_node_id + " -> " + node_id)
                    edges.push({
                        "key": last_node_id + " -> " + node_id,
                        "source": last_node_id,
                        "target": node_id,
                        "contents": {}
                    })
                }
                last_node_id = node_id;
                y += 15;
            }
            y = 0;
            x += 15;
        }
        return { "nodes": nodes, "edges": edges }
    }

    useEffect(() => {
        const graph = new Graph();
        if (sample_id) {
            const api = new Api();
            api.getSample(sample_id)
                .then((response) => {
                    setSample(response.data);
                })
                .catch((error) => {
                    console.log(error);
                });
        }

        const samplegraph = buildGraph(sample)
        for (const node_id in samplegraph.nodes) {
            graph.addNode(node_id, samplegraph.nodes[node_id]);
        }
        for (const edge of samplegraph.edges) {
            graph.addEdge(edge.source, edge.target, edge.contents);
        }

        loadGraph(graph);
    }, [loadGraph]);

    return null;
};

export const GraphView = (props: { "sample_id": string | null }) => {
    const sample_id = props.sample_id
    return (
        <Container>
            <SigmaContainer style={{ height: "500px", width: "500px" }}>
                <LoadGraph sample_id={sample_id} />
            </SigmaContainer>
        </Container>
    );
};