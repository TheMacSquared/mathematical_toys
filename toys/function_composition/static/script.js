// === STAN APLIKACJI ===
var state = {
    fId: 'power',
    fParam: 2,
    gId: 'shift',
    gParam: 3,
    x0: 2,
    results: null,
    functions: null
};

var debounceTimer = null;

var COLORS = {
    g: '#3b82f6',
    f: '#22c55e',
    fg: '#6366f1',
    markerG: '#3b82f6',
    markerFG: '#6366f1',
    x0Line: '#94a3b8'
};

// === PARAMETRY FUNKCJI (fallback jesli /api/functions nie zaladuje) ===
var PARAM_CONFIG = {
    'shift':  { min: -5, max: 5, step: 0.5, def: 3 },
    'scale':  { min: -3, max: 3, step: 0.5, def: 2 },
    'power':  { values: [-2, -1, 0.5, 1, 2, 3], def: 2 },
    'sin':    { min: 0.1, max: 5, step: 0.1, def: 1 },
    'cos':    { min: 0.1, max: 5, step: 0.1, def: 1 },
    'exp':    { min: -2, max: 2, step: 0.1, def: 1 },
    'abs':    null,
    'ln':     null
};

// === INICJALIZACJA ===
document.addEventListener('DOMContentLoaded', function() {
    loadFunctions();
    setupInputs();
    updateParamControl('f');
    updateParamControl('g');
    updatePlot();
});

function loadFunctions() {
    fetch('/api/functions')
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (data.success) {
                state.functions = data.functions;
                // Update PARAM_CONFIG from server data
                for (var key in data.functions) {
                    var fn = data.functions[key];
                    if (fn.has_param) {
                        if (fn.param_values) {
                            PARAM_CONFIG[key] = { values: fn.param_values, def: fn.param_default };
                        } else {
                            PARAM_CONFIG[key] = {
                                min: fn.param_min, max: fn.param_max,
                                step: fn.param_step, def: fn.param_default
                            };
                        }
                    } else {
                        PARAM_CONFIG[key] = null;
                    }
                }
            }
        })
        .catch(function() {});
}

// === KONTROLKI ===
function setupInputs() {
    document.getElementById('f-select').addEventListener('change', function() {
        state.fId = this.value;
        updateParamControl('f');
        scheduleUpdate();
    });

    document.getElementById('g-select').addEventListener('change', function() {
        state.gId = this.value;
        updateParamControl('g');
        scheduleUpdate();
    });

    document.getElementById('x0-slider').addEventListener('input', function() {
        state.x0 = parseFloat(this.value);
        document.getElementById('x0-value').textContent = state.x0.toFixed(1);
        scheduleUpdate();
    });

    document.getElementById('btn-update').addEventListener('click', function() {
        updatePlot();
    });
}

