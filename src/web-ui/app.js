const SCHEMA = {
    Heating: [
        { key: 'ControlSource', type: 'select', options: ['internal', 'spot-hinta'] },
        { key: 'QuarterHourInterval', type: 'checkbox' },
        { key: 'HeatingHours', type: 'text' },
        { key: 'ConsecutiveHours', type: 'checkbox' },
    ],
    NordPool: [
        { key: 'DataSource', type: 'select', options: ['elering'] },
        { key: 'PriceArea', type: 'select', options: ['fi', 'ee'] },
        { key: 'TimeZone', type: 'select', options: ['Europe/Helsinki', 'UTC'] },
    ],
    Heatpump: [
        { key: 'TargetTemperature', type: 'text' },
        { key: 'OperationMode', type: 'select',
          options: ['heat', 'dry', 'cool', 'fan_only', 'heat_cool'] },
        { key: 'FanSpeed', type: 'select', options: ['auto', '1', '2', '3', '4', '5'] },
        { key: 'VaneHorizontal', type: 'select',
          options: ['auto', '1_left', '2', '3', '4', '5_right', 'split', 'swing'] },
        { key: 'VaneVertical', type: 'select',
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

function createCheckbox(section, field, value) {
    const id = `${section}-${field.key}`;
    const wrapper = document.createElement('div');
    const input = document.createElement('input');
    const label = document.createElement('label');

    input.type = 'checkbox';
    input.id = id;
    input.dataset.section = section;
    input.dataset.key = field.key;
    input.dataset.fieldType = 'checkbox';
    input.checked = String(value).trim().toLowerCase() === 'true';
    label.htmlFor = id;
    label.textContent = field.key;

    wrapper.className = 'checkbox';
    wrapper.append(input, label);
    return wrapper;
}

function createSelect(section, field, value) {
    const id = `${section}-${field.key}`;
    const wrapper = document.createElement('div');
    const label = document.createElement('label');
    const select = document.createElement('select');
    const current = value === undefined || value === null ? '' : String(value);
    const options = [...field.options];

    if (current !== '' && !options.includes(current)) {
        options.unshift(current);
    }

    label.htmlFor = id;
    label.textContent = field.key;
    select.id = id;
    select.dataset.section = section;
    select.dataset.key = field.key;
    select.dataset.fieldType = 'select';

    options.forEach((option) => {
        const item = document.createElement('option');
        item.value = option;
        item.textContent = option;
        item.selected = option === current;
        select.appendChild(item);
    });

    wrapper.append(label, select);
    return wrapper;
}

function createTextInput(section, field, value) {
    const id = `${section}-${field.key}`;
    const wrapper = document.createElement('div');
    const label = document.createElement('label');
    const input = document.createElement('input');

    label.htmlFor = id;
    label.textContent = field.key;
    input.type = 'text';
    input.id = id;
    input.dataset.section = section;
    input.dataset.key = field.key;
    input.dataset.fieldType = 'text';
    input.value = value === undefined || value === null ? '' : value;

    wrapper.append(label, input);
    return wrapper;
}

function createInput(section, field, value) {
    if (field.type === 'checkbox') {
        return createCheckbox(section, field, value);
    }
    if (field.type === 'select') {
        return createSelect(section, field, value);
    }
    return createTextInput(section, field, value);
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
    document.querySelectorAll('[data-section]').forEach((input) => {
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
