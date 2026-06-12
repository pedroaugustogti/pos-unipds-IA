import { View } from './View.js';

export class ProductView extends View {
    #productList = document.querySelector('#productList');
    #sortSelect = document.querySelector('#sortSelect');

    #buttons;
    #productTemplate;
    #onBuyProduct;
    #currentProducts = [];
    #currentDisableButtons = true;

    constructor() {
        super();
        this.init();
    }

    async init() {
        this.#productTemplate = await this.loadTemplate('./src/view/templates/product-card.html');
        this.#sortSelect.addEventListener('change', () => this.#applySortAndRender());
    }

    onUserSelected(user) {
        this.setButtonsState(user.id ? false : true);
    }

    registerBuyProductCallback(callback) {
        this.#onBuyProduct = callback;
    }

    #sortProducts(products, sortBy) {
        const sorted = [...products];
        switch (sortBy) {
            case 'category':
                sorted.sort((a, b) => a.category.localeCompare(b.category));
                break;
            case 'price-asc':
                sorted.sort((a, b) => a.price - b.price);
                break;
            case 'price-desc':
                sorted.sort((a, b) => b.price - a.price);
                break;
            default:
                break;
        }
        return sorted;
    }

    #applySortAndRender() {
        const sorted = this.#sortProducts(this.#currentProducts, this.#sortSelect.value);
        this.#renderList(sorted, this.#currentDisableButtons);
    }

    render(products, disableButtons = true) {
        if (!this.#productTemplate) return;
        this.#currentProducts = products;
        this.#currentDisableButtons = disableButtons;
        this.#applySortAndRender();
    }

    #renderList(products, disableButtons) {
        const html = products.map(product => {
            return this.replaceTemplate(this.#productTemplate, {
                id: product.id,
                name: product.name,
                category: product.category,
                price: product.price,
                color: product.color,
                product: JSON.stringify(product)
            });
        }).join('');

        this.#productList.innerHTML = html;
        this.attachBuyButtonListeners();
        this.setButtonsState(disableButtons);
    }

    setButtonsState(disabled) {
        if (!this.#buttons) {
            this.#buttons = document.querySelectorAll('.buy-now-btn');
        }
        this.#buttons.forEach(button => {
            button.disabled = disabled;
        });
    }

    attachBuyButtonListeners() {
        this.#buttons = document.querySelectorAll('.buy-now-btn');
        this.#buttons.forEach(button => {

            button.addEventListener('click', (event) => {
                const product = JSON.parse(button.dataset.product);
                const originalText = button.innerHTML;

                button.innerHTML = '<i class="bi bi-check-circle-fill"></i> Added';
                button.classList.remove('btn-primary');
                button.classList.add('btn-success');
                setTimeout(() => {
                    button.innerHTML = originalText;
                    button.classList.remove('btn-success');
                    button.classList.add('btn-primary');
                }, 500);
                this.#onBuyProduct(product, button);

            });
        });
    }
}
