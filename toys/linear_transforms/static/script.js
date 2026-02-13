// === STAN APLIKACJI ===
const state = {
    matrix: [[1, 0], [0, 1]],
    results: null,
    showCircle: true,
    showEigenvectors: false,
    presets: {}
};

let debounceTimer = null;

const COLORS = {
    unitSquare: 'rgba(99, 102, 241, 0.3)',
    unitSquareLine: '#6366f1',
    transformedSquare: 'rgba(239, 68, 68, 0.3)',
    transformedSquareLine: '#ef4444',
    e1: '#22c55e',
    e2: '#3b82f6',
    te1: '#dc2626',
    te2: '#f97316',
    circle: 'rgba(99, 102, 241, 0.2)',
    transformedCircle: 'rgba(239, 68, 68, 0.2)',
    eigen1: '#a855f7',
    eigen2: '#ec4899'
};

const PLOT_RANGE = [-5, 5];

// === INICJALIZACJA ===
document.addEventListener('DOMContentLoaded', function() {
    setupPlot();
    setupInputs();
    setupPresets();
    setupDisplayOptions();
    triggerComputation();
});

// === WYKRES ===
function setupPlot() {
    const layout = {
        xaxis: {
            range: [...PLOT_RANGE],
            gridcolor: '#e2e8f0',
            zeroline: true,
            zerolinecolor: '#94a3b8',
            zerolinewidth: 1.5,
            dtick: 1,
            scaleanchor: 'y',
            scaleratio: 1
        },
        yaxis: {
            range: [...PLOT_RANGE],
            gridcolor: '#e2e8f0',
            zeroline: true,
            zerolinecolor: '#94a3b8',
            zerolinewidth: 1.5,
            dtick: 1
        },
        plot_bgcolor: '#f8fafc',
        paper_bgcolor: 'transparent',
        margin: { t: 10, b: 40, l: 50, r: 10 },
        showlegend: true,
        legend: {
            x: 0.01, y: 0.99,
            bgcolor: 'rgba(255,255,255,0.85)',
            bordercolor: '#e2e8f0',
            borderwidth: 1,
            font: { size: 11 }
        },
        hovermode: 'closest',
        dragmode: false
    };

    const config = {
        responsive: true,
        displayModeBar: false,
        displaylogo: false,
        scrollZoom: false,
        doubleClick: false
    };

    Plotly.newPlot('plot', [], layout, config);
}

// === KONTROLKI ===
function setupInputs() {
    ['m00', 'm01', 'm10', 'm11'].forEach(id => {
        document.getElementById(id).addEventListener('input', function() {
            const val = parseFloat(this.value);
            if (isNaN(val)) return;
            readMatrixFromInputs();
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => triggerComputation(), 200);
        });
    });
}

function readMatrixFromInputs() {
    state.matrix = [
        [parseFloat(document.getElementById('m00').value) || 0,
         parseFloat(document.getElementById('m01').value) || 0],
        [parseFloat(document.getElementById('m10').value) || 0,
         parseFloat(document.getElementById('m11').value) || 0]
    ];
}

function setMatrixInputs(matrix) {
    document.getElementById('m00').value = matrix[0][0];
    document.getElementById('m01').value = matrix[0][1];
    document.getElementById('m10').value = matrix[1][0];
    document.getElementById('m11').value = matrix[1][1];
    state.matrix = matrix.map(row => [...row]);
}

function setupPresets() {
    // Laduj presety z backendu
    fetch('/api/presets')
        .then(r => r.json())
        .then(data => {
            if (data.success) state.presets = data.presets;
        })
        .catch(() => {});

    document.querySelectorAll('.lt-preset-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const type = this.dataset.type;
            const preset = state.presets[type];
            if (preset) {
                setMatrixInputs(preset.matrix);
                showPresetDescription(preset.description);
                triggerComputation();
            }
        });
    });
}

function showPresetDescription(text) {
    const el = document.getElementById('preset-desc');
    const textEl = document.getElementById('preset-desc-text');
    textEl.textContent = text;
    el.style.display = '';
}

