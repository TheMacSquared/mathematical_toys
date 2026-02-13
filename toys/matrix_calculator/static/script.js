// === STAN APLIKACJI ===
const state = {
    rows: 3,
    cols: 3,
    results: null,
    presets: {}
};

// === INICJALIZACJA ===
document.addEventListener('DOMContentLoaded', function() {
    buildMatrixTable();
    setupControls();
    setupPresets();
    // Ustaw domyslna macierz jednostkowa
    setMatrixValues([[1, 0, 0], [0, 1, 0], [0, 0, 1]]);
});

// === TABELA MACIERZY ===
function buildMatrixTable() {
    const tbody = document.getElementById('matrix-tbody');
    tbody.innerHTML = '';

    for (let i = 0; i < state.rows; i++) {
        const tr = document.createElement('tr');
        for (let j = 0; j < state.cols; j++) {
            const td = document.createElement('td');
            const input = document.createElement('input');
            input.type = 'number';
            input.className = 'st-input mc-cell-input';
            input.id = 'cell-' + i + '-' + j;
            input.value = '0';
            input.step = '1';
            td.appendChild(input);
            tr.appendChild(td);
        }
        tbody.appendChild(tr);
    }
}

function getMatrixFromInputs() {
    const matrix = [];
    for (let i = 0; i < state.rows; i++) {
        const row = [];
        for (let j = 0; j < state.cols; j++) {
            const val = parseFloat(document.getElementById('cell-' + i + '-' + j).value);
            row.push(isNaN(val) ? 0 : val);
        }
        matrix.push(row);
    }
    return matrix;
}

function setMatrixValues(matrix) {
    for (let i = 0; i < matrix.length && i < state.rows; i++) {
        for (let j = 0; j < matrix[i].length && j < state.cols; j++) {
            document.getElementById('cell-' + i + '-' + j).value = matrix[i][j];
        }
    }
}

// === KONTROLKI ===
function setupControls() {
    document.getElementById('size-rows').addEventListener('change', function() {
        state.rows = parseInt(this.value);
        buildMatrixTable();
    });

    document.getElementById('size-cols').addEventListener('change', function() {
        state.cols = parseInt(this.value);
        buildMatrixTable();
    });

    document.getElementById('btn-compute').addEventListener('click', function() {
        triggerComputation();
    });
}

function setupPresets() {
    fetch('/api/presets')
        .then(r => r.json())
        .then(data => {
            if (data.success) state.presets = data.presets;
        })
        .catch(() => {});

    document.querySelectorAll('.mc-preset-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const type = this.dataset.type;
            const preset = state.presets[type];
            if (preset) {
                const m = preset.matrix;
                state.rows = m.length;
                state.cols = m[0].length;
                document.getElementById('size-rows').value = state.rows;
                document.getElementById('size-cols').value = state.cols;
                buildMatrixTable();
                setMatrixValues(m);
                triggerComputation();
            }
        });
    });
}

// === OBLICZENIA ===
async function triggerComputation() {
    const matrix = getMatrixFromInputs();

    try {
        const response = await fetch('/api/compute', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ matrix: matrix })
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.error || 'HTTP ' + response.status);
        }

        const data = await response.json();

        if (data.success) {
            state.results = data;
            displayResults();
        }
    } catch (error) {
        console.error('Blad obliczen:', error.message);
    }
}

