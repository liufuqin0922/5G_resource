// 文档就绪函数
document.addEventListener('DOMContentLoaded', function() {
    console.log('5G资源管理系统初始化完成');
    
    // 初始化提示框
    initializeTooltips();
    
    // 初始化表格排序
    initializeTableSort();
    
    // 初始化确认对话框
    initializeDeleteConfirmation();
    
    // 初始化表单验证
    initializeFormValidation();
    
    // 添加导航栏激活状态
    setActiveNavItem();
    
    // 添加表格搜索功能
    initializeTableSearch();
});

// 初始化Bootstrap提示框
function initializeTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// 设置导航栏当前项的激活状态
function setActiveNavItem() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href && currentPath.includes(href) && href !== '/') {
            link.classList.add('active');
        } else if (href === '/' && currentPath === '/') {
            link.classList.add('active');
        }
    });
}

// 初始化删除确认对话框
function initializeDeleteConfirmation() {
    const deleteButtons = document.querySelectorAll('.delete-confirm');
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('确定要删除这条记录吗？此操作不可恢复。')) {
                e.preventDefault();
            }
        });
    });
}

// 初始化表单验证
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
}

// 初始化表格排序功能
function initializeTableSort() {
    document.querySelectorAll('th.sortable').forEach(headerCell => {
        headerCell.addEventListener('click', () => {
            const table = headerCell.closest('table');
            const headerIndex = Array.prototype.indexOf.call(headerCell.parentElement.children, headerCell);
            const currentIsAscending = headerCell.classList.contains('th-sort-asc');
            
            // 清除所有标题的排序状态
            table.querySelectorAll('th').forEach(th => th.classList.remove('th-sort-asc', 'th-sort-desc'));
            
            // 设置新的排序状态
            headerCell.classList.toggle('th-sort-asc', !currentIsAscending);
            headerCell.classList.toggle('th-sort-desc', currentIsAscending);
            
            // 获取表格内容并排序
            const tableBody = table.querySelector('tbody');
            const rows = Array.from(tableBody.querySelectorAll('tr'));
            
            // 排序行
            const sortedRows = rows.sort((a, b) => {
                const aColText = a.querySelector(`td:nth-child(${headerIndex + 1})`).textContent.trim();
                const bColText = b.querySelector(`td:nth-child(${headerIndex + 1})`).textContent.trim();
                
                return currentIsAscending
                    ? aColText.localeCompare(bColText)
                    : bColText.localeCompare(aColText);
            });
            
            // 移除现有行并添加排序后的行
            while (tableBody.firstChild) {
                tableBody.removeChild(tableBody.firstChild);
            }
            
            tableBody.append(...sortedRows);
        });
    });
}

// 初始化表格搜索功能
function initializeTableSearch() {
    const searchInputs = document.querySelectorAll('.table-search');
    
    searchInputs.forEach(input => {
        input.addEventListener('keyup', function() {
            const searchValue = this.value.toLowerCase();
            const tableId = this.getAttribute('data-table-id');
            const table = document.getElementById(tableId);
            
            if (!table) return;
            
            const rows = table.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                let found = false;
                const cells = row.querySelectorAll('td');
                
                cells.forEach(cell => {
                    if (cell.textContent.toLowerCase().indexOf(searchValue) > -1) {
                        found = true;
                    }
                });
                
                row.style.display = found ? '' : 'none';
            });
        });
    });
}

// 显示通知消息
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show notification-alert`;
    notification.role = 'alert';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    document.body.appendChild(notification);
    
    // 5秒后自动关闭
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 5000);
}

// 格式化日期
function formatDate(dateString) {
    const date = new Date(dateString);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

// 导出表格为CSV
function exportTableToCSV(tableId, filename = 'export.csv') {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    let csv = [];
    const rows = table.querySelectorAll('tr');
    
    for (let i = 0; i < rows.length; i++) {
        const row = [], cols = rows[i].querySelectorAll('td, th');
        
        for (let j = 0; j < cols.length; j++) {
            // 引用字段值并处理逗号
            let data = cols[j].innerText.replace(/(\r\n|\n|\r)/gm, ' ').replace(/"/g, '""');
            row.push('"' + data + '"');
        }
        
        csv.push(row.join(','));
    }
    
    // 下载CSV文件
    const csvFile = new Blob([csv.join('\n')], {type: 'text/csv;charset=utf-8;'});
    const link = document.createElement('a');
    link.href = URL.createObjectURL(csvFile);
    link.setAttribute('download', filename);
    link.style.display = 'none';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
} 