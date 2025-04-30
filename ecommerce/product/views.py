import random

from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect

from .forms import AddToCartForm
from .models import Category, Product

from ecommerce.cart.cart import Cart

def search(request):
    query = request.GET.get('query', '')
    products = Product.objects.filter(Q(title__icontains=query) | Q(description__icontains=query))

    return render(request, 'product/search.html', {'products': products, 'query': query})

def product(request, category_slug, product_slug):
    cart = Cart(request)

    queryset = Product.objects.filter(category__slug=category_slug, slug=product_slug)

    product = get_object_or_404(Product, category__slug=category_slug, slug=product_slug)

    if request.method == 'POST':
        form = AddToCartForm(request.POST)

        if form.is_valid():
            quantity = int(form.cleaned_data['quantity'])-1

            cart.add(product_id=product.id, quantity=quantity, update_quantity=True)

            messages.success(request, 'The product was added to the cart')

            # return redirect('product', category_slug=category_slug, product_slug=product_slug)
    else:
        form = AddToCartForm()

    similar_products = list(product.category.products.exclude(id=product.id))

    if len(similar_products) >= 4:
        similar_products = random.sample(similar_products, 4)

    context = {
        'form': form,
        'product': product,
        'similar_products': similar_products
    }

    return render(request, 'product/product.html', context)