function setupDisplayOptions() {
    document.getElementById('show-circle').addEventListener('change', function() {
        state.showCircle = this.checked;
        if (state.results) updatePlot();
    });
    document.getElementById('show-eigenvectors').addEventListener('change', function() {
        state.showEigenvectors = this.checked;
        if (state.results) updatePlot();
    });
}

// === OBLICZENIA ===
async function triggerComputation() {
    const loadingEl = document.getElementById('loading');

    try {
        loadingEl.classList.add('st-loading--active');

        const response = await fetch('/api/compute', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ matrix: state.matrix })
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.error || 'HTTP ' + response.status);
        }

        const data = await response.json();

        if (data.success) {
            state.results = data;
            updateStats();
            updatePlot();
        }

    } catch (error) {
        console.error('Blad obliczen:', error.message);
    } finally {
        loadingEl.classList.remove('st-loading--active');
    }
}

// === AKTUALIZACJA WYKRESU ===
function updatePlot() {
    const res = state.results;
    if (!res) return;

    const traces = [];

    // Kwadrat jednostkowy (przed)
    traces.push({
        x: res.unit_square.x,
        y: res.unit_square.y,
        mode: 'lines',
        name: 'Kwadrat jednostkowy',
        fill: 'toself',
        fillcolor: COLORS.unitSquare,
        line: { color: COLORS.unitSquareLine, width: 2, dash: 'dash' },
        hoverinfo: 'skip'
    });

    // Przeksztalcony kwadrat
    traces.push({
        x: res.transformed_square.x,
        y: res.transformed_square.y,
        mode: 'lines',
        name: 'Obraz kwadratu',
        fill: 'toself',
        fillcolor: COLORS.transformedSquare,
        line: { color: COLORS.transformedSquareLine, width: 2.5 },
        hoverinfo: 'skip'
    });

    // Okrag jednostkowy
    if (state.showCircle) {
        traces.push({
            x: res.circle.x,
            y: res.circle.y,
            mode: 'lines',
            name: 'Okrag jednostkowy',
            line: { color: COLORS.unitSquareLine, width: 1.5, dash: 'dot' },
            hoverinfo: 'skip'
        });

        traces.push({
            x: res.transformed_circle.x,
            y: res.transformed_circle.y,
            mode: 'lines',
            name: 'Obraz okregu',
            line: { color: COLORS.transformedSquareLine, width: 2 },
            hoverinfo: 'skip'
        });
    }

    // Wektory bazowe e1, e2 (przed)
    traces.push({
        x: [0, 1], y: [0, 0],
        mode: 'lines+markers',
        name: 'e\u2081',
        line: { color: COLORS.e1, width: 3 },
        marker: { size: 8, symbol: 'arrow', angleref: 'previous', color: COLORS.e1 },
        hoverinfo: 'skip',
        showlegend: false
    });
    traces.push({
        x: [0, 0], y: [0, 1],
        mode: 'lines+markers',
        name: 'e\u2082',
        line: { color: COLORS.e2, width: 3 },
        marker: { size: 8, symbol: 'arrow', angleref: 'previous', color: COLORS.e2 },
        hoverinfo: 'skip',
        showlegend: false
    });

    // Wektory bazowe (po transformacji)
    traces.push({
        x: [0, res.e1[0]], y: [0, res.e1[1]],
        mode: 'lines+markers',
        name: 'A\u00b7e\u2081',
        line: { color: COLORS.te1, width: 3 },
        marker: { size: 8, symbol: 'arrow', angleref: 'previous', color: COLORS.te1 },
        hovertemplate: 'A\u00b7e\u2081 = (%{x:.2f}, %{y:.2f})<extra></extra>'
    });
    traces.push({
        x: [0, res.e2[0]], y: [0, res.e2[1]],
        mode: 'lines+markers',
        name: 'A\u00b7e\u2082',
        line: { color: COLORS.te2, width: 3 },
        marker: { size: 8, symbol: 'arrow', angleref: 'previous', color: COLORS.te2 },
        hovertemplate: 'A\u00b7e\u2082 = (%{x:.2f}, %{y:.2f})<extra></extra>'
    });

    // Wektory wlasne
    if (state.showEigenvectors && res.eigen_real && res.eigenvectors) {
        for (let i = 0; i < 2; i++) {
            const ev = res.eigenvectors[i];
            if (ev[0] === null || ev[1] === null) continue;
            const scale = 4;
            const color = i === 0 ? COLORS.eigen1 : COLORS.eigen2;
            traces.push({
                x: [-ev[0] * scale, ev[0] * scale],
                y: [-ev[1] * scale, ev[1] * scale],
                mode: 'lines',
                name: '\u03BB' + (i + 1) + ' = ' + (res.eigenvalues[i] !== null ? res.eigenvalues[i].toFixed(2) : '?'),
                line: { color: color, width: 2, dash: 'dashdot' },
                hoverinfo: 'skip'
            });
        }
    }

    // Ustal zakres
    const allX = res.transformed_square.x.concat(res.e1[0], res.e2[0]);
    const allY = res.transformed_square.y.concat(res.e1[1], res.e2[1]);
    const maxAbs = Math.max(
        Math.abs(Math.min(...allX)),
        Math.abs(Math.max(...allX)),
        Math.abs(Math.min(...allY)),
        Math.abs(Math.max(...allY)),
        2
    );
    const range = Math.ceil(maxAbs) + 1.5;

    Plotly.react('plot', traces, {
        xaxis: {
            range: [-range, range],
            gridcolor: '#e2e8f0',
            zeroline: true,
            zerolinecolor: '#94a3b8',
            zerolinewidth: 1.5,
            dtick: 1,
            scaleanchor: 'y',
            scaleratio: 1
        },
        yaxis: {
            range: [-range, range],
            gridcolor: '#e2e8f0',
            zeroline: true,
            zerolinecolor: '#94a3b8',
            zerolinewidth: 1.5,
            dtick: 1
        },
        plot_bgcolor: '#f8fafc',
        paper_bgcolor: 'transparent',
        margin: { t: 10, b: 40, l: 50, r: 10 },
        showlegend: true,
        legend: {
            x: 0.01, y: 0.99,
            bgcolor: 'rgba(255,255,255,0.85)',
            bordercolor: '#e2e8f0',
            borderwidth: 1,
            font: { size: 11 }
        },
        hovermode: 'closest',
        dragmode: false
    }, {
        responsive: true,
        displayModeBar: false,
        displaylogo: false,
        scrollZoom: false,
        doubleClick: false
    });
}

