// @ts-nocheck

import { useState, useEffect } from 'react';

import {
    createStyles,
    ScrollArea,
    UnstyledButton,
    Group,
    Text,
    Center,
} from '@mantine/core';
import { keys } from '@mantine/utils';
import { IconSelector, IconChevronDown, IconChevronUp } from '@tabler/icons';
import { DataTable } from "mantine-datatable";

const useStyles = createStyles((theme) => ({
    th: {
        padding: '0 !important',
    },

    control: {
        width: '100%',
        padding: `${theme.spacing.xs}px ${theme.spacing.md}px`,

        '&:hover': {
            backgroundColor: theme.colorScheme === 'dark' ? theme.colors.dark[6] : theme.colors.gray[0],
        },
    },

    icon: {
        width: 21,
        height: 21,
        borderRadius: 21,
    },
}));

interface SortableRowData {
    _id: string;
    name: string;
    created_at: string;
    updated_at: string;
}

interface NodeEntry {
    node_type: string;
    node_id: string;
}

interface RowData extends SortableRowData {
    tags: string[];
    upstream: NodeEntry[];
    downstream: NodeEntry[];
}

interface TableSortProps {
    data: RowData[];
}




function prepForFilter(data: any) {
    if (typeof data === 'string') {
        return data.toLowerCase().trim();
    } else if (typeof data === "undefined") {
        return "";
    } else {
        return data.toString().toLowerCase().trim();
    }
}
function filterData(data: RowData[], search: string) {
    const query = search.toLowerCase().trim();
    return data.filter((item) =>
        keys(data[0]).some((key) => prepForFilter(item[key]).includes(query))
    );
}

function sortData(
    data: RowData[],
    payload: { sortBy: keyof SortableRowData | null; reversed: boolean; search: string }
) {
    const { sortBy } = payload;

    if (!sortBy) {
        return filterData(data, payload.search);
    }

    return filterData(
        [...data].sort((a, b) => {
            if (payload.reversed) {
                return b[sortBy].localeCompare(a[sortBy]);
            }

            return a[sortBy].localeCompare(b[sortBy]);
        }),
        payload.search
    );
}

export function MaterialsTable({ data }: TableSortProps) {
    const ITEMS_PER_PAGE = 10;
    const [page, setPage] = useState(1);
    const [records, setRecords] = useState(data.slice(0, ITEMS_PER_PAGE));

    useEffect(() => {
        const from = (page - 1) * ITEMS_PER_PAGE;
        const to = from + ITEMS_PER_PAGE;
        setRecords(data.slice(from, to));
    }, [page]);

    return (
        <ScrollArea>
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
                totalRecords={data.length}
                onPageChange={(page) => setPage(page)}
                // define columns
                columns={[
                    {
                        accessor: 'name',
                    },
                    {
                        accessor: 'upstream',
                        render: ({ upstream }) => (
                            <Text> {upstream.length} </Text>
                        )
                    },
                    {
                        accessor: 'downstream',
                        render: ({ downstream }) => (
                            <Text> {downstream.length} </Text>
                        )
                    },
                    {
                        accessor: 'created_at',
                    },
                ]}
            // execute this callback when a row is clicked
            // onRowClick={({ name, party, bornIn }) =>
            //     alert(`You clicked on ${name}, a ${party.toLowerCase()} president born in ${bornIn}`)
            // }
            />
        </ScrollArea>
    );
}