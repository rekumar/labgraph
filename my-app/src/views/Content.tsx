import Tables from '../components/Tables';
import { GraphView } from '../components/GraphView';
import { Container } from '@mantine/core';
import { useEffect, useState } from 'react';
import { Api, SampleSummaryData } from '../api/api';

function Content() {
    const [selectedSamples, setSelectedSamples] = useState<string[]>(["647a3f470996f47f43dc1e2f", "647a3f470996f47f43dc1e2a"]);

    // retriee sample ids upon initial mount
    useEffect(() => {
        const api = new Api();
        api.getSampleSummary(200)
            .then((response) => {
                console.log(response.data);
                const sample_ids = response.data.map((sample: SampleSummaryData) => sample._id);
                setSelectedSamples(sample_ids);
            })
            .catch((error) => {
                console.log(error);
            });
    }, []);


    return (
        <>
            <GraphView selectedSamples={selectedSamples} />
            <Tables />


        </>
    )
};

export default Content;