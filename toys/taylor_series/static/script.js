// === STAN APLIKACJI ===
const state = {
    func: 'sin',
    degree: 5,
    center: 0,
    evalPoint: null,
    results: null
};

let debounceTimer = null;

const COLORS = {
    original: '#6366f1',
    taylor: '#ef4444',
    convergence: 'rgba(245, 158, 11, 0.15)',
    convergenceLine: '#f59e0b',
    center: '#22c55e'
};

// === INICJALIZACJA ===
document.addEventListener('DOMContentLoaded', function() {
    setupInputs();
    updatePlot();
});

// === KONTROLKI ===
function setupInputs() {
    // Funkcja
    document.getElementById('func-select').addEventListener('change', function() {
        state.func = this.value;
        scheduleUpdate();
    });

    // Stopien - suwak
    document.getElementById('degree-slider').addEventListener('input', function() {
        state.degree = parseInt(this.value);
        document.getElementById('degree-value').textContent = state.degree;
        scheduleUpdate();
    });

    // Punkt rozwiniecia
    document.getElementById('center-input').addEventListener('input', function() {
        var val = parseFloat(this.value);
        if (!isNaN(val)) {
            state.center = val;
            scheduleUpdate();
        }
    });

    // Punkt ewaluacji
    document.getElementById('eval-point').addEventListener('input', function() {
        var val = parseFloat(this.value);
        state.evalPoint = isNaN(val) ? null : val;
        scheduleUpdate();
    });

    // Przycisk
    document.getElementById('btn-update').addEventListener('click', function() {
        updatePlot();
    });
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
            degree: state.degree,
            center: state.center
        };
        if (state.evalPoint !== null) {
            body.eval_point = state.evalPoint;
        }

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

    // Oryginalna funkcja
    traces.push({
        x: res.func_data.x,
        y: res.func_data.y,
        mode: 'lines',
        name: 'f(x)',
        line: { color: COLORS.original, width: 3 },
        connectgaps: false,
        hovertemplate: 'f(%{x:.3f}) = %{y:.6f}<extra></extra>'
    });

    // Wielomian Taylora
    traces.push({
        x: res.taylor_data.x,
        y: res.taylor_data.y,
        mode: 'lines',
        name: 'T\u2099(x), n=' + state.degree,
        line: { color: COLORS.taylor, width: 2.5, dash: 'solid' },
        hovertemplate: 'T(%{x:.3f}) = %{y:.6f}<extra></extra>'
    });

    // Punkt rozwiniecia
    var centerY = null;
    for (var i = 0; i < res.func_data.x.length; i++) {
        if (Math.abs(res.func_data.x[i] - res.center) < 0.05) {
            centerY = res.func_data.y[i];
            break;
        }
    }
    if (centerY !== null) {
        traces.push({
            x: [res.center],
            y: [centerY],
            mode: 'markers',
            name: 'a = ' + res.center,
            marker: { color: COLORS.center, size: 12, line: { color: 'white', width: 2 } },
            hovertemplate: 'a = %{x}<extra></extra>'
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
        shapes: []
    };

    // Promien zbieznosci - zaznacz obszar
    if (res.convergence_radius !== null) {
        var r = res.convergence_radius;
        layout.shapes.push({
            type: 'rect',
            x0: res.center - r, x1: res.center + r,
            y0: 0, y1: 1,
            yref: 'paper',
            fillcolor: COLORS.convergence,
            line: { width: 0 }
        });
        layout.shapes.push({
            type: 'line',
            x0: res.center - r, x1: res.center - r,
            y0: 0, y1: 1,
            yref: 'paper',
            line: { color: COLORS.convergenceLine, width: 1.5, dash: 'dash' }
        });
        layout.shapes.push({
            type: 'line',
            x0: res.center + r, x1: res.center + r,
            y0: 0, y1: 1,
            yref: 'paper',
            line: { color: COLORS.convergenceLine, width: 1.5, dash: 'dash' }
        });
    }

    var config = {
        responsive: true,
        displayModeBar: false,
        displaylogo: false
    };

    Plotly.newPlot('plot', traces, layout, config);
}

// === INFORMACJE ===
function updateInfo() {
    var res = state.results;
    if (!res) return;

    // Wielomian
    document.getElementById('polynomial-text').textContent = 'T(x) = ' + res.polynomial;

    // Promien zbieznosci
    var convInfo = document.getElementById('convergence-info');
    if (res.convergence_radius !== null) {
        convInfo.style.display = '';
        document.getElementById('convergence-radius').textContent = 'R = ' + res.convergence_radius;
    } else {
        convInfo.style.display = '';
        document.getElementById('convergence-radius').textContent = 'R = \u221e';
    }

    // Blad
    var errorDisplay = document.getElementById('error-display');
    if (res.error_at_point !== null) {
        errorDisplay.style.display = '';
        var errVal = res.error_at_point;
        if (errVal < 1e-10) {
            document.getElementById('error-value').textContent = '< 10\u207b\u00b9\u2070';
        } else if (errVal < 0.001) {
            document.getElementById('error-value').textContent = errVal.toExponential(3);
        } else {
            document.getElementById('error-value').textContent = errVal.toFixed(6);
        }
    } else {
        errorDisplay.style.display = 'none';
    }

    // Tabela wspolczynnikow
    updateCoefficientsTable(res.coefficients);
}

function updateCoefficientsTable(coefficients) {
    var tbody = document.getElementById('coefficients-tbody');
    var html = '';
    for (var n = 0; n < coefficients.length; n++) {
        var c = coefficients[n];
        var cls = '';
        if (Math.abs(c) < 1e-15) cls = ' class="ts-coeff--zero"';
        else cls = ' class="ts-coeff--nonzero"';

        html += '<tr' + cls + '>';
        html += '<td>' + n + '</td>';
        html += '<td>' + formatCoeff(c) + '</td>';
        html += '</tr>';
    }
    tbody.innerHTML = html;
}

function formatCoeff(val) {
    if (Math.abs(val) < 1e-15) return '0';
    if (Math.abs(val - Math.round(val)) < 1e-10) return Math.round(val).toString();
    return val.toFixed(8);
}
