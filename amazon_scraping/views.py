from django.shortcuts import render
from .utils import fetch_data
# Create your views here.

def index(request):
    
    if request.method == "POST":
        query = request.POST["search"]
        if query is None or query == "":
            return render(request,"index.html",{"query":query,"error_message":"Please enter a query"})
        products = fetch_data(query)
        print(query)
        print(products)
        return render(request,"index.html",{"products":products,"query":query})
    return render(request,"index.html")