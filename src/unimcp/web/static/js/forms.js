/**
 * forms.js
 * Handles dynamic HTML form generation based on JSON Schema
 */

const FormGenerator = {
    createInput: function(name, details) {
        const type = details.type || 'string';
        const required = details.required || false;
        const labelText = `${name}${required ? ' *' : ''}`;

        const wrapper = document.createElement('div');
        wrapper.className = 'flex flex-col gap-1 mb-4';

        const label = document.createElement('label');
        label.className = 'text-xs font-medium text-slate-400';
        label.innerText = labelText;
        wrapper.appendChild(label);

        let input;

        if (details.enum) {
            input = document.createElement('select');
            input.className = 'bg-slate-900 border border-slate-600 rounded px-3 py-2 text-sm text-white focus:ring-2 focus:ring-blue-500 outline-none';
            details.enum.forEach(opt => {
                const o = document.createElement('option');
                o.value = opt;
                o.text = opt;
                input.appendChild(o);
            });
        } else if (type === 'string') {
            input = document.createElement('input');
            input.type = 'text';
            input.className = 'bg-slate-900 border border-slate-600 rounded px-3 py-2 text-sm text-white focus:ring-2 focus:ring-blue-500 outline-none';
        } else if (type === 'number' || type === 'integer') {
            input = document.createElement('input');
            input.type = 'number';
            input.className = 'bg-slate-900 border border-slate-600 rounded px-3 py-2 text-sm text-white focus:ring-2 focus:ring-blue-500 outline-none';
        } else if (type === 'boolean') {
            input = document.createElement('input');
            input.type = 'checkbox';
            input.className = 'w-4 h-4 rounded text-blue-600 bg-slate-900 border-slate-600 focus:ring-blue-500';
            label.className = 'flex items-center gap-2 text-xs font-medium text-slate-400';
            label.appendChild(input);
            input.id = `check-${name}`;
            // Fix label placement for checkbox
            const textLabel = document.createElement('span');
            textLabel.innerText = labelText;
            label.appendChild(textLabel);
            wrapper.appendChild(label);
        } else {
            input = document.createElement('textarea');
            input.className = 'bg-slate-900 border border-slate-600 rounded px-3 py-2 text-sm text-white focus:ring-2 focus:ring-blue-500 outline-none';
            input.rows = 3;
        }

        if (input) {
            input.name = name;
            input.dataset.type = type;
            wrapper.appendChild(input);
        }

        return wrapper;
    },

    generateForm: function(schema, container) {
        container.innerHTML = '';
        const properties = schema.properties || {};
        const required = schema.required || [];

        if (Object.keys(properties).length === 0) {
            container.innerHTML = '<p class="text-slate-500 italic text-sm">This tool requires no arguments.</p>';
            return;
        }

        for (const [name, details] of Object.entries(properties)) {
            const input = this.createInput(name, { ...details, required: required.includes(name) });
            container.appendChild(input);
        }
    },

    getValues: function(container) {
        const args = {};
        const inputs = container.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            if (input.type === 'checkbox') {
                args[input.name] = input.checked;
            } else {
                args[input.name] = input.value;
            }
        });
        return args;
    }
};
