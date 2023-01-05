import axios from "axios";

const URL = process.env.NODE_ENV === "production" ? "" : "http://localhost:8896"

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
    getSampleSummary = () => {
        return this.init().get("/sample/summary");
    };

    getSample = (sample_id: string) => {
        return this.init().get(`/sample/${sample_id}`);
    };

    // Nodes

    getNode = (node_type: string, node_id: string) => {
        return this.init().get(`/${node_type}/${node_id}`);
    };


    // getUserList = (params) => {
    //     return this.init().get("/users", { params: params });
    // };
    // addNewUser = (data) => {
    //     return this.init().post("/users", data);
    // };
}