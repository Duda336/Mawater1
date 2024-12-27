// Sample car data (in a real application, this would come from a backend)
const cars = [
    {
        id: 1,
        brand: 'BMW',
        model: 'M5',
        year: 2024,
        price: 85000,
        mileage: '15,000 km',
        location: 'Doha, Qatar',
        image: 'https://images.unsplash.com/photo-1555215695-3004980ad54e?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80',
        description: 'Luxury sedan with exceptional performance',
        features: ['Leather Seats', 'Navigation', 'Sunroof', 'Premium Sound System']
    },
    {
        id: 2,
        brand: 'Mercedes',
        model: 'S-Class',
        year: 2024,
        price: 95000,
        mileage: '10,000 km',
        location: 'Doha, Qatar',
        image: 'https://images.unsplash.com/photo-1618843479313-40f8afb4b4d8?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80',
        description: 'Ultimate luxury and comfort',
        features: ['Massage Seats', '360 Camera', 'Head-up Display', 'Driver Assistance']
    },
    {
        id: 3,
        brand: 'Audi',
        model: 'RS7',
        year: 2024,
        price: 120000,
        mileage: '5,000 km',
        location: 'Doha, Qatar',
        image: 'https://images.unsplash.com/photo-1503376780353-7e6692767b70?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80',
        description: 'Sporty performance with elegant design',
        features: ['Sport Package', 'Carbon Fiber', 'Bang & Olufsen Sound', 'RS Sport Exhaust']
    },
    {
        id: 4,
        brand: 'Toyota',
        model: 'Land Cruiser',
        year: 2024,
        price: 75000,
        mileage: '20,000 km',
        location: 'Doha, Qatar',
        image: 'https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80',
        description: 'Legendary SUV with ultimate reliability',
        features: ['4x4', 'Multi-terrain Select', 'Crawl Control', 'Premium Interior']
    }
];

let currentView = 'grid';
let currentPage = 1;
const itemsPerPage = 8;

// Function to create car cards
function createCarCard(car) {
    const features = car.features ? `
        <div class="car-features">
            ${car.features.map(feature => `<span class="feature-tag">${feature}</span>`).join('')}
        </div>
    ` : '';

    if (currentView === 'grid') {
        return `
            <div class="car-card">
                <img src="${car.image}" alt="${car.brand} ${car.model}" class="car-image">
                <div class="car-details">
                    <h3>${car.brand} ${car.model}</h3>
                    <p class="price">$${car.price.toLocaleString()}</p>
                    <p class="year">Year: ${car.year}</p>
                    <p class="mileage">Mileage: ${car.mileage}</p>
                    <p class="location"><i class="fas fa-map-marker-alt"></i> ${car.location}</p>
                    <p>${car.description}</p>
                    ${features}
                    <button class="cta-button" onclick="contactDealer(${car.id})">Contact Dealer</button>
                </div>
            </div>
        `;
    } else {
        return `
            <div class="car-card list-view">
                <img src="${car.image}" alt="${car.brand} ${car.model}" class="car-image">
                <div class="car-details">
                    <div class="car-info">
                        <h3>${car.brand} ${car.model}</h3>
                        <p class="price">$${car.price.toLocaleString()}</p>
                        <div class="car-specs">
                            <span><i class="fas fa-calendar"></i> ${car.year}</span>
                            <span><i class="fas fa-tachometer-alt"></i> ${car.mileage}</span>
                            <span><i class="fas fa-map-marker-alt"></i> ${car.location}</span>
                        </div>
                        <p>${car.description}</p>
                        ${features}
                    </div>
                    <div class="car-actions">
                        <button class="cta-button" onclick="contactDealer(${car.id})">Contact Dealer</button>
                    </div>
                </div>
            </div>
        `;
    }
}