// === WYSWIETLANIE WYNIKOW ===
function displayResults() {
    const res = state.results;
    if (!res) return;

    document.getElementById('results-section').style.display = '';

    // Rozmiar
    document.getElementById('stat-size').textContent = res.rows + '\u00d7' + res.cols;

    // Rzad
    document.getElementById('stat-rank').textContent = res.rank;

    // Wyznacznik
    const detItem = document.getElementById('det-item');
    const detEl = document.getElementById('stat-det');
    if (res.det !== null) {
        detItem.style.display = '';
        detEl.textContent = formatNumber(res.det);
    } else {
        detItem.style.display = 'none';
    }

    // Slad
    const traceItem = document.getElementById('trace-item');
    const traceEl = document.getElementById('stat-trace');
    if (res.trace !== null) {
        traceItem.style.display = '';
        traceEl.textContent = formatNumber(res.trace);
    } else {
        traceItem.style.display = 'none';
    }

    // Wartosci wlasne
    const eigenSection = document.getElementById('eigen-section');
    if (res.eigenvalues !== null) {
        eigenSection.style.display = '';
        const eigenDisplay = document.getElementById('eigenvalues-display');
        if (res.eigenvalues_complex) {
            eigenDisplay.innerHTML = res.eigenvalues.map(function(v, i) {
                var imSign = v.im >= 0 ? '+' : '-';
                return '<span class="mc-eigenvalue">\u03BB<sub>' + (i + 1) + '</sub> = '
                    + formatNumber(v.re) + ' ' + imSign + ' ' + formatNumber(Math.abs(v.im)) + 'i</span>';
            }).join('');
        } else {
            eigenDisplay.innerHTML = res.eigenvalues.map(function(v, i) {
                return '<span class="mc-eigenvalue">\u03BB<sub>' + (i + 1) + '</sub> = ' + formatNumber(v) + '</span>';
            }).join('');
        }
    } else {
        eigenSection.style.display = 'none';
    }

    // Macierz odwrotna
    const inverseSection = document.getElementById('inverse-section');
    if (res.inverse) {
        inverseSection.style.display = '';
        document.getElementById('inverse-display').innerHTML = renderMatrix(res.inverse);
    } else {
        inverseSection.style.display = 'none';
    }

    // Transpozycja
    document.getElementById('transpose-display').innerHTML = renderMatrix(res.transpose);

    // Eliminacja Gaussa
    displayGaussSteps(res.gauss_steps);
}

function displayGaussSteps(steps) {
    const container = document.getElementById('gauss-steps');
    var html = '';

    for (var i = 0; i < steps.length; i++) {
        var step = steps[i];
        var stepClass = 'mc-gauss-step';
        if (step.operation === 'swap') stepClass += ' mc-gauss-step--swap';
        else if (step.operation === 'scale') stepClass += ' mc-gauss-step--scale';
        else if (step.operation === 'eliminate') stepClass += ' mc-gauss-step--eliminate';

        html += '<div class="' + stepClass + '">';
        html += '<div class="mc-gauss-step__header">';
        html += '<span class="mc-gauss-step__num">Krok ' + i + '</span>';
        html += '<span class="mc-gauss-step__desc">' + step.description + '</span>';
        html += '</div>';
        html += renderMatrix(step.matrix);
        html += '</div>';
    }

    container.innerHTML = html;
}

function renderMatrix(matrix) {
    var html = '<div class="mc-rendered-matrix">';
    html += '<div class="mc-rendered-bracket mc-rendered-bracket--left"></div>';
    html += '<table class="mc-rendered-table"><tbody>';
    for (var i = 0; i < matrix.length; i++) {
        html += '<tr>';
        for (var j = 0; j < matrix[i].length; j++) {
            var val = matrix[i][j];
            var cls = 'mc-rendered-cell';
            if (Math.abs(val) < 1e-10) cls += ' mc-rendered-cell--zero';
            else if (Math.abs(val - 1) < 1e-10) cls += ' mc-rendered-cell--one';
            html += '<td class="' + cls + '">' + formatNumber(val) + '</td>';
        }
        html += '</tr>';
    }
    html += '</tbody></table>';
    html += '<div class="mc-rendered-bracket mc-rendered-bracket--right"></div>';
    html += '</div>';
    return html;
}

function formatNumber(val) {
    if (Math.abs(val) < 1e-10) return '0';
    if (Number.isInteger(val) || Math.abs(val - Math.round(val)) < 1e-8) {
        return Math.round(val).toString();
    }
    return val.toFixed(4);
}
