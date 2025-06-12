import React, { useMemo } from 'react';
import { AgGridReact } from 'ag-grid-react';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';

const DataGrid = ({ columns, data, options = {} }) => {
  // turn your column defs into AG-Grid’s format
  const columnDefs = useMemo(() =>
    columns.map(col => ({
      headerName: col.title,
      field: col.field,
      sortable: Boolean(col.sorter),
      filter: Boolean(col.headerFilter),
      resizable: true,
    }))
  , [columns]);

  // sensible defaults for every column
  const defaultColDef = useMemo(() => ({
    flex: 1,
    minWidth: 120,
  }), []);

  return (
    <div
      className="ag-theme-alpine"
      style={{ width: '100%', height: '600px' /* tweak as needed */ }}
    >
      <AgGridReact
        rowData={data}
        columnDefs={columnDefs}
        defaultColDef={defaultColDef}
        pagination={true}
        paginationPageSize={options.paginationSize ?? 20}
        onRowClicked={event => {
          if (options.rowClick) {
            // mimic your old (e, row) API
            options.rowClick(event, { getData: () => event.data });
          }
        }}
        {...options.agGridProps /* advanced AG-Grid overrides */ }
      />
    </div>
  );
};

export default DataGrid;
