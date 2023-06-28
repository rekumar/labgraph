import { keys } from '@mantine/utils';

interface RowData { test: string }
interface SortableRowData { test: string }

export function prepForFilter(data: any) {
    if (typeof data === 'string') {
        return data.toLowerCase().trim();
    } else if (typeof data === "undefined") {
        return "";
    } else {
        return data.toString().toLowerCase().trim();
    }
}
export function filterData(data: RowData[], search: string) {
    const query = search.toLowerCase().trim();
    return data.filter((item) =>
        keys(data[0]).some((key) => prepForFilter(item[key]).includes(query))
    );
}

export function sortData(
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