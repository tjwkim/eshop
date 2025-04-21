import json
import os
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, current_app

# 블루프린트 생성
main_bp = Blueprint('main', __name__)
cart_bp = Blueprint('cart', __name__, url_prefix='/cart')

# Jinja2 환경에 min 함수 추가
@main_bp.app_template_global()
def min_value(*args):
    return min(args)

# 자동차 부품 데이터 로드
def load_parts_data():
    json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'automobileParts.json')
    with open(json_path, 'r', encoding='utf-8') as file:
        return json.load(file)

# 메인 페이지 - 상품 목록 표시
@main_bp.route('/')
def index():
    parts = load_parts_data()
    page = request.args.get('page', 1, type=int)
    per_page = 8
    
    # 필터링 매개변수
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    manufacturer = request.args.get('manufacturer')
    
    # 검색 기능
    search_query = request.args.get('search', '')
    
    # 필터링 적용
    filtered_parts = parts
    
    if search_query:
        filtered_parts = [part for part in filtered_parts if 
                      search_query.lower() in part['name'].lower() or 
                      search_query.lower() in part['description'].lower() or
                      search_query.lower() in part['manufacturer'].lower()]
    
    if min_price is not None:
        filtered_parts = [part for part in filtered_parts if part['price'] >= min_price]
        
    if max_price is not None:
        filtered_parts = [part for part in filtered_parts if part['price'] <= max_price]
        
    if manufacturer:
        filtered_parts = [part for part in filtered_parts if part['manufacturer'] == manufacturer]
    
    # 정렬
    sort_by = request.args.get('sort_by', 'price')
    sort_order = request.args.get('sort_order', 'asc')
    
    if sort_by == 'price':
        filtered_parts = sorted(filtered_parts, key=lambda x: x['price'], 
                               reverse=(sort_order == 'desc'))
    elif sort_by == 'name':
        filtered_parts = sorted(filtered_parts, key=lambda x: x['name'], 
                               reverse=(sort_order == 'desc'))
    
    # 페이지네이션
    total_items = len(filtered_parts)
    total_pages = (total_items + per_page - 1) // per_page
    start_idx = (page - 1) * per_page
    end_idx = min(start_idx + per_page, total_items)
    current_parts = filtered_parts[start_idx:end_idx]
    
    # 제조사 목록 (필터용)
    manufacturers = sorted(list(set(part['manufacturer'] for part in parts)))
    
    return render_template('products.html', 
                          parts=current_parts, 
                          page=page,
                          total_pages=total_pages, 
                          search_query=search_query,
                          min_price=min_price,
                          max_price=max_price,
                          manufacturer=manufacturer,
                          manufacturers=manufacturers,
                          sort_by=sort_by,
                          sort_order=sort_order)

# 상품 상세 페이지
@main_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    parts = load_parts_data()
    product = next((part for part in parts if part['id'] == product_id), None)
    if product:
        return render_template('product_detail.html', product=product)
    return redirect(url_for('main.index'))

# 장바구니 관련 라우트
@cart_bp.route('/')
def view_cart():
    cart_items = session.get('cart', [])
    parts = load_parts_data()
    
    # 장바구니에 있는 상품 정보 가져오기
    cart_products = []
    total_price = 0
    
    for cart_item in cart_items:
        product = next((part for part in parts if part['id'] == cart_item['id']), None)
        if product:
            quantity = cart_item['quantity']
            item_total = product['price'] * quantity
            cart_products.append({
                'id': product['id'],
                'name': product['name'],
                'price': product['price'],
                'quantity': quantity,
                'item_total': item_total
            })
            total_price += item_total
    
    return render_template('cart.html', cart_items=cart_products, total_price=total_price)

@cart_bp.route('/add', methods=['POST'])
def add_to_cart():
    product_id = request.form.get('product_id', type=int)
    quantity = request.form.get('quantity', 1, type=int)
    
    # 장바구니에 추가
    cart = session.get('cart', [])
    
    # 이미 장바구니에 있는지 확인
    for item in cart:
        if item['id'] == product_id:
            item['quantity'] += quantity
            session['cart'] = cart
            return redirect(url_for('cart.view_cart'))
    
    # 새로운 상품 추가
    cart.append({'id': product_id, 'quantity': quantity})
    session['cart'] = cart
    
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/remove', methods=['POST'])
def remove_from_cart():
    product_id = request.form.get('product_id', type=int)
    
    cart = session.get('cart', [])
    cart = [item for item in cart if item['id'] != product_id]
    session['cart'] = cart
    
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/update', methods=['POST'])
def update_cart():
    product_id = request.form.get('product_id', type=int)
    quantity = request.form.get('quantity', 1, type=int)
    
    cart = session.get('cart', [])
    for item in cart:
        if item['id'] == product_id:
            item['quantity'] = quantity
            break
            
    session['cart'] = cart
    return redirect(url_for('cart.view_cart'))