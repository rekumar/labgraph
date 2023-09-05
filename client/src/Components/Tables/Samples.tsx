import { useState, useEffect } from 'react';
import {
    ScrollArea,
    MultiSelect,
} from '@mantine/core';
import { DataTable } from "mantine-datatable";
import { Api, SampleData } from '../../api/api';
import { samples } from '../../__mock__/samples';
interface SortableRowData {
    _id: string;
    name: string;
    description: string;
    created_at: string;
    // updated_at?: string;
}

interface RowData extends SortableRowData {
    tags: string[];
    nodes: {
        [node_type: string]: string[];
    };
}

interface TableSortProps {
    data: RowData[];
}


function uniqueTags(data: SampleData[]) {
    const tags = data.reduce((acc, { tags }) => {
        tags.forEach((tag) => {
            if (!acc.includes(tag)) {
                acc.push(tag);
            }
        });
        return acc;
    }, [] as string[]);
    tags.sort();
    return tags;
}
export function SampleTable() {
    const api = new Api();
    const ITEMS_PER_PAGE = 10;



    const [data, setData] = useState(samples)
    const [page, setPage] = useState(1);
    const [taggedRecords, setTaggedRecords] = useState(data);
    const [records, setRecords] = useState(taggedRecords.slice(0, ITEMS_PER_PAGE));
    const allTags = uniqueTags(data);
    const [selectedTags, setSelectedTags] = useState<string[]>([]);

    const handleInitialSetup = (data: SampleData[]) => {
        setData(data);
        setTaggedRecords(data);
        setRecords(data.slice(0, ITEMS_PER_PAGE));
    }

    useEffect(() => {
        api
            .getSampleSummary()
            .then((response) => {
                handleInitialSetup(response.data);
                console.log("received " + response.data.length + " samples");

            })
            .catch((err) => {
                console.log("error retrieving samples: " + err);
            });

    }, []);

    const handleTagChange = (tags: string[]) => {
        setSelectedTags(tags);
        var thisTaggedRecords: SampleData[] = [];
        if (tags.length === 0) {
            thisTaggedRecords = data;
        } else {
            thisTaggedRecords = data.filter((row) => tags.every(this_tag => row.tags.includes(this_tag)));
        }
        setTaggedRecords(thisTaggedRecords);
        setPage(1);
        setRecords(thisTaggedRecords.slice(0, ITEMS_PER_PAGE));
    };

    const handlePageChange = (page: number) => {
        setPage(page);
        const from = (page - 1) * ITEMS_PER_PAGE;
        const to = from + ITEMS_PER_PAGE;
        setRecords(taggedRecords.slice(from, to));
    };

    return (
        <ScrollArea>
            <MultiSelect
                label="Tags"
                data={allTags}
                value={selectedTags}
                onChange={(value) => handleTagChange(value)}
                placeholder="Select tags to filter the table."
                searchable
                clearable
                clearButtonLabel='Clear selection'
                maxDropdownHeight={160}
            />
            <DataTable
                withBorder
                borderRadius="sm"
                withColumnBorders
                striped
                highlightOnHover
                // provide data
                records={records}
                recordsPerPage={ITEMS_PER_PAGE}
                page={page}
                totalRecords={taggedRecords.length}
                onPageChange={(page) => handlePageChange(page)}
                // define columns
                columns={[
                    {
                        accessor: 'name',
                    },
                    {
                        accessor: 'description',
                    },
                    // {
                    //     accessor: 'nodes',
                    //     render: (nodes: NodeList) => {
                    //         return (
                    //             <Text>{nodes.Action.length + nodes.Analysis.length + nodes.Measurement.length + nodes.Material.length}</Text>
                    //         );
                    //     },
                    // },
                    {
                        accessor: 'created_at',
                    },
                ]}
                onRowClick={({ name, description, nodes }) =>
                    alert(`You clicked on ${name}, a ${description.toLowerCase()} president born in ${nodes}`)
                }
            />
        </ScrollArea>
    );
}