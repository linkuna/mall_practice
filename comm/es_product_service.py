from sqlalchemy import func

from model import *
from utils.mysql_tool import data_to_dict
from es_model import EsProduct


# 导入全部商品
def import_all_impl():
    count = 0
    for product in get_product_list():
        print(product.keys())
        result = create_product(product)
        count += 1 if result else 0
    return count


def get_product_list(_id=None):
    """
    SQL 语句:
    select
            p.id id,
            p.product_sn productSn,
            p.brand_id brandId,
            p.brand_name brandName,
            p.product_category_id productCategoryId,
            p.product_category_name productCategoryName,
            p.pic pic,
            p.name name,
            p.sub_title subTitle,
            p.price price,
            p.sale sale,
            p.new_status newStatus,
            p.recommand_status recommandStatus,
            p.stock stock,
            p.promotion_type promotionType,
            p.keywords keywords,
            p.sort sort,
            pav.id attr_id,
            pav.value attr_value,
            pav.product_attribute_id attr_product_attribute_id,
            pa.type attr_type,
            pa.name attr_name
        from pms_product p
        left join pms_product_attribute_value pav on p.id = pav.product_id
        left join pms_product_attribute pa on pav.product_attribute_id= pa.id
        where delete_status = 0 and publish_status = 1 group by id;
    """
    product_query = db.session.query(p.id.label('_id'), p.product_sn.label('productSn'), p.brand_id.label('brandId'),
                                     p.brand_name.label('brandName'), p.product_category_id.label('productCategoryId'),
                                     p.product_category_name.label('productCategoryName'), p.pic,
                                     p.name, p.sub_title.label('subTitle'), p.price, p.sale,
                                     p.new_status.label('newStatus'), p.recommand_status.label('recommendStatus'),
                                     p.stock, p.promotion_type.label('promotionType'),
                                     p.keywords.label('keywords'),
                                     p.sort,
                                     pav.id.label('attr_id'), pav.value.label('attr_value'),
                                     pav.product_attribute_id.label('attr_product_attribute_id'),
                                     func.group_concat(pa.type).label('attr_type'),
                                     func.group_concat(pa.name).label('attr_name')) \
        .filter(p.delete_status == 0, p.publish_status == 1).join(pav, p.id == pav.product_id) \
        .join(pa, pav.product_attribute_id == pa.id)
    if _id is not None:
        product_list = product_query.filter(p.id == _id).all()
    else:
        product_list = product_query.all()
    product_map = {}
    for product in product_list:
        product_keys, product_attr_keys = product.keys[:-5], product.keys[-5:]
        if product[0] in product_map:
            es_product = product_map[product[0]]
        else:
            es_product = EsProduct(data_to_dict(product_keys, product[:-5]))
        es_product.add_attr_value(data_to_dict(product_attr_keys, product[-5:]))
        product_map[product[0]] = es_product

    for product in product_map.values():
        yield product


def get_product(_id):
    es_product = EsProduct.get(_id)
    return es_product


def delete_product(_id):
    es_product = EsProduct.get(_id)
    es_product.delete()


def create_product_by_id(_id):
    for product in get_product_list(_id):
        return create_product(product)


def recommend_product(_id):
    es_product = EsProduct.get(_id)
    es_product.update(recommendStatus=1)


def create_product(_id=None):
    es_product = EsProduct(**data_to_dict(product.keys(), product))
    return es_product.save()


def search_product(search_param):
    product_search = EsProduct.search().query("match", **search_param)
    res = product_search.execute()
    print(res)
    return {}
