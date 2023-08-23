// @ts-nocheck

import { useState } from 'react';
import React from 'react';

import {
    createStyles,
    Table,
    ScrollArea,
    UnstyledButton,
    Group,
    Text,
    Center,
    TextInput,
} from '@mantine/core';
import { keys } from '@mantine/utils';
import { IconSelector, IconChevronDown, IconChevronUp, IconSearch } from '@tabler/icons';

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
    description: string;
    created_at: string;
    updated_at: string;
}

interface NodeEntry {
    node_type: string;
    node_id: string;
}

interface RowData extends SortableRowData {
    tags: string[];
}

interface TableSortProps {
    data: RowData[];
}

interface ThProps {
    children: React.ReactNode;
    reversed: boolean;
    sorted: boolean;
    onSort(): void;
}

function Th({ children, reversed, sorted, onSort }: ThProps) {
    const { classes } = useStyles();
    const Icon = sorted ? (reversed ? IconChevronUp : IconChevronDown) : IconSelector;
    return (
        <th className={classes.th}>
            <UnstyledButton onClick={onSort} className={classes.control}>
                <Group position="apart">
                    <Text weight={500} size="sm">
                        {children}
                    </Text>
                    <Center className={classes.icon}>
                        <Icon size={14} stroke={1.5} />
                    </Center>
                </Group>
            </UnstyledButton>
        </th>
    );
}

interface UnsortableThProps {
    children: React.ReactNode;
}
function UnsortableTh({ children }: UnsortableThProps) {
    const { classes } = useStyles();
    return (
        <th className={classes.th}>
            <UnstyledButton className={classes.control}>
                <Group position="apart">
                    <Text weight={500} size="sm">
                        {children}
                    </Text>
                </Group>
            </UnstyledButton>
        </th>
    );
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

export function ActorsTable({ data }: TableSortProps) {
    const [search, setSearch] = useState('');
    const [sortedData, setSortedData] = useState(data);
    const [sortBy, setSortBy] = useState<keyof SortableRowData | null>(null);
    const [reverseSortDirection, setReverseSortDirection] = useState(false);

    const setSorting = (field: keyof SortableRowData) => {
        const reversed = field === sortBy ? !reverseSortDirection : false;
        setReverseSortDirection(reversed);
        setSortBy(field);
        setSortedData(sortData(data, { sortBy: field, reversed, search }));
    };

    const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const { value } = event.currentTarget;
        setSearch(value);
        setSortedData(sortData(data, { sortBy, reversed: reverseSortDirection, search: value }));
    };

    const rows = sortedData.map((row) => (
        <tr key={row._id}>
            <td>{row.name}</td>
            <td><Text lineClamp={1}>{row.description}</Text></td>
            <td>{row.tags}</td>
            <td>{row.created_at}</td>
            {/* <td>{row.updated_at}</td> */}
        </tr>
    ));

    return (
        <ScrollArea>
            <TextInput
                placeholder="Search by any field"
                mb="md"
                icon={<IconSearch size={14} stroke={1.5} />}
                value={search}
                onChange={handleSearchChange}
            />
            <Table
                horizontalSpacing="md"
                verticalSpacing="xs"
                sx={{ tableLayout: 'fixed', minWidth: 700 }}
            >
                <thead>
                    <tr>
                        <Th
                            sorted={sortBy === 'name'}
                            reversed={reverseSortDirection}
                            onSort={() => setSorting('name')}
                        >
                            Name
                        </Th>
                        <Th
                            sorted={sortBy === 'name'}
                            reversed={reverseSortDirection}
                            onSort={() => setSorting('name')}
                        >
                            Description
                        </Th>
                        <UnsortableTh>
                            Tags
                        </UnsortableTh>
                        <Th
                            sorted={sortBy === 'created_at'}
                            reversed={reverseSortDirection}
                            onSort={() => setSorting('created_at')}
                        >
                            Created At
                        </Th>

                    </tr>
                </thead>
                <tbody>
                    {rows.length > 0 ? (
                        rows
                    ) : (
                        <tr>
                            <td colSpan={Object.keys(data[0]).length}>
                                <Text weight={500} align="center">
                                    Nothing found
                                </Text>
                            </td>
                        </tr>
                    )}
                </tbody>
            </Table>
        </ScrollArea>
    );
}