// Function to filter cars
function filterCars() {
    const searchInput = document.getElementById('search-input')?.value.toLowerCase() || '';
    const brandFilter = document.getElementById('brand-filter')?.value.toLowerCase() || '';
    const priceFilter = document.getElementById('price-filter')?.value || '';
    const yearFilter = document.getElementById('year-filter')?.value || '';

    let filteredCars = cars;

    if (searchInput) {
        filteredCars = filteredCars.filter(car => 
            car.brand.toLowerCase().includes(searchInput) ||
            car.model.toLowerCase().includes(searchInput) ||
            car.description.toLowerCase().includes(searchInput)
        );
    }

    if (brandFilter) {
        filteredCars = filteredCars.filter(car => car.brand.toLowerCase() === brandFilter);
    }

    if (priceFilter) {
        const [min, max] = priceFilter.split('-').map(num => parseInt(num) || Infinity);
        filteredCars = filteredCars.filter(car => car.price >= min && car.price < max);
    }

    if (yearFilter) {
        filteredCars = filteredCars.filter(car => car.year.toString() === yearFilter);
    }

    displayCars(filteredCars);
    updatePagination(filteredCars.length);
}

// Function to display cars
function displayCars(carsToDisplay) {
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const paginatedCars = carsToDisplay.slice(startIndex, endIndex);
    
    const carListings = document.getElementById('car-listings');
    if (carListings) {
        carListings.innerHTML = paginatedCars.map(car => createCarCard(car)).join('');
    }
}

// Function to update pagination
function updatePagination(totalItems) {
    const totalPages = Math.ceil(totalItems / itemsPerPage);
    const pageInfo = document.getElementById('page-info');
    const prevButton = document.getElementById('prev-page');
    const nextButton = document.getElementById('next-page');

    if (pageInfo) pageInfo.textContent = `Page ${currentPage} of ${totalPages}`;
    if (prevButton) prevButton.disabled = currentPage === 1;
    if (nextButton) nextButton.disabled = currentPage === totalPages;
}

// Function to handle contact dealer
function contactDealer(carId) {
    const car = cars.find(c => c.id === carId);
    const message = `I'm interested in the ${car.year} ${car.brand} ${car.model}`;
    const contactForm = document.querySelector('#contact-form textarea');
    if (contactForm) {
        contactForm.value = message;
        document.querySelector('#contact').scrollIntoView({ behavior: 'smooth' });
    }
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    // Initialize car listings
    filterCars();

    // Add filter event listeners
    const filterElements = ['search-input', 'brand-filter', 'price-filter', 'year-filter'];
    filterElements.forEach(elementId => {
        const element = document.getElementById(elementId);
        if (element) {
            element.addEventListener('input', filterCars);
        }
    });

    // View toggle buttons
    const viewButtons = document.querySelectorAll('.view-button');
    viewButtons.forEach(button => {
        button.addEventListener('click', () => {
            currentView = button.dataset.view;
            viewButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            filterCars();
        });
    });

    // Pagination buttons
    const prevButton = document.getElementById('prev-page');
    const nextButton = document.getElementById('next-page');

    if (prevButton) {
        prevButton.addEventListener('click', () => {
            if (currentPage > 1) {
                currentPage--;
                filterCars();
            }
        });
    }

    if (nextButton) {
        nextButton.addEventListener('click', () => {
            const totalPages = Math.ceil(cars.length / itemsPerPage);
            if (currentPage < totalPages) {
                currentPage++;
                filterCars();
            }
        });
    }

    // Handle contact form submission
    const contactForm = document.getElementById('contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', (e) => {
            e.preventDefault();
            alert('Thank you for your message. We will contact you soon!');
            e.target.reset();
        });
    }

    // Handle sell car form submission
    const sellCarForm = document.getElementById('sell-car-form');
    if (sellCarForm) {
        sellCarForm.addEventListener('submit', (e) => {
            e.preventDefault();
            alert('Thank you for listing your car. Our team will review your submission and contact you soon!');
            e.target.reset();
        });
    }
});

// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth'
            });
        }
    });
});
