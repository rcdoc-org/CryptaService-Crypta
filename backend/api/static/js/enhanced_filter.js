(function() {
    // read config values injected into the page
    const csrfToken         = document.querySelector('meta[name="csrf-token"]').content;
    const filterURL         = document.querySelector('meta[name="filter-url"]').content;
    const filterSidebar     = document.getElementById('filterSidebar');
    const baseSelect        = document.getElementById('baseSelect');
    const columnForm        = document.getElementById('columnForm');
    const applyBtn          = document.getElementById('applyColumnsBtn');

    let lastBase = null;
    
    let currentColumns      = [];   // will hold {title, field}[]

    let table;                      // Tabulator Instance

    // keep most recent stats_info from the server
    let lastStatsInfo = [];
    // keep the user's last slider/radio settings
    let currentStats = {};

    // 1) Gather which filters are check + which base (person/location) is selected.
    function gatherFilters() {
        const checked = Array.from(
            filterSidebar.querySelectorAll('input.filter-checkbox:checked')
            ).map(chk => chk.value);
        const base = baseSelect.value;

        // collect stats
        const stats = {};
        // number ranges
        document.querySelectorAll('.stats-range').forEach(r => {
            const f = r.dataset.field;
            const minIn = document.getElementById(`stat_min_${f}`);
            const maxIn = document.getElementById(`stat_max_${f}`);

            // Only send if the user has changed value
            if (+minIn.value > +r.min || +maxIn.value < +r.max) {
                stats[`${f}_min`] = minIn.value;
                stats[`${f}_max`] = maxIn.value;
            }
        });
        // boolean
        document.querySelectorAll('.stats-boolean:checked').forEach( r => {
            stats[r.dataset.field] = r.value; // "true", "false", "all"
        });

        return { base, filters: checked, stats };
    }

    function renderStatsFilters(info, savedStats) {
        const ctr = document.getElementById('statsFilters');
        ctr.innerHTML = '';

        // build list of fields that are BOTH in the "Statistics" category AND currently visible:
        const visibleStats = currentColumns
        .filter(col => col.category === 'Statistics' && table.getColumn(col.field)?.isVisible())
        .map(col => col.field);

          // only keep the stats_info entries for those fields
        info = info.filter(s => visibleStats.includes(s.field));
        if (!info.length) return;

        const heading = document.createElement('h6');
        heading.textContent = 'Statistics';
        ctr.appendChild(heading);

        info.forEach(({ field, display, type, min, max }) => {
            const div = document.createElement('div');
            div.className = 'mb-3';

            if (type === 'boolean') {
                const title_lbl = document.createElement('label');
                title_lbl.textContent = `${display}:`;
                const breakline = document.createElement('br');
                div.appendChild(title_lbl);
                div.appendChild(breakline);
                ['true', 'false', 'all'].forEach(val => {
                    const rd = document.createElement('div');
                    rd.className = 'form-check form-check-inline';
                    const inp = document.createElement('input');
                    inp.className = 'form-check-input stats-boolean';
                    inp.type = 'radio';
                    inp.name = `stat_${field}`;
                    inp.dataset.field = field;
                    inp.value = val;
                    
                    if (val === 'all') inp.checked = true;
                    const lbl = document.createElement('label');
                    lbl.className = 'form-check-label';
                    lbl.textContent = val.charAt(0).toUpperCase() + val.slice(1);
                    rd.append(inp, lbl);
                    div.appendChild(rd);
                    inp.checked = (savedStats[field] || 'all') === val
                });
            } else { // number 
                const currentMin = savedStats[`${field}_min`] != null
                         ? savedStats[`${field}_min`] 
                         : min;
                const currentMax = savedStats[`${field}_max`] != null
                         ? savedStats[`${field}_max`]
                         : max;

                const lbl = document.createElement('label');
                lbl.textContent = `${display}:`;

                const minIn = document.createElement('input');
                minIn.type = 'number';
                minIn.id = `stat_min_${field}`;
                minIn.value = currentMin;
                minIn.className = 'form-control form-control-sm d-inline-block w-auto me-2 stats-min';

                const maxIn = document.createElement('input');
                maxIn.type = 'number';
                maxIn.id = `stat_max_${field}`;
                maxIn.value = currentMax;
                maxIn.className = 'form-control form-control-sm d-inline-block w-auto stats-max';

                const range = document.createElement('input');
                range.type = 'range';
                range.className = 'form-range stats-range';
                range.dataset.field = field;
                range.min = min; 
                range.max = max; 
                range.value = currentMin;
                range.step = (max - min) / 100 || 1;

                // sync them together
                range.addEventListener('input', () => {
                    minIn.value = range.value;
                });
                minIn.addEventListener('change', () => {
                    range.value = minIn.value;
                });

                div.append(lbl, minIn, maxIn, range);
            }

            div.querySelectorAll('input').forEach( i => i.addEventListener('change', updateView));
            ctr.appendChild(div);
        });
    }

    function clearFilters() {
        filterSidebar
            .querySelectorAll('input.filter-checkbox:checked')
            .forEach(cb => cb.checked = false);

        document.getElementById('activeFilters').innerHTML = '';

        lastBase = null;
    }

    function toggle() {
        clearFilters();
        updateView();
    }

    // 2) Replace the sidebar HTML wholesale with the server-rendered version
    function renderFilters(html) {
        filterSidebar.innerHTML = html;
    }

    // 3) Render 'active' filter badges at the top, with an X to remove each one.
    function renderActiveFilters(data) {
        const container = document.getElementById('activeFilters');
        container.innerHTML = '';
      
        data.filters.forEach(f => {
          const [field, value] = f.split(':', 2);
      
          // Build the badge
          const badge = document.createElement('span');
          badge.className = 'badge bg-secondary me-1';
          badge.textContent = `${field}: ${value}`;    // or use a nicer label if you read data-display
      
          // The “×” icon
          const x = document.createElement('i');
          x.className = 'fas fa-times ms-1';
          x.style.cursor = 'pointer';
      
          x.addEventListener('click', () => {
            // **re-query** the *current* checkbox in the sidebar
            const selector = `.filter-checkbox[value="${field}:${value}"]`;
            const cb = document.querySelector(selector);
            if (cb) {
              cb.checked = false;
              updateView();   // now gathers from the live inputs
            }
          });
      
          badge.appendChild(x);
          container.appendChild(badge);
        });
      }
      

    // 4) Core Function: gather filters, show badges, POST to Django, then update sidebar
    // and table
    function updateView() {
        const data = gatherFilters();
        currentStats = data.stats;
        const baseChanged = data.base !== lastBase;
        lastBase = data.base;

        fetch(filterURL, {
            method: 'POST',
            headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
            },
            body: JSON.stringify(data)
        })
        .then(res => res.json())
        .then(payload => {
            // 1) Update the side bar
            renderFilters(payload.filters_html);

            // savethe returned stats_info to be reused
            lastStatsInfo = payload.stats_info;
            const freshData = gatherFilters();
            renderActiveFilters(freshData);
            renderActiveFilters(data);

            // Grab dyanmic columns from server
            const dynamicCols = payload.grid.columns;

            // define always-visible Details Column
            const detailCol = {
                titleFormatter: "html",
                title: "<i class='fas fa-search'></i>",
                headerSort: false,
                hozAlign: "center",
                width: 40,
                formatter: cell => "<i class='fas fa-search'></i>",
                cellClick: (e, cell) => {
                    const rowData = cell.getRow().getData();
                    showDetailModal(rowData);
                },
            };

            // inital-only fields
            const defaults = data.base === "person"
                ? ["First Name", "Middle Name", "Last Name"]
                : ["Name", "Type"];
            
            // merge detailCol + dynamicCols, tagging each dynamic col with visible:true/false
            const allCols = [
                detailCol,
                ...dynamicCols.map(col => ({
                ...col,
                visible: defaults.includes(col.field)   // true for default, false otherwise
                }))
            ];

            // —— initialize or re-initialize on base change
            if (!table || baseChanged) {
                if (!table) {
                // very first creation
                table = new Tabulator("#data-grid", {
                    layout: "fitColumns",
                    data: payload.grid.data,
                    columns: allCols,
                    placeholder: "No Data Available",
                });
                } else {
                // base just flipped
                table.setColumns(allCols);
                table.setData(payload.grid.data);
                }
            } else {
                // normal filter refresh
                table.setColumns(allCols); 
                table.setData(payload.grid.data);
                }

            currentColumns = dynamicCols;
            populateColumnForm();

            // render stats for any visible
            renderStatsFilters(lastStatsInfo, currentStats);


            // Result determining and updating of the header for results
            const rowCount = payload.grid.data.length;
            const headerEl = document.getElementById('results-header');
            headerEl.textContent = `Results (${rowCount})`; 
        });
    }

    function showDetailModal(data) {
        const body = JSON.stringify(data, null, 2);
        document.getElementById('detailModalBody').textContent = body;
        const modal = new bootstrap.Modal(document.getElementById('detailModal'));
        modal.show();
    }

    // 5) Build the column-chooser form inside the modal
    function populateColumnForm() {
        columnForm.innerHTML = '';
        // group by `category`
        const byCat = currentColumns.reduce((acc, col) => {
            (acc[col.category] = acc[col.category] || []).push(col);
            return acc;
        }, {});

        const accordion = document.createElement("div");
        accordion.className = "accordion";
        accordion.id = "columnsAccordion";

        Object.entries(byCat).forEach(([cat, cols], idx) => {
            const count = cols.length
            const item = document.createElement("div");
            item.className = "accordion-item";
            item.innerHTML = `
            <h2 class="accordion-header" id="heading${idx}">
                <button class="accordion-button ${idx>0?"collapsed":""}"
                        type="button"
                        data-bs-toggle="collapse"
                        data-bs-target="#collapse${idx}"
                        aria-expanded="${idx===0}"
                        aria-controls="collapse${idx}">
                ${cat} (${count})
                </button>
            </h2>
            <div id="collapse${idx}"
                class="accordion-collapse collapse ${idx===0?"show":""}"
                aria-labelledby="heading${idx}"
                data-bs-parent="#columnsAccordion">
                <div class="accordion-body row">
                ${cols.map(col => `
                    <div class="col-6 form-check">
                    <input class="form-check-input" type="checkbox"
                            id="col_${col.field}"
                            value="${col.field}"
                            ${table.getColumn(col.field)?.isVisible() ? "checked" : ""}>
                    <label class="form-check-label" for="col_${col.field}">
                        ${col.title}
                    </label>
                    </div>
                `).join("")}
                </div>
            </div>
            `;
            accordion.appendChild(item);
        });

        columnForm.appendChild(accordion);
    }

    // 6) Auto Grow Elements for large text boxes
    function auto_grow(el) {
        el.style.height = 'auto';
        el.style.height = el.scrollHeight + 'px';
    }

    function getCookie(name) {
        let cookieValue = null;
        document.cookie.split(';').forEach(c => {
            c = c.trim();
            if (c.startsWith(name + '=')) {
            cookieValue = decodeURIComponent(c.slice(name.length + 1));
            }
        });
        return cookieValue;
    }

    function makeHidden(name, value) {
        const inp = document.createElement('input')
        inp.type = 'hidden';
        inp.name = name;
        inp.value = value;
        return inp;
    }

    async function uploadAttachment() {
        const fileInput = document.getElementById('attachment');
        if (!fileInput || fileInput.files.length === 0) {
            return null;
        }

        const file = fileInput.files[0];
        const fd = new FormData();
        fd.append('attachment', file);

        const response = await fetch('/api/upload-tmp', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrfToken'),
            },
            body: fd
        });

        if(!response.ok) {
            throw new Error('Upload failed');
        }
        return response.json();
    }

    // 7) Wire up events and inital load
    function init(){

        // Email Checker and confirmation system
        // Ensures no missing mandatory items and gives user confirmation box before sending
        const form = document.getElementById('emailForm');
        const sendBtn = document.getElementById('sendEmailBtn');
        const subjectEl = document.getElementById('subject');
        const bodyEl = document.getElementById('body');
        const cbs =  [
            {el: document.getElementById('personalEmail'), label: 'Personal Emails'},
            {el: document.getElementById('parishEmail'), label: 'Parish Emails'},
            {el: document.getElementById('diocesanEmail'), label: 'Diocesan Emails'},
        ];

        // Sending email logic And confirmtion boxes.
        sendBtn.addEventListener('click', async (e) => {
            e.preventDefault();

            // trim and test mandatory items
            const subj = subjectEl.value.trim();
            const bdy = bodyEl.value.trim();
            const checked = cbs
                .filter(cb => cb.el.checked)
                .map(cb => cb.label);

            // gather missing
            const missing = [];
            if(!subj)   missing.push('Subject');
            if(!bdy)    missing.push('Body');
            if(!checked.length) missing.push('At least one recipient type');

            if (missing.length) {
                alert('Please provide: ' + missing.join(', '));
                return;
            }

            const summary =
            ` Please confirm before sending:\n\n` +
            `Subject: ${subj}\n` +
            `Recipients: ${checked.join(', ')}\n\n` +
            `Body:\n${bdy}`;

            if(!confirm(summary)) {
                // user cancelled
                return;
            }

            try {
                const uploadResult = await uploadAttachment();
                if (uploadResult && uploadResult.url) {
                    // inject hidden field with temp path
                    let hidden = form.querySelector('input[name="temp_attachment_path"]');
                    if (!hidden) {
                        hidden = document.createElement('input');
                        hidden.type = 'hidden';
                        hidden.name = 'temp_attachment_path';
                        form.appendChild(hidden);
                    }
                    hidden.value = uploadResult.url;
                }
            } catch (err) {
                alert('Failed to upload attachment: ' + err.message);
                return;
            }

            // Grad and inject current filters
            const { base, filters } = gatherFilters();
            form.appendChild(makeHidden('base', base));
            filters.forEach(f => form.appendChild(makeHidden('filters', f)));

            // all good actually submit
            form.submit();

        });

        // Used for auto growing the input box for email body.
        auto_grow(bodyEl)
        bodyEl.addEventListener('input', () => auto_grow(bodyEl));

        // When "Apply" is clicked for column display modal, show/hide columns then close modal
        applyBtn.addEventListener('click', () => {
            const checkFields = Array.from(columnForm.querySelectorAll('input:checked'))
                                    .map(i=>i.value);
            
            currentColumns.forEach(col => {
                if (checkFields.includes(col.field)) {
                table.showColumn(col.field);
                } else {
                table.hideColumn(col.field);
                }
            });

            table.redraw(true);

            // after showing/hiding columns, re-render stats for newly-visible ones
            renderStatsFilters(lastStatsInfo, currentStats);
            // bootstrap modal hide
            const modalEl = document.getElementById('columnModal');
            bootstrap.Modal.getInstance(modalEl).hide();
        })

        // Whenever a filter checkbox or the base-toggle radio changes, re-fetch
        filterSidebar.addEventListener('change', updateView);
        baseSelect.addEventListener('change', toggle);

        // ensure we populate everytime the modal opens
        const colModalEl = document.getElementById('columnModal');
        colModalEl.addEventListener('show.bs.modal', () => {
            populateColumnForm();
        });

        // Delegate toggle and checkbox events
        updateView();
        }

    // run init() once the DOM is ready
    if(document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }})();