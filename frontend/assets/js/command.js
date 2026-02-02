/**
 * Raj Leads Generator - Power Features
 * Command Palette (Ctrl + K)
 */

const CommandPalette = {
    isOpen: false,
    selectedIndex: 0,
    commands: [
        { title: 'Search Leads', icon: 'fa-search', action: () => window.location.href = 'index.html', shortcut: 'S' },
        { title: 'View History', icon: 'fa-history', action: () => window.location.href = 'history.html', shortcut: 'H' },
        { title: 'Settings', icon: 'fa-gear', action: () => window.location.href = 'settings.html', shortcut: 'G' },
        { title: 'Toggle Theme', icon: 'fa-moon', action: () => document.getElementById('themeToggle')?.click(), shortcut: 'T' },
        {
            title: 'New Search', icon: 'fa-plus', action: () => {
                if (window.location.pathname.includes('index.html')) {
                    document.getElementById('keyword')?.focus();
                } else {
                    window.location.href = 'index.html';
                }
            }, shortcut: 'N'
        },
        { title: 'Export Results', icon: 'fa-file-excel', action: () => document.getElementById('exportBtn')?.click(), shortcut: 'E' }
    ],

    init() {
        this.createDOM();
        this.bindEvents();
    },

    createDOM() {
        if (document.querySelector('.cmd-backdrop')) return;

        const backdrop = document.createElement('div');
        backdrop.className = 'cmd-backdrop';
        backdrop.innerHTML = `
            <div class="cmd-modal">
                <div class="cmd-header">
                    <i class="fas fa-search"></i>
                    <input type="text" class="cmd-input" placeholder="Type a command...">
                    <span class="cmd-shortcut">Esc</span>
                </div>
                <div class="cmd-body"></div>
            </div>
        `;
        document.body.appendChild(backdrop);

        this.elements = {
            backdrop: backdrop,
            input: backdrop.querySelector('.cmd-input'),
            body: backdrop.querySelector('.cmd-body')
        };
    },

    bindEvents() {
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                this.toggle();
            }
            if (this.isOpen) {
                if (e.key === 'Escape') this.close();
                if (e.key === 'ArrowDown') this.navigate(1);
                if (e.key === 'ArrowUp') this.navigate(-1);
                if (e.key === 'Enter') this.execute();
            }
        });

        this.elements.input.addEventListener('input', (e) => {
            this.render(e.target.value);
        });

        this.elements.backdrop.addEventListener('click', (e) => {
            if (e.target === this.elements.backdrop) this.close();
        });
    },

    toggle() {
        this.isOpen = !this.isOpen;
        this.elements.backdrop.classList.toggle('active', this.isOpen);
        if (this.isOpen) {
            this.elements.input.value = '';
            this.elements.input.focus();
            this.render();
        }
    },

    close() {
        this.isOpen = false;
        this.elements.backdrop.classList.remove('active');
    },

    render(filter = '') {
        const filtered = this.commands.filter(cmd =>
            cmd.title.toLowerCase().includes(filter.toLowerCase())
        );

        this.elements.body.innerHTML = '';
        this.selectedIndex = 0;
        this.currentCommands = filtered;

        filtered.forEach((cmd, index) => {
            const item = document.createElement('div');
            item.className = `cmd-item ${index === 0 ? 'selected' : ''}`;
            item.innerHTML = `
                <i class="fas ${cmd.icon}"></i>
                <span>${cmd.title}</span>
                ${cmd.shortcut ? `<span class="cmd-shortcut">${cmd.shortcut}</span>` : ''}
            `;
            item.addEventListener('click', () => {
                this.execute(index);
            });
            item.addEventListener('mouseover', () => {
                this.selectedIndex = index;
                this.updateSelection();
            });
            this.elements.body.appendChild(item);
        });

        if (filtered.length === 0) {
            this.elements.body.innerHTML = '<div style="padding:1rem; color:var(--text-muted); text-align:center;">No commands found</div>';
        }
    },

    navigate(direction) {
        this.selectedIndex += direction;
        if (this.selectedIndex < 0) this.selectedIndex = this.currentCommands.length - 1;
        if (this.selectedIndex >= this.currentCommands.length) this.selectedIndex = 0;
        this.updateSelection();
    },

    updateSelection() {
        const items = this.elements.body.querySelectorAll('.cmd-item');
        items.forEach((item, index) => {
            item.classList.toggle('selected', index === this.selectedIndex);
            if (index === this.selectedIndex) item.scrollIntoView({ block: 'nearest' });
        });
    },

    execute(index = this.selectedIndex) {
        const cmd = this.currentCommands[index];
        if (cmd) {
            cmd.action();
            this.close();
        }
    }
};

document.addEventListener('DOMContentLoaded', () => CommandPalette.init());
