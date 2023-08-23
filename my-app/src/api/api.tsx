import axios from "axios";

const URL = process.env.NODE_ENV === "production" ? "" : "http://localhost:8899/api"

export interface NodeList {
    [node_type: string]: string[];
}
export interface SampleSummaryData {
    "_id": string;
    "name": string;
    "description": string;
    "created_at": string;
    "nodes": NodeList;
    "tags": string[];
}

export interface SampleData {
    "name": string;
    "description": string;
    "created_at": string;
    "nodes": NodeList;
    "tags": string[];
    [otherOptions: string]: any;
}

export interface EdgeData {
    "node_type": string;
    "node_id": string;
}

export interface NodeData {
    "_id": string;
    "name": string;
    "description": string;
    "created_at": string;
    "tags": string[];
    "upstream": EdgeData[];
    "downstream": EdgeData[];
    [otherOptions: string]: any;
}

export interface NodeForGraph {
    "_id": string;
    "x": number;
    "y": number;
    "label": string;
    "size": number;
    "contents": { [otherOptions: string]: any };
}


export interface EdgeForGraph {
    "source": string;
    "target": string;
    "contents": {
        [otherOptions: string]: any;
    };
}
export interface GraphData {
    "nodes": NodeForGraph[];
    "edges": EdgeForGraph[];
}

export class Api {
    client: any;
    api_token: null;
    api_url: string | undefined;
    constructor() {
        this.api_token = null;
        this.client = null;
        this.api_url = URL;
    }
    init = () => {
        //   this.api_token = getCookie("ACCESS_TOKEN");
        let headers = {
            Accept: "application/json"
        };
        //   if (this.api_token) {
        //     headers.Authorization = `Bearer ${
        //       this.api_token
        //     }`;
        //   }
        this.client = axios.create({ baseURL: this.api_url, timeout: 31000, headers: headers });
        return this.client;
    };

    // Samples
    getSampleSummary = (count: number = 0): Promise<{ data: SampleSummaryData[] }> => {
        return this.init().get("/sample/summary/" + count);
    };

    getSample = (sample_id: string): Promise<{ data: SampleData }> => {
        return this.init().get(`/sample/${sample_id}`);
    };

    // Nodes
    getNode = (node_type: string, node_id: string): Promise<{ data: NodeData }> => {
        return this.init().get(`/${node_type}/${node_id}`);
    };

    getCompleteGraph = (): Promise<{ data: GraphData }> => {
        return this.init().get("/graph/complete");
    };

    getSamplesGraph = (sample_ids: string[]): Promise<{ data: GraphData }> => {
        return this.init().post("/graph/samples", { "sample_ids": sample_ids });
    };

    // addNewUser = (data) => {
    //     return this.init().post("/users", data);
    // };
}