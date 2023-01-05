import axios from "axios";

const URL = process.env.NODE_ENV === "production" ? "" : "http://localhost:8895/api"

interface NodeList {
    Material: string[];
    Action: string[];
    Analysis: string[];
    Measurement: string[];
}
interface SampleSummaryData {
    "_id": string;
    "name": string;
    "description": string;
    "created_at": string;
    "nodes": NodeList;
    "tags": string[];
}

interface SampleData {
    "name": string;
    "description": string;
    "created_at": string;
    "nodes": NodeList;
    "tags": string[];
    [otherOptions: string]: any;
}

interface EdgeData {
    "node_type": string;
    "node_id": string;
}
interface NodeData {
    "_id": string;
    "name": string;
    "description": string;
    "upstream": EdgeData[];
    "downstream": EdgeData[];
    "created_at": string;
    "tags": string[];
    [otherOptions: string]: any;
}


export default class Api {
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
    getSampleSummary = (): Promise<{ data: SampleSummaryData[] }> => {
        return this.init().get("/sample/summary");
    };

    getSample = (sample_id: string): Promise<SampleData> => {
        return this.init().get(`/sample/${sample_id}`);
    };

    // Nodes
    getNode = (node_type: string, node_id: string): Promise<NodeData> => {
        return this.init().get(`/${node_type}/${node_id}`);
    };

    // addNewUser = (data) => {
    //     return this.init().post("/users", data);
    // };
}