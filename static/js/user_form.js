document.addEventListener('DOMContentLoaded', function() {
    // تفعيل دالة التحقق من الدور عند تحميل الصفحة
    const roleSelect = document.getElementById('id_role');
    if (roleSelect) {
        toggleGovernorateField(roleSelect.value);
        
        // إضافة مستمع لتغيير الدور
        roleSelect.addEventListener('change', function() {
            toggleGovernorateField(this.value);
        });
    }
});

function toggleGovernorateField(role) {
    const governorateField = document.getElementById('div_id_governorate');
    const governorateInput = document.getElementById('id_governorate');
    
    if (governorateField && governorateInput) {
        if (role === 'supervisor') {
            // إظهار حقل المحافظة وجعله إلزامي
            governorateField.style.display = 'block';
            governorateInput.required = true;
            
            // إضافة علامة الحقل الإلزامي
            const label = governorateField.querySelector('label');
            if (label && !label.innerHTML.includes('*')) {
                label.innerHTML += ' *';
            }
        } else {
            // إخفاء حقل المحافظة وجعله غير إلزامي
            governorateField.style.display = 'none';
            governorateInput.required = false;
            governorateInput.value = '';
        }
    }
}