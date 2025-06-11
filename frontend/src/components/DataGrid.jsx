import React, { useEffect, useRef } from 'react';
import * as Tabulator from 'tabulator-tables';
import 'tabulator-tables/dist/css/tabulator.min.css';

const DataGrid = ({ columns, data, options = {} }) => {
    const gridRef = useRef(null);

    useEffect(() => {
        const table = new Tabulator(gridRef.current, {
            data,
            columns,
            layout: 'fitColumns',
            pagination: 'local',
            paginationSize: 20,
            ...options,
        });
        return () => table.destroy();
    }, [columns, data, options]);
};

export default DataGrid;