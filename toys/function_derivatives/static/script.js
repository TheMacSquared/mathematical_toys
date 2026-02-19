// === STAN APLIKACJI ===
var state = {
    func: 'sin',
    params: {},
    viewMode: 'separate',
    xMin: -6.28,
    xMax: 6.28,
    results: null,
    functionDefs: {}
};

var debounceTimer = null;

var COLORS = {
    func: '#6366f1',
    derivative: '#ef4444'
};

// === INICJALIZACJA ===
document.addEventListener('DOMContentLoaded', function() {
    loadFunctions();
});

// === LADOWANIE FUNKCJI ===
function loadFunctions() {
    fetch('/api/functions')
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (data.success) {
                state.functionDefs = data.functions;
                populateFunctionSelect();
                setupInputs();
                setupViewModeToggle();
                buildParamInputs(state.func);
                updatePlot();
            }
        });
}

function populateFunctionSelect() {
    var select = document.getElementById('func-select');
    select.innerHTML = '';
    var order = ['sin', 'cos', 'exp', 'ln', 'linear', 'quadratic', 'cubic', 'power', 'sqrt', 'tan'];
    for (var i = 0; i < order.length; i++) {
        var key = order[i];
        if (state.functionDefs[key]) {
            var opt = document.createElement('option');
            opt.value = key;
            opt.textContent = state.functionDefs[key].name;
            select.appendChild(opt);
        }
    }
}

// === KONTROLKI ===
function setupInputs() {
    document.getElementById('func-select').addEventListener('change', function() {
        state.func = this.value;
        var def = state.functionDefs[state.func];
        if (def) {
            state.xMin = def.default_range[0];
            state.xMax = def.default_range[1];
            document.getElementById('x-min').value = Math.round(state.xMin * 100) / 100;
            document.getElementById('x-max').value = Math.round(state.xMax * 100) / 100;
        }
        buildParamInputs(state.func);
        scheduleUpdate();
    });

    document.getElementById('x-min').addEventListener('input', function() {
        var val = parseFloat(this.value);
        if (!isNaN(val)) {
            state.xMin = val;
            scheduleUpdate();
        }
    });

    document.getElementById('x-max').addEventListener('input', function() {
        var val = parseFloat(this.value);
        if (!isNaN(val)) {
            state.xMax = val;
            scheduleUpdate();
        }
    });

    document.getElementById('btn-update').addEventListener('click', function() {
        updatePlot();
    });
}

function setupViewModeToggle() {
    var options = document.querySelectorAll('.fd-view-mode__option');
    for (var i = 0; i < options.length; i++) {
        options[i].addEventListener('click', function() {
            for (var j = 0; j < options.length; j++) {
                options[j].classList.remove('fd-view-mode__option--active');
            }
            this.classList.add('fd-view-mode__option--active');
            state.viewMode = this.getAttribute('data-mode');
            togglePlotVisibility();
            drawPlots();
        });
    }
}

function togglePlotVisibility() {
    var separatePlots = document.getElementById('separate-plots');
    var combinedPlot = document.getElementById('combined-plot');

    if (state.viewMode === 'separate') {
        separatePlots.classList.remove('fd-plot-hidden');
        combinedPlot.classList.add('fd-plot-hidden');
    } else {
        separatePlots.classList.add('fd-plot-hidden');
        combinedPlot.classList.remove('fd-plot-hidden');
    }
}

// === DYNAMICZNE PARAMETRY ===
function buildParamInputs(funcId) {
    var container = document.getElementById('params-container');
    var def = state.functionDefs[funcId];
    if (!def) return;

    state.params = {};
    var html = '<div class="st-input-group"><label>Parametry</label>';
    html += '<div class="fd-params__grid">';

    for (var i = 0; i < def.params.length; i++) {
        var p = def.params[i];
        state.params[p.id] = p.default;
        html += '<div class="st-input-group">';
        html += '<label for="param-' + p.id + '">' + p.label + '</label>';
        html += '<input type="number" id="param-' + p.id + '" class="st-input fd-param-input" ';
        html += 'value="' + p.default + '" ';
        html += 'min="' + p.min + '" max="' + p.max + '" step="' + p.step + '" ';
        html += 'data-param="' + p.id + '">';
        html += '</div>';
    }

    html += '</div></div>';
    container.innerHTML = html;

    // Bind event listeners
    var inputs = container.querySelectorAll('.fd-param-input');
    for (var j = 0; j < inputs.length; j++) {
        inputs[j].addEventListener('input', function() {
            var val = parseFloat(this.value);
            if (!isNaN(val)) {
                state.params[this.getAttribute('data-param')] = val;
                scheduleUpdate();
            }
        });
    }
}