function updateParamControl(which) {
    var funcId = which === 'f' ? state.fId : state.gId;
    var config = PARAM_CONFIG[funcId];
    var group = document.getElementById(which + '-param-group');
    var valueEl = document.getElementById(which + '-param-value');

    if (!config) {
        // No parameter for this function
        group.style.display = 'none';
        if (which === 'f') state.fParam = null;
        else state.gParam = null;
        return;
    }

    group.style.display = '';

    if (config.values) {
        // Discrete values - replace slider with select
        var currentVal = which === 'f' ? state.fParam : state.gParam;
        if (currentVal === null || config.values.indexOf(currentVal) === -1) {
            currentVal = config.def;
        }

        var selectHtml = '<select id="' + which + '-param" class="fc-param-select">';
        for (var i = 0; i < config.values.length; i++) {
            var v = config.values[i];
            var selected = v === currentVal ? ' selected' : '';
            selectHtml += '<option value="' + v + '"' + selected + '>' + v + '</option>';
        }
        selectHtml += '</select>';

        var container = document.getElementById(which + '-param');
        if (container) container.remove();
        var label = group.querySelector('label');
        label.insertAdjacentHTML('afterend', selectHtml);

        document.getElementById(which + '-param').addEventListener('change', function() {
            var val = parseFloat(this.value);
            if (which === 'f') state.fParam = val;
            else state.gParam = val;
            valueEl.textContent = formatParam(val);
            scheduleUpdate();
        });

        if (which === 'f') state.fParam = currentVal;
        else state.gParam = currentVal;
        valueEl.textContent = formatParam(currentVal);
    } else {
        // Continuous - use range slider
        var currentVal = which === 'f' ? state.fParam : state.gParam;
        if (currentVal === null || currentVal < config.min || currentVal > config.max) {
            currentVal = config.def;
        }

        var existingEl = document.getElementById(which + '-param');
        if (existingEl && existingEl.tagName === 'SELECT') {
            existingEl.remove();
        }

        if (!document.getElementById(which + '-param')) {
            var label = group.querySelector('label');
            label.insertAdjacentHTML('afterend',
                '<input type="range" id="' + which + '-param" class="fc-slider">');
        }

        var slider = document.getElementById(which + '-param');
        slider.min = config.min;
        slider.max = config.max;
        slider.step = config.step;
        slider.value = currentVal;

        // Remove old listeners by cloning
        var newSlider = slider.cloneNode(true);
        slider.parentNode.replaceChild(newSlider, slider);

        newSlider.addEventListener('input', function() {
            var val = parseFloat(this.value);
            if (which === 'f') state.fParam = val;
            else state.gParam = val;
            valueEl.textContent = formatParam(val);
            scheduleUpdate();
        });

        if (which === 'f') state.fParam = currentVal;
        else state.gParam = currentVal;
        valueEl.textContent = formatParam(currentVal);
    }
}

function formatParam(v) {
    if (v === null) return '-';
    if (v === Math.floor(v)) return v.toString();
    return v.toFixed(1);
}

function scheduleUpdate() {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(function() {
        updatePlot();
    }, 200);
}

// === OBLICZENIA ===
async function updatePlot() {
    var loadingEl = document.getElementById('loading');

    try {
        loadingEl.classList.add('st-loading--active');

        var body = {
            f_id: state.fId,
            g_id: state.gId,
            x0: state.x0
        };
        if (state.fParam !== null) body.f_param = state.fParam;
        if (state.gParam !== null) body.g_param = state.gParam;

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
            updatePipeline();
        }
    } catch (error) {
        console.error('Blad:', error.message);
    } finally {
        loadingEl.classList.remove('st-loading--active');
    }
}

