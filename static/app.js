const cartInput = document.getElementById('cart-content');
const calculateBtn = document.getElementById('calculate-btn');
const resultContainer = document.getElementById('result-container');
const priceDisplay = document.getElementById('price-display');
const breakdownContainer = document.getElementById('breakdown-container');
const breakdownToggle = document.getElementById('breakdown-toggle');
const breakdownContent = document.getElementById('breakdown-content');

// Toggle breakdown visibility
breakdownToggle.addEventListener('click', () => {
    const isOpen = breakdownContent.style.display !== 'none';
    breakdownContent.style.display = isOpen ? 'none' : 'block';
    breakdownToggle.classList.toggle('open', !isOpen);
});

// Fill with movie names when Tab is pressed on empty textarea
cartInput.addEventListener('keydown', (e) => {
    if (e.key === 'Tab' && !cartInput.value.trim()) {
        e.preventDefault();
        const movieNames = "Back to the Future 1\nBack to the Future 2\nBack to the Future 3\nLa chèvre";
        cartInput.value = movieNames;
        console.log('Filled with:', cartInput.value);
    }
}, true);

calculateBtn.addEventListener('click', async () => {
    const content = cartInput.value;
    if (!content.trim()) {
        console.error("Cart content is empty.");
        priceDisplay.innerHTML = `<p style="color: #ff6b6b">Please enter items in the cart.</p>`;
        resultContainer.style.display = 'block';
        breakdownContainer.style.display = 'none';
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

        // Display breakdown if available
        if (data.breakdown) {
            displayBreakdown(data.breakdown);
            breakdownContainer.style.display = 'block';
            breakdownContent.style.display = 'none';
            breakdownToggle.classList.remove('open');
        }

    } catch (error) {
        console.error("Failed to calculate price:", error);
        priceDisplay.innerHTML = `<p style="color: #ff6b6b">${error.message}</p>`;
        resultContainer.style.display = 'block';
        breakdownContainer.style.display = 'none';
    } finally {
        calculateBtn.textContent = "Calculate Price";
        calculateBtn.disabled = false;
    }
});

function displayBreakdown(breakdown) {
    const itemsContainer = document.getElementById('breakdown-items');
    itemsContainer.innerHTML = '';

    // Display individual items
    breakdown.items.forEach(item => {
        const itemDiv = document.createElement('div');
        itemDiv.className = 'breakdown-item';

        const nameDiv = document.createElement('div');
        nameDiv.className = 'item-name';

        const titleSpan = document.createElement('span');
        titleSpan.className = 'item-title';

        // Always show count
        titleSpan.innerHTML = `${item.count}x&nbsp;&nbsp;&nbsp;&nbsp;${item.title}`;

        const seriesSpan = document.createElement('span');
        seriesSpan.className = 'item-series';
        seriesSpan.textContent = item.series
            ? `Franchise: ${item.series}`
            : 'Standalone';

        nameDiv.appendChild(titleSpan);
        nameDiv.appendChild(seriesSpan);

        const priceSpan = document.createElement('span');
        priceSpan.className = 'item-price';
        // Show total price for duplicated items
        const totalPrice = item.price * item.count;
        priceSpan.textContent = `€${totalPrice.toFixed(2)}`;

        itemDiv.appendChild(nameDiv);
        itemDiv.appendChild(priceSpan);

        itemsContainer.appendChild(itemDiv);
    });

    // Update summary
    document.getElementById('bttf-subtotal').textContent = `€${breakdown.bttf_subtotal.toFixed(2)}`;
    document.getElementById('bttf-total').textContent = `€${breakdown.bttf_total.toFixed(2)}`;
    document.getElementById('summary-total').textContent = `€${breakdown.total.toFixed(2)}`;

    // Show discount if applicable
    const discountRow = document.getElementById('discount-row');
    const otherRow = document.getElementById('other-row');

    if (breakdown.bttf_discount > 0) {
        document.getElementById('discount-percent').textContent = breakdown.discount_percentage.toFixed(0);
        document.getElementById('discount-amount').textContent = `-€${breakdown.bttf_discount.toFixed(2)}`;
        discountRow.style.display = 'flex';
    } else {
        discountRow.style.display = 'none';
    }

    // Show other movies total if applicable
    if (breakdown.other_total > 0) {
        document.getElementById('other-total').textContent = `€${breakdown.other_total.toFixed(2)}`;
        otherRow.style.display = 'flex';
    } else {
        otherRow.style.display = 'none';
    }
}
