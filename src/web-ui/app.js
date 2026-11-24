const SCHEMA = {
    Heating: [
        { key: 'ControlSource', type: 'list', options: ['internal', 'spot-hinta'] },
        { key: 'QuarterHourInterval', type: 'checkbox' },
        { key: 'HeatingHours', type: 'text' },
        { key: 'ConsecutiveHours', type: 'checkbox' },
    ],
    NordPool: [
        { key: 'DataSource', type: 'list', options: ['elering'] },
        { key: 'PriceArea', type: 'list', options: ['fi', 'ee'] },
        { key: 'TimeZone', type: 'list', options: ['Europe/Helsinki', 'UTC'] },
    ],
    Heatpump: [
        { key: 'TargetTemperature', type: 'text' },
        { key: 'OperationMode', type: 'list',
          options: ['heat', 'dry', 'cool', 'fan_only', 'heat_cool'] },
        { key: 'FanSpeed', type: 'list', options: ['auto', '1', '2', '3', '4', '5'] },
        { key: 'VaneHorizontal', type: 'list',
          options: ['auto', '1_left', '2', '3', '4', '5_right', 'split', 'swing'] },
        { key: 'VaneVertical', type: 'list',
          options: ['auto', '1_up', '2', '3', '4', '5_down', 'swing'] },
    ],
    SpotHinta: [
        { key: 'QuickCode', type: 'text' },
    ],
};

function showStatus(message, kind) {
    const status = document.getElementById('status');
    status.textContent = message;
    status.className = kind || '';
}

function createInput(section, field, value) {
    const id = `${section}-${field.key}`;
    const wrapper = document.createElement('div');
    const input = document.createElement('input');

    input.id = id;
    input.dataset.section = section;
    input.dataset.key = field.key;

    if (field.type === 'checkbox') {
        input.type = 'checkbox';
        input.dataset.fieldType = 'checkbox';
        input.checked = String(value).trim().toLowerCase() === 'true';
        const label = document.createElement('label');
        label.htmlFor = id;
        label.textContent = field.key;
        wrapper.className = 'checkbox';
        wrapper.append(input, label);
        return wrapper;
    }

    input.type = 'text';
    input.dataset.fieldType = 'text';
    input.value = value === undefined || value === null ? '' : value;
    const label = document.createElement('label');
    label.htmlFor = id;
    label.textContent = field.key;
    wrapper.append(label, input);

    if (field.options) {
        const list = document.createElement('datalist');
        list.id = `${id}-options`;
        field.options.forEach((option) => {
            const item = document.createElement('option');
            item.value = option;
            list.appendChild(item);
        });
        input.setAttribute('list', list.id);
        wrapper.appendChild(list);
    }

    return wrapper;
}

function renderForm(config) {
    const form = document.getElementById('config-form');
    form.replaceChildren();

    Object.entries(SCHEMA).forEach(([section, fields]) => {
        const fieldset = document.createElement('fieldset');
        const legend = document.createElement('legend');
        legend.textContent = section;
        fieldset.appendChild(legend);

        const values = config[section] || {};
        fields.forEach((field) => {
            fieldset.appendChild(createInput(section, field, values[field.key]));
        });
        form.appendChild(fieldset);
    });

    const button = document.createElement('button');
    button.type = 'submit';
    button.textContent = 'Save';
    form.appendChild(button);
}

function buildPayload() {
    const payload = {};
    document.querySelectorAll('input[data-section]').forEach((input) => {
        const section = input.dataset.section;
        if (!payload[section]) {
            payload[section] = {};
        }
        payload[section][input.dataset.key] = input.dataset.fieldType === 'checkbox'
            ? (input.checked ? 'True' : 'False')
            : input.value;
    });
    return payload;
}

async function loadConfig() {
    try {
        const response = await fetch('/api/config');
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.message || 'Could not load configuration.');
        }
        renderForm(data);
    } catch (error) {
        showStatus(error.message, 'error');
    }
}

async function saveConfig(event) {
    event.preventDefault();
    try {
        const response = await fetch('/api/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(buildPayload()),
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.message || 'Could not save configuration.');
        }
        showStatus('Saved. Changes apply on the next scheduled run.', 'ok');
    } catch (error) {
        showStatus(error.message, 'error');
    }
}

document.getElementById('config-form').addEventListener('submit', saveConfig);
loadConfig();