// === WYKRES ===
function drawPlot() {
    var res = state.results;
    if (!res) return;

    var traces = [];

    // g(x) - wewnetrzna (niebieska, przerywana)
    traces.push({
        x: res.g_curve.x,
        y: res.g_curve.y,
        mode: 'lines',
        name: 'g(x) = ' + res.g_label.replace('t', 'x'),
        line: { color: COLORS.g, width: 2, dash: 'dash' },
        connectgaps: false,
        hovertemplate: 'g(%{x:.2f}) = %{y:.4f}<extra></extra>'
    });

    // f(x) - zewnetrzna (zielona, przerywana)
    traces.push({
        x: res.f_curve.x,
        y: res.f_curve.y,
        mode: 'lines',
        name: 'f(x) = ' + res.f_label.replace('t', 'x'),
        line: { color: COLORS.f, width: 2, dash: 'dash' },
        connectgaps: false,
        hovertemplate: 'f(%{x:.2f}) = %{y:.4f}<extra></extra>'
    });

    // f(g(x)) - zlozenie (fioletowa, gruba)
    traces.push({
        x: res.fg_curve.x,
        y: res.fg_curve.y,
        mode: 'lines',
        name: 'f(g(x)) = ' + res.fg_label,
        line: { color: COLORS.fg, width: 3 },
        connectgaps: false,
        hovertemplate: 'f(g(%{x:.2f})) = %{y:.4f}<extra></extra>'
    });

    // Marker: (x0, g(x0)) na krzywej g
    if (res.g_x0 !== null) {
        traces.push({
            x: [res.x0],
            y: [res.g_x0],
            mode: 'markers',
            name: 'g(' + res.x0 + ') = ' + formatNum(res.g_x0),
            marker: { color: COLORS.markerG, size: 11, line: { color: 'white', width: 2 } },
            hovertemplate: 'g(x\u2080) = ' + formatNum(res.g_x0) + '<extra></extra>'
        });
    }

    // Marker: (x0, f(g(x0))) na krzywej f(g)
    if (res.f_g_x0 !== null) {
        traces.push({
            x: [res.x0],
            y: [res.f_g_x0],
            mode: 'markers',
            name: 'f(g(' + res.x0 + ')) = ' + formatNum(res.f_g_x0),
            marker: {
                color: COLORS.markerFG, size: 13,
                symbol: 'diamond',
                line: { color: 'white', width: 2 }
            },
            hovertemplate: 'f(g(x\u2080)) = ' + formatNum(res.f_g_x0) + '<extra></extra>'
        });
    }

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
        hovermode: 'closest',
        shapes: [
            // Vertical line at x0
            {
                type: 'line',
                x0: res.x0, x1: res.x0,
                y0: 0, y1: 1,
                yref: 'paper',
                line: { color: COLORS.x0Line, width: 1, dash: 'dot' }
            }
        ]
    };

    var config = {
        responsive: true,
        displayModeBar: false,
        displaylogo: false
    };

    Plotly.newPlot('plot', traces, layout, config);
}

function formatNum(v) {
    if (v === null || v === undefined) return '?';
    if (Math.abs(v) < 0.001 && v !== 0) return v.toExponential(2);
    if (v === Math.round(v)) return v.toString();
    return v.toFixed(4);
}

// === INFORMACJE (sidebar) ===
function updateInfo() {
    var res = state.results;
    if (!res) return;

    var panel = document.getElementById('results-panel');
    panel.style.display = '';

    document.getElementById('result-fg').textContent =
        res.f_g_x0 !== null ? formatNum(res.f_g_x0) : 'niezdefiniowane';
    document.getElementById('result-gf').textContent =
        res.g_f_x0 !== null ? formatNum(res.g_f_x0) : 'niezdefiniowane';
    document.getElementById('result-sum').textContent =
        res.f_x0_plus_g_x0 !== null ? formatNum(res.f_x0_plus_g_x0) : 'niezdefiniowane';
    document.getElementById('result-prod').textContent =
        res.f_x0_times_g_x0 !== null ? formatNum(res.f_x0_times_g_x0) : 'niezdefiniowane';
}

// === PIPELINE DIAGRAM ===
function updatePipeline() {
    var res = state.results;
    if (!res) return;

    document.getElementById('pipeline-fg').innerHTML =
        '<span class="fc-pipeline__label">f \u2218 g :</span>' +
        buildPipelineHTML(res.pipeline_fg, ['start', 'g', 'result-fg']);

    document.getElementById('pipeline-gf').innerHTML =
        '<span class="fc-pipeline__label">g \u2218 f :</span>' +
        buildPipelineHTML(res.pipeline_gf, ['start', 'f', 'result-gf']);
}

function buildPipelineHTML(steps, cssClasses) {
    var html = '';
    for (var i = 0; i < steps.length; i++) {
        if (i > 0) {
            html += '<span class="fc-pipeline__arrow">\u2192</span>';
        }
        var step = steps[i];
        var cls = cssClasses[i] || '';
        var val = step.value !== null ? formatNum(step.value) : '?';
        html += '<div class="fc-pipeline__step fc-pipeline__step--' + cls + '">';
        html += '<span class="fc-pipeline__step-value">' + val + '</span>';
        if (step.detail) {
            html += '<span class="fc-pipeline__step-detail">' + step.detail + '</span>';
        } else {
            html += '<span class="fc-pipeline__step-detail">' + step.label + '</span>';
        }
        html += '</div>';
    }
    return html;
}
