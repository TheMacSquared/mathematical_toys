// === STAN APLIKACJI ===
var state = {
    func: 'quadratic',
    params: {},
    x0: 1.0,
    xMin: -5,
    xMax: 5,
    results: null,
    functionDefs: {}
};

var debounceTimer = null;

var COLORS = {
    func: '#6366f1',
    tangent: '#ef4444',
    point: '#22c55e'
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
                buildParamInputs(state.func);
                updatePlot();
            }
        });
}

function populateFunctionSelect() {
    var select = document.getElementById('func-select');
    select.innerHTML = '';
    var order = ['quadratic', 'cubic', 'sin', 'cos', 'exp', 'ln', 'linear', 'power', 'sqrt', 'tan'];
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

    document.getElementById('x0-input').addEventListener('input', function() {
        var val = parseFloat(this.value);
        if (!isNaN(val)) {
            state.x0 = val;
            scheduleUpdate();
        }
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

// === DYNAMICZNE PARAMETRY ===
function buildParamInputs(funcId) {
    var container = document.getElementById('params-container');
    var def = state.functionDefs[funcId];
    if (!def) return;

    state.params = {};
    var html = '<div class="st-input-group"><label>Parametry</label>';
    html += '<div class="tl-params__grid">';

    for (var i = 0; i < def.params.length; i++) {
        var p = def.params[i];
        state.params[p.id] = p.default;
        html += '<div class="st-input-group">';
        html += '<label for="param-' + p.id + '">' + p.label + '</label>';
        html += '<input type="number" id="param-' + p.id + '" class="st-input tl-param-input" ';
        html += 'value="' + p.default + '" ';
        html += 'min="' + p.min + '" max="' + p.max + '" step="' + p.step + '" ';
        html += 'data-param="' + p.id + '">';
        html += '</div>';
    }

    html += '</div></div>';
    container.innerHTML = html;

    var inputs = container.querySelectorAll('.tl-param-input');
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
            x0: state.x0,
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
            drawPlot();
            updateInfo();
        }
    } catch (error) {
        console.error('Błąd:', error.message);
    } finally {
        loadingEl.classList.remove('st-loading--active');
    }
}

// === WYKRES ===
function drawPlot() {
    var res = state.results;
    if (!res) return;

    var traces = [];

    // Funkcja
    traces.push({
        x: res.func_data.x,
        y: res.func_data.y,
        mode: 'lines',
        name: 'f(x)',
        line: { color: COLORS.func, width: 3 },
        connectgaps: false,
        hovertemplate: 'f(%{x:.3f}) = %{y:.6f}<extra></extra>'
    });

    // Styczna
    traces.push({
        x: res.tangent_data.x,
        y: res.tangent_data.y,
        mode: 'lines',
        name: 'styczna',
        line: { color: COLORS.tangent, width: 2.5, dash: 'dash' },
        hovertemplate: 'y = %{y:.6f}<extra>styczna</extra>'
    });

    // Punkt stycznosci
    traces.push({
        x: [res.tangent_point.x],
        y: [res.tangent_point.y],
        mode: 'markers',
        name: 'x\u2080 = ' + res.tangent_point.x,
        marker: {
            color: COLORS.point,
            size: 12,
            line: { color: 'white', width: 2 }
        },
        hovertemplate: 'x\u2080 = %{x:.4f}<br>f(x\u2080) = %{y:.6f}<extra></extra>'
    });

    var layout = {
        xaxis: {
            title: 'x',
            gridcolor: '#e2e8f0',
            zeroline: true,
            zerolinecolor: '#94a3b8',
            zerolinewidth: 1
        },
        yaxis: {
            title: 'y',
            range: res.y_range,
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

    var config = {
        responsive: true,
        displayModeBar: false,
        displaylogo: false
    };

    Plotly.newPlot('plot', traces, layout, config);

    // Klikanie na wykresie zmienia x0
    document.getElementById('plot').on('plotly_click', function(data) {
        if (data.points.length > 0) {
            state.x0 = Math.round(data.points[0].x * 100) / 100;
            document.getElementById('x0-input').value = state.x0;
            scheduleUpdate();
        }
    });
}

// === INFORMACJE ===
function updateInfo() {
    var res = state.results;
    if (!res) return;

    // Panel informacyjny
    var infoPanel = document.getElementById('tangent-info');
    infoPanel.style.display = '';

    document.getElementById('info-fvalue').textContent = formatNumber(res.func_value_at_x0);
    document.getElementById('info-slope').textContent = formatNumber(res.slope);

    // Kat stycznej w stopniach
    var angleDeg = Math.atan(res.slope) * 180 / Math.PI;
    document.getElementById('info-angle').textContent = formatNumber(angleDeg) + '\u00b0';

    // Rownanie stycznej
    document.getElementById('equation-text').textContent = res.tangent_equation;
}

function formatNumber(val) {
    if (Math.abs(val) < 1e-10) return '0';
    if (Math.abs(val - Math.round(val)) < 1e-8) return Math.round(val).toString();
    return val.toFixed(4);
}
