from utils.logging import view_logs_base,clear_logs



def view_Product_logs(request):
    return view_logs_base(request,'Product.jsonl')
    

def view_Product_Variant_logs(request):
    return view_logs_base(request,'ProductVariant.jsonl')

def delete_logs_product(request):
    return clear_logs(request,"Product.jsonl")

def delete_logs_product_variant(request):
    return clear_logs(request,'ProductVariant.jsonl')