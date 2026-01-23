const cartInput = document.getElementById('cart-content');
const calculateBtn = document.getElementById('calculate-btn');
const resultContainer = document.getElementById('result-container');
const priceDisplay = document.getElementById('price-display');

// Fill placeholder content when Tab is pressed on empty textarea
cartInput.addEventListener('keydown', (e) => {
    if (e.key === 'Tab' && !cartInput.value.trim()) {
        e.preventDefault();
        // Use placeholder directly - browser already decoded &#10; entities
        cartInput.value = cartInput.placeholder;
        console.log('Filled with:', cartInput.value);
    }
}, true);

calculateBtn.addEventListener('click', async () => {
    const content = cartInput.value;
    if (!content.trim()) {
        console.error("Cart content is empty.");
        priceDisplay.innerHTML = `<p style="color: #ff6b6b">Please enter items in the cart.</p>`;
        resultContainer.style.display = 'block';
        return;
    }

    // Show loading state (optional enhancement)
    calculateBtn.textContent = "Calculating...";
    calculateBtn.disabled = true;

    try {
        const response = await fetch('/api/v1/price', {
            method: 'POST',
            headers: {
                'Content-Type': 'text/plain'
            },
            body: content
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            let errorMessage = "Unknown error occurred.";

            if (errorData.detail && typeof errorData.detail === 'object') {
                if (errorData.detail.missing_movies) {
                    const missingMovies = errorData.detail.missing_movies.join(', ');
                    errorMessage = `Movie(s) not found: ${missingMovies}`;
                } else {
                    errorMessage = errorData.detail.message || JSON.stringify(errorData.detail);
                }
            } else {
                errorMessage = errorData.detail || `Error: ${response.statusText}`;
            }

            console.error("Error response from server:", errorMessage);
            throw new Error(errorMessage);
        }

        const data = await response.json();

        // Display result
        const price = data.price.toFixed(2);
        priceDisplay.innerHTML = `<h2>${price}<span class="currency">€</span></h2>`;
        resultContainer.style.display = 'block';

    } catch (error) {
        console.error("Failed to calculate price:", error);
        priceDisplay.innerHTML = `<p style="color: #ff6b6b">${error.message}</p>`;
        resultContainer.style.display = 'block';
    } finally {
        calculateBtn.textContent = "Calculate Price";
        calculateBtn.disabled = false;
    }
});