function scheduleUpdate() {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(function() {
        updatePlot();
    }, 250);
}

// === OBLICZENIA ===
async function updatePlot() {
    var loadingEl = document.getElementById('loading');

    try {
        loadingEl.classList.add('st-loading--active');

        var body = {
            func: state.func,
            params: state.params,
            view_mode: state.viewMode,
            x_min: state.xMin,
            x_max: state.xMax
        };

        var response = await fetch('/api/compute', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });

        if (!response.ok) {
            var err = await response.json();
            throw new Error(err.error || 'HTTP ' + response.status);
        }

        var data = await response.json();

        if (data.success) {
            state.results = data;
            updateFormulas();
            drawPlots();
        }
    } catch (error) {
        console.error('Blad:', error.message);
    } finally {
        loadingEl.classList.remove('st-loading--active');
    }
}

// === WYKRESY ===
function drawPlots() {
    if (!state.results) return;

    if (state.viewMode === 'separate') {
        drawSeparatePlots();
    } else {
        drawCombinedPlot();
    }
}

function drawSeparatePlots() {
    var res = state.results;
    var config = { responsive: true, displayModeBar: false, displaylogo: false };

    // Wykres funkcji
    var funcTraces = [{
        x: res.func_data.x,
        y: res.func_data.y,
        mode: 'lines',
        name: 'f(x)',
        line: { color: COLORS.func, width: 3 },
        connectgaps: false,
        hovertemplate: 'f(%{x:.3f}) = %{y:.6f}<extra></extra>'
    }];

    var funcLayout = makePlotLayout('f(x)', res.y_range_func);
    Plotly.newPlot('plot-func', funcTraces, funcLayout, config);

    // Wykres pochodnej
    var derivTraces = [{
        x: res.derivative_data.x,
        y: res.derivative_data.y,
        mode: 'lines',
        name: "f'(x)",
        line: { color: COLORS.derivative, width: 3 },
        connectgaps: false,
        hovertemplate: "f'(%{x:.3f}) = %{y:.6f}<extra></extra>"
    }];

    var derivLayout = makePlotLayout("f'(x)", res.y_range_deriv);
    Plotly.newPlot('plot-deriv', derivTraces, derivLayout, config);
}

function drawCombinedPlot() {
    var res = state.results;
    var config = { responsive: true, displayModeBar: false, displaylogo: false };

    var traces = [
        {
            x: res.func_data.x,
            y: res.func_data.y,
            mode: 'lines',
            name: 'f(x)',
            line: { color: COLORS.func, width: 3 },
            connectgaps: false,
            hovertemplate: 'f(%{x:.3f}) = %{y:.6f}<extra></extra>'
        },
        {
            x: res.derivative_data.x,
            y: res.derivative_data.y,
            mode: 'lines',
            name: "f'(x)",
            line: { color: COLORS.derivative, width: 2.5, dash: 'dash' },
            connectgaps: false,
            hovertemplate: "f'(%{x:.3f}) = %{y:.6f}<extra></extra>"
        }
    ];

    var layout = makePlotLayout('f(x) i f\'(x)', res.y_range_combined);
    Plotly.newPlot('plot-combined', traces, layout, config);
}

function makePlotLayout(title, yRange) {
    return {
        xaxis: {
            title: 'x',
            gridcolor: '#e2e8f0',
            zeroline: true,
            zerolinecolor: '#94a3b8',
            zerolinewidth: 1
        },
        yaxis: {
            title: 'y',
            range: yRange,
            gridcolor: '#e2e8f0',
            zeroline: true,
            zerolinecolor: '#94a3b8',
            zerolinewidth: 1
        },
        plot_bgcolor: '#f8fafc',
        paper_bgcolor: '#f8fafc',
        margin: { t: 30, b: 50, l: 60, r: 20 },
        showlegend: true,
        legend: {
            x: 0.01, y: 0.99,
            bgcolor: 'rgba(255,255,255,0.85)',
            bordercolor: '#e2e8f0',
            borderwidth: 1
        },
        hovermode: 'closest'
    };
}

// === WZORY ===
function updateFormulas() {
    var res = state.results;
    if (!res) return;

    document.getElementById('formula-func').textContent = res.func_formula;
    document.getElementById('formula-deriv').textContent = res.derivative_formula;
}