// === PANEL WYNIKOW ===
function updateStats() {
    const res = state.results;
    if (!res) return;

    // Wyznacznik
    const detEl = document.getElementById('stat-det');
    detEl.textContent = res.det.toFixed(4);
    const detDisplay = document.getElementById('det-display');
    detDisplay.classList.remove('lt-det-display--positive', 'lt-det-display--negative', 'lt-det-display--zero');
    if (Math.abs(res.det) < 1e-10) {
        detDisplay.classList.add('lt-det-display--zero');
    } else if (res.det > 0) {
        detDisplay.classList.add('lt-det-display--positive');
    } else {
        detDisplay.classList.add('lt-det-display--negative');
    }

    // Rzad i slad
    document.getElementById('stat-rank').textContent = res.rank;
    document.getElementById('stat-trace').textContent = res.trace.toFixed(4);

    // Wartosci wlasne
    const eigenEl = document.getElementById('stat-eigenvalues');
    if (res.eigenvalues) {
        if (res.eigen_real) {
            eigenEl.textContent = '\u03BB\u2081 = ' + (res.eigenvalues[0] !== null ? res.eigenvalues[0].toFixed(4) : '?')
                + ',  \u03BB\u2082 = ' + (res.eigenvalues[1] !== null ? res.eigenvalues[1].toFixed(4) : '?');
        } else {
            eigenEl.textContent = 'Zespolone (\u03BB \u2208 \u2102)';
        }
    } else {
        eigenEl.textContent = '-';
    }

    // Typ transformacji
    document.getElementById('stat-type').textContent = res.transform_type;
}
