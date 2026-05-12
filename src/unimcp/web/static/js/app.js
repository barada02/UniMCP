/**
 * app.js
 * Main frontend logic for UniMCP Dashboard
 */

const app = {
    state: {
        connected: false,
        currentTool: null,
        activeTab: 'explorer'
    },

    // --- UI Element Cache ---
    el: {
        endpoint: document.getElementById('endpoint'),
        btnConnect: document.getElementById('btn-connect'),
        btnDisconnect: document.getElementById('btn-disconnect'),
        connStatus: document.getElementById('conn-status'),
        viewExplorer: document.getElementById('view-explorer'),
        viewTester: document.getElementById('view-tester'),
        listTools: document.getElementById('list-tools'),
        listPrompts: document.getElementById('list-prompts'),
        listResources: document.getElementById('list-resources'),
        selectedToolName: document.getElementById('selected-tool-name'),
        selectedToolDesc: document.getElementById('selected-tool-desc'),
        dynamicForm: document.getElementById('dynamic-form'),
        resultContainer: document.getElementById('result-container'),
        resultOutput: document.getElementById('result-output'),
        btnExecute: document.getElementById('btn-execute')
    },

    // --- Navigation ---
    setTab: function(tab) {
        this.state.activeTab = tab;

        // Update tab buttons
        document.getElementById('tab-explorer').className = tab === 'explorer'
            ? 'px-4 py-2 text-sm font-medium rounded-t-lg transition-colors border-b-2 border-blue-500 bg-slate-700 text-white'
            : 'px-4 py-2 text-sm font-medium rounded-t-lg transition-colors border-b-2 border-transparent hover:bg-slate-700 text-slate-400';

        document.getElementById('tab-tester').className = tab === 'tester'
            ? 'px-4 py-2 text-sm font-medium rounded-t-lg transition-colors border-b-2 border-blue-500 bg-slate-700 text-white'
            : 'px-4 py-2 text-sm font-medium rounded-t-lg transition-colors border-b-2 border-transparent hover:bg-slate-700 text-slate-400';

        // Toggle views
        this.el.viewExplorer.classList.toggle('hidden', tab !== 'explorer');
        this.el.viewTester.classList.toggle('hidden', tab !== 'tester');
    },

    // --- Connection ---
    connect: async function() {
        const endpoint = this.el.endpoint.value;
        if (!endpoint) return alert('Please enter an endpoint');

        this.el.btnConnect.disabled = true;
        this.el.connStatus.innerText = 'Connecting...';
        this.el.connStatus.className = 'text-xs text-center py-2 rounded bg-slate-600 text-white';

        try {
            const res = await fetch('/api/connect', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ endpoint })
            });
            const data = await res.json();

            if (res.ok) {
                this.state.connected = true;
                this.updateConnectionUI(true);
                this.refreshExplorer();
            } else {
                throw new Error(data.detail || 'Connection failed');
            }
        } catch (e) {
            alert(e.message);
        } finally {
            this.el.btnConnect.disabled = false;
            this.updateConnectionUI(this.state.connected);
        }
    },

    disconnect: async function() {
        try {
            const res = await fetch('/api/disconnect', { method: 'POST' });
            if (res.ok) {
                this.state.connected = false;
                this.updateConnectionUI(false);
                this.refreshExplorer();
            }
        } catch (e) {
            alert('Failed to disconnect');
        }
    },

    updateConnectionUI: function(connected) {
        this.el.btnConnect.classList.toggle('hidden', connected);
        this.el.btnDisconnect.classList.toggle('hidden', !connected);

        if (connected) {
            this.el.connStatus.innerText = 'Connected';
            this.el.connStatus.className = 'text-xs text-center py-2 rounded bg-green-900 text-green-400 border border-green-700';
        } else {
            this.el.connStatus.innerText = 'Disconnected';
            this.el.connStatus.className = 'text-xs text-center py-2 rounded bg-slate-700 text-slate-400';
        }
    },

    // --- Explorer ---
    refreshExplorer: async function() {
        if (!this.state.connected) return;

        try {
            const res = await fetch('/api/explore');
            const data = await res.json();

            this.renderList(this.el.listTools, data.tools, 'tool');
            this.renderList(this.el.listPrompts, data.prompts, 'prompt');
            this.renderList(this.el.listResources, data.resources, 'resource');
        } catch (e) {
            console.error('Explorer refresh failed', e);
        }
    },

    renderList: function(container, items, type) {
        container.innerHTML = '';
        if (!items || items.length === 0) {
            container.innerHTML = '<p class="text-slate-500 italic text-sm">None available.</p>';
            return;
        }

        items.forEach(item => {
            const btn = document.createElement('button');
            btn.className = 'w-full text-left px-3 py-2 text-sm rounded bg-slate-700 hover:bg-slate-600 text-slate-200 transition-colors border border-slate-600 overflow-hidden text-ellipsis whitespace-nowrap';
            btn.innerText = item;

            if (type === 'tool') {
                btn.onclick = () => this.selectTool(item);
            }
            container.appendChild(btn);
        });
    },

    // --- Tool Tester ---
    selectTool: async function(name) {
        this.state.currentTool = name;
        this.setTab('tester');

        this.el.selectedToolName.innerText = name;
        this.el.selectedToolDesc.innerText = 'Loading details...';
        this.el.dynamicForm.innerHTML = '';
        this.el.resultContainer.classList.add('hidden');

        try {
            const res = await fetch(`/api/tool/${name}`);
            const details = await res.json();

            this.el.selectedToolDesc.innerText = details.description || 'No description provided.';
            FormGenerator.generateForm(details, this.el.dynamicForm);
        } catch (e) {
            this.el.selectedToolDesc.innerText = 'Error loading tool details.';
        }
    },

    executeTool: async function() {
        if (!this.state.currentTool) return;

        const args = FormGenerator.getValues(this.el.dynamicForm);
        this.el.btnExecute.disabled = true;
        this.el.resultContainer.classList.add('hidden');

        try {
            const res = await fetch('/api/execute', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    tool: this.state.currentTool,
                    arguments: args
                })
            });
            const data = await res.json();

            if (res.ok) {
                this.el.resultContainer.classList.remove('hidden');
                this.el.resultOutput.innerText = data.result;
            } else {
                alert('Execution failed: ' + (data.detail || 'Unknown error'));
            }
        } catch (e) {
            alert('Execution failed: ' + e.message);
        } finally {
            this.el.btnExecute.disabled = false;
        }
    },

    init: function() {
        const defaultEndpoint = document.getElementById('endpoint').value;
        if (defaultEndpoint) {
            // Initial run is just to set the UI, don't auto-connect
        }
    }
};

document.addEventListener('DOMContentLoaded', () => app.init());
