/* Employee Management System JavaScript Utilities */

document.addEventListener('DOMContentLoaded', function () {
    // Dark Mode Toggle Support
    const themeToggleBtn = document.getElementById('themeToggleBtn');
    const currentTheme = localStorage.getItem('theme') || 'light';

    if (currentTheme === 'dark') {
        document.documentElement.setAttribute('data-bs-theme', 'dark');
        if (themeToggleBtn) {
            themeToggleBtn.innerHTML = '<i class="bi bi-sun-fill text-warning fs-5"></i>';
        }
    }

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', function () {
            let theme = document.documentElement.getAttribute('data-bs-theme');
            if (theme === 'dark') {
                document.documentElement.setAttribute('data-bs-theme', 'light');
                localStorage.setItem('theme', 'light');
                themeToggleBtn.innerHTML = '<i class="bi bi-moon-stars-fill text-secondary fs-5"></i>';
            } else {
                document.documentElement.setAttribute('data-bs-theme', 'dark');
                localStorage.setItem('theme', 'dark');
                themeToggleBtn.innerHTML = '<i class="bi bi-sun-fill text-warning fs-5"></i>';
            }
        });
    }

    // Sidebar toggle handler
    const sidebarToggle = document.getElementById('sidebarToggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function (e) {
            e.preventDefault();
            document.getElementById('wrapper').classList.toggle('toggled');
        });
    }

    // Auto-dismiss alerts after 5 seconds
    const autoAlerts = document.querySelectorAll('.alert-dismissible');
    autoAlerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Dynamic Net Salary Calculation in Salary Forms
    const basicInput = document.getElementById('basicSalary');
    if (basicInput) {
        const hraInput = document.getElementById('hra');
        const daInput = document.getElementById('da');
        const bonusInput = document.getElementById('bonus');
        const incentivesInput = document.getElementById('incentives');
        const deductionsInput = document.getElementById('deductions');
        const taxInput = document.getElementById('tax');
        const netDisplay = document.getElementById('netSalaryDisplay');

        function calculateNetSalary() {
            const basic = parseFloat(basicInput.value) || 0;
            const hra = parseFloat(hraInput ? hraInput.value : 0) || 0;
            const da = parseFloat(daInput ? daInput.value : 0) || 0;
            const bonus = parseFloat(bonusInput ? bonusInput.value : 0) || 0;
            const incentives = parseFloat(incentivesInput ? incentivesInput.value : 0) || 0;
            const deductions = parseFloat(deductionsInput ? deductionsInput.value : 0) || 0;
            const tax = parseFloat(taxInput ? taxInput.value : 0) || 0;

            const gross = basic + hra + da + bonus + incentives;
            const totalDeductions = deductions + tax;
            const net = gross - totalDeductions;

            if (netDisplay) {
                netDisplay.value = net.toFixed(2);
            }
        }

        [basicInput, hraInput, daInput, bonusInput, incentivesInput, deductionsInput, taxInput].forEach(input => {
            if (input) {
                input.addEventListener('input', calculateNetSalary);
            }
        });

        calculateNetSalary(); // initial calculation
    }
});
