document.addEventListener('DOMContentLoaded', function() {
    // 수량 입력 필드의 최소값 제한
    const quantityInputs = document.querySelectorAll('input[name="quantity"]');
    quantityInputs.forEach(input => {
        input.addEventListener('change', function() {
            if (this.value < 1) {
                this.value = 1;
            }
        });
    });
});