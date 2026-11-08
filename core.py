"""作者：Wangyuan；日期：2026-10-29；职责：显式商品的草稿/报价，不登录或发布。"""
import drafts,math

def run(payload):
    if not isinstance(payload,dict):raise TypeError('输入须对象')
    if 'text' in payload:return drafts.scan_compliance(str(payload['text']))
    products=payload.get('products',[])
    if not isinstance(products,list):raise TypeError('products须数组')
    ids=[p['id'] for p in products]
    if len(set(ids))!=len(ids):raise ValueError('ID重复')
    for row in products:
        for key in ['base_price','extra_unit_price']:
            price=float(row[key])
            if not math.isfinite(price) or price<0:raise ValueError('价格须非负有限值')
    drafts.PRODUCTS={row['id']:row for row in products}
    return {'listings':[drafts.build_listing(row['id']) for row in products],'quotes':[drafts.calculate_quote(row['id'],extra_units=payload.get('extra_units',0),rush=payload.get('rush',False)) for row in products],'notice':'提示规则仅是本地启发式，不证明符合任何现行平台规则；仅生成草稿。'}
