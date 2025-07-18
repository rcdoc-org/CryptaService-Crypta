import React, { useMemo } from 'react';
import { AgGridReact } from 'ag-grid-react';
import { ModuleRegistry } from 'ag-grid-community';
import { AllCommunityModule } from 'ag-grid-community';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';

// Register all community modules
ModuleRegistry.registerModules([AllCommunityModule]);

const DataGrid = ({ columns, data, options = {} }) => {
  // turn your column defs into AG-Grid’s format
  console.log('Data: ', data);
  const columnDefs = useMemo(() =>
    columns.map(col => {
      const { title, field, sorter, headerFilter, ...rest } = col;
      return {
        headerName: title,
        field,
        sortable: Boolean(sorter),
        filter: Boolean(headerFilter),
        resizable: true,
        ...rest,
      };
    })
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
        frameworkComponents={options.frameworkComponents}
        pagination={true}
        paginationPageSize={options.paginationSize ?? 20}
        rowSelection="single"
        onSelectionChanged={event => {
          if (options.onSelect) {
            const row = event.api.getSelectedRows()[0] || null;
            options.onSelect(row);
          }
        }}
